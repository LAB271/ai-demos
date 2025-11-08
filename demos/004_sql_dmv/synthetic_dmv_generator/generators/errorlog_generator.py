"""
Generator for synthetic SQL Server Error Log entries.
"""

import random
from datetime import datetime, timedelta
from typing import List

from ..models.errorlog import ErrorLogEntry


class ErrorLogGenerator:
    """Generates realistic SQL Server error log entries."""

    # Common error messages patterns from real SQL Server logs
    POLICY_VIOLATIONS = [
        "Policy 'COMPANY SQL - Windows Authentication' has been violated.",
        "Policy 'COMPANY SQL - SQL login moet policy checked zijn' has been violated.",
        "Policy 'COMPANY SQL - Password Policy' has been violated.",
        "Policy 'COMPANY SQL - Password Expiration' has been violated.",
    ]

    ERROR_MESSAGES = [
        "Error: 34052<c/> Severity: 16<c/> State: 1.",
        "Error: 18456<c/> Severity: 14<c/> State: 8.",  # Login failed
        "Error: 1205<c/> Severity: 13<c/> State: 51.",  # Deadlock
        "Error: 825<c/> Severity: 10<c/> State: 2.",    # Read retry
        "Error: 17806<c/> Severity: 20<c/> State: 2.",  # SSPI handshake failed
    ]

    CERTIFICATE_MESSAGES = [
        "Certificaatscript Module dbatools geinstalleerd Module SqlServer geinstalleerd Nieuwste certificaat 57D1CA509DBDB45D6CF80485440 4A2801F7F6919<c/> Huidige certificaat 57D1CA509DBDB45D6CF804854404A2801F7F6919 Gelijk<c/> certificaat niet instellen verloopt: 10/06/2026 08:00:52",
    ]

    INFORMATIONAL_MESSAGES = [
        "SQL Server is starting at normal priority base (=7). This is an informational message only. No user action is required.",
        "Database backed up. Database: {db_name}, creation date(time): {date}, pages dumped: {pages}, first LSN: {lsn1}, last LSN: {lsn2}.",
        "Recovery is complete. This is an informational message only. No user action is required.",
        "Clearing tempdb database.",
        "The Service Broker endpoint is in disabled or stopped state.",
    ]

    WARNING_MESSAGES = [
        "The SQL Server cannot obtain a LOCK resource at this time. Rerun your statement when there are fewer active users.",
        "Autogrow of file '{file}' in database '{db}' was cancelled by user or timed out after {ms} milliseconds.",
        "SQL Server has encountered {count} occurrence(s) of I/O requests taking longer than 15 seconds to complete.",
    ]

    STARTUP_MESSAGES = [
        "This instance of SQL Server has been using a process ID of {pid} since {date} (local) {date_utc} (UTC). This is an informational message only; no user action is required.",
        "Server name is '{server}'. This is an informational message only. No user action is required.",
    ]

    def __init__(self, start_time: datetime, end_time: datetime, seed: int = 42):
        """
        Initialize the error log generator.

        Args:
            start_time: Start time for log entries
            end_time: End time for log entries
            seed: Random seed for reproducibility
        """
        self.start_time = start_time
        self.end_time = end_time
        self.random = random.Random(seed)
        self.entries: List[ErrorLogEntry] = []

    def generate(self) -> List[ErrorLogEntry]:
        """
        Generate synthetic error log entries.

        Returns:
            List of ErrorLogEntry objects
        """
        self.entries = []

        # Add startup message at the beginning
        self._add_startup_message()

        # Generate periodic entries
        self._generate_policy_check_entries()
        self._generate_certificate_check_entries()
        self._generate_informational_entries()
        self._generate_error_entries()
        self._generate_warning_entries()

        # Sort by date descending (newest first, like real SQL Server logs)
        self.entries.sort(key=lambda x: x.date, reverse=True)

        return self.entries

    def _add_startup_message(self):
        """Add SQL Server startup message."""
        pid = self.random.randint(10000, 99999)
        local_time = self.start_time.strftime("%-m-%-d-%Y %H:%M:%S")
        utc_time = self.start_time.strftime("%-m-%-d-%Y %H:%M:%S")

        message = f"This instance of SQL Server has been using a process ID of {pid} since {local_time} (local) {utc_time} (UTC). This is an informational message only; no user action is required."

        self.entries.append(
            ErrorLogEntry(
                date=self.start_time + timedelta(seconds=23),
                source="spid32s",
                severity="Unknown",
                message=message,
            )
        )

    def _generate_policy_check_entries(self):
        """Generate policy violation check entries (every 30 minutes)."""
        current_time = self.start_time
        policy_index = 0

        while current_time < self.end_time:
            # Alternate between different policies
            policy_msg = self.POLICY_VIOLATIONS[policy_index % len(self.POLICY_VIOLATIONS)]
            policy_index += 1

            spid = self.random.randint(50, 130)

            # Policy violation message
            self.entries.append(
                ErrorLogEntry(
                    date=current_time,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=policy_msg,
                )
            )

            # Corresponding error message
            self.entries.append(
                ErrorLogEntry(
                    date=current_time,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=self.ERROR_MESSAGES[0],  # Error 34052
                )
            )

            current_time += timedelta(minutes=30)

    def _generate_certificate_check_entries(self):
        """Generate certificate check entries (every 60 minutes, offset by 30 min)."""
        current_time = self.start_time + timedelta(minutes=30, seconds=37)

        while current_time < self.end_time:
            spid = self.random.randint(50, 130)

            self.entries.append(
                ErrorLogEntry(
                    date=current_time,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=self.CERTIFICATE_MESSAGES[0],
                )
            )

            current_time += timedelta(hours=1)

    def _generate_informational_entries(self):
        """Generate random informational messages."""
        num_entries = int((self.end_time - self.start_time).total_seconds() / 3600 / 24)  # ~1 per day

        for _ in range(num_entries):
            timestamp = self._random_timestamp()
            spid = self.random.randint(50, 130)

            msg_template = self.random.choice(self.INFORMATIONAL_MESSAGES)
            message = self._format_message(msg_template)

            self.entries.append(
                ErrorLogEntry(
                    date=timestamp,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=message,
                )
            )

    def _generate_error_entries(self):
        """Generate random error messages."""
        # Errors are rarer - about 2-5 per day
        num_errors = int((self.end_time - self.start_time).total_seconds() / 3600 / 24 * self.random.uniform(2, 5))

        for _ in range(num_errors):
            timestamp = self._random_timestamp()
            spid = self.random.randint(50, 200)

            error_msg = self.random.choice(self.ERROR_MESSAGES[1:])  # Skip the policy error

            self.entries.append(
                ErrorLogEntry(
                    date=timestamp,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=error_msg,
                )
            )

    def _generate_warning_entries(self):
        """Generate random warning messages."""
        # Warnings are occasional - about 1-3 per day
        num_warnings = int((self.end_time - self.start_time).total_seconds() / 3600 / 24 * self.random.uniform(1, 3))

        for _ in range(num_warnings):
            timestamp = self._random_timestamp()
            spid = self.random.randint(50, 200)

            msg_template = self.random.choice(self.WARNING_MESSAGES)
            message = self._format_message(msg_template)

            self.entries.append(
                ErrorLogEntry(
                    date=timestamp,
                    source=f"spid{spid}",
                    severity="Unknown",
                    message=message,
                )
            )

    def _random_timestamp(self) -> datetime:
        """Generate a random timestamp between start and end time."""
        delta = self.end_time - self.start_time
        random_seconds = self.random.randint(0, int(delta.total_seconds()))
        return self.start_time + timedelta(seconds=random_seconds)

    def _format_message(self, template: str) -> str:
        """Format a message template with random values."""
        replacements = {
            "{db_name}": self.random.choice(["master", "tempdb", "msdb", "AdventureWorks", "Production"]),
            "{date}": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "{date_utc}": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "{pages}": str(self.random.randint(1000, 100000)),
            "{lsn1}": f"{self.random.randint(1000, 9999)}:{self.random.randint(100, 999)}:{self.random.randint(1, 99)}",
            "{lsn2}": f"{self.random.randint(1000, 9999)}:{self.random.randint(100, 999)}:{self.random.randint(1, 99)}",
            "{file}": self.random.choice(["tempdb", "AdventureWorks_log", "Production_data"]),
            "{db}": self.random.choice(["tempdb", "AdventureWorks", "Production"]),
            "{ms}": str(self.random.randint(30000, 120000)),
            "{count}": str(self.random.randint(1, 10)),
            "{pid}": str(self.random.randint(10000, 99999)),
            "{server}": "SQL-SERVER-01",
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        return result
