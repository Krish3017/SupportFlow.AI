from state.schema import AgentState
from shared.persistence import get_customer, link_contact_company_customer
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
    customer = None

    if customer_id and customer_id != "anonymous":
        customer = get_customer(customer_id)

        # 1. Try finding company customer directly via customer_id
        comp_match = company_service.find_customer(customer_id)
        if comp_match:
            company_customer = comp_match

        # 2. If not matched, try via linked company_customer_id or email from SupportFlow DB
        if not company_customer and customer:
            comp_cust_id = customer.get("company_customer_id")
            cust_email = customer.get("email")

            if comp_cust_id:
                direct_match = company_service.repo.get_customer_by_id(comp_cust_id)
                if direct_match:
                    company_customer = dict(direct_match)
            elif cust_email and "@" in cust_email and not cust_email.endswith(".supportflow"):
                comp_res = company_service.get_customer_by_email(cust_email)
                if comp_res.get("found") and comp_res.get("customer"):
                    company_customer = comp_res["customer"]
                    if customer.get("id"):
                        link_contact_company_customer(customer["id"], company_customer["customer_id"])

        if company_customer:
            logger.info(f"✅ Company customer matched: {company_customer.get('name')} ({company_customer.get('customer_id')}) | Tier: {company_customer.get('customer_tier')}")

    if not customer_id or customer_id == "anonymous":
        logger.info("ℹ️ No customer ID provided, using anonymous context")
        return {"customer_context": None, "company_customer": company_customer}

    if customer:
        logger.info(f"✅ SupportFlow Customer found: {customer.get('name')} | Tier: {customer.get('tier')}")
    else:
        logger.info(f"⚠️ Customer {customer_id} not found in SupportFlow database")

    return {"customer_context": customer, "company_customer": company_customer}