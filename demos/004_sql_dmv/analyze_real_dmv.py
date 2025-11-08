#!/usr/bin/env python3
"""
Analyze real DMV data to understand patterns and statistics.

This script parses existing Query Store DMV files and extracts statistical
patterns that can inform synthetic data generation.
"""

import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from synthetic_dmv_generator.analyzers.dmv_parser import DMVFileParser
from synthetic_dmv_generator.analyzers.statistical_analyzer import StatisticalAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Analyze real SQL Server Query Store DMV data")
    parser.add_argument(
        "input_dir", type=Path, help="Directory containing Query Store DMV files (*.txt files)"
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=1000,
        help="Maximum rows to parse per file (default: 1000, use -1 for all)",
    )
    parser.add_argument(
        "--delimiter", type=str, default=";", help="Field delimiter in files (default: semicolon)"
    )

    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"Error: Directory not found: {args.input_dir}")
        sys.exit(1)

    max_rows = None if args.max_rows == -1 else args.max_rows

    print("=" * 80)
    print("SQL Server Query Store DMV Analyzer")
    print("=" * 80)
    print(f"\nInput directory: {args.input_dir}")
    print(f"Max rows per file: {max_rows if max_rows else 'All'}")
    print(f"Delimiter: '{args.delimiter}'")
    print()

    # Parse DMV files
    parser_obj = DMVFileParser(delimiter=args.delimiter)
    print("Parsing DMV files...")
    data = parser_obj.parse_query_store_files(args.input_dir, max_rows_per_file=max_rows)

    if not data:
        print("Error: No DMV data found or parsed successfully.")
        sys.exit(1)

    # Analyze data
    print("\n" + "=" * 80)
    print("Statistical Analysis")
    print("=" * 80)

    analyzer = StatisticalAnalyzer()

    # Analyze runtime statistics
    if data.runtime_stats:
        print("\n[Runtime Statistics Profile]")
        profile = analyzer.analyze_runtime_stats(data.runtime_stats)

        print(f"\nDuration (microseconds):")
        print(f"  Mean:   {profile.duration_mean:,.0f} µs ({profile.duration_mean/1000:.2f} ms)")
        print(f"  Median: {profile.duration_median:,.0f} µs ({profile.duration_median/1000:.2f} ms)")
        print(f"  Std Dev: {profile.duration_std:,.0f} µs")
        print(f"  P95:    {profile.duration_p95:,.0f} µs ({profile.duration_p95/1000:.2f} ms)")
        print(f"  P99:    {profile.duration_p99:,.0f} µs ({profile.duration_p99/1000:.2f} ms)")

        print(f"\nCPU Time (microseconds):")
        print(f"  Mean:   {profile.cpu_mean:,.0f} µs ({profile.cpu_mean/1000:.2f} ms)")
        print(f"  CPU/Duration ratio: {profile.cpu_to_duration_ratio:.1%}")

        print(f"\nLogical I/O Reads (8KB pages):")
        print(f"  Mean:   {profile.logical_reads_mean:,.0f} pages ({profile.logical_reads_mean*8/1024:.2f} MB)")
        print(f"  Std Dev: {profile.logical_reads_std:,.0f} pages")

        print(f"\nPhysical I/O Reads:")
        print(f"  Mean:   {profile.physical_reads_mean:,.0f} pages ({profile.physical_reads_mean*8/1024:.2f} MB)")
        print(f"  Physical/Logical ratio: {profile.physical_read_ratio:.1%}")
        print(f"  Cache hit ratio: {(1-profile.physical_read_ratio):.1%}")

        print(f"\nRow Counts:")
        print(f"  Mean:   {profile.rowcount_mean:,.0f} rows")

        print(f"\nExecution Frequency:")
        print(f"  Avg executions/hour: {profile.executions_per_hour:.1f}")

        print(f"\nCorrelations:")
        print(f"  Duration ↔ Logical Reads: {profile.duration_logical_reads_correlation:.3f}")

    # Analyze wait statistics
    if data.wait_stats:
        print("\n[Wait Statistics]")
        wait_dist = analyzer.analyze_wait_stats(data.wait_stats)
        print("\nWait Category Distribution:")
        for category, proportion in sorted(wait_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:20s}: {proportion:6.1%}")

    # Analyze query patterns
    if data.queries and data.runtime_stats:
        print("\n[Query Patterns]")
        patterns = analyzer.analyze_query_patterns(data.queries, data.runtime_stats)
        print(f"  OLTP queries:        {patterns['oltp_proportion']:6.1%}")
        print(f"  OLAP queries:        {patterns['olap_proportion']:6.1%}")
        print(f"  Mixed/Other queries: {patterns['mixed_proportion']:6.1%}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Query texts:       {len(data.query_texts):6d}")
    print(f"Queries:           {len(data.queries):6d}")
    print(f"Plans:             {len(data.plans):6d}")
    print(f"Runtime stats:     {len(data.runtime_stats):6d}")
    print(f"Wait stats:        {len(data.wait_stats):6d}")
    print(f"Time intervals:    {len(data.intervals):6d}")

    print("\n✓ Analysis complete!")
    print("\nUse these insights to configure your synthetic data generation.")


if __name__ == "__main__":
    main()
