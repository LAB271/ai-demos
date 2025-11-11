"""Query text model."""

from dataclasses import dataclass

from .base import DMVEntity


@dataclass
class QueryText(DMVEntity):
    """Represents the SQL text of a query."""

    query_text_id: int
    query_sql_text: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"query_text_id": self.query_text_id, "query_sql_text": self.query_sql_text}

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        # Escape delimiter in SQL text
        escaped_text = self.query_sql_text.replace(delimiter, f"\\{delimiter}")
        return f"{self.query_text_id}{delimiter}{escaped_text}"
