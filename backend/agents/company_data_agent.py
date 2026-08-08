import re
import logging
from typing import Optional, Dict, Any, Tuple
from state.schema import AgentState
from company_data.service import CompanyDataService
from company_data.tools import (
    get_customer_by_email,
    get_customer_by_id,
    get_customer_orders,
    get_order_details,
    get_order_status,
    get_shipment_status,
    get_payment_status,
    get_product_details,
    get_customer_subscription,
)
from shared.persistence import _get_db

logger = logging.getLogger(__name__)


def is_policy_or_faq_inquiry(message: str) -> bool:
    msg = message.lower()
    policy_keywords = [
        "refund policy",
        "return policy",
        "shipping policy",
        "privacy policy",
        "terms of service",
        "what is your refund",
        "what is your return",
        "how do i return",
        "how to cancel policy",
        "warranty policy",
    ]
    return any(kw in msg for kw in policy_keywords)


def resolve_company_customer_id(state: AgentState) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolves the company_customer_id and customer name for the active contact.
    """
    comp_cust = state.get("company_customer")
    if comp_cust and comp_cust.get("customer_id"):
        return comp_cust["customer_id"], comp_cust.get("name")

    contact_id = state.get("customer_id")
    if not contact_id or contact_id == "anonymous":
        return None, None

    # Check SupportFlow DB for linked company_customer_id
    conn = _get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email, company_customer_id FROM supportflow.customers WHERE id = %s", (contact_id,)
            )
            row = cur.fetchone()
            if row:
                if row['company_customer_id']:
                    return row['company_customer_id'], None
                if row['email'] and "@" in row['email'] and not row['email'].endswith(".supportflow"):
                    comp_match = CompanyDataService().get_customer_by_email(row['email'])
                    if comp_match.get("found") and comp_match.get("customer"):
                        return comp_match["customer"]["customer_id"], comp_match["customer"]["name"]
    except Exception as e:
        logger.debug(f"DB lookup in resolve_company_customer_id failed: {e}")
    finally:
        conn.close()

    # Direct email match fallback
    if "@" in contact_id and not contact_id.endswith(".supportflow"):
        comp_match = CompanyDataService().get_customer_by_email(contact_id)
        if comp_match.get("found") and comp_match.get("customer"):
            return comp_match["customer"]["customer_id"], comp_match["customer"]["name"]

    return None, None


async def company_data_agent_node(state: AgentState) -> AgentState:
    logger.info("[COMPANY_DATA] Agent node invoked")
    message = state.get("customer_message", "")
    intent = state.get("intent", "")

    # Check if policy/FAQ inquiry -> skip company DB, let Knowledge Agent handle via RAG
    if is_policy_or_faq_inquiry(message):
        logger.info("[COMPANY_DATA] Policy/FAQ inquiry detected. Skipping company database search.")
        return {"company_data_context": None}

    # Extract parameters from message
    order_ids = re.findall(r"\bORD-\d+\b", message, re.IGNORECASE)
    product_ids = re.findall(r"\bPROD-\d+\b", message, re.IGNORECASE)
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", message)

    # Determine if company business data is required
    business_intents = {"order_status", "refund_request", "billing_issue", "account_issue", "product_question"}
    needs_company_data = (
        intent in business_intents
        or len(order_ids) > 0
        or len(product_ids) > 0
        or "order" in message.lower()
        or "shipment" in message.lower()
        or "tracking" in message.lower()
        or "payment" in message.lower()
        or "subscription" in message.lower()
        or "account" in message.lower()
    )

    if not needs_company_data:
        logger.info("[COMPANY_DATA] Business data not required for this request.")
        return {"company_data_context": None}

    # Public Product Query
    if product_ids or (intent == "product_question" and not order_ids and "order" not in message.lower()):
        query = product_ids[0] if product_ids else message
        logger.info(f"[COMPANY_DATA] Fetching public product details for: {query}")
        prod_res = get_product_details(query)
        if prod_res.get("found"):
            if "product" in prod_res:
                p = prod_res["product"]
                sec = (
                    f"Product Record:\n"
                    f"- Name: {p['product_name']}\n"
                    f"- Category: {p['category']}\n"
                    f"- Price: ${p['price']}\n"
                    f"- Stock Status: {p['stock_status']}\n"
                    f"- Description: {p['description']}"
                )
                return {"company_data_context": sec}
            elif "products" in prod_res:
                prods_summary = "\n".join([f"- {p['product_name']} (${p['price']}) - Status: {p['stock_status']}" for p in prod_res["products"]])
                return {"company_data_context": f"Matching Products:\n{prods_summary}"}

    # Resolve active customer identity for scoped account data
    company_customer_id, customer_name = resolve_company_customer_id(state)

    # If identity is unresolved, do NOT expose account data
    if not company_customer_id:
        logger.info("[COMPANY_DATA] Customer identity unresolved. Scoped data access denied.")
        return {
            "company_data_context": (
                "Identity Unresolved: To assist with account-specific information (such as orders, shipments, payments, or subscriptions), "
                "please log in to your account or provide the email address associated with your account."
            )
        }

    retrieved_sections = []

    # Scenario A: Order ID lookup (SCOPED & AUTHORIZED)
    if order_ids:
        for ord_id in set(order_ids):
            logger.info(f"[COMPANY_DATA] Scoped fetching for Order ID '{ord_id}' (User: {company_customer_id})")
            details = get_order_details(ord_id, company_customer_id)
            if details.get("found"):
                order_info = details["order"]
                shipment_info = details.get("shipment") or {}
                payment_info = details.get("payment") or {}
                items_info = details.get("items") or []

                item_names = ", ".join([f"{it['product_name']} (x{it['quantity']})" for it in items_info])
                sec = (
                    f"Order Record:\n"
                    f"- Order ID: {order_info['order_id']}\n"
                    f"- Date: {order_info['order_date']}\n"
                    f"- Status: {order_info['status']}\n"
                    f"- Total Amount: ${order_info['total_amount']} {order_info['currency']}\n"
                    f"- Items: {item_names if item_names else 'N/A'}\n"
                    f"- Expected Delivery: {order_info.get('expected_delivery_date') or 'N/A'}\n"
                    f"- Actual Delivery: {order_info.get('actual_delivery_date') or 'N/A'}\n"
                    f"- Carrier: {shipment_info.get('carrier', 'N/A')}\n"
                    f"- Tracking Number: {shipment_info.get('tracking_number', 'N/A')}\n"
                    f"- Shipment Status: {shipment_info.get('shipment_status', 'N/A')}\n"
                    f"- Payment Status: {payment_info.get('payment_status', 'N/A')}\n"
                    f"- Payment Method: {payment_info.get('payment_method', 'N/A')}"
                )
                retrieved_sections.append(sec)
            else:
                retrieved_sections.append(f"Order Search: Order '{ord_id}' was not found for your account.")

    # Scenario B: Subscription inquiry
    elif "subscription" in message.lower() or (intent == "account_issue" and "plan" in message.lower()):
        logger.info(f"[COMPANY_DATA] Scoped subscription fetch for customer: {company_customer_id}")
        sub_res = get_customer_subscription(company_customer_id)
        if sub_res.get("found"):
            sub = sub_res["subscription"]
            sec = (
                f"Subscription Record:\n"
                f"- Customer: {sub_res.get('customer_name')}\n"
                f"- Subscription ID: {sub['subscription_id']}\n"
                f"- Plan: {sub['plan']}\n"
                f"- Status: {sub['status']}\n"
                f"- Billing Cycle: {sub['billing_cycle']}\n"
                f"- Renewal Date: {sub['renewal_date']}\n"
                f"- Amount: ${sub['amount']}"
            )
            retrieved_sections.append(sec)
        else:
            retrieved_sections.append(sub_res.get("message", "No subscription record found for your account."))

    # Scenario C: Payment status inquiry
    elif "payment" in message.lower() or intent == "billing_issue":
        logger.info(f"[COMPANY_DATA] Scoped payment fetch for customer: {company_customer_id}")
        orders_res = get_customer_orders(company_customer_id, limit=1)
        if orders_res.get("found") and orders_res.get("orders"):
            latest_order = orders_res["orders"][0]
            payment_res = get_payment_status(latest_order["order_id"], company_customer_id)
            if payment_res.get("found"):
                sec = (
                    f"Payment Record for Order {latest_order['order_id']}:\n"
                    f"- Payment ID: {payment_res['payment_id']}\n"
                    f"- Payment Status: {payment_res['payment_status']}\n"
                    f"- Amount: ${payment_res['amount']}\n"
                    f"- Method: {payment_res['payment_method']}\n"
                    f"- Transaction Ref: {payment_res.get('transaction_reference', 'N/A')}\n"
                    f"- Date: {payment_res['payment_date']}"
                )
                retrieved_sections.append(sec)
            else:
                retrieved_sections.append(f"Payment Search: No payment record found for order {latest_order['order_id']}.")
        else:
            retrieved_sections.append("Payment Search: No orders found for your account.")

    # Scenario D: General Order / Shipment Inquiry ("Where is my order?")
    else:
        logger.info(f"[COMPANY_DATA] Scoped order fetch for customer: {company_customer_id}")
        orders_res = get_customer_orders(company_customer_id, limit=3)
        if orders_res.get("found") and orders_res.get("orders"):
            orders_summary = []
            for o in orders_res["orders"]:
                ship = o.get("shipment") or {}
                orders_summary.append(
                    f"Order {o['order_id']} | Status: {o['status']} | Date: {o['order_date']} | Total: ${o['total_amount']} | "
                    f"Carrier: {ship.get('carrier', 'N/A')} | Tracking: {ship.get('tracking_number', 'N/A')} | "
                    f"Shipment Status: {ship.get('shipment_status', 'N/A')} | Expected Delivery: {o.get('expected_delivery_date', 'N/A')}"
                )
            sec = f"Recent Orders for Customer {orders_res.get('customer_name')} ({orders_res.get('customer_id')}):\n" + "\n".join(orders_summary)
            retrieved_sections.append(sec)
        else:
            retrieved_sections.append(orders_res.get("message", "No recent orders found for your account."))

    context_str = "\n\n".join(retrieved_sections) if retrieved_sections else None
    logger.info(f"[COMPANY_DATA] Scoped context generated ({len(retrieved_sections)} sections).")
    return {"company_data_context": context_str}
