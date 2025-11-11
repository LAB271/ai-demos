"""Wait statistics model."""

from dataclasses import dataclass

from .base import DMVEntity


@dataclass
class WaitStats(DMVEntity):
    """Represents query wait statistics."""

    plan_id: int
    runtime_stats_interval_id: int
    wait_category_id: int
    wait_category: str
    total_query_wait_time_ms: float
    avg_query_wait_time_ms: float
    last_query_wait_time_ms: float
    min_query_wait_time_ms: float
    max_query_wait_time_ms: float
    stdev_query_wait_time_ms: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "runtime_stats_interval_id": self.runtime_stats_interval_id,
            "wait_category_id": self.wait_category_id,
            "wait_category": self.wait_category,
            "total_query_wait_time_ms": self.total_query_wait_time_ms,
            "avg_query_wait_time_ms": self.avg_query_wait_time_ms,
            "last_query_wait_time_ms": self.last_query_wait_time_ms,
            "min_query_wait_time_ms": self.min_query_wait_time_ms,
            "max_query_wait_time_ms": self.max_query_wait_time_ms,
            "stdev_query_wait_time_ms": self.stdev_query_wait_time_ms,
        }

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        d = self.to_dict()
        return delimiter.join([str(v) for v in d.values()])
