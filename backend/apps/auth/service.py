import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import uuid4
from shared.persistence import _get_db, ensure_contact, link_contact_company_customer
from company_data.service import CompanyDataService
from core.errors import SupportFlowException, ValidationError
from core.logging_config import get_logger

logger = get_logger(__name__)

SESSION_EXPIRE_HOURS = 24 * 7  # 7 days session


def hash_password(password: str) -> str:
    """
    Hashes a password securely using PBKDF2 HMAC SHA256 with random salt.
    """
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}${hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a plain password against the stored salt$hash string.
    """
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(computed_hash, expected_hash)
    except Exception:
        return False


class AuthService:
    """
    Customer Identity & Authentication Service.
    """

    def _create_session(self, customer_id: str) -> str:
        token = f"sf_sess_{uuid4().hex}"
        now = datetime.utcnow()
        expires = now + timedelta(hours=SESSION_EXPIRE_HOURS)
        conn = _get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO supportflow.customer_sessions (session_token, customer_id, created_at, expires_at)
                    VALUES (%s, %s, %s, %s)
                """, (token, customer_id, now.isoformat(), expires.isoformat()))
            conn.commit()
        finally:
            conn.close()
        return token

    def register_customer(self, email: str, password: str, name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        email_clean = email.strip().lower()
        if not email_clean or "@" not in email_clean:
            raise ValidationError("A valid email address is required.", details={"code": "INVALID_EMAIL"})
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.", details={"code": "WEAK_PASSWORD"})

        conn = _get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, password_hash, company_customer_id FROM supportflow.customers WHERE LOWER(email) = LOWER(%s)", (email_clean,))
                existing = cur.fetchone()
                pw_hash = hash_password(password)

                if existing:
                    if existing['password_hash']:
                        raise ValidationError("A customer account with this email already exists.", details={"code": "USER_EXISTS"})
                    contact_id = existing['id']
                    cur.execute(
                        "UPDATE supportflow.customers SET password_hash = %s, name = COALESCE(%s, name) WHERE id = %s",
                        (pw_hash, name or email_clean.split("@")[0], contact_id)
                    )
                    company_cust_id = existing['company_customer_id']
                else:
                    contact_id = f"cust_{uuid4().hex[:12]}"
                    now = datetime.utcnow().isoformat()
                    cur.execute("""
                        INSERT INTO supportflow.customers (id, name, email, password_hash, tier, sentiment, joined_date, last_interaction)
                        VALUES (%s, %s, %s, %s, 'standard', 'neutral', %s, %s)
                    """, (contact_id, name or email_clean.split("@")[0], email_clean, pw_hash, now, now))
                    company_cust_id = None

            conn.commit()
        finally:
            conn.close()

        # Company Customer exact email match
        if not company_cust_id:
            try:
                comp_res = CompanyDataService().get_customer_by_email(email_clean)
                if comp_res.get("found") and comp_res.get("customer"):
                    company_cust_id = comp_res["customer"]["customer_id"]
                    link_contact_company_customer(contact_id, company_cust_id)
            except Exception as e:
                logger.error(f"Company DB matching error during registration: {e}")

        token = self._create_session(contact_id)
        user_info = {
            "id": contact_id,
            "email": email_clean,
            "name": name or email_clean.split("@")[0],
            "company_customer_id": company_cust_id,
        }
        return token, user_info

    def login_customer(self, email: str, password: str) -> Tuple[str, Dict[str, Any]]:
        email_clean = email.strip().lower()
        conn = _get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, email, password_hash, company_customer_id FROM supportflow.customers WHERE LOWER(email) = LOWER(%s)",
                    (email_clean,)
                )
                row = cur.fetchone()

            if not row or not row['password_hash']:
                raise ValidationError("Invalid email or password.", details={"code": "INVALID_CREDENTIALS"})

            if not verify_password(password, row['password_hash']):
                raise ValidationError("Invalid email or password.", details={"code": "INVALID_CREDENTIALS"})

            contact_id = row['id']
            company_cust_id = row['company_customer_id']
        finally:
            conn.close()

        # Attempt exact company customer email match if not set
        if not company_cust_id:
            try:
                comp_res = CompanyDataService().get_customer_by_email(email_clean)
                if comp_res.get("found") and comp_res.get("customer"):
                    company_cust_id = comp_res["customer"]["customer_id"]
                    link_contact_company_customer(contact_id, company_cust_id)
            except Exception:
                pass

        token = self._create_session(contact_id)
        user_info = {
            "id": contact_id,
            "email": row['email'],
            "name": row['name'],
            "company_customer_id": company_cust_id,
        }
        return token, user_info

    def logout_customer(self, token: str) -> bool:
        if not token:
            return True
        conn = _get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM supportflow.customer_sessions WHERE session_token = %s", (token,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_authenticated_customer(self, token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        conn = _get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.session_token, c.id, c.name, c.email, c.company_customer_id
                    FROM supportflow.customer_sessions s
                    JOIN supportflow.customers c ON s.customer_id = c.id
                    WHERE s.session_token = %s
                """, (token,))
                row = cur.fetchone()

            if not row:
                return None

            company_cust_id = row['company_customer_id']
            if not company_cust_id and row['email']:
                try:
                    comp_res = CompanyDataService().get_customer_by_email(row['email'])
                    if comp_res.get("found") and comp_res.get("customer"):
                        company_cust_id = comp_res["customer"]["customer_id"]
                        link_contact_company_customer(row['id'], company_cust_id)
                except Exception:
                    pass

            return {
                "id": row['id'],
                "email": row['email'],
                "name": row['name'],
                "company_customer_id": company_cust_id,
            }
        finally:
            conn.close()
