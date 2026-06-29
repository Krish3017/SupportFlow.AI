"""
Filtering and Sorting Utilities
Reusable query building for filtered lists
"""
from typing import Optional, List, Tuple
from enum import Enum

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class QueryBuilder:
    """Build SQL queries with filters dynamically"""

    def __init__(self, base_query: str):
        self.base_query = base_query
        self.conditions: List[str] = []
        self.parameters: List[any] = []

    def add_filter(self, column: str, value: Optional[any], operator: str = "="):
        """Add a filter condition if value is not None"""
        if value is not None:
            self.conditions.append(f"{column} {operator} ?")
            self.parameters.append(value)
        return self

    def add_in_filter(self, column: str, values: Optional[List[any]]):
        """Add an IN filter for multiple values"""
        if values and len(values) > 0:
            placeholders = ",".join(["?" for _ in values])
            self.conditions.append(f"{column} IN ({placeholders})")
            self.parameters.extend(values)
        return self

    def add_like_filter(self, column: str, pattern: Optional[str]):
        """Add a LIKE filter for text search"""
        if pattern:
            self.conditions.append(f"{column} LIKE ?")
            self.parameters.append(f"%{pattern}%")
        return self

    def add_sort(self, column: str, order: SortOrder = SortOrder.DESC):
        """Add ORDER BY clause"""
        self.base_query += f" ORDER BY {column} {order.value.upper()}"
        return self

    def add_pagination(self, limit: int, offset: int):
        """Add pagination"""
        self.base_query += " LIMIT ? OFFSET ?"
        self.parameters.extend([limit, offset])
        return self

    def build(self) -> Tuple[str, List[any]]:
        """Build final query with parameters"""
        query = self.base_query
        if self.conditions:
            query += " WHERE " + " AND ".join(self.conditions)
        return query, self.parameters

def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize column names to prevent SQL injection

    Only allows alphanumeric characters and underscores
    """
    return "".join(c for c in identifier if c.isalnum() or c == "_")
