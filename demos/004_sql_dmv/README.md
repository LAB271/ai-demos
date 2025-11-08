# SQL Server Query Store DMV Synthetic Data Generator

A comprehensive Python system for generating realistic synthetic SQL Server Query Store DMV (Dynamic Management View) data. This tool is designed to help develop and test SQL Server performance analysis and optimization systems without requiring access to production data.

## Overview

This generator creates synthetic data that mirrors the structure and statistical patterns of real SQL Server Query Store data, including:

- **Query texts** - Realistic SQL queries (OLTP, OLAP, problematic patterns)
- **Query metadata** - Query hashes, parameterization info
- **Execution plans** - Plan characteristics (parallel, trivial, etc.)
- **Runtime statistics** - Duration, CPU time, I/O reads, memory usage, row counts
- **Wait statistics** - Wait categories and times
- **Time intervals** - Hourly collection windows
- **Error logs** - Synthetic SQL Server error log entries (errors, warnings, informational messages)

## Features

### Realistic Data Generation
- **Statistical accuracy** - Uses log-normal distributions for durations, correlated metrics
- **Multiple workload types** - OLTP, OLAP, mixed, and problem scenarios
- **Performance pressure simulation** - CPU, I/O, and memory pressure factors
- **Referential integrity** - Maintains proper relationships between all entities

### Pre-defined Workload Scenarios
1. **OLTP** - Fast, frequent transactional queries
2. **OLAP** - Slow, complex analytical queries
3. **Mixed** - Balanced OLTP/OLAP workload
4. **CPU Pressure** - High CPU utilization
5. **I/O Bottleneck** - Disk I/O problems
6. **Memory Pressure** - Memory spills and pressure
7. **Blocking** - Lock contention issues
8. **Parameter Sniffing** - Performance variability

### Export Formats
- **Text files** - Semicolon-delimited (matches SQL Server export format)
- **CSV files** - With headers for easy analysis
- **Both formats** - Side-by-side comparison

## Installation

### Prerequisites
- Python 3.14+
- Dependencies: numpy, pandas, faker, scipy, scikit-learn

### Install Dependencies

```bash
cd /Users/iheitlager/wc/ai-demos
uv sync
```

## Usage

### Quick Start - Generate Synthetic Data

Generate 7 days of mixed workload data:

```bash
cd demos/004_sql_server
python generate_synthetic_dmv.py --workload mixed --days 7 --queries 100
```

### Analyze Real DMV Data First

If you have real DMV exports, analyze them first to understand patterns:

```bash
python analyze_real_dmv.py /path/to/dmv/files --max-rows 1000
```

This will output:
- Duration statistics (mean, median, P95, P99)
- CPU/Duration ratios
- I/O patterns and cache hit ratios
- Wait category distributions
- Query type proportions



### Generate with Different Workload Scenarios

**OLTP workload** (fast, frequent queries):
```bash
python generate_synthetic_dmv.py --workload oltp --days 3 --queries 50
```

**OLAP workload** (analytical queries):
```bash
python generate_synthetic_dmv.py --workload olap --days 5 --queries 30
```

**CPU pressure scenario**:
```bash
python generate_synthetic_dmv.py --workload cpu_pressure --days 2 --queries 75
```

**I/O bottleneck scenario**:
```bash
python generate_synthetic_dmv.py --workload io_bottleneck --days 3 --queries 60
```

### Custom Pressure Factors

Override workload defaults with custom pressure multipliers:

```bash
python generate_synthetic_dmv.py \
  --workload mixed \
  --days 7 \
  --queries 100 \
  --cpu-pressure 2.5 \
  --io-pressure 1.8 \
  --memory-pressure 2.0
```

### Export Formats

**Text format (semicolon-delimited, SQL Server compatible)**:
```bash
python generate_synthetic_dmv.py --workload mixed --format text
```

**CSV format (with headers)**:
```bash
python generate_synthetic_dmv.py --workload mixed --format csv
```

**Both formats**:
```bash
python generate_synthetic_dmv.py --workload mixed --format both
```

### Advanced Configuration

```bash
python generate_synthetic_dmv.py \
  --workload mixed \
  --days 14 \
  --queries 200 \
  --interval-hours 1 \
  --output ./my_synthetic_data \
  --format both \
  --seed 12345 \
  --cpu-pressure 1.5
```

### Command-Line Options

**generate_synthetic_dmv.py**:
- `--workload` - Workload scenario (oltp, olap, mixed, cpu_pressure, io_bottleneck, memory_pressure, blocking, parameter_sniffing)
- `--days` - Number of days to generate (default: 7)
- `--queries` - Number of unique queries (default: 100)
- `--interval-hours` - Stats collection interval in hours (default: 1)
- `--output` - Output directory (default: ./synthetic_output)
- `--format` - Export format: text, csv, or both (default: text)
- `--seed` - Random seed for reproducibility (default: 42)
- `--cpu-pressure` - CPU pressure multiplier (optional)
- `--io-pressure` - I/O pressure multiplier (optional)
- `--memory-pressure` - Memory pressure multiplier (optional)

**analyze_real_dmv.py**:
- `input_dir` - Directory containing Query Store DMV files
- `--max-rows` - Max rows to parse per file (default: 1000, use -1 for all)
- `--delimiter` - Field delimiter (default: semicolon)

## Output Files

The generator creates files matching SQL Server Query Store DMV structure:

```
synthetic_output/
├── sys.query_store_runtime_stats_interval.txt  # Time intervals
├── sys.query_store_query_text.txt              # SQL query texts
├── sys.query_store_query.txt                   # Query metadata
├── sys.query_store_plan.txt                    # Execution plans
├── sys.query_store_runtime_stats.txt           # Runtime statistics
└── sys.query_store_wait_stats.txt              # Wait statistics
```

## Architecture

### Module Structure

```
synthetic_dmv_generator/
├── config.py                   # Configuration and constants
├── analyzers/                  # Analysers
│   ├── dmv_parser.py
│   └── statistical_analyzer.py
├── models/                     # Data models
│   ├── base.py
│   ├── errorlog.py
│   ├── intervals.py
│   ├── query_text.py
│   ├── query.py
│   ├── plan.py
│   ├── runtime_stats.py
│   └── wait_stats.py
├── generators/                 # Data generators
│   ├── base_generator.py
│   ├── errorlog_generator.py
│   ├── synthetic_generator.py
│   └── workload_patterns.py
├── analyzers/                  # Real data analyzers
│   ├── dmv_parser.py
│   └── statistical_analyzer.py
├── exporters/                  # Export to various formats
│   ├── text_exporter.py
│   ├── errorlog_exporter.py
│   └── csv_exporter.py
└── utils/                      # Utilities
    ├── distributions.py        # Statistical distributions
    ├── correlations.py         # Relationship tracking
    └── validators.py           # Data validation
```

### Key Design Principles

1. **Statistical Realism**
   - Log-normal distributions for query durations (matches reality)
   - Correlated metrics (CPU ∝ duration, physical reads ∝ logical reads)
   - Realistic wait time distributions

2. **Referential Integrity**
   - Query text → Query → Plan → Runtime Stats → Wait Stats
   - Proper foreign key relationships maintained
   - Time interval associations preserved

3. **Configurability**
   - Multiple workload scenarios
   - Adjustable pressure factors
   - Customizable time ranges and volumes

4. **Extensibility**
   - Easy to add new workload patterns
   - Pluggable exporters
   - Modular generator architecture

## Use Cases

### 1. Develop SQL Optimization Systems
Generate realistic test data to develop AI-powered query optimization tools:

```bash
python generate_synthetic_dmv.py --workload mixed --days 30 --queries 200
```

### 2. Test Performance Analysis Tools
Create specific problem scenarios for testing analysis algorithms:

```bash
python generate_synthetic_dmv.py --workload cpu_pressure --days 7
python generate_synthetic_dmv.py --workload io_bottleneck --days 7
```

### 3. Training and Demos
Generate clean, shareable data for training without exposing production queries:

```bash
python generate_synthetic_dmv.py --workload oltp --days 3 --format csv --queries 50
```

### 4. Benchmark Testing
Create reproducible datasets for performance testing:

```bash
python generate_synthetic_dmv.py --workload mixed --days 7 --seed 12345
```

### 5. Claude-based Analysis Development
Perfect for developing systems that use Claude to analyze SQL Server performance:

```bash
# Generate problematic workload
python generate_synthetic_dmv.py --workload parameter_sniffing --days 5

# Use output files with Claude to develop analysis prompts
# Feed the synthetic DMV data to Claude for optimization recommendations
```

## LLM Analysis Workflow

After generating synthetic DMV data, use `parse_dmv_for_llm.py` to create a consolidated JSON summary optimized for LLM analysis:

### Generate LLM-Ready Summary

```bash
# Parse synthetic DMV data and error logs into LLM-friendly JSON
python parse_dmv_for_llm.py ./synthetic_output --output dmv_summary_for_llm.json
```

This script:
- **Aggregates all DMV files** - Combines query texts, runtime stats, wait stats, and error logs
- **Calculates key metrics** - Computes averages, P95/P99 percentiles, totals
- **Identifies problems** - Highlights slow queries, high CPU/IO consumers, error patterns
- **Produces compact JSON** - Optimized format for LLM token limits (~10-50KB instead of MBs)

### LLM Analysis Use Cases

**1. Performance Optimization Recommendations**
```bash
# Generate data with performance issues
python generate_synthetic_dmv.py --workload cpu_pressure --days 7 --queries 100

# Create LLM summary
python parse_dmv_for_llm.py ./synthetic_output

# Feed dmv_summary_for_llm.json to Claude/GPT-4 with prompt:
# "Analyze this SQL Server performance data and provide optimization recommendations"
```

**2. Root Cause Analysis**
```bash
# Generate problematic workload
python generate_synthetic_dmv.py --workload io_bottleneck --days 5

# Parse for LLM
python parse_dmv_for_llm.py ./synthetic_output

# Ask LLM: "What is causing the I/O bottleneck in this system?"
```

**3. Query Tuning Suggestions**
```bash
# Generate mixed workload with various query patterns
python generate_synthetic_dmv.py --workload mixed --days 14 --queries 200

# Create summary
python parse_dmv_for_llm.py ./synthetic_output

# Ask LLM: "Which queries should be optimized first and how?"
```

### Output Structure

The `dmv_summary_for_llm.json` contains:
- **Summary statistics** - Total queries, time ranges, execution counts
- **Top slow queries** - Worst performers with full SQL text
- **Resource consumers** - High CPU, I/O, memory usage queries
- **Wait analysis** - Breakdown of wait categories and bottlenecks
- **Error patterns** - Categorized errors from the error log
- **Performance trends** - Temporal patterns and anomalies

### Example LLM Prompts

Copy the JSON content and use these prompts:

```
"Analyze this SQL Server DMV data and identify the top 5 performance bottlenecks"

"Based on the wait statistics, what is the primary constraint on this system?"

"Review the slow queries and suggest specific index improvements"

"Identify any parameter sniffing or plan quality issues"

"Provide an executive summary of database health and urgent actions needed"
```

## Understanding the Data

### Runtime Statistics
- **Duration** - Total query execution time (microseconds)
- **CPU Time** - CPU consumption (microseconds, typically 60-90% of duration)
- **Logical Reads** - Data pages read from buffer pool (8KB pages)
- **Physical Reads** - Disk reads (depends on cache hit ratio, ~5-10% of logical)
- **Row Count** - Rows returned/affected
- **Memory** - Max memory grant used (8KB pages)

### Wait Statistics
Common wait categories:
- **Buffer IO** - Waiting for data pages from disk
- **Network IO** - Client network communication
- **Parallelism** - Parallel query coordination waits
- **Memory** - Memory grant waits
- **Preemptive** - External waits (OS, CLR)

### Query Types Generated

**OLTP queries**:
- Point lookups by ID
- Single-row inserts
- Targeted updates
- Small deletes

**OLAP queries**:
- Multi-table joins
- Aggregations (SUM, AVG, COUNT)
- GROUP BY operations
- Large result sets

**Problematic queries**:
- Leading wildcard searches (`LIKE '%value%'`)
- Functions on indexed columns
- Missing WHERE clauses (table scans)
- Cross joins

## Performance Tips

### Generate Large Datasets
For very large datasets (100k+ queries), consider:
- Lower interval hours (--interval-hours 4)
- Generate in batches
- Use CSV format for faster processing

### Reproducibility
Always use `--seed` for reproducible results:
```bash
python generate_synthetic_dmv.py --workload mixed --seed 42
```

### Memory Usage
Monitor memory when generating:
- 100 queries, 7 days ≈ 50 MB RAM
- 1000 queries, 30 days ≈ 500 MB RAM

## Examples

### Example 1: Analyze Real Data, Then Generate Similar

```bash
# Step 1: Analyze your real DMV exports
python analyze_real_dmv.py /path/to/real/dmv/files

# Step 2: Based on analysis, generate similar synthetic data
python generate_synthetic_dmv.py \
  --workload mixed \
  --days 7 \
  --queries 100 \
  --cpu-pressure 1.2 \
  --io-pressure 1.5
```

### Example 2: Create Multiple Scenario Datasets

```bash
# Generate baseline
python generate_synthetic_dmv.py --workload mixed --days 7 --output ./baseline

# Generate CPU pressure scenario
python generate_synthetic_dmv.py --workload cpu_pressure --days 7 --output ./cpu_problem

# Generate I/O problem scenario
python generate_synthetic_dmv.py --workload io_bottleneck --days 7 --output ./io_problem
```

### Example 3: Training Data for ML Models

```bash
# Generate diverse training data
for workload in oltp olap cpu_pressure io_bottleneck memory_pressure; do
  python generate_synthetic_dmv.py \
    --workload $workload \
    --days 7 \
    --format csv \
    --output "./training_data/$workload"
done
```

## Limitations

- **No actual query plans** - Plan XML not generated (can be added)
- **Simplified wait categories** - Real SQL Server has 800+ wait types
- **No temporal patterns** - Doesn't simulate time-of-day patterns
- **No index usage stats** - Doesn't generate index DMV data (yet)

## Future Enhancements

Potential additions:
- [ ] Generate actual XML query plans
- [ ] Time-of-day workload patterns
- [ ] Index usage statistics
- [ ] Missing index recommendations
- [ ] Blocking chain simulation
- [ ] Deadlock scenario generation
- [ ] Integration with SQL Server via pyodbc

## Troubleshooting

**Issue**: "No module named 'synthetic_dmv_generator'"
```bash
# Make sure you're in the correct directory
cd demos/004_sql_server
python generate_synthetic_dmv.py --help
```

**Issue**: Memory error with large datasets
```bash
# Reduce queries or days
python generate_synthetic_dmv.py --queries 50 --days 3
```

**Issue**: Files have wrong encoding
```bash
# Files use UTF-8 with BOM (matching SQL Server)
# Most tools handle this automatically
```

## Contributing

To add new workload scenarios:

1. Edit [workload_patterns.py](synthetic_dmv_generator/generators/workload_patterns.py)
2. Define new `QueryTypeProfile` or `WorkloadScenario`
3. Register in `get_workload_by_name()`

## License

Part of the ai-demos project. See main repository LICENSE.

## Support

For issues or questions:
1. Check this README
2. Review example commands
3. Open an issue in the main repository

## Citation

If you use this generator in research or publications:

```
SQL Server Query Store DMV Synthetic Data Generator
Part of ai-demos repository
https://github.com/LAB271/ai-demos
```

---

**Ready to start?** Generate your first synthetic dataset:

```bash
python generate_synthetic_dmv.py --workload mixed --days 7 --queries 100
```

Then use the output files to develop your Claude-powered SQL Server optimization system!
