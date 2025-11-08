"""Export DMV data to CSV format."""

import csv
from pathlib import Path


class CSVExporter:
    """Exports DMV data to CSV files with headers."""

    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize CSV exporter.

        Args:
            encoding: File encoding (default: utf-8)
        """
        self.encoding = encoding

    def export_to_csv(self, entities: list, output_path: Path, headers: list[str]):
        """
        Export entities to CSV file.

        Args:
            entities: List of entity objects
            output_path: Output file path
            headers: List of column headers
        """
        with open(output_path, "w", encoding=self.encoding, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            for entity in entities:
                writer.writerow(entity.to_dict())

        print(f"  Exported {len(entities)} records to {output_path.name}")

    def export_all(self, generator, output_dir: Path):
        """
        Export all DMV data to CSV files.

        Args:
            generator: SyntheticDMVGenerator instance
            output_dir: Output directory path
        """
        from ..config import (
            INTERVAL_COLUMNS,
            QUERY_TEXT_COLUMNS,
            QUERY_COLUMNS,
            PLAN_COLUMNS,
            RUNTIME_STATS_COLUMNS,
            WAIT_STATS_COLUMNS,
        )

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nExporting to CSV in {output_dir}...")

        self.export_to_csv(
            generator.intervals, output_dir / "sys.query_store_runtime_stats_interval.csv", INTERVAL_COLUMNS
        )
        self.export_to_csv(generator.query_texts, output_dir / "sys.query_store_query_text.csv", QUERY_TEXT_COLUMNS)
        self.export_to_csv(generator.queries, output_dir / "sys.query_store_query.csv", QUERY_COLUMNS)
        self.export_to_csv(generator.plans, output_dir / "sys.query_store_plan.csv", PLAN_COLUMNS)
        self.export_to_csv(
            generator.runtime_stats, output_dir / "sys.query_store_runtime_stats.csv", RUNTIME_STATS_COLUMNS
        )
        self.export_to_csv(generator.wait_stats, output_dir / "sys.query_store_wait_stats.csv", WAIT_STATS_COLUMNS)

        print(f"\n✓ CSV export complete! Files written to {output_dir}")
