"""Runtime statistics model."""

from dataclasses import dataclass
from datetime import datetime

from .base import DMVEntity


@dataclass
class RuntimeStats(DMVEntity):
    """Represents query runtime statistics for a time interval."""

    runtime_stats_id: int
    plan_id: int
    runtime_stats_interval_id: int
    execution_type_id: int
    execution_type: str
    first_execution_time: datetime
    last_execution_time: datetime
    count_executions: int
    # Duration stats (microseconds)
    avg_duration: float
    last_duration: float
    min_duration: float
    max_duration: float
    # CPU stats (microseconds)
    avg_cpu_time: float
    last_cpu_time: float
    min_cpu_time: float
    max_cpu_time: float
    # Logical I/O reads (8KB pages)
    avg_logical_io_reads: float
    last_logical_io_reads: float
    min_logical_io_reads: float
    max_logical_io_reads: float
    # Logical I/O writes (8KB pages)
    avg_logical_io_writes: float
    last_logical_io_writes: float
    min_logical_io_writes: float
    max_logical_io_writes: float
    # Physical I/O reads (8KB pages)
    avg_physical_io_reads: float
    last_physical_io_reads: float
    min_physical_io_reads: float
    max_physical_io_reads: float
    # CLR time (microseconds)
    avg_clr_time: float
    last_clr_time: float
    min_clr_time: float
    max_clr_time: float
    # Memory (8KB pages)
    avg_query_max_used_memory: float
    last_query_max_used_memory: float
    min_query_max_used_memory: float
    max_query_max_used_memory: float
    # Row count
    avg_rowcount: float
    last_rowcount: float
    min_rowcount: float
    max_rowcount: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "runtime_stats_id": self.runtime_stats_id,
            "plan_id": self.plan_id,
            "runtime_stats_interval_id": self.runtime_stats_interval_id,
            "execution_type_id": self.execution_type_id,
            "execution_type": self.execution_type,
            "first_execution_time": self.first_execution_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000 +00:00",
            "last_execution_time": self.last_execution_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000 +00:00",
            "count_executions": self.count_executions,
            "avg_duration": self.avg_duration,
            "last_duration": self.last_duration,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "avg_cpu_time": self.avg_cpu_time,
            "last_cpu_time": self.last_cpu_time,
            "min_cpu_time": self.min_cpu_time,
            "max_cpu_time": self.max_cpu_time,
            "avg_logical_io_reads": self.avg_logical_io_reads,
            "last_logical_io_reads": self.last_logical_io_reads,
            "min_logical_io_reads": self.min_logical_io_reads,
            "max_logical_io_reads": self.max_logical_io_reads,
            "avg_logical_io_writes": self.avg_logical_io_writes,
            "last_logical_io_writes": self.last_logical_io_writes,
            "min_logical_io_writes": self.min_logical_io_writes,
            "max_logical_io_writes": self.max_logical_io_writes,
            "avg_physical_io_reads": self.avg_physical_io_reads,
            "last_physical_io_reads": self.last_physical_io_reads,
            "min_physical_io_reads": self.min_physical_io_reads,
            "max_physical_io_reads": self.max_physical_io_reads,
            "avg_clr_time": self.avg_clr_time,
            "last_clr_time": self.last_clr_time,
            "min_clr_time": self.min_clr_time,
            "max_clr_time": self.max_clr_time,
            "avg_query_max_used_memory": self.avg_query_max_used_memory,
            "last_query_max_used_memory": self.last_query_max_used_memory,
            "min_query_max_used_memory": self.min_query_max_used_memory,
            "max_query_max_used_memory": self.max_query_max_used_memory,
            "avg_rowcount": self.avg_rowcount,
            "last_rowcount": self.last_rowcount,
            "min_rowcount": self.min_rowcount,
            "max_rowcount": self.max_rowcount,
        }

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        d = self.to_dict()
        return delimiter.join([str(v) for v in d.values()])
