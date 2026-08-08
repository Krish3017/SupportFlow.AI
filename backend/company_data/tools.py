from typing import Dict, Any
from company_data.service import CompanyDataService

_service = CompanyDataService()


def get_customer_by_email(email: str) -> Dict[str, Any]:
    """
    Retrieve company customer details by email address.
    """
    if not email or not isinstance(email, str):
        return {"found": False, "error": "Invalid email parameter."}
    return _service.get_customer_by_email(email.strip())


def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
    """
    Retrieve company customer details by customer ID (e.g. CUST-1001).
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"found": False, "error": "Invalid customer_id parameter."}
    return _service.get_customer_by_id(customer_id.strip())


def get_customer_orders(customer_id_or_email: str, limit: int = 5) -> Dict[str, Any]:
    """
    Retrieve recent orders for a customer specified by ID or email.
    """
    if not customer_id_or_email or not isinstance(customer_id_or_email, str):
        return {"found": False, "error": "Invalid customer identifier parameter."}
    return _service.get_customer_orders(customer_id_or_email.strip(), limit=limit)


def get_order_details(order_id: str) -> Dict[str, Any]:
    """
    Retrieve full order details including line items, shipment, payment, and shipping address.
    """
    if not order_id or not isinstance(order_id, str):
        return {"found": False, "error": "Invalid order_id parameter."}
    return _service.get_order_details(order_id.strip())


def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Retrieve current order status, delivery dates, and tracking reference for an order.
    """
    if not order_id or not isinstance(order_id, str):
        return {"found": False, "error": "Invalid order_id parameter."}
    return _service.get_order_status(order_id.strip())


def get_shipment_status(order_id_or_tracking: str) -> Dict[str, Any]:
    """
    Retrieve shipment status and tracking details using an order ID or tracking number.
    """
    if not order_id_or_tracking or not isinstance(order_id_or_tracking, str):
        return {"found": False, "error": "Invalid shipment identifier parameter."}
    return _service.get_shipment_status(order_id_or_tracking.strip())


def get_payment_status(order_id_or_payment_id: str) -> Dict[str, Any]:
    """
    Retrieve payment status, payment method, amount, and transaction reference.
    """
    if not order_id_or_payment_id or not isinstance(order_id_or_payment_id, str):
        return {"found": False, "error": "Invalid payment identifier parameter."}
    return _service.get_payment_status(order_id_or_payment_id.strip())


def get_product_details(product_id_or_name: str) -> Dict[str, Any]:
    """
    Retrieve product specifications, price, and stock status by product ID or name query.
    """
    if not product_id_or_name or not isinstance(product_id_or_name, str):
        return {"found": False, "error": "Invalid product identifier parameter."}
    return _service.get_product_details(product_id_or_name.strip())


def get_customer_subscription(customer_id_or_email: str) -> Dict[str, Any]:
    """
    Retrieve customer subscription plan, billing cycle, renewal date, and status.
    """
    if not customer_id_or_email or not isinstance(customer_id_or_email, str):
        return {"found": False, "error": "Invalid customer identifier parameter."}
    return _service.get_customer_subscription(customer_id_or_email.strip())


COMPANY_DATA_TOOLS = {
    "get_customer_by_email": get_customer_by_email,
    "get_customer_by_id": get_customer_by_id,
    "get_customer_orders": get_customer_orders,
    "get_order_details": get_order_details,
    "get_order_status": get_order_status,
    "get_shipment_status": get_shipment_status,
    "get_payment_status": get_payment_status,
    "get_product_details": get_product_details,
    "get_customer_subscription": get_customer_subscription,
}
