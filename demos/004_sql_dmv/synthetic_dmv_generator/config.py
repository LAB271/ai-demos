"""Configuration and constants for DMV synthetic data generation."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class WaitCategory(Enum):
    """SQL Server wait categories."""

    BUFFER_IO = "Buffer IO"
    NETWORK_IO = "Network IO"
    MEMORY = "Memory"
    PARALLELISM = "Parallelism"
    PREEMPTIVE = "Preemptive"
    IDLE = "Idle"
    LOCK = "Lock"
    LATCH = "Latch"
    CPU = "CPU"


class ExecutionType(Enum):
    """Query execution types."""

    REGULAR = "Regular"
    ABORTED = "Aborted"
    EXCEPTION = "Exception"


@dataclass
class GeneratorConfig:
    """Configuration for synthetic data generation."""

    # Time range configuration
    start_time: datetime = datetime.now(timezone.utc) - timedelta(days=7)
    end_time: datetime = datetime.now(timezone.utc)
    interval_hours: int = 1

    # Volume configuration
    num_unique_queries: int = 100
    num_plans_per_query_range: tuple[int, int] = (1, 3)
    executions_per_hour_range: tuple[int, int] = (10, 1000)

    # Workload characteristics
    workload_type: str = "mixed"  # 'oltp', 'olap', 'mixed', 'problem'
    cpu_pressure_factor: float = 1.0  # 1.0 = normal, >1.0 = CPU pressure
    io_pressure_factor: float = 1.0  # 1.0 = normal, >1.0 = I/O pressure
    memory_pressure_factor: float = 1.0  # 1.0 = normal, >1.0 = memory pressure

    # Query patterns
    proportion_oltp: float = 0.7  # Fast, frequent queries
    proportion_olap: float = 0.2  # Slow, analytical queries
    proportion_problematic: float = 0.1  # Queries with issues

    # Statistical parameters
    random_seed: int = 42

    # File paths
    output_directory: str = "./synthetic_output"
    delimiter: str = ";"


@dataclass
class QueryTypeProfile:
    """Profile for different query types."""

    name: str
    avg_duration_ms: float
    duration_stddev: float
    avg_cpu_ms: float
    cpu_stddev: float
    avg_logical_reads: int
    logical_reads_stddev: int
    avg_rows: int
    rows_stddev: int
    execution_frequency: int  # executions per hour


# Pre-defined query type profiles
OLTP_PROFILE = QueryTypeProfile(
    name="OLTP",
    avg_duration_ms=50,
    duration_stddev=20,
    avg_cpu_ms=30,
    cpu_stddev=15,
    avg_logical_reads=100,
    logical_reads_stddev=50,
    avg_rows=10,
    rows_stddev=5,
    execution_frequency=500,
)

OLAP_PROFILE = QueryTypeProfile(
    name="OLAP",
    avg_duration_ms=5000,
    duration_stddev=2000,
    avg_cpu_ms=4000,
    cpu_stddev=1500,
    avg_logical_reads=100000,
    logical_reads_stddev=50000,
    avg_rows=10000,
    rows_stddev=5000,
    execution_frequency=5,
)

PROBLEM_PROFILE = QueryTypeProfile(
    name="Problematic",
    avg_duration_ms=15000,
    duration_stddev=5000,
    avg_cpu_ms=10000,
    cpu_stddev=3000,
    avg_logical_reads=500000,
    logical_reads_stddev=200000,
    avg_rows=50000,
    rows_stddev=20000,
    execution_frequency=2,
)


# SQL Server version constants
SQL_SERVER_VERSION = "15.0.4445.1"
COMPATIBILITY_LEVEL = 150

# File column definitions
WAIT_STATS_COLUMNS = [
    "plan_id",
    "runtime_stats_interval_id",
    "wait_category_id",
    "wait_category",
    "total_query_wait_time_ms",
    "avg_query_wait_time_ms",
    "last_query_wait_time_ms",
    "min_query_wait_time_ms",
    "max_query_wait_time_ms",
    "stdev_query_wait_time_ms",
]

RUNTIME_STATS_COLUMNS = [
    "runtime_stats_id",
    "plan_id",
    "runtime_stats_interval_id",
    "execution_type_id",
    "execution_type",
    "first_execution_time",
    "last_execution_time",
    "count_executions",
    "avg_duration",
    "last_duration",
    "min_duration",
    "max_duration",
    "avg_cpu_time",
    "last_cpu_time",
    "min_cpu_time",
    "max_cpu_time",
    "avg_logical_io_reads",
    "last_logical_io_reads",
    "min_logical_io_reads",
    "max_logical_io_reads",
    "avg_logical_io_writes",
    "last_logical_io_writes",
    "min_logical_io_writes",
    "max_logical_io_writes",
    "avg_physical_io_reads",
    "last_physical_io_reads",
    "min_physical_io_reads",
    "max_physical_io_reads",
    "avg_clr_time",
    "last_clr_time",
    "min_clr_time",
    "max_clr_time",
    "avg_query_max_used_memory",
    "last_query_max_used_memory",
    "min_query_max_used_memory",
    "max_query_max_used_memory",
    "avg_rowcount",
    "last_rowcount",
    "min_rowcount",
    "max_rowcount",
]

QUERY_COLUMNS = [
    "query_id",
    "query_text_id",
    "context_settings_id",
    "object_id",
    "batch_sql_handle",
    "query_hash",
    "is_internal_query",
    "query_parameterization_type",
    "query_parameterization_type_desc",
]

QUERY_TEXT_COLUMNS = ["query_text_id", "query_sql_text"]

PLAN_COLUMNS = [
    "plan_id",
    "query_id",
    "plan_group_id",
    "engine_version",
    "compatibility_level",
    "query_plan_hash",
    "query_plan",
    "is_online_index_plan",
    "is_trivial_plan",
    "is_parallel_plan",
    "is_forced_plan",
    "is_natively_compiled",
    "force_failure_count",
    "last_force_failure_reason",
    "last_force_failure_reason_desc",
    "count_compiles",
    "initial_compile_start_time",
    "last_compile_start_time",
    "last_execution_time",
    "avg_compile_duration",
    "last_compile_duration",
]

INTERVAL_COLUMNS = ["runtime_stats_interval_id", "start_time", "end_time", "comment"]
