"""Base classes for DMV data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DMVEntity(ABC):
    """Base class for all DMV entities."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert entity to dictionary for export."""
        pass

    @abstractmethod
    def to_delimited_string(self, delimiter: str = ";") -> str:
        """Convert entity to delimited string for export."""
        pass
