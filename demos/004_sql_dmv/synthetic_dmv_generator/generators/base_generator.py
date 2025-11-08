"""Base generator class for synthetic DMV data."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import numpy as np

from ..config import GeneratorConfig
from ..utils.correlations import EntityRelationships, IdGenerator
from ..utils.distributions import DistributionSampler, CorrelationGenerator


class BaseGenerator(ABC):
    """Base class for all DMV data generators."""

    def __init__(self, config: GeneratorConfig):
        """
        Initialize generator with configuration.

        Args:
            config: Generator configuration
        """
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)
        self.sampler = DistributionSampler(self.rng)
        self.correlator = CorrelationGenerator(self.rng)
        self.id_gen = IdGenerator()
        self.relationships = EntityRelationships()

    @abstractmethod
    def generate(self):
        """Generate synthetic data."""
        pass

    def _generate_time_intervals(self) -> list:
        """
        Generate time intervals based on configuration.

        Returns:
            List of (interval_id, start_time, end_time) tuples
        """
        intervals = []
        current_time = self.config.start_time
        interval_id = 1

        while current_time < self.config.end_time:
            end_time = min(current_time + timedelta(hours=self.config.interval_hours), self.config.end_time)
            intervals.append((interval_id, current_time, end_time))
            interval_id += 1
            current_time = end_time

        return intervals

    def _generate_hash(self, length: int = 16) -> str:
        """
        Generate a random hex hash.

        Args:
            length: Length of hex string

        Returns:
            Hex hash string
        """
        return "0x" + "".join([f"{self.rng.integers(0, 256):02X}" for _ in range(length)])

    def _generate_execution_times(
        self, interval_start: datetime, interval_end: datetime, num_executions: int
    ) -> tuple[datetime, datetime]:
        """
        Generate first and last execution times within an interval.

        Args:
            interval_start: Interval start time
            interval_end: Interval end time
            num_executions: Number of executions

        Returns:
            Tuple of (first_execution_time, last_execution_time)
        """
        interval_duration = (interval_end - interval_start).total_seconds()

        if num_executions == 1:
            # Single execution - place randomly in interval
            offset_seconds = self.rng.uniform(0, interval_duration)
            exec_time = interval_start + timedelta(seconds=offset_seconds)
            return exec_time, exec_time

        # Multiple executions - spread across interval
        first_offset = self.rng.uniform(0, interval_duration * 0.2)  # Early in interval
        last_offset = self.rng.uniform(interval_duration * 0.8, interval_duration)  # Late in interval

        first_time = interval_start + timedelta(seconds=first_offset)
        last_time = interval_start + timedelta(seconds=last_offset)

        return first_time, last_time
