#!/usr/bin/env python3
"""
Generate synthetic SQL Server Query Store DMV data.

This script generates realistic synthetic DMV data based on configurable
workload scenarios and performance characteristics.
"""

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from synthetic_dmv_generator.config import GeneratorConfig
from synthetic_dmv_generator.generators.synthetic_generator import SyntheticDMVGenerator
from synthetic_dmv_generator.generators.errorlog_generator import ErrorLogGenerator
from synthetic_dmv_generator.generators.workload_patterns import list_available_workloads
from synthetic_dmv_generator.exporters.text_exporter import TextExporter
from synthetic_dmv_generator.exporters.csv_exporter import CSVExporter
from synthetic_dmv_generator.exporters.errorlog_exporter import ErrorLogExporter


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic SQL Server Query Store DMV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 7 days of mixed workload data
  python generate_synthetic_dmv.py --workload mixed --days 7 --queries 100

  # Generate data with CPU pressure
  python generate_synthetic_dmv.py --workload cpu_pressure --days 3 --queries 50

  # Generate OLTP workload and export as CSV
  python generate_synthetic_dmv.py --workload oltp --format csv --output ./oltp_data

Available workloads:
  """ + "\n  ".join(list_available_workloads())
    )

    parser.add_argument(
        "--workload",
        type=str,
        default="mixed",
        choices=list_available_workloads(),
        help="Workload scenario to generate (default: mixed)",
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days of data to generate (default: 7)"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=100,
        help="Number of unique queries to generate (default: 100)",
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=1,
        help="Runtime stats collection interval in hours (default: 1)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="./synthetic_output",
        help="Output directory (default: ./synthetic_output)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="text",
        choices=["text", "csv", "both"],
        help="Output format: text (semicolon-delimited), csv, or both (default: text)",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--cpu-pressure",
        type=float,
        default=None,
        help="CPU pressure multiplier (overrides workload default, e.g., 2.0 = 2x pressure)",
    )
    parser.add_argument(
        "--io-pressure",
        type=float,
        default=None,
        help="I/O pressure multiplier (overrides workload default)",
    )
    parser.add_argument(
        "--memory-pressure",
        type=float,
        default=None,
        help="Memory pressure multiplier (overrides workload default)",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("SQL Server Query Store DMV Synthetic Data Generator")
    print("=" * 80)
    print(f"\nWorkload:       {args.workload}")
    print(f"Duration:       {args.days} days")
    print(f"Unique queries: {args.queries}")
    print(f"Interval:       {args.interval_hours} hour(s)")
    print(f"Output:         {args.output}")
    print(f"Format:         {args.format}")
    print(f"Random seed:    {args.seed}")

    # Configure generation
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=args.days)

    config = GeneratorConfig(
        start_time=start_time,
        end_time=end_time,
        interval_hours=args.interval_hours,
        num_unique_queries=args.queries,
        workload_type=args.workload,
        random_seed=args.seed,
        output_directory=str(args.output),
    )

    # Override pressure factors if specified
    if args.cpu_pressure is not None:
        config.cpu_pressure_factor = args.cpu_pressure
        print(f"CPU pressure:   {args.cpu_pressure}x (custom)")
    if args.io_pressure is not None:
        config.io_pressure_factor = args.io_pressure
        print(f"I/O pressure:   {args.io_pressure}x (custom)")
    if args.memory_pressure is not None:
        config.memory_pressure_factor = args.memory_pressure
        print(f"Memory pressure: {args.memory_pressure}x (custom)")

    print("\n" + "=" * 80)

    # Generate DMV data
    generator = SyntheticDMVGenerator(config)
    generator.generate()

    # Generate Error Log data
    errorlog_generator = ErrorLogGenerator(start_time, end_time, seed=args.seed)
    errorlog_entries = errorlog_generator.generate()

    # Export data
    print("\n" + "=" * 80)
    print("Exporting Data")
    print("=" * 80)

    if args.format in ["text", "both"]:
        text_exporter = TextExporter()
        output_dir = args.output / "text" if args.format == "both" else args.output
        text_exporter.export_all(generator, output_dir)

    if args.format in ["csv", "both"]:
        csv_exporter = CSVExporter()
        output_dir = args.output / "csv" if args.format == "both" else args.output
        csv_exporter.export_all(generator, output_dir)

    # Export Error Log (always exported to the main output directory)
    errorlog_exporter = ErrorLogExporter()
    errorlog_exporter.export(errorlog_entries, args.output)

    print("\n" + "=" * 80)
    print("Generation Statistics")
    print("=" * 80)
    print(f"Time intervals:    {len(generator.intervals):6d}")
    print(f"Query texts:       {len(generator.query_texts):6d}")
    print(f"Query instances:   {len(generator.queries):6d}")
    print(f"Execution plans:   {len(generator.plans):6d}")
    print(f"Runtime stats:     {len(generator.runtime_stats):6d}")
    print(f"Wait stats:        {len(generator.wait_stats):6d}")
    print(f"Error log entries: {len(errorlog_entries):6d}")

    # Calculate some summary statistics
    total_executions = sum(stat.count_executions for stat in generator.runtime_stats)
    avg_duration = sum(stat.avg_duration for stat in generator.runtime_stats) / len(generator.runtime_stats) if generator.runtime_stats else 0

    print(f"\nTotal query executions: {total_executions:,}")
    print(f"Avg query duration:     {avg_duration/1000:.2f} ms")

    print("\n✓ All done!")
    print(f"\nYour synthetic DMV data is ready at: {args.output}")
    print("\nNext steps:")
    print("  1. Review the generated files")
    print("  2. Use this data to develop your SQL Server optimization system")
    print("  3. Test your Claude-based analysis tools with this realistic data")


if __name__ == "__main__":
    main()
