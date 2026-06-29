"""
Standard API Response Models
Consistent response format across all endpoints
"""
from typing import TypeVar, Generic, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper"""
    success: bool = True
    data: T
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    """Error detail structure"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated data response"""
    success: bool = True
    data: list[T]
    pagination: Dict[str, Any]
    message: Optional[str] = None

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        limit: int,
        message: Optional[str] = None
    ):
        """Factory method for creating paginated responses"""
        return cls(
            data=items,
            pagination={
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            },
            message=message
        )

def success(data: T, message: Optional[str] = None) -> SuccessResponse[T]:
    """Create a success response"""
    return SuccessResponse(data=data, message=message)

def error(message: str, details: Optional[Dict[str, Any]] = None) -> ErrorDetail:
    """Create an error response"""
    return ErrorDetail(error=message, details=details)

def paginated(
    items: list[T],
    total: int,
    page: int,
    limit: int,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """Create a paginated response"""
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        limit=limit,
        message=message
    )
