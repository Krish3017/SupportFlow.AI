from state.schema import AgentState
from database import get_customer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def customer_intelligence_agent_node(state: AgentState) -> AgentState:
    logger.info("👤 CUSTOMER INTELLIGENCE AGENT CALLED")
    customer_id = state.get("customer_id")
    logger.info(f"🔍 Looking up customer: {customer_id}")

    if not customer_id or customer_id == "anonymous":
        logger.info("ℹ️  No customer ID provided, using anonymous context")
        return {"customer_context": None}

    customer = get_customer(customer_id)
    if customer:
        logger.info(f"✅ Customer found: {customer.get('name')} | Tier: {customer.get('tier')} | Orders: {customer.get('total_orders')}")
    else:
        logger.info(f"⚠️  Customer {customer_id} not found in database")

    return {"customer_context": customer}