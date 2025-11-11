"""Execution plan model."""

from dataclasses import dataclass
from datetime import datetime

from .base import DMVEntity


@dataclass
class ExecutionPlan(DMVEntity):
    """Represents a query execution plan."""

    plan_id: int
    query_id: int
    plan_group_id: int
    engine_version: str
    compatibility_level: int
    query_plan_hash: str
    query_plan: str | None
    is_online_index_plan: int
    is_trivial_plan: int
    is_parallel_plan: int
    is_forced_plan: int
    is_natively_compiled: int
    force_failure_count: int
    last_force_failure_reason: int
    last_force_failure_reason_desc: str
    count_compiles: int
    initial_compile_start_time: datetime
    last_compile_start_time: datetime
    last_execution_time: datetime
    avg_compile_duration: float
    last_compile_duration: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "query_id": self.query_id,
            "plan_group_id": self.plan_group_id,
            "engine_version": self.engine_version,
            "compatibility_level": self.compatibility_level,
            "query_plan_hash": self.query_plan_hash,
            "query_plan": self.query_plan or "NULL",
            "is_online_index_plan": self.is_online_index_plan,
            "is_trivial_plan": self.is_trivial_plan,
            "is_parallel_plan": self.is_parallel_plan,
            "is_forced_plan": self.is_forced_plan,
            "is_natively_compiled": self.is_natively_compiled,
            "force_failure_count": self.force_failure_count,
            "last_force_failure_reason": self.last_force_failure_reason,
            "last_force_failure_reason_desc": self.last_force_failure_reason_desc,
            "count_compiles": self.count_compiles,
            "initial_compile_start_time": self.initial_compile_start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            + "0000 +00:00",
            "last_compile_start_time": self.last_compile_start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            + "0000 +00:00",
            "last_execution_time": self.last_execution_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "0000 +00:00",
            "avg_compile_duration": self.avg_compile_duration,
            "last_compile_duration": self.last_compile_duration,
        }

    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert to delimited string."""
        d = self.to_dict()
        return delimiter.join([str(v) for v in d.values()])
