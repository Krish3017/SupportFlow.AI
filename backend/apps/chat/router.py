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


@router.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    async def generate():
        try:
            start_time = time.time()

            contact_id = ensure_contact(request.customer_id, "chat")
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
            record_execution_steps(execution_id, result, request.message, duration)
            complete_execution(execution_id, result, duration)

            final_response = result.get("final_response", "I apologize, but I couldn't generate a response.")

            store_assistant_message(conversation_id, final_response, execution_id)
            create_ticket_on_escalation(conversation_id, contact_id, result)
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

            words = final_response.split()
            for word in words:
                chunk = json.dumps({"content": word + " "})
                yield f"data: {chunk}\n\n"

            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'conversation_id': conversation_id})}\n\n"

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            emit_activity("system", f"Chat error: {str(e)}", level="error")
            yield f"data: {json.dumps({'content': 'Sorry, an error occurred.'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    from shared.persistence import _get_db
    conn = _get_db()
    try:
        conv = conn.execute(
            "SELECT id, status FROM conversations WHERE id = ?",
            (conversation_id,)
        ).fetchone()

        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = conn.execute("""
            SELECT id, role, content, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,)).fetchall()

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
async def get_session_conversation(session_id: str):
    from shared.persistence import _get_db
    conn = _get_db()
    try:
        conv = conn.execute("""
            SELECT id, status FROM conversations
            WHERE session_token = ? AND status NOT IN ('closed', 'archived')
            ORDER BY updated_at DESC LIMIT 1
        """, (session_id,)).fetchone()

        if not conv:
            return {"conversation_id": None, "status": None}

        return {"conversation_id": conv['id'], "status": conv['status']}
    finally:
        conn.close()
