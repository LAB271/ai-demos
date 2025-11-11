"""
Models for SQL Server Error Log entries.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ErrorLogEntry:
    """Represents a single SQL Server error log entry."""

    date: datetime
    source: str  # e.g., 'spid112', 'spid32s', 'Logon'
    severity: str  # e.g., 'Unknown', 'Error', 'Warning', 'Information'
    message: str
    log_id: str = ""
    process_id: str = ""
    mail_item_id: str = ""
    account_id: str = ""
    last_modified: str = ""
    last_modified_by: str = ""

    def __post_init__(self):
        """Validate the entry."""
        if not self.date:
            raise ValueError("date is required")
        if not self.source:
            raise ValueError("source is required")
        if not self.message:
            raise ValueError("message is required")
