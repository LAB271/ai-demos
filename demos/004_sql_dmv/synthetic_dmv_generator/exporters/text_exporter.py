"""Export DMV data to semicolon-delimited text files (matching SQL Server export format)."""

from pathlib import Path


class TextExporter:
    """Exports DMV data to text files with customizable delimiter."""

    def __init__(self, delimiter: str = ";", encoding: str = "utf-8"):
        """
        Initialize text exporter.

        Args:
            delimiter: Field delimiter (default: semicolon)
            encoding: File encoding (default: utf-8)
        """
        self.delimiter = delimiter
        self.encoding = encoding

    def export_intervals(self, intervals: list, output_path: Path):
        """Export runtime stats intervals."""
        with open(output_path, "w", encoding=self.encoding) as f:
            # Add BOM for UTF-8
            f.write("\ufeff")
            for interval in intervals:
                f.write(interval.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(intervals)} intervals to {output_path.name}")

    def export_query_texts(self, query_texts: list, output_path: Path):
        """Export query texts."""
        with open(output_path, "w", encoding=self.encoding) as f:
            f.write("\ufeff")
            for query_text in query_texts:
                f.write(query_text.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(query_texts)} query texts to {output_path.name}")

    def export_queries(self, queries: list, output_path: Path):
        """Export queries."""
        with open(output_path, "w", encoding=self.encoding) as f:
            f.write("\ufeff")
            for query in queries:
                f.write(query.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(queries)} queries to {output_path.name}")

    def export_plans(self, plans: list, output_path: Path):
        """Export execution plans."""
        with open(output_path, "w", encoding=self.encoding) as f:
            f.write("\ufeff")
            for plan in plans:
                f.write(plan.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(plans)} plans to {output_path.name}")

    def export_runtime_stats(self, runtime_stats: list, output_path: Path):
        """Export runtime statistics."""
        with open(output_path, "w", encoding=self.encoding) as f:
            f.write("\ufeff")
            for stat in runtime_stats:
                f.write(stat.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(runtime_stats)} runtime stats to {output_path.name}")

    def export_wait_stats(self, wait_stats: list, output_path: Path):
        """Export wait statistics."""
        with open(output_path, "w", encoding=self.encoding) as f:
            f.write("\ufeff")
            for stat in wait_stats:
                f.write(stat.to_delimited_string(self.delimiter) + "\n")

        print(f"  Exported {len(wait_stats)} wait stats to {output_path.name}")

    def export_all(self, generator, output_dir: Path):
        """
        Export all DMV data to text files.

        Args:
            generator: SyntheticDMVGenerator instance
            output_dir: Output directory path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nExporting to {output_dir}...")

        self.export_intervals(generator.intervals, output_dir / "sys.query_store_runtime_stats_interval.txt")
        self.export_query_texts(generator.query_texts, output_dir / "sys.query_store_query_text.txt")
        self.export_queries(generator.queries, output_dir / "sys.query_store_query.txt")
        self.export_plans(generator.plans, output_dir / "sys.query_store_plan.txt")
        self.export_runtime_stats(generator.runtime_stats, output_dir / "sys.query_store_runtime_stats.txt")
        self.export_wait_stats(generator.wait_stats, output_dir / "sys.query_store_wait_stats.txt")

        print(f"\n✓ Export complete! Files written to {output_dir}")
