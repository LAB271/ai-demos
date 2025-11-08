#!/usr/bin/env python3
"""
Parse SQL Server DMV and Error Log files into a consolidated JSON summary for LLM analysis.

This script reads all synthetic DMV files and the error log, aggregates the data,
and produces a compact JSON file suitable for LLM-based performance analysis.
"""

import argparse
import csv
import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def parse_semicolon_delimited(filepath: Path, skip_bom: bool = True) -> List[List[str]]:
    """Parse semicolon-delimited files (DMV format)."""
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig' if skip_bom else 'utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(line.split(';'))
    return rows


def parse_error_log(filepath: Path) -> List[Dict[str, str]]:
    """Parse UTF-16 LE error log file."""
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-16') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
    except Exception as e:
        print(f"Warning: Could not parse error log: {e}")
    return entries


def parse_query_texts(filepath: Path) -> Dict[str, str]:
    """Parse query text file and return dict of query_text_id -> sql_text."""
    query_texts = {}
    rows = parse_semicolon_delimited(filepath)
    for row in rows:
        if len(row) >= 2:
            query_text_id = row[0]
            sql_text = row[1]
            query_texts[query_text_id] = sql_text
    return query_texts


def parse_runtime_stats(filepath: Path) -> List[Dict[str, Any]]:
    """Parse runtime statistics file."""
    stats = []
    rows = parse_semicolon_delimited(filepath)

    for row in rows:
        if len(row) >= 37:  # Expected number of columns
            try:
                stats.append({
                    'runtime_stats_id': row[0],
                    'plan_id': row[1],
                    'runtime_stats_interval_id': row[2],
                    'execution_type': row[3],
                    'execution_type_desc': row[4],
                    'first_execution_time': row[5],
                    'last_execution_time': row[6],
                    'count_executions': int(row[7]) if row[7] else 0,
                    'avg_duration': float(row[8]) if row[8] else 0.0,
                    'last_duration': float(row[9]) if row[9] else 0.0,
                    'min_duration': float(row[10]) if row[10] else 0.0,
                    'max_duration': float(row[11]) if row[11] else 0.0,
                    'avg_cpu_time': float(row[16]) if row[16] else 0.0,
                    'avg_logical_io_reads': float(row[24]) if row[24] else 0.0,
                    'avg_logical_io_writes': float(row[28]) if row[28] else 0.0,
                    'avg_physical_io_reads': float(row[20]) if row[20] else 0.0,
                })
            except (ValueError, IndexError) as e:
                continue  # Skip malformed rows

    return stats


def parse_wait_stats(filepath: Path) -> List[Dict[str, Any]]:
    """Parse wait statistics file."""
    wait_stats = []
    rows = parse_semicolon_delimited(filepath)

    for row in rows:
        if len(row) >= 6:
            try:
                wait_stats.append({
                    'plan_id': row[0],
                    'runtime_stats_interval_id': row[1],
                    'wait_category_id': row[2],
                    'wait_category': row[3],
                    'total_query_wait_time_ms': float(row[4]) if row[4] else 0.0,
                    'avg_query_wait_time_ms': float(row[5]) if row[5] else 0.0,
                })
            except (ValueError, IndexError):
                continue

    return wait_stats


def parse_queries(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Parse query metadata file."""
    queries = {}
    rows = parse_semicolon_delimited(filepath)

    for row in rows:
        if len(row) >= 9:  # Match actual export format (9 fields)
            query_id = row[0]
            queries[query_id] = {
                'query_text_id': row[1],
                'context_settings_id': row[2],
                'object_id': row[3],
                'batch_sql_handle': row[4],
                'query_hash': row[5],
                'is_internal_query': row[6],
                'query_parameterization_type': row[7],
                'query_parameterization_type_desc': row[8],
            }

    return queries


def analyze_dmv_data(data_dir: Path) -> Dict[str, Any]:
    """Analyze all DMV data and create comprehensive summary."""

    print("Parsing DMV files...")

    # Parse all files
    query_texts = parse_query_texts(data_dir / "sys.query_store_query_text.txt")
    queries = parse_queries(data_dir / "sys.query_store_query.txt")
    runtime_stats = parse_runtime_stats(data_dir / "sys.query_store_runtime_stats.txt")
    wait_stats = parse_wait_stats(data_dir / "sys.query_store_wait_stats.txt")
    error_log = parse_error_log(data_dir / "sqlserver_log.txt")

    print(f"  Loaded {len(query_texts)} query texts")
    print(f"  Loaded {len(queries)} queries")
    print(f"  Loaded {len(runtime_stats)} runtime stats")
    print(f"  Loaded {len(wait_stats)} wait stats")
    print(f"  Loaded {len(error_log)} error log entries")

    # Build query -> text mapping
    query_to_text = {}
    for query_id, query_meta in queries.items():
        text_id = query_meta['query_text_id']
        if text_id in query_texts:
            query_to_text[query_id] = query_texts[text_id]

    # Build plan -> query mapping from runtime stats
    plan_to_query = {}
    for stat in runtime_stats:
        plan_id = stat['plan_id']
        if plan_id not in plan_to_query:
            # Find query_id for this plan_id (would need plan file, simplify by using plan_id)
            plan_to_query[plan_id] = plan_id

    # Aggregate runtime stats by plan
    plan_aggregates = defaultdict(lambda: {
        'count_executions': 0,
        'total_duration_ms': 0.0,
        'total_cpu_ms': 0.0,
        'total_logical_reads': 0.0,
        'total_logical_writes': 0.0,
        'max_duration_ms': 0.0,
        'samples': 0,
    })

    for stat in runtime_stats:
        plan_id = stat['plan_id']
        agg = plan_aggregates[plan_id]
        agg['count_executions'] += stat['count_executions']
        agg['total_duration_ms'] += stat['avg_duration'] * stat['count_executions']
        agg['total_cpu_ms'] += stat['avg_cpu_time'] * stat['count_executions']
        agg['total_logical_reads'] += stat['avg_logical_io_reads'] * stat['count_executions']
        agg['total_logical_writes'] += stat['avg_logical_io_writes'] * stat['count_executions']
        agg['max_duration_ms'] = max(agg['max_duration_ms'], stat['max_duration'])
        agg['samples'] += 1

    # Aggregate wait stats by category
    wait_category_totals = defaultdict(float)
    wait_category_counts = defaultdict(int)

    for wait in wait_stats:
        category = wait['wait_category']
        wait_category_totals[category] += wait['total_query_wait_time_ms']
        wait_category_counts[category] += 1

    # Sort and get top queries by various metrics
    top_n = 20

    # Top by CPU
    top_by_cpu = sorted(
        plan_aggregates.items(),
        key=lambda x: x[1]['total_cpu_ms'],
        reverse=True
    )[:top_n]

    # Top by duration
    top_by_duration = sorted(
        plan_aggregates.items(),
        key=lambda x: x[1]['total_duration_ms'],
        reverse=True
    )[:top_n]

    # Top by logical reads
    top_by_reads = sorted(
        plan_aggregates.items(),
        key=lambda x: x[1]['total_logical_reads'],
        reverse=True
    )[:top_n]

    # Top by executions
    top_by_executions = sorted(
        plan_aggregates.items(),
        key=lambda x: x[1]['count_executions'],
        reverse=True
    )[:top_n]

    # Analyze error log
    error_summary = analyze_error_log(error_log)

    # Calculate overall statistics
    total_executions = sum(agg['count_executions'] for agg in plan_aggregates.values())
    total_duration = sum(agg['total_duration_ms'] for agg in plan_aggregates.values())
    total_cpu = sum(agg['total_cpu_ms'] for agg in plan_aggregates.values())

    # Detect query patterns
    query_patterns = analyze_query_patterns(query_texts)

    # Build final summary
    summary = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_unique_queries': len(query_texts),
            'total_query_instances': len(queries),
            'total_executions': total_executions,
            'total_runtime_stat_samples': len(runtime_stats),
            'total_wait_stat_samples': len(wait_stats),
            'total_error_log_entries': len(error_log),
        },

        'overall_statistics': {
            'total_duration_ms': total_duration,
            'total_cpu_ms': total_cpu,
            'avg_duration_per_execution_ms': total_duration / total_executions if total_executions > 0 else 0,
            'avg_cpu_per_execution_ms': total_cpu / total_executions if total_executions > 0 else 0,
        },

        'query_patterns': query_patterns,

        'top_queries_by_cpu': format_top_queries(top_by_cpu, plan_aggregates, query_texts, 'total_cpu_ms'),
        'top_queries_by_duration': format_top_queries(top_by_duration, plan_aggregates, query_texts, 'total_duration_ms'),
        'top_queries_by_reads': format_top_queries(top_by_reads, plan_aggregates, query_texts, 'total_logical_reads'),
        'top_queries_by_executions': format_top_queries(top_by_executions, plan_aggregates, query_texts, 'count_executions'),

        'wait_statistics': {
            'by_category': [
                {
                    'category': category,
                    'total_wait_time_ms': total_ms,
                    'avg_wait_time_ms': total_ms / wait_category_counts[category],
                    'sample_count': wait_category_counts[category],
                }
                for category, total_ms in sorted(
                    wait_category_totals.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:15]  # Top 15 wait categories
            ]
        },

        'error_log_summary': error_summary,
    }

    return summary


def format_top_queries(top_list: List[tuple], aggregates: Dict, query_texts: Dict, metric: str) -> List[Dict[str, Any]]:
    """Format top queries list for JSON output."""
    result = []

    for plan_id, agg in top_list:
        # Get query text (simplified - would need proper plan->query->text mapping)
        query_snippet = f"Plan {plan_id}"  # Placeholder
        if plan_id in query_texts:
            query_snippet = query_texts[plan_id][:200]  # First 200 chars

        avg_duration = agg['total_duration_ms'] / agg['count_executions'] if agg['count_executions'] > 0 else 0
        avg_cpu = agg['total_cpu_ms'] / agg['count_executions'] if agg['count_executions'] > 0 else 0

        result.append({
            'plan_id': plan_id,
            'query_snippet': query_snippet,
            'executions': agg['count_executions'],
            'total_duration_ms': round(agg['total_duration_ms'], 2),
            'avg_duration_ms': round(avg_duration, 2),
            'total_cpu_ms': round(agg['total_cpu_ms'], 2),
            'avg_cpu_ms': round(avg_cpu, 2),
            'total_logical_reads': round(agg['total_logical_reads'], 2),
            'max_duration_ms': round(agg['max_duration_ms'], 2),
        })

    return result


def analyze_query_patterns(query_texts: Dict[str, str]) -> Dict[str, Any]:
    """Analyze query patterns and categorize queries."""
    patterns = {
        'SELECT': 0,
        'INSERT': 0,
        'UPDATE': 0,
        'DELETE': 0,
        'WITH (CTE)': 0,
        'bulk insert': 0,
        'SELECT INTO': 0,
        'Window Functions': 0,
        'JOINs': 0,
        'Problematic (LIKE %)': 0,
        'Functions on columns': 0,
        'Parameterized': 0,
    }

    for text in query_texts.values():
        text_upper = text.upper()

        # Basic query types
        if text_upper.startswith('SELECT'):
            patterns['SELECT'] += 1
        elif text_upper.startswith('INSERT'):
            patterns['INSERT'] += 1
        elif text_upper.startswith('UPDATE'):
            patterns['UPDATE'] += 1
        elif text_upper.startswith('DELETE'):
            patterns['DELETE'] += 1
        elif text_upper.startswith('WITH'):
            patterns['WITH (CTE)'] += 1

        # Advanced patterns
        if 'INSERT BULK' in text_upper:
            patterns['bulk insert'] += 1
        if 'INTO #' in text_upper or 'INTO @' in text_upper:
            patterns['SELECT INTO'] += 1
        if 'ROW_NUMBER()' in text_upper or 'OVER (PARTITION' in text_upper:
            patterns['Window Functions'] += 1
        if 'JOIN' in text_upper:
            patterns['JOINs'] += 1
        if "LIKE '%" in text_upper:
            patterns['Problematic (LIKE %)'] += 1
        if 'YEAR(' in text_upper or 'MONTH(' in text_upper:
            patterns['Functions on columns'] += 1
        if '@PARAM' in text_upper or '@P0' in text_upper:
            patterns['Parameterized'] += 1

    return patterns


def analyze_error_log(error_entries: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze error log entries and create summary."""
    if not error_entries:
        return {'total_entries': 0}

    # Count by message type
    message_counts = Counter()
    severity_counts = Counter()
    source_counts = Counter()

    errors = []
    warnings = []
    policy_violations = []

    for entry in error_entries:
        message = entry.get('Message', '')
        severity = entry.get('Severity', 'Unknown')
        source = entry.get('Source', 'Unknown')

        message_counts[message[:100]] += 1  # First 100 chars as key
        severity_counts[severity] += 1
        source_counts[source] += 1

        # Categorize
        if 'Error:' in message:
            errors.append({
                'date': entry.get('Date', ''),
                'source': source,
                'message': message[:200],
            })
        elif 'Policy' in message and 'violated' in message:
            policy_violations.append({
                'date': entry.get('Date', ''),
                'policy': message.split("'")[1] if "'" in message else 'Unknown',
            })
        elif 'Autogrow' in message or 'timed out' in message:
            warnings.append({
                'date': entry.get('Date', ''),
                'message': message[:200],
            })

    return {
        'total_entries': len(error_entries),
        'error_count': len(errors),
        'warning_count': len(warnings),
        'policy_violation_count': len(policy_violations),

        'top_messages': [
            {'message': msg[:150], 'count': count}
            for msg, count in message_counts.most_common(10)
        ],

        'severity_distribution': dict(severity_counts),

        'recent_errors': errors[:10],  # Last 10 errors
        'recent_warnings': warnings[:10],  # Last 10 warnings

        'policy_violations_summary': {
            'total': len(policy_violations),
            'unique_policies': len(set(pv['policy'] for pv in policy_violations)),
            'policies': Counter(pv['policy'] for pv in policy_violations).most_common(5),
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse SQL Server DMV data for LLM analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--input',
        type=Path,
        default='./synthetic_output',
        help='Input directory containing DMV and error log files (default: ./synthetic_output)',
    )

    parser.add_argument(
        '--output',
        type=Path,
        default='./dmv_summary_for_llm.json',
        help='Output JSON file (default: ./dmv_summary_for_llm.json)',
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output (more readable but larger)',
    )

    args = parser.parse_args()

    print("=" * 80)
    print("SQL Server DMV Parser for LLM Analysis")
    print("=" * 80)
    print(f"\nInput directory:  {args.input}")
    print(f"Output file:      {args.output}")

    # Analyze data
    summary = analyze_dmv_data(args.input)

    # Write JSON output
    print(f"\nWriting summary to {args.output}...")
    with open(args.output, 'w') as f:
        if args.pretty:
            json.dump(summary, f, indent=2)
        else:
            json.dump(summary, f)

    # Print summary
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print(f"Total unique queries:     {summary['metadata']['total_unique_queries']:,}")
    print(f"Total executions:         {summary['metadata']['total_executions']:,}")
    print(f"Total error log entries:  {summary['metadata']['total_error_log_entries']:,}")
    print(f"Avg duration per query:   {summary['overall_statistics']['avg_duration_per_execution_ms']:.2f} ms")
    print(f"Avg CPU per query:        {summary['overall_statistics']['avg_cpu_per_execution_ms']:.2f} ms")

    print("\nQuery Pattern Distribution:")
    for pattern, count in sorted(summary['query_patterns'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {pattern:25s}: {count:4d}")

    print(f"\n✓ Summary written to: {args.output}")
    print(f"  File size: {args.output.stat().st_size / 1024:.1f} KB")

    print("\nNext steps:")
    print("  1. Review the JSON summary")
    print("  2. Feed this summary to an LLM for performance analysis")
    print("  3. Ask the LLM to identify optimization opportunities")


if __name__ == "__main__":
    main()
