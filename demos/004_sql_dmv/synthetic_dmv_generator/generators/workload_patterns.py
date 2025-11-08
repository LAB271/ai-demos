"""Workload pattern definitions for different query types."""

from dataclasses import dataclass

from ..config import OLTP_PROFILE, OLAP_PROFILE, PROBLEM_PROFILE, QueryTypeProfile


@dataclass
class WorkloadScenario:
    """Defines a complete workload scenario."""

    name: str
    description: str
    query_profiles: list[tuple[QueryTypeProfile, float]]  # (profile, proportion)
    cpu_pressure: float = 1.0
    io_pressure: float = 1.0
    memory_pressure: float = 1.0


# Pre-defined workload scenarios
OLTP_WORKLOAD = WorkloadScenario(
    name="OLTP",
    description="Online Transaction Processing - fast, frequent queries",
    query_profiles=[(OLTP_PROFILE, 0.95), (OLAP_PROFILE, 0.05)],
    cpu_pressure=0.8,
    io_pressure=0.7,
    memory_pressure=0.8,
)

OLAP_WORKLOAD = WorkloadScenario(
    name="OLAP",
    description="Online Analytical Processing - slow, complex analytical queries",
    query_profiles=[(OLAP_PROFILE, 0.8), (OLTP_PROFILE, 0.15), (PROBLEM_PROFILE, 0.05)],
    cpu_pressure=1.5,
    io_pressure=2.0,
    memory_pressure=1.8,
)

MIXED_WORKLOAD = WorkloadScenario(
    name="Mixed",
    description="Mixed workload with both OLTP and OLAP queries",
    query_profiles=[(OLTP_PROFILE, 0.6), (OLAP_PROFILE, 0.3), (PROBLEM_PROFILE, 0.1)],
    cpu_pressure=1.0,
    io_pressure=1.0,
    memory_pressure=1.0,
)

CPU_PRESSURE_WORKLOAD = WorkloadScenario(
    name="CPU Pressure",
    description="Workload with high CPU utilization",
    query_profiles=[(OLTP_PROFILE, 0.4), (OLAP_PROFILE, 0.4), (PROBLEM_PROFILE, 0.2)],
    cpu_pressure=2.5,
    io_pressure=1.2,
    memory_pressure=1.5,
)

IO_BOTTLENECK_WORKLOAD = WorkloadScenario(
    name="I/O Bottleneck",
    description="Workload with high I/O pressure and slow disk responses",
    query_profiles=[(OLAP_PROFILE, 0.6), (PROBLEM_PROFILE, 0.3), (OLTP_PROFILE, 0.1)],
    cpu_pressure=1.2,
    io_pressure=3.0,
    memory_pressure=1.0,
)

MEMORY_PRESSURE_WORKLOAD = WorkloadScenario(
    name="Memory Pressure",
    description="Workload with insufficient memory causing spills to tempdb",
    query_profiles=[(OLAP_PROFILE, 0.5), (PROBLEM_PROFILE, 0.4), (OLTP_PROFILE, 0.1)],
    cpu_pressure=1.3,
    io_pressure=1.8,
    memory_pressure=3.0,
)

BLOCKING_WORKLOAD = WorkloadScenario(
    name="Blocking/Locking",
    description="Workload with high contention and blocking",
    query_profiles=[(OLTP_PROFILE, 0.7), (OLAP_PROFILE, 0.2), (PROBLEM_PROFILE, 0.1)],
    cpu_pressure=0.6,  # Low CPU because queries are waiting
    io_pressure=1.0,
    memory_pressure=1.0,
)

PARAMETER_SNIFFING_WORKLOAD = WorkloadScenario(
    name="Parameter Sniffing",
    description="Queries with parameter sniffing issues causing performance variability",
    query_profiles=[(OLTP_PROFILE, 0.5), (PROBLEM_PROFILE, 0.5)],  # High variability
    cpu_pressure=1.5,
    io_pressure=1.5,
    memory_pressure=1.2,
)


def get_workload_by_name(name: str) -> WorkloadScenario:
    """
    Get a workload scenario by name.

    Args:
        name: Workload name (case-insensitive)

    Returns:
        WorkloadScenario

    Raises:
        ValueError: If workload name is not found
    """
    workloads = {
        "oltp": OLTP_WORKLOAD,
        "olap": OLAP_WORKLOAD,
        "mixed": MIXED_WORKLOAD,
        "cpu_pressure": CPU_PRESSURE_WORKLOAD,
        "io_bottleneck": IO_BOTTLENECK_WORKLOAD,
        "memory_pressure": MEMORY_PRESSURE_WORKLOAD,
        "blocking": BLOCKING_WORKLOAD,
        "parameter_sniffing": PARAMETER_SNIFFING_WORKLOAD,
    }

    name_lower = name.lower()
    if name_lower not in workloads:
        available = ", ".join(workloads.keys())
        raise ValueError(f"Unknown workload '{name}'. Available: {available}")

    return workloads[name_lower]


def list_available_workloads() -> list[str]:
    """Get list of available workload scenario names."""
    return [
        "oltp",
        "olap",
        "mixed",
        "cpu_pressure",
        "io_bottleneck",
        "memory_pressure",
        "blocking",
        "parameter_sniffing",
    ]
