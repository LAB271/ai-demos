"""Query metadata model."""

from dataclasses import dataclass

from .base import DMVEntity


@dataclass
class Query(DMVEntity):
    """Represents query metadata."""

    query_id: int
    query_text_id: int
    context_settings_id: int
    object_id: int
    batch_sql_handle: str | None
    query_hash: str
    is_internal_query: int
    query_parameterization_type: int
    query_parameterization_type_desc: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "query_text_id": self.query_text_id,
            "context_settings_id": self.context_settings_id,
            "object_id": self.object_id,
            "batch_sql_handle": self.batch_sql_handle or "NULL",
            "query_hash": self.query_hash,
            "is_internal_query": self.is_internal_query,
            "query_parameterization_type": self.query_parameterization_type,
            "query_parameterization_type_desc": self.query_parameterization_type_desc,
        }

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        d = self.to_dict()
        return delimiter.join(
            [
                str(d["query_id"]),
                str(d["query_text_id"]),
                str(d["context_settings_id"]),
                str(d["object_id"]),
                str(d["batch_sql_handle"]),
                str(d["query_hash"]),
                str(d["is_internal_query"]),
                str(d["query_parameterization_type"]),
                str(d["query_parameterization_type_desc"]),
            ]
        )
