"""
Custom Exceptions
Centralized error handling for SupportFlow AI
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class SupportFlowException(Exception):
    """Base exception for all SupportFlow errors"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

# ═══════════════════════════════════════════════════════════════
# CLIENT ERRORS (4xx)
# ═══════════════════════════════════════════════════════════════

class NotFoundError(SupportFlowException):
    """Resource not found (404)"""

    def __init__(self, resource: str, identifier: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"{resource} with ID '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

class ValidationError(SupportFlowException):
    """Invalid input data (422)"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class UnauthorizedError(SupportFlowException):
    """Authentication required (401)"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class ForbiddenError(SupportFlowException):
    """Insufficient permissions (403)"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

class ConflictError(SupportFlowException):
    """Resource conflict (409)"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )

class RateLimitError(SupportFlowException):
    """Too many requests (429)"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Too many requests. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after}
        )

# ═══════════════════════════════════════════════════════════════
# SERVER ERRORS (5xx)
# ═══════════════════════════════════════════════════════════════

class DatabaseError(SupportFlowException):
    """Database operation failed (500)"""

    def __init__(self, operation: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Database error during {operation}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class ExternalServiceError(SupportFlowException):
    """External service failure (502)"""

    def __init__(self, service: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"External service error: {service}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )

class AgentExecutionError(SupportFlowException):
    """Agent execution failed (500)"""

    def __init__(self, agent: str, error: str):
        super().__init__(
            message=f"Agent '{agent}' execution failed: {error}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"agent": agent, "error": error}
        )

# ═══════════════════════════════════════════════════════════════
# ERROR CONVERSION
# ═══════════════════════════════════════════════════════════════

def to_http_exception(error: SupportFlowException) -> HTTPException:
    """Convert SupportFlowException to FastAPI HTTPException"""
    return HTTPException(
        status_code=error.status_code,
        detail={
            "success": False,
            "error": error.message,
            "details": error.details
        }
    )
