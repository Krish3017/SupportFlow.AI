import hmac
import hashlib
from typing import Optional
from fastapi import Header, Cookie, HTTPException, Depends
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

ADMIN_SESSION_COOKIE_NAME = "sf_admin_session"

def _hash_token(secret: str, text: str) -> str:
    return hmac.new(secret.encode("utf-8"), text.encode("utf-8"), hashlib.sha256).hexdigest()

def create_admin_token() -> str:
    """Generates a verifiable HMAC signature for admin session."""
    sig = _hash_token(settings.ADMIN_SESSION_SECRET, settings.ADMIN_USERNAME)
    return f"sf_admin_{sig[:24]}"

def verify_admin_token(token: str) -> bool:
    """Verifies if the provided admin session token is valid."""
    if not token:
        return False
    expected = create_admin_token()
    return hmac.compare_digest(token, expected)

def require_admin_auth(
    authorization: Optional[str] = Header(None),
    x_admin_token: Optional[str] = Header(None),
    sf_admin_session: Optional[str] = Cookie(None),
):
    """
    FastAPI dependency enforcing admin authentication on /api/admin/* endpoints.
    Accepts:
    - Authorization: Bearer <admin_token> or Bearer <admin_password>
    - X-Admin-Token: <admin_token> or <admin_password>
    - sf_admin_session HTTP-only cookie
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_admin_token:
        token = x_admin_token.strip()
    elif sf_admin_session:
        token = sf_admin_session.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Admin authentication required.")

    # Check if token is valid signed session token or exact admin password
    if verify_admin_token(token) or hmac.compare_digest(token, settings.ADMIN_PASSWORD):
        return True

    raise HTTPException(status_code=403, detail="Invalid admin credentials.")
