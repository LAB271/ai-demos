"""Time interval model for Query Store runtime statistics."""

from dataclasses import dataclass
from datetime import datetime

from .base import DMVEntity


@dataclass
class RuntimeStatsInterval(DMVEntity):
    """Represents a time interval for runtime statistics collection."""

    runtime_stats_interval_id: int
    start_time: datetime
    end_time: datetime
    comment: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "runtime_stats_interval_id": self.runtime_stats_interval_id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000 +00:00",
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000 +00:00",
            "comment": self.comment or "NULL",
        }

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        d = self.to_dict()
        return delimiter.join([str(d["runtime_stats_interval_id"]), d["start_time"], d["end_time"], d["comment"]])
