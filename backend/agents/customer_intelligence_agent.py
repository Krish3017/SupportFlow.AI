from state.schema import AgentState
from database import get_customer
from company_data.service import CompanyDataService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

company_service = CompanyDataService()


async def customer_intelligence_agent_node(state: AgentState) -> AgentState:
    logger.info("👤 CUSTOMER INTELLIGENCE AGENT CALLED")
    customer_id = state.get("customer_id")
    logger.info(f"🔍 Looking up customer: {customer_id}")

    company_customer = None
    if customer_id and customer_id != "anonymous":
        comp_match = company_service.find_customer(customer_id)
        if comp_match:
            company_customer = comp_match
            logger.info(f"✅ Company customer matched: {comp_match.get('name')} ({comp_match.get('customer_id')}) | Tier: {comp_match.get('customer_tier')}")

    if not customer_id or customer_id == "anonymous":
        logger.info("ℹ️  No customer ID provided, using anonymous context")
        return {"customer_context": None, "company_customer": company_customer}

    customer = get_customer(customer_id)
    if customer:
        logger.info(f"✅ SupportFlow Customer found: {customer.get('name')} | Tier: {customer.get('tier')}")
    else:
        logger.info(f"⚠️  Customer {customer_id} not found in SupportFlow database")

    return {"customer_context": customer, "company_customer": company_customer}