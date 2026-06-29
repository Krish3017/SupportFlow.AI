"""
Pagination Utilities
Reusable pagination for list endpoints
"""
from typing import TypeVar, Generic
from pydantic import BaseModel, Field
from core.config import settings

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Items per page (max {settings.MAX_PAGE_SIZE})"
    )

    @property
    def offset(self) -> int:
        """Calculate SQL offset from page and limit"""
        return (self.page - 1) * self.limit

class PaginationMeta(BaseModel):
    """Pagination metadata for responses"""
    total: int
    page: int
    limit: int
    pages: int

class PaginatedResult(BaseModel, Generic[T]):
    """Generic paginated result container"""
    items: list[T]
    meta: PaginationMeta

def paginate(
    items: list[T],
    total: int,
    params: PaginationParams
) -> PaginatedResult[T]:
    """
    Create a paginated result

    Args:
        items: List of items for current page
        total: Total count of items across all pages
        params: Pagination parameters

    Returns:
        PaginatedResult with items and metadata
    """
    return PaginatedResult(
        items=items,
        meta=PaginationMeta(
            total=total,
            page=params.page,
            limit=params.limit,
            pages=(total + params.limit - 1) // params.limit if params.limit > 0 else 0
        )
    )
