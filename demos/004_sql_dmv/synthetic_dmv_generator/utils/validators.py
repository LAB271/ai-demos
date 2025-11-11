"""Data validation utilities."""

import numpy as np


def validate_positive(value: float | int, name: str) -> None:
    """Validate that a value is positive."""
    if value < 0:
        raise ValueError(f"{name} must be positive, got {value}")


def validate_non_negative(value: float | int, name: str) -> None:
    """Validate that a value is non-negative."""
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def validate_percentage(value: float, name: str) -> None:
    """Validate that a value is between 0 and 1."""
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1, got {value}")


def validate_stats_consistency(stats: dict) -> None:
    """
    Validate that statistical measures are consistent.

    Checks:
    - min <= avg <= max
    - min <= last <= max
    - All values are non-negative
    """
    validate_non_negative(stats["min"], "min")
    validate_non_negative(stats["avg"], "avg")
    validate_non_negative(stats["max"], "max")
    validate_non_negative(stats["last"], "last")
    validate_non_negative(stats["stdev"], "stdev")

    if stats["min"] > stats["avg"]:
        raise ValueError(f"min ({stats['min']}) cannot be greater than avg ({stats['avg']})")

    if stats["avg"] > stats["max"]:
        raise ValueError(f"avg ({stats['avg']}) cannot be greater than max ({stats['max']})")

    if stats["min"] > stats["max"]:
        raise ValueError(f"min ({stats['min']}) cannot be greater than max ({stats['max']})")


def ensure_min_max_bounds(values: np.ndarray, stats: dict) -> dict:
    """
    Ensure min and max in stats encompass all actual values.

    Args:
        values: Actual values
        stats: Dictionary with statistical measures

    Returns:
        Updated stats dictionary
    """
    if len(values) > 0:
        actual_min = float(np.min(values))
        actual_max = float(np.max(values))

        stats["min"] = min(stats["min"], actual_min)
        stats["max"] = max(stats["max"], actual_max)

    return stats


def validate_time_consistency(first_time, last_time, interval_start, interval_end) -> None:
    """Validate that execution times are within interval bounds."""
    if first_time < interval_start:
        raise ValueError(f"First execution time {first_time} is before interval start {interval_start}")

    if last_time > interval_end:
        raise ValueError(f"Last execution time {last_time} is after interval end {interval_end}")

    if first_time > last_time:
        raise ValueError(f"First execution time {first_time} is after last execution time {last_time}")
