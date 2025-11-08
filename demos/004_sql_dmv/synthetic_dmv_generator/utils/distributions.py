"""Statistical distribution utilities for realistic data generation."""

import numpy as np
from numpy.random import Generator


class DistributionSampler:
    """Sampler for various statistical distributions."""

    def __init__(self, rng: Generator):
        """Initialize with a random number generator."""
        self.rng = rng

    def log_normal(self, mean: float, stddev: float, size: int = 1) -> np.ndarray:
        """
        Generate log-normal distributed values (common for query durations).

        Log-normal is realistic for performance metrics because:
        - Most queries are fast (left-skewed)
        - Some queries are very slow (long right tail)
        """
        if stddev == 0 or mean == 0:
            return np.full(size, mean)

        # Convert to log-normal parameters
        variance = stddev**2
        mu = np.log(mean**2 / np.sqrt(variance + mean**2))
        sigma = np.sqrt(np.log(variance / mean**2 + 1))

        return self.rng.lognormal(mu, sigma, size)

    def normal(self, mean: float, stddev: float, size: int = 1, min_val: float = 0) -> np.ndarray:
        """Generate normal distributed values with optional minimum."""
        values = self.rng.normal(mean, stddev, size)
        return np.maximum(values, min_val)

    def poisson(self, lam: float, size: int = 1) -> np.ndarray:
        """Generate Poisson distributed values (good for execution counts)."""
        return self.rng.poisson(lam, size)

    def exponential(self, scale: float, size: int = 1) -> np.ndarray:
        """Generate exponential distributed values (good for wait times)."""
        return self.rng.exponential(scale, size)

    def uniform(self, low: float, high: float, size: int = 1) -> np.ndarray:
        """Generate uniform distributed values."""
        return self.rng.uniform(low, high, size)

    def choice(self, choices: list, size: int = 1, probabilities: list[float] | None = None) -> np.ndarray:
        """Choose from a list with optional probability weights."""
        return self.rng.choice(choices, size=size, p=probabilities)


class CorrelationGenerator:
    """Generate correlated values for realistic relationships."""

    def __init__(self, rng: Generator):
        """Initialize with a random number generator."""
        self.rng = rng

    def correlated_values(
        self, base_values: np.ndarray, correlation: float, mean: float, stddev: float
    ) -> np.ndarray:
        """
        Generate values correlated with base values.

        Args:
            base_values: Base values to correlate with
            correlation: Correlation coefficient (-1 to 1)
            mean: Mean of the generated values
            stddev: Standard deviation of the generated values

        Returns:
            Correlated values
        """
        if len(base_values) == 0:
            return np.array([])

        # Standardize base values
        base_standardized = (base_values - np.mean(base_values)) / (np.std(base_values) + 1e-10)

        # Generate independent random values
        independent = self.rng.normal(0, 1, len(base_values))

        # Combine to create correlation
        correlated_standardized = correlation * base_standardized + np.sqrt(1 - correlation**2) * independent

        # Transform to desired mean and stddev
        return mean + stddev * correlated_standardized

    def cpu_from_duration(self, durations: np.ndarray, cpu_ratio_mean: float = 0.8) -> np.ndarray:
        """
        Generate CPU time from duration (typically 60-90% of duration).

        Args:
            durations: Query durations in microseconds
            cpu_ratio_mean: Mean ratio of CPU to duration

        Returns:
            CPU times in microseconds
        """
        # CPU is typically 60-90% of duration
        cpu_ratios = self.rng.uniform(0.6, 0.95, len(durations))
        cpu_times = durations * cpu_ratios
        return cpu_times

    def logical_reads_from_duration(self, durations: np.ndarray, reads_per_ms: float = 100) -> np.ndarray:
        """
        Generate logical reads correlated with duration.

        Args:
            durations: Query durations in microseconds
            reads_per_ms: Average logical reads per millisecond

        Returns:
            Logical read counts
        """
        duration_ms = durations / 1000.0
        base_reads = duration_ms * reads_per_ms
        # Add some variability
        noise = self.rng.normal(1.0, 0.3, len(durations))
        return np.maximum(1, (base_reads * noise).astype(int))

    def physical_reads_from_logical(self, logical_reads: np.ndarray, cache_hit_ratio: float = 0.95) -> np.ndarray:
        """
        Generate physical reads from logical reads based on cache hit ratio.

        Args:
            logical_reads: Logical read counts
            cache_hit_ratio: Buffer pool cache hit ratio (0.90-0.99 typical)

        Returns:
            Physical read counts
        """
        miss_ratio = 1 - cache_hit_ratio
        physical_reads = logical_reads * miss_ratio
        # Add some randomness
        physical_reads = physical_reads * self.rng.uniform(0.5, 1.5, len(logical_reads))
        return np.maximum(0, physical_reads.astype(int))


def compute_stats(values: np.ndarray) -> dict:
    """
    Compute statistical measures (avg, min, max, last, stdev).

    Args:
        values: Array of values

    Returns:
        Dictionary with statistical measures
    """
    if len(values) == 0:
        return {"avg": 0, "min": 0, "max": 0, "last": 0, "stdev": 0}

    return {
        "avg": float(np.mean(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "last": float(values[-1]),
        "stdev": float(np.std(values)),
    }
