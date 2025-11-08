"""Statistical analysis of real DMV data to extract patterns."""

import numpy as np
from dataclasses import dataclass
from collections import Counter


@dataclass
class StatisticalProfile:
    """Statistical profile extracted from real data."""

    # Duration statistics (microseconds)
    duration_mean: float
    duration_std: float
    duration_median: float
    duration_p95: float
    duration_p99: float

    # CPU statistics (microseconds)
    cpu_mean: float
    cpu_std: float
    cpu_to_duration_ratio: float

    # I/O statistics
    logical_reads_mean: float
    logical_reads_std: float
    physical_reads_mean: float
    physical_read_ratio: float  # physical/logical

    # Row count statistics
    rowcount_mean: float
    rowcount_std: float

    # Execution frequency
    executions_per_hour: float

    # Wait statistics
    wait_category_distribution: dict[str, float]  # category -> proportion

    # Correlations
    duration_logical_reads_correlation: float


class StatisticalAnalyzer:
    """Analyze DMV data to extract statistical patterns."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def analyze_runtime_stats(self, runtime_stats: list[dict]) -> StatisticalProfile:
        """
        Analyze runtime statistics to extract patterns.

        Args:
            runtime_stats: List of runtime stat dictionaries

        Returns:
            Statistical profile
        """
        if not runtime_stats:
            return self._default_profile()

        # Extract numeric values (handle different column names from parsing)
        durations = []
        cpu_times = []
        logical_reads = []
        physical_reads = []
        rowcounts = []
        executions = []

        for row in runtime_stats:
            try:
                # Try to extract duration (avg_duration)
                duration = self._safe_float(row.get("col_8") or row.get("avg_duration"), 0)
                if duration > 0:
                    durations.append(duration)

                # CPU time
                cpu = self._safe_float(row.get("col_12") or row.get("avg_cpu_time"), 0)
                if cpu > 0:
                    cpu_times.append(cpu)

                # Logical reads
                logical = self._safe_float(row.get("col_16") or row.get("avg_logical_io_reads"), 0)
                if logical > 0:
                    logical_reads.append(logical)

                # Physical reads
                physical = self._safe_float(row.get("col_24") or row.get("avg_physical_io_reads"), 0)
                if physical > 0:
                    physical_reads.append(physical)

                # Row counts
                rows = self._safe_float(row.get("col_36") or row.get("avg_rowcount"), 0)
                if rows > 0:
                    rowcounts.append(rows)

                # Execution count
                exec_count = self._safe_float(row.get("col_7") or row.get("count_executions"), 1)
                executions.append(exec_count)

            except (ValueError, KeyError):
                continue

        # Convert to numpy arrays
        durations = np.array(durations) if durations else np.array([1000])
        cpu_times = np.array(cpu_times) if cpu_times else np.array([800])
        logical_reads = np.array(logical_reads) if logical_reads else np.array([100])
        physical_reads = np.array(physical_reads) if physical_reads else np.array([10])
        rowcounts = np.array(rowcounts) if rowcounts else np.array([10])
        executions = np.array(executions) if executions else np.array([1])

        # Calculate statistics
        return StatisticalProfile(
            duration_mean=float(np.mean(durations)),
            duration_std=float(np.std(durations)),
            duration_median=float(np.median(durations)),
            duration_p95=float(np.percentile(durations, 95)),
            duration_p99=float(np.percentile(durations, 99)),
            cpu_mean=float(np.mean(cpu_times)),
            cpu_std=float(np.std(cpu_times)),
            cpu_to_duration_ratio=float(np.mean(cpu_times) / np.mean(durations)) if np.mean(durations) > 0 else 0.8,
            logical_reads_mean=float(np.mean(logical_reads)),
            logical_reads_std=float(np.std(logical_reads)),
            physical_reads_mean=float(np.mean(physical_reads)),
            physical_read_ratio=float(np.mean(physical_reads) / np.mean(logical_reads))
            if np.mean(logical_reads) > 0
            else 0.05,
            rowcount_mean=float(np.mean(rowcounts)),
            rowcount_std=float(np.std(rowcounts)),
            executions_per_hour=float(np.mean(executions)),
            wait_category_distribution={},
            duration_logical_reads_correlation=float(np.corrcoef(durations[:len(logical_reads)], logical_reads[:len(durations)])[0, 1])
            if len(durations) > 1 and len(logical_reads) > 1 and len(durations) == len(logical_reads)
            else 0.7,
        )

    def analyze_wait_stats(self, wait_stats: list[dict]) -> dict[str, float]:
        """
        Analyze wait statistics to extract category distribution.

        Args:
            wait_stats: List of wait stat dictionaries

        Returns:
            Dictionary mapping wait category to proportion
        """
        if not wait_stats:
            return {
                "Buffer IO": 0.3,
                "Network IO": 0.2,
                "Parallelism": 0.2,
                "Memory": 0.1,
                "Preemptive": 0.1,
                "Idle": 0.1,
            }

        categories = []
        for row in wait_stats:
            try:
                # Wait category is typically in col_3
                category = row.get("col_3", "Unknown")
                if category and category != "Unknown":
                    categories.append(category)
            except (KeyError, ValueError):
                continue

        if not categories:
            return {"Buffer IO": 0.3, "Network IO": 0.2, "Parallelism": 0.2}

        # Count occurrences
        category_counts = Counter(categories)
        total = sum(category_counts.values())

        # Convert to proportions
        return {cat: count / total for cat, count in category_counts.items()}

    def analyze_query_patterns(self, queries: list[dict], runtime_stats: list[dict]) -> dict:
        """
        Analyze query patterns to categorize queries.

        Args:
            queries: List of query dictionaries
            runtime_stats: List of runtime stat dictionaries

        Returns:
            Dictionary with query pattern analysis
        """
        # Group runtime stats by plan/query
        plan_stats = {}
        for row in runtime_stats:
            plan_id = row.get("col_1", "0")
            duration = self._safe_float(row.get("col_8"), 0)
            exec_count = self._safe_float(row.get("col_7"), 1)

            if plan_id not in plan_stats:
                plan_stats[plan_id] = {"durations": [], "executions": []}

            plan_stats[plan_id]["durations"].append(duration)
            plan_stats[plan_id]["executions"].append(exec_count)

        # Categorize queries
        oltp_count = 0  # Fast, frequent
        olap_count = 0  # Slow, infrequent
        mixed_count = 0

        for plan_id, stats in plan_stats.items():
            avg_duration = np.mean(stats["durations"])
            avg_executions = np.mean(stats["executions"])

            # Classification heuristics
            if avg_duration < 1000 and avg_executions > 10:  # < 1ms, frequent
                oltp_count += 1
            elif avg_duration > 100000 and avg_executions < 10:  # > 100ms, infrequent
                olap_count += 1
            else:
                mixed_count += 1

        total = oltp_count + olap_count + mixed_count
        if total == 0:
            return {"oltp_proportion": 0.7, "olap_proportion": 0.2, "mixed_proportion": 0.1}

        return {
            "oltp_proportion": oltp_count / total,
            "olap_proportion": olap_count / total,
            "mixed_proportion": mixed_count / total,
        }

    def _safe_float(self, value: str | float, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                # Handle decimal comma
                value = value.replace(",", ".")
                return float(value)
            except (ValueError, AttributeError):
                return default
        return default

    def _default_profile(self) -> StatisticalProfile:
        """Return a default profile when no data is available."""
        return StatisticalProfile(
            duration_mean=10000,
            duration_std=5000,
            duration_median=5000,
            duration_p95=20000,
            duration_p99=30000,
            cpu_mean=8000,
            cpu_std=4000,
            cpu_to_duration_ratio=0.8,
            logical_reads_mean=1000,
            logical_reads_std=500,
            physical_reads_mean=50,
            physical_read_ratio=0.05,
            rowcount_mean=100,
            rowcount_std=50,
            executions_per_hour=10,
            wait_category_distribution={"Buffer IO": 0.4, "Network IO": 0.3, "Parallelism": 0.3},
            duration_logical_reads_correlation=0.7,
        )
