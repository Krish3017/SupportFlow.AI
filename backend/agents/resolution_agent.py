from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from state.schema import AgentState
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatGroq(
    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0"))
)

RESOLUTION_PROMPT = """You are a helpful customer support agent for ShopEase, an e-commerce company.

Use the provided context (company data and/or knowledge base) to answer the customer's question accurately and politely.
If company data context contains order, shipment, payment, or subscription details, summarize them directly and clearly for the customer.
If specific required information is missing from the context, politely ask the customer for clarification.
If the context does not contain enough information and cannot be resolved, say you will escalate to a human agent.

Keep responses concise, friendly, and professional.

Context:
{context}

Customer Intent: {intent}
"""

async def resolution_agent_node(state: AgentState) -> AgentState:
    logger.info("💬 RESOLUTION AGENT CALLED")
    message = state.get("customer_message")
    retrieved_context = state.get("retrieved_context", "")
    company_data_context = state.get("company_data_context", "")
    intent = state.get("intent", "general_inquiry")
    chat_history = state.get("chat_history", [])

    context_parts = []
    if company_data_context:
        context_parts.append(f"--- Company Business Data ---\n{company_data_context}")
    if retrieved_context:
        context_parts.append(f"--- Knowledge Base / Policies ---\n{retrieved_context}")

    context = "\n\n".join(context_parts) if context_parts else "No specific context available."

    logger.info(f"🎯 Generating response for intent: {intent}")

    messages = [
        SystemMessage(content=RESOLUTION_PROMPT.format(context=context, intent=intent))
    ]

    # Add chat history except current message
    for msg in chat_history[:-1]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Add current message
    messages.append(HumanMessage(content=message))

    response = await llm.ainvoke(messages)

    logger.info(f"✅ Final response generated: {response.content[:100]}...")
    return {"final_response": response.content}