from state.schema import AgentState
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def priority_agent_node(state: AgentState) -> AgentState:
    logger.info("⚡ PRIORITY AGENT CALLED")
    intent = state.get("intent")
    sentiment = state.get("sentiment")
    confidence = state.get("confidence", 1.0)
    customer = state.get("customer_context") or {}
    tier = customer.get("tier", "free")

    # Start with base priority
    priority = "low"

    if tier == "vip":
        priority = "high"
    elif tier == "premium":
        priority = "medium"

    # Upgrade based on intent and sentiment
    if intent in ["refund_request", "billing_issue"] and sentiment == "negative":
        priority = "critical"
    elif intent == "complaint" and sentiment == "negative":
        priority = "high"
    elif confidence < 0.6:
        priority = "high"

    logger.info(f"✅ Priority assigned: {priority} | Intent: {intent} | Sentiment: {sentiment} | Tier: {tier}")
    return {"priority": priority}