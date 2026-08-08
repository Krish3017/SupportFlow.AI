from typing import Dict, Any
from company_data.service import CompanyDataService

_service = CompanyDataService()


def get_customer_by_email(email: str) -> Dict[str, Any]:
    if not email or not isinstance(email, str):
        return {"found": False, "error": "Invalid email parameter."}
    return _service.get_customer_by_email(email.strip())


def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
    if not customer_id or not isinstance(customer_id, str):
        return {"found": False, "error": "Invalid customer_id parameter."}
    return _service.get_customer_by_id(customer_id.strip())


def get_customer_orders(company_customer_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Retrieve orders for the authenticated customer only.
    """
    if not company_customer_id or not isinstance(company_customer_id, str):
        return {"found": False, "error": "Identity unresolved. Cannot retrieve orders."}
    return _service.get_customer_orders_scoped(company_customer_id.strip(), limit=limit)


def get_order_details(order_id: str, company_customer_id: str) -> Dict[str, Any]:
    """
    Retrieve order details ONLY if the order belongs to the authenticated customer.
    """
    if not order_id or not isinstance(order_id, str):
        return {"found": False, "error": "Invalid order_id parameter."}
    return _service.get_order_details_scoped(order_id.strip(), company_customer_id)


def get_order_status(order_id: str, company_customer_id: str) -> Dict[str, Any]:
    """
    Retrieve order status ONLY if the order belongs to the authenticated customer.
    """
    if not order_id or not isinstance(order_id, str):
        return {"found": False, "error": "Invalid order_id parameter."}
    return _service.get_order_status_scoped(order_id.strip(), company_customer_id)


def get_shipment_status(order_id_or_tracking: str, company_customer_id: str) -> Dict[str, Any]:
    """
    Retrieve shipment status ONLY if the order belongs to the authenticated customer.
    """
    if not order_id_or_tracking or not isinstance(order_id_or_tracking, str):
        return {"found": False, "error": "Invalid shipment identifier parameter."}
    return _service.get_shipment_status_scoped(order_id_or_tracking.strip(), company_customer_id)


def get_payment_status(order_id_or_payment_id: str, company_customer_id: str) -> Dict[str, Any]:
    """
    Retrieve payment status ONLY if it belongs to the authenticated customer.
    """
    if not order_id_or_payment_id or not isinstance(order_id_or_payment_id, str):
        return {"found": False, "error": "Invalid payment identifier parameter."}
    return _service.get_payment_status_scoped(order_id_or_payment_id.strip(), company_customer_id)


def get_product_details(product_id_or_name: str) -> Dict[str, Any]:
    """
    Retrieve public product catalog details.
    """
    if not product_id_or_name or not isinstance(product_id_or_name, str):
        return {"found": False, "error": "Invalid product identifier parameter."}
    return _service.get_product_details(product_id_or_name.strip())


def get_customer_subscription(company_customer_id: str) -> Dict[str, Any]:
    """
    Retrieve subscription details for the authenticated customer only.
    """
    if not company_customer_id or not isinstance(company_customer_id, str):
        return {"found": False, "error": "Identity unresolved. Cannot retrieve subscription."}
    return _service.get_customer_subscription_scoped(company_customer_id.strip())


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
