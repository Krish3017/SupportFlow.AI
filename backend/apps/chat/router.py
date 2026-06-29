"""
Chat Module Router
Customer-facing chat API with full persistence
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from state.schema import AgentState
from agents.intent_agent import intent_agent_node
from agents.knowledge_agent import knowledge_agent_node
from agents.resolution_agent import resolution_agent_node
from agents.escalation_agent import escalation_agent_node
from agents.customer_intelligence_agent import customer_intelligence_agent_node
from agents.priority_agent import priority_agent_node
from langgraph.graph import StateGraph, START, END
from database import save_conversation
from shared.persistence import persist_workflow_result, emit_activity
from uuid import uuid4
from collections import defaultdict
from core.logging_config import get_logger
import json

logger = get_logger(__name__)

sessions: dict = defaultdict(list)

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

# Build LangGraph workflow
graph = StateGraph(AgentState)
graph.add_node("intent_agent", intent_agent_node)
graph.add_node("customer_intelligence_agent", customer_intelligence_agent_node)
graph.add_node("priority_agent", priority_agent_node)
graph.add_node("knowledge_agent", knowledge_agent_node)
graph.add_node("resolution_agent", resolution_agent_node)
graph.add_node("escalation_agent", escalation_agent_node)

graph.add_edge(START, "intent_agent")
graph.add_edge("intent_agent", "customer_intelligence_agent")
graph.add_edge("customer_intelligence_agent", "priority_agent")
graph.add_conditional_edges("priority_agent", should_use_knowledge)
graph.add_edge("knowledge_agent", "resolution_agent")
graph.add_edge("resolution_agent", "escalation_agent")
graph.add_edge("escalation_agent", END)
workflow = graph.compile()

@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"🚀 NEW REQUEST: {request.message}")

    session_id = request.session_id or str(uuid4())

    sessions[session_id].append({
        "role": "user",
        "content": request.message
    })

    async def generate():
        try:
            result = await workflow.ainvoke({
                "customer_message": request.message,
                "customer_id": request.customer_id,
                "session_id": session_id,
                "chat_history": sessions[session_id]
            })

            # Legacy persistence (conversations table)
            save_conversation(result)

            # New persistence (tickets, customers, executions, messages, activity)
            try:
                persist_workflow_result(
                    customer_id=request.customer_id,
                    session_id=session_id,
                    channel="chat",
                    message=request.message,
                    result=result,
                )
            except Exception as pe:
                logger.warning(f"Persistence error (non-blocking): {pe}")

            final_response = result.get("final_response", "I apologize, but I couldn't generate a response.")

            sessions[session_id].append({
                "role": "assistant",
                "content": final_response
            })

            words = final_response.split()
            for word in words:
                chunk = json.dumps({"content": word + " "})
                yield f"data: {chunk}\n\n"

            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            emit_activity("system", f"Chat error: {str(e)}", level="error")
            yield f"data: {json.dumps({'content': 'Sorry, an error occurred.'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
