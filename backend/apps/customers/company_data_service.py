"""
Company Data Admin Service
--------------------------
Provides admin-side access to company business data for a SupportFlow customer.

Access pattern enforced:
  SupportFlow customer → customers.company_customer_id → Company DB

Rules:
- company_customer_id must be resolved from SupportFlow DB first.
- No arbitrary customer lookup by name or unverified email.
- No company data is copied into SupportFlow DB.
- Returns structured dicts — does not expose SQLite row objects directly.
"""
from typing import Optional, Dict, Any, List
from shared.persistence import _get_db
from company_data.service import CompanyDataService
from core.errors import NotFoundError, ForbiddenError
from core.logging_config import get_logger

logger = get_logger(__name__)

_company_service = CompanyDataService()


def _resolve_company_customer_id(sf_customer_id: str) -> Optional[str]:
    """
    Look up company_customer_id from the SupportFlow customers table
    using the SupportFlow customer's own ID.  Never trusts a caller-supplied
    company_customer_id directly.
    """
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT company_customer_id FROM customers WHERE id = ?",
            (sf_customer_id,)
        ).fetchone()
        return row['company_customer_id'] if row else None
    finally:
        conn.close()


def get_company_profile_for_customer(sf_customer_id: str) -> Dict[str, Any]:
    """
    Return the company business profile for a SupportFlow customer.
    Raises NotFoundError if the SupportFlow customer does not exist.
    Returns {"linked": False} if no company_customer_id mapping exists yet.
    """
    conn = _get_db()
    try:
        sf_row = conn.execute(
            "SELECT id, email, company_customer_id FROM customers WHERE id = ?",
            (sf_customer_id,)
        ).fetchone()
    finally:
        conn.close()

    if not sf_row:
        raise NotFoundError(resource="Customer", identifier=sf_customer_id)

    company_customer_id = sf_row['company_customer_id']
    if not company_customer_id:
        return {"linked": False, "company_customer_id": None}

    result = _company_service.get_customer_by_id(company_customer_id)
    if not result.get("found"):
        # Mapping exists but company record is missing — treat as unlinked
        logger.warning(
            f"SupportFlow customer {sf_customer_id} has stale company_customer_id "
            f"{company_customer_id} — no matching company record found."
        )
        return {"linked": False, "company_customer_id": company_customer_id, "stale": True}

    return {
        "linked": True,
        "company_customer_id": company_customer_id,
        "profile": result["customer"],
    }


def get_orders_for_customer(sf_customer_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Return recent orders for a SupportFlow customer via the company_customer_id mapping.
    """
    company_customer_id = _resolve_company_customer_id(sf_customer_id)
    if not company_customer_id:
        return {"linked": False, "orders": []}

    return _company_service.get_customer_orders_scoped(company_customer_id, limit=limit)


def get_order_detail_for_customer(sf_customer_id: str, order_id: str) -> Dict[str, Any]:
    """
    Return a specific order's detail, verified against the SupportFlow customer mapping.
    Raises ForbiddenError if the order does not belong to this customer.
    """
    company_customer_id = _resolve_company_customer_id(sf_customer_id)
    if not company_customer_id:
        raise ForbiddenError("Customer has no linked company account.")

    result = _company_service.get_order_details_scoped(order_id, company_customer_id)
    if not result.get("found"):
        raise NotFoundError(resource="Order", identifier=order_id)

    return result


def get_subscription_for_customer(sf_customer_id: str) -> Dict[str, Any]:
    """
    Return subscription details for a SupportFlow customer.
    """
    company_customer_id = _resolve_company_customer_id(sf_customer_id)
    if not company_customer_id:
        return {"linked": False, "subscription": None}

    return _company_service.get_customer_subscription_scoped(company_customer_id)
