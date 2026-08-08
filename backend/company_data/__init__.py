"""
Company Data Module
Provides an isolated company business database, repository, service layer, and agent tools.
"""

from company_data.connection import get_company_db_connection, get_company_db, get_company_db_path
from company_data.schema import create_company_schema
from company_data.seed import seed_company_database
from company_data.repository import CompanyRepository
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
    COMPANY_DATA_TOOLS,
)

__all__ = [
    "get_company_db_connection",
    "get_company_db",
    "get_company_db_path",
    "create_company_schema",
    "seed_company_database",
    "CompanyRepository",
    "CompanyDataService",
    "get_customer_by_email",
    "get_customer_by_id",
    "get_customer_orders",
    "get_order_details",
    "get_order_status",
    "get_shipment_status",
    "get_payment_status",
    "get_product_details",
    "get_customer_subscription",
    "COMPANY_DATA_TOOLS",
]
