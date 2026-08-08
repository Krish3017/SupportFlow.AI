import re
import logging
from typing import Optional, Dict, Any
from state.schema import AgentState
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

logger = logging.getLogger(__name__)


def is_policy_or_faq_inquiry(message: str) -> bool:
    """
    Returns True if the message is a general policy/FAQ inquiry (which should use RAG/Knowledge base).
    """
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


async def company_data_agent_node(state: AgentState) -> AgentState:
    """
    Company Data Agent Node.
    Determines whether company business data is needed, invokes controlled tools,
    and attaches formatted company data context to the state.
    """
    logger.info("[COMPANY_DATA] Agent node invoked")
    message = state.get("customer_message", "")
    intent = state.get("intent", "")
    customer_id = state.get("customer_id", "")
    company_customer = state.get("company_customer") or state.get("customer_context") or {}

    # Check if policy/FAQ inquiry -> skip company DB, let Knowledge Agent handle via RAG
    if is_policy_or_faq_inquiry(message):
        logger.info("[COMPANY_DATA] Policy/FAQ inquiry detected. Skipping company database search.")
        return {"company_data_context": None}

    # Extract potential identifiers from message via regex
    order_ids = re.findall(r"\bORD-\d+\b", message, re.IGNORECASE)
    customer_ids = re.findall(r"\bCUST-\d+\b", message, re.IGNORECASE)
    product_ids = re.findall(r"\bPROD-\d+\b", message, re.IGNORECASE)
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", message)

    target_email = emails[0] if emails else company_customer.get("email")
    if not target_email and customer_id and "@" in customer_id:
        target_email = customer_id

    target_customer_id = customer_ids[0].upper() if customer_ids else company_customer.get("customer_id")
    if not target_customer_id and customer_id and customer_id.upper().startswith("CUST-"):
        target_customer_id = customer_id.upper()

    customer_identifier = target_customer_id or target_email

    # Determine if company business data is required based on intent and query
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

    retrieved_sections = []

    # Scenario A: Explicit Order ID given in prompt or state
    if order_ids:
        for ord_id in set(order_ids):
            logger.info(f"[COMPANY_DATA] Fetching details for Order ID: {ord_id}")
            details = get_order_details(ord_id)
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
                retrieved_sections.append(f"Order Search: No order record found for Order ID '{ord_id}'.")

    # Scenario B: Subscription inquiry
    elif "subscription" in message.lower() or (intent == "account_issue" and "plan" in message.lower()):
        if customer_identifier:
            logger.info(f"[COMPANY_DATA] Fetching subscription for customer: {customer_identifier}")
            sub_res = get_customer_subscription(customer_identifier)
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
                retrieved_sections.append(sub_res.get("message", "No subscription record found."))
        else:
            retrieved_sections.append(
                "Subscription Search: Customer identifier missing. Please ask customer to provide their registered email address or customer ID."
            )

    # Scenario C: Payment status inquiry without explicit order ID
    elif "payment" in message.lower() or intent == "billing_issue":
        if customer_identifier:
            logger.info(f"[COMPANY_DATA] Fetching recent order payment status for customer: {customer_identifier}")
            orders_res = get_customer_orders(customer_identifier, limit=1)
            if orders_res.get("found") and orders_res.get("orders"):
                latest_order = orders_res["orders"][0]
                payment_res = get_payment_status(latest_order["order_id"])
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
                    retrieved_sections.append(f"Payment Search: No payment found for latest order {latest_order['order_id']}.")
            else:
                retrieved_sections.append(orders_res.get("message", "No orders found for customer to check payment status."))
        else:
            retrieved_sections.append(
                "Payment Search: Customer identifier missing. Please ask customer for order ID or registered email."
            )

    # Scenario D: Product details query
    elif product_ids or intent == "product_question":
        query = product_ids[0] if product_ids else message
        logger.info(f"[COMPANY_DATA] Fetching product details for: {query}")
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
                retrieved_sections.append(sec)
            elif "products" in prod_res:
                prods_summary = "\n".join([f"- {p['product_name']} (${p['price']}) - Status: {p['stock_status']}" for p in prod_res["products"]])
                retrieved_sections.append(f"Matching Products:\n{prods_summary}")
        else:
            retrieved_sections.append(prod_res.get("message", "No product details found."))

    # Scenario E: General Order / Shipment Inquiry ("Where is my order?")
    elif customer_identifier:
        logger.info(f"[COMPANY_DATA] Fetching customer orders for customer: {customer_identifier}")
        orders_res = get_customer_orders(customer_identifier, limit=3)
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
            retrieved_sections.append(orders_res.get("message", "No recent orders found for this customer."))
    else:
        retrieved_sections.append(
            "Customer matching: Unable to identify customer or order ID. Please ask the customer to provide their order ID or registered email address."
        )

    context_str = "\n\n".join(retrieved_sections) if retrieved_sections else None
    logger.info(f"[COMPANY_DATA] Context generated ({len(retrieved_sections)} sections).")
    return {"company_data_context": context_str}
