# Quick Start Guide

Get started with the SQL Server DMV Synthetic Data Generator in 5 minutes.

## Installation

```bash
cd /Users/iheitlager/wc/ai-demos
uv sync
```

## Generate Your First Synthetic Dataset

### Basic Generation

Generate 7 days of mixed OLTP/OLAP workload data:

```bash
cd demos/004_sql_server
uv run generate_synthetic_dmv.py --workload mixed --days 7 --queries 100
```

Output:
```
✓ Generation complete!
Your synthetic DMV data is ready at: ./synthetic_output
```

### View Generated Files

```bash
ls -lh synthetic_output/
```

You should see:
- `sys.query_store_runtime_stats_interval.txt` - Time intervals
- `sys.query_store_query_text.txt` - SQL queries
- `sys.query_store_query.txt` - Query metadata
- `sys.query_store_plan.txt` - Execution plans
- `sys.query_store_runtime_stats.txt` - Performance metrics
- `sys.query_store_wait_stats.txt` - Wait statistics

### Inspect the Data

```bash
# View query texts
head -n 5 synthetic_output/sys.query_store_query_text.txt

# Check runtime statistics
head -n 3 synthetic_output/sys.query_store_runtime_stats.txt
```

## Analyze Real DMV Data (Optional)

If you have real SQL Server DMV exports:

```bash
uv run analyze_real_dmv.py /path/to/your/dmv/files --max-rows 1000
```

This shows you:
- Query duration patterns
- CPU utilization ratios
- I/O characteristics
- Wait statistics distribution

Use these insights to configure your synthetic generation.

## Try Different Workload Scenarios

### OLTP Workload (Fast, Frequent Queries)

```bash
uv run generate_synthetic_dmv.py --workload oltp --days 3 --queries 50
```

### OLAP Workload (Analytical Queries)

```bash
uv run generate_synthetic_dmv.py --workload olap --days 5 --queries 30
```

### CPU Pressure Problem Scenario

```bash
uv run generate_synthetic_dmv.py --workload cpu_pressure --days 2 --queries 75
```

### I/O Bottleneck Scenario

```bash
uv run generate_synthetic_dmv.py --workload io_bottleneck --days 3 --queries 60
```

## Export as CSV for Analysis

```bash
uv run generate_synthetic_dmv.py --workload mixed --days 7 --format csv
```

## Custom Configuration

Fine-tune pressure factors:

```bash
uv run generate_synthetic_dmv.py \
  --workload mixed \
  --days 7 \
  --queries 100 \
  --cpu-pressure 2.0 \
  --io-pressure 1.5 \
  --memory-pressure 2.0 \
  --output ./my_custom_data
```

## Use with Claude for SQL Optimization

1. **Generate problem scenario data:**
   ```bash
   uv run generate_synthetic_dmv.py --workload cpu_pressure --days 7 --format csv
   ```

2. **Feed to Claude for analysis:**
   - Upload the generated CSV files
   - Ask Claude to identify performance issues
   - Request optimization recommendations

3. **Example Claude prompt:**
   ```
   I have SQL Server Query Store DMV data. Please analyze the runtime statistics
   and wait statistics to identify:
   1. The top 10 most expensive queries
   2. Queries with high CPU utilization
   3. Queries causing I/O bottlenecks
   4. Missing index opportunities

   Suggest specific optimizations for each problematic query.
   ```

## Available Workload Types

- `oltp` - Fast transactional queries
- `olap` - Analytical queries with aggregations
- `mixed` - Balanced OLTP/OLAP workload
- `cpu_pressure` - High CPU utilization
- `io_bottleneck` - Disk I/O problems
- `memory_pressure` - Memory spills
- `blocking` - Lock contention
- `parameter_sniffing` - Query plan variability

## Common Use Cases

### 1. Testing Your Analysis Tool

```bash
# Generate baseline
uv run generate_synthetic_dmv.py --workload mixed --days 7 --output ./baseline --seed 42

# Generate problem scenario
uv run generate_synthetic_dmv.py --workload cpu_pressure --days 7 --output ./problem --seed 42

# Compare analysis results
```

### 2. Training Data for ML Models

```bash
for workload in oltp olap cpu_pressure io_bottleneck; do
  uv run generate_synthetic_dmv.py \
    --workload $workload \
    --days 7 \
    --format csv \
    --output "./training/$workload"
done
```

### 3. Demo Data for Presentations

```bash
# Clean, understandable data
uv run generate_synthetic_dmv.py --workload oltp --days 3 --queries 20 --format both
```

## Next Steps

1. **Read the full README** - [README.md](README.md)
2. **Experiment with different workloads** - Try all 8 scenarios
3. **Integrate with your analysis system** - Use generated data as input
4. **Develop Claude prompts** - Test optimization prompts with synthetic data

## Troubleshooting

**Command not found:**
```bash
# Make sure you use uv run
uv run generate_synthetic_dmv.py --help
```

**Memory issues:**
```bash
# Reduce scale
uv run generate_synthetic_dmv.py --queries 25 --days 2
```

**Need reproducible results:**
```bash
# Use --seed
uv run generate_synthetic_dmv.py --workload mixed --seed 12345
```

## Help

```bash
# Generation help
uv run generate_synthetic_dmv.py --help

# Analyzer help
uv run analyze_real_dmv.py --help
```

---

**Ready?** Generate your first dataset now:

```bash
uv run generate_synthetic_dmv.py --workload mixed --days 7
```

Then start building your Claude-powered SQL optimization system!
