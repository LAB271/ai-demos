"""Parser for SQL Server Query Store DMV files."""

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedDMVData:
    """Container for parsed DMV data."""

    query_texts: list[dict]
    queries: list[dict]
    plans: list[dict]
    runtime_stats: list[dict]
    wait_stats: list[dict]
    intervals: list[dict]


class DMVFileParser:
    """Parser for semicolon-delimited DMV export files."""

    def __init__(self, delimiter: str = ";"):
        """
        Initialize parser.

        Args:
            delimiter: Field delimiter (default: semicolon)
        """
        self.delimiter = delimiter

    def parse_file(self, file_path: Path, max_rows: int | None = None) -> list[dict]:
        """
        Parse a single DMV file.

        Args:
            file_path: Path to the DMV file
            max_rows: Maximum number of rows to parse (None for all)

        Returns:
            List of dictionaries with column names as keys
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        rows = []
        with open(file_path, encoding="utf-8-sig") as f:  # utf-8-sig handles BOM
            # Read first line to get column count
            first_line = f.readline().strip()
            if not first_line:
                return []

            # Determine number of columns from first data row
            num_columns = len(first_line.split(self.delimiter))

            # Reset to beginning
            f.seek(0)

            reader = csv.DictReader(
                f, delimiter=self.delimiter, fieldnames=[f"col_{i}" for i in range(num_columns)]
            )

            for i, row in enumerate(reader):
                if max_rows and i >= max_rows:
                    break
                rows.append(row)

        return rows

    def parse_query_store_files(
        self, directory: Path, max_rows_per_file: int | None = 1000
    ) -> ParsedDMVData | None:
        """
        Parse all Query Store DMV files in a directory.

        Args:
            directory: Directory containing DMV files
            max_rows_per_file: Maximum rows to parse per file

        Returns:
            ParsedDMVData object with all parsed data
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        data = ParsedDMVData(
            query_texts=[], queries=[], plans=[], runtime_stats=[], wait_stats=[], intervals=[]
        )

        # Map file names to data containers
        file_mapping = {
            "sys.query_store_query_text.txt": data.query_texts,
            "sys.query_store_query.txt": data.queries,
            "sys.query_store_plan.txt": data.plans,
            "sys.query_store_runtime_stats.txt": data.runtime_stats,
            "sys.query_store_wait_stats.txt": data.wait_stats,
            "sys.query_store_runtime_stats_interval.txt": data.intervals,
        }

        found_any = False
        for file_name, container in file_mapping.items():
            file_path = directory / file_name
            if file_path.exists():
                print(f"Parsing {file_name}...")
                rows = self.parse_file(file_path, max_rows=max_rows_per_file)
                container.extend(rows)
                print(f"  Loaded {len(rows)} rows")
                found_any = True
            else:
                print(f"  Skipping {file_name} (not found)")

        return data if found_any else None

    def parse_intervals_file(self, file_path: Path) -> list[dict]:
        """
        Parse runtime_stats_interval file.

        Returns:
            List of interval dictionaries with parsed timestamps
        """
        return self.parse_file(file_path)

    def parse_wait_stats_sample(self, file_path: Path, sample_size: int = 100) -> list[dict]:
        """
        Parse a sample of wait statistics.

        Args:
            file_path: Path to wait stats file
            sample_size: Number of rows to sample

        Returns:
            Sample of wait statistics
        """
        return self.parse_file(file_path, max_rows=sample_size)


def detect_delimiter(file_path: Path, sample_lines: int = 5) -> str:
    """
    Detect the delimiter used in a file.

    Args:
        file_path: Path to the file
        sample_lines: Number of lines to sample

    Returns:
        Detected delimiter
    """
    with open(file_path, encoding="utf-8-sig") as f:
        sample = [f.readline() for _ in range(sample_lines)]

    # Check common delimiters
    delimiters = [";", ",", "\t", "|"]
    delimiter_counts = {delim: sum(line.count(delim) for line in sample) for delim in delimiters}

    # Return delimiter with highest count
    return max(delimiter_counts, key=delimiter_counts.get)
