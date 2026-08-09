from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from state.schema import AgentState
from agents.intent_agent import intent_agent_node
from agents.knowledge_agent import knowledge_agent_node
from agents.resolution_agent import resolution_agent_node
from agents.escalation_agent import escalation_agent_node
from agents.customer_intelligence_agent import customer_intelligence_agent_node
from agents.priority_agent import priority_agent_node
from agents.company_data_agent import company_data_agent_node
from langgraph.graph import StateGraph, START, END
from shared.persistence import (
    ensure_contact,
    get_or_create_conversation,
    store_user_message,
    create_execution,
    complete_execution,
    record_execution_steps,
    store_assistant_message,
    create_ticket_on_escalation,
    update_contact_stats,
    emit_activity,
    get_conversation_messages,
)
from uuid import uuid4
from core.logging_config import get_logger
import time
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    customer_id: str = "anonymous"
    session_id: str = ""


def should_use_knowledge(state: AgentState) -> str:
    intent = state.get("intent")
    knowledge_intents = [
        "order_status",
        "refund_request",
        "technical_issue",
        "product_question",
        "billing_issue",
        "account_issue"
    ]
    if intent in knowledge_intents:
        return "knowledge_agent"
    return "resolution_agent"


graph = StateGraph(AgentState)
graph.add_node("intent_agent", intent_agent_node)
graph.add_node("customer_intelligence_agent", customer_intelligence_agent_node)
graph.add_node("priority_agent", priority_agent_node)
graph.add_node("company_data_agent", company_data_agent_node)
graph.add_node("knowledge_agent", knowledge_agent_node)
graph.add_node("resolution_agent", resolution_agent_node)
graph.add_node("escalation_agent", escalation_agent_node)

graph.add_edge(START, "intent_agent")
graph.add_edge("intent_agent", "customer_intelligence_agent")
graph.add_edge("customer_intelligence_agent", "priority_agent")
graph.add_edge("priority_agent", "company_data_agent")
graph.add_conditional_edges("company_data_agent", should_use_knowledge)
graph.add_edge("knowledge_agent", "resolution_agent")
graph.add_edge("resolution_agent", "escalation_agent")
graph.add_edge("escalation_agent", END)
workflow = graph.compile()


from fastapi import APIRouter, HTTPException, Header, Cookie
from apps.auth.service import AuthService

@router.post("/chat")
async def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    sf_session: Optional[str] = Cookie(None)
):
    session_id = request.session_id or str(uuid4())
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif sf_session:
        token = sf_session.strip()

    target_customer_id = request.customer_id
    if token:
        auth_cust = AuthService().get_authenticated_customer(token)
        if auth_cust:
            target_customer_id = auth_cust["id"]

    async def generate():
        try:
            start_time = time.time()

            contact_id = ensure_contact(target_customer_id, "chat")
            conversation_id = get_or_create_conversation(contact_id, "chat", session_id)
            chat_history = get_conversation_messages(conversation_id)

            user_msg_id = store_user_message(conversation_id, request.message)
            execution_id = create_execution(user_msg_id, conversation_id)

            chat_history.append({"role": "user", "content": request.message})

            result = await workflow.ainvoke({
                "customer_message": request.message,
                "customer_id": contact_id,
                "session_id": session_id,
                "chat_history": chat_history
            })

            duration = time.time() - start_time
            final_response = result.get("final_response", "I apologize, but I couldn't generate a response.")

            # Critical Persistence: Store assistant message and ticket on escalation
            try:
                store_assistant_message(conversation_id, final_response, execution_id)
                create_ticket_on_escalation(conversation_id, contact_id, result)
            except Exception as e:
                logger.error(f"Failed critical conversation persistence: {e}", exc_info=True)

            # Stream response chunks to client immediately
            words = final_response.split()
            for word in words:
                chunk = json.dumps({"content": word + " "})
                yield f"data: {chunk}\n\n"

            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'conversation_id': conversation_id})}\n\n"

            # Non-critical telemetry and observatory recording (post-stream)
            try:
                record_execution_steps(execution_id, result, request.message, duration)
                complete_execution(execution_id, result, duration)
                update_contact_stats(contact_id, result)
                emit_activity(
                    "conversation",
                    f"[CHAT] {result.get('intent', 'unknown')} from {contact_id}",
                    metadata={
                        "conversation_id": conversation_id,
                        "execution_id": execution_id,
                        "channel": "chat",
                        "intent": result.get("intent"),
                    }
                )
            except Exception as e:
                logger.error(f"Failed non-critical telemetry persistence: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            try:
                emit_activity("system", f"Chat error: {str(e)}", level="error")
            except Exception:
                pass
            yield f"data: {json.dumps({'content': 'Sorry, an error occurred.'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"


    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    authorization: Optional[str] = Header(None),
    sf_session: Optional[str] = Cookie(None)
):
    from shared.persistence import _get_db
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif sf_session:
        token = sf_session.strip()

    authenticated_customer_id = None
    if token:
        auth_cust = AuthService().get_authenticated_customer(token)
        if auth_cust:
            authenticated_customer_id = auth_cust["id"]

    conn = _get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, status, contact_id FROM supportflow.conversations WHERE id = %s",
                (conversation_id,)
            )
            conv = cur.fetchone()

            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Security check: If request is authenticated, ensure customer owns this conversation
            if authenticated_customer_id and conv['contact_id'] != authenticated_customer_id:
                raise HTTPException(status_code=403, detail="Access denied to this conversation.")

            cur.execute("""
                SELECT id, role, content, timestamp
                FROM supportflow.messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """, (conversation_id,))
            messages = cur.fetchall()

        return {
            "conversation_id": conv['id'],
            "status": conv['status'],
            "messages": [
                {
                    "id": m['id'],
                    "role": m['role'],
                    "content": m['content'],
                    "timestamp": m['timestamp'],
                }
                for m in messages
            ]
        }
    finally:
        conn.close()


@router.get("/chat/session/{session_id}")
async def get_session_conversation(
    session_id: str,
    authorization: Optional[str] = Header(None),
    sf_session: Optional[str] = Cookie(None)
):
    from shared.persistence import _get_db
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif sf_session:
        token = sf_session.strip()

    authenticated_customer_id = None
    if token:
        auth_cust = AuthService().get_authenticated_customer(token)
        if auth_cust:
            authenticated_customer_id = auth_cust["id"]

    conn = _get_db()
    try:
        with conn.cursor() as cur:
            if authenticated_customer_id:
                cur.execute("""
                    SELECT id, status FROM supportflow.conversations
                    WHERE contact_id = %s AND status NOT IN ('closed', 'archived')
                    ORDER BY updated_at DESC LIMIT 1
                """, (authenticated_customer_id,))
                conv = cur.fetchone()
                if conv:
                    return {"conversation_id": conv['id'], "status": conv['status']}
                return {"conversation_id": None, "status": None}

            cur.execute("""
                SELECT id, status, contact_id FROM supportflow.conversations
                WHERE session_token = %s AND status NOT IN ('closed', 'archived')
                ORDER BY updated_at DESC LIMIT 1
            """, (session_id,))
            conv = cur.fetchone()

            if not conv:
                return {"conversation_id": None, "status": None}

            if conv['contact_id'] and not conv['contact_id'].startswith("anon_"):
                return {"conversation_id": None, "status": None}

            return {"conversation_id": conv['id'], "status": conv['status']}
    finally:
        conn.close()
