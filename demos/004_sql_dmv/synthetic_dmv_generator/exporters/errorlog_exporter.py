"""
Exporter for SQL Server Error Log in UTF-16 LE format.
"""

from pathlib import Path
from typing import List

from ..models.errorlog import ErrorLogEntry


class ErrorLogExporter:
    """Exports error log entries to UTF-16 LE CSV format (matching SQL Server format)."""

    COLUMNS = [
        "Date",
        "Source",
        "Severity",
        "Message",
        "Log ID",
        "Process ID",
        "Mail Item ID",
        "Account ID",
        "Last Modified",
        "Last Modified By",
    ]

    def export(self, entries: List[ErrorLogEntry], output_path: Path, filename: str = "sqlserver_log.txt"):
        """
        Export error log entries to a UTF-16 LE CSV file.

        Args:
            entries: List of ErrorLogEntry objects
            output_path: Directory to write the file
            filename: Name of the output file
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename

        # Write with UTF-16 LE encoding and BOM
        # Note: using 'utf-16' (not 'utf-16-le') ensures BOM is written
        # Use newline="" to prevent Python from converting \r\n to \r\r\n
        with open(filepath, "w", encoding="utf-16", newline="") as f:
            # Write header
            header = ",".join(self.COLUMNS)
            f.write(header + "\r\n")

            # Write entries (sorted by date descending - newest first)
            sorted_entries = sorted(entries, key=lambda x: x.date, reverse=True)

            for entry in sorted_entries:
                row = self._format_row(entry)
                f.write(row + "\r\n")

        print(f"✓ Exported {len(entries)} error log entries to: {filepath}")

    def _format_row(self, entry: ErrorLogEntry) -> str:
        """
        Format an error log entry as a CSV row.

        Args:
            entry: ErrorLogEntry object

        Returns:
            Formatted CSV row string
        """
        # Format date as MM/DD/YYYY HH:MM:SS
        date_str = entry.date.strftime("%m/%d/%Y %H:%M:%S")

        fields = [
            date_str,
            entry.source,
            entry.severity,
            entry.message,
            entry.log_id,
            entry.process_id,
            entry.mail_item_id,
            entry.account_id,
            entry.last_modified,
            entry.last_modified_by,
        ]

        return ",".join(fields)
