from typing import Optional, Dict, Any, List
from company_data.repository import CompanyRepository


class CompanyDataService:
    """
    Company Data Service Layer.
    Encapsulates business operations and enforces strict customer-scoped data access security.
    """

    def __init__(self, repo: Optional[CompanyRepository] = None):
        self.repo = repo or CompanyRepository()

    def find_customer(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Resolves customer by customer_id, email, or phone.
        """
        if not identifier:
            return None
        identifier = identifier.strip()
        if "@" in identifier:
            return self.repo.get_customer_by_email(identifier)
        if identifier.upper().startswith("CUST-"):
            cust = self.repo.get_customer_by_id(identifier.upper())
            if cust:
                return cust
        if identifier.startswith("+") or identifier.replace("-", "").isdigit():
            cust = self.repo.get_customer_by_phone(identifier)
            if cust:
                return cust
        # Fallbacks
        cust = self.repo.get_customer_by_id(identifier)
        if cust:
            return cust
        return self.repo.get_customer_by_email(identifier)

    def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        customer = self.repo.get_customer_by_email(email)
        if not customer:
            return {"found": False, "message": f"No customer found with email '{email}'."}
        addresses = self.repo.get_addresses_by_customer_id(customer["customer_id"])
        customer_data = dict(customer)
        customer_data["addresses"] = addresses
        return {"found": True, "customer": customer_data}

    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        customer = self.repo.get_customer_by_id(customer_id)
        if not customer:
            return {"found": False, "message": f"No customer found with ID '{customer_id}'."}
        addresses = self.repo.get_addresses_by_customer_id(customer["customer_id"])
        customer_data = dict(customer)
        customer_data["addresses"] = addresses
        return {"found": True, "customer": customer_data}

    # =========================================================================
    # AUTHORIZED / SCOPED DATA ACCESS METHODS
    # All methods require company_customer_id of the authenticated user
    # =========================================================================

    def get_customer_orders_scoped(self, company_customer_id: str, limit: int = 5) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved. Please log in or provide registered email."}

        customer = self.repo.get_customer_by_id(company_customer_id)
        if not customer:
            return {"found": False, "message": f"Customer '{company_customer_id}' not found."}

        orders = self.repo.get_customer_orders(company_customer_id, limit=limit)
        enriched_orders = []
        for o in orders:
            order_info = dict(o)
            order_info["shipment"] = self.repo.get_shipment_by_order_id(o["order_id"])
            order_info["payment"] = self.repo.get_payment_by_order_id(o["order_id"])
            enriched_orders.append(order_info)

        return {
            "found": True,
            "customer_id": customer["customer_id"],
            "customer_name": customer["name"],
            "orders_count": len(enriched_orders),
            "orders": enriched_orders,
        }

    def get_order_details_scoped(self, order_id: str, company_customer_id: str) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved. Cannot verify order ownership."}

        order = self.repo.get_order_by_id(order_id)
        if not order or order["customer_id"] != company_customer_id:
            return {"found": False, "message": f"Order '{order_id}' was not found for your account."}

        customer = self.repo.get_customer_by_id(company_customer_id)
        items = self.repo.get_order_items(order["order_id"])
        payment = self.repo.get_payment_by_order_id(order["order_id"])
        shipment = self.repo.get_shipment_by_order_id(order["order_id"])
        shipping_address = None
        if order.get("shipping_address_id"):
            shipping_address = self.repo.get_address_by_id(order["shipping_address_id"])

        return {
            "found": True,
            "order": dict(order),
            "customer": customer,
            "items": items,
            "payment": payment,
            "shipment": shipment,
            "shipping_address": shipping_address,
        }

    def get_order_status_scoped(self, order_id: str, company_customer_id: str) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved. Cannot verify order ownership."}

        order = self.repo.get_order_by_id(order_id)
        if not order or order["customer_id"] != company_customer_id:
            return {"found": False, "message": f"Order '{order_id}' was not found for your account."}

        shipment = self.repo.get_shipment_by_order_id(order["order_id"])
        return {
            "found": True,
            "order_id": order["order_id"],
            "order_date": order["order_date"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "currency": order["currency"],
            "expected_delivery_date": order["expected_delivery_date"],
            "actual_delivery_date": order["actual_delivery_date"],
            "tracking_information": order["tracking_information"],
            "shipment_status": shipment["shipment_status"] if shipment else "no_shipment_record",
            "carrier": shipment["carrier"] if shipment else None,
            "tracking_number": shipment["tracking_number"] if shipment else None,
        }

    def get_shipment_status_scoped(self, order_id_or_tracking: str, company_customer_id: str) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved."}

        shipment = None
        if order_id_or_tracking.upper().startswith("ORD-"):
            shipment = self.repo.get_shipment_by_order_id(order_id_or_tracking)
        else:
            shipment = self.repo.get_shipment_by_tracking(order_id_or_tracking)
            if not shipment:
                shipment = self.repo.get_shipment_by_order_id(order_id_or_tracking)

        if not shipment:
            return {"found": False, "message": f"No shipment record found for '{order_id_or_tracking}'."}

        order = self.repo.get_order_by_id(shipment["order_id"])
        if not order or order["customer_id"] != company_customer_id:
            return {"found": False, "message": f"No shipment record found for your account matching '{order_id_or_tracking}'."}

        return {
            "found": True,
            "shipment_id": shipment["shipment_id"],
            "order_id": shipment["order_id"],
            "carrier": shipment["carrier"],
            "tracking_number": shipment["tracking_number"],
            "shipment_status": shipment["shipment_status"],
            "shipped_at": shipment["shipped_at"],
            "estimated_delivery": shipment["estimated_delivery"],
            "delivered_at": shipment["delivered_at"],
            "order_status": order["status"],
        }

    def get_payment_status_scoped(self, order_id_or_payment_id: str, company_customer_id: str) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved."}

        payment = None
        if order_id_or_payment_id.upper().startswith("PAY-"):
            payment = self.repo.get_payment_by_id(order_id_or_payment_id)
        else:
            payment = self.repo.get_payment_by_order_id(order_id_or_payment_id)

        if not payment or payment["customer_id"] != company_customer_id:
            return {"found": False, "message": f"No payment record found for your account matching '{order_id_or_payment_id}'."}

        return {
            "found": True,
            "payment_id": payment["payment_id"],
            "order_id": payment["order_id"],
            "customer_id": payment["customer_id"],
            "amount": payment["amount"],
            "payment_method": payment["payment_method"],
            "payment_status": payment["payment_status"],
            "transaction_reference": payment["transaction_reference"],
            "payment_date": payment["payment_date"],
        }

    def get_product_details(self, product_id_or_name: str) -> Dict[str, Any]:
        product = None
        if product_id_or_name.upper().startswith("PROD-"):
            product = self.repo.get_product_by_id(product_id_or_name)

        if not product:
            products = self.repo.get_products_by_name(product_id_or_name)
            if products:
                return {"found": True, "products": products}
            return {"found": False, "message": f"No product found for query '{product_id_or_name}'."}

        return {"found": True, "product": product}

    def get_customer_subscription_scoped(self, company_customer_id: str) -> Dict[str, Any]:
        if not company_customer_id:
            return {"found": False, "message": "Identity unresolved."}

        customer = self.repo.get_customer_by_id(company_customer_id)
        if not customer:
            return {"found": False, "message": f"Customer '{company_customer_id}' not found."}

        sub = self.repo.get_subscription_by_customer_id(company_customer_id)
        if not sub:
            return {
                "found": False,
                "customer_id": customer["customer_id"],
                "customer_name": customer["name"],
                "message": "No active or past subscription found for your account.",
            }

        return {
            "found": True,
            "customer_id": customer["customer_id"],
            "customer_name": customer["name"],
            "subscription": sub,
        }
