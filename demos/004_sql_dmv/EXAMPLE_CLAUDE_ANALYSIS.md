# Example: Using Synthetic DMV Data with Claude for SQL Server Optimization

This guide shows how to use the generated synthetic DMV data with Claude to develop and test a SQL Server optimization system.

## Step 1: Generate Problem Scenario Data

First, generate synthetic data with a known performance problem:

```bash
cd demos/004_sql_server

# Generate CPU pressure scenario
uv run generate_synthetic_dmv.py \
  --workload cpu_pressure \
  --days 7 \
  --queries 50 \
  --format csv \
  --output ./cpu_pressure_scenario
```

## Step 2: Prepare Data for Claude

The generator creates these files in CSV format:
- `sys.query_store_runtime_stats.csv` - Performance metrics
- `sys.query_store_query_text.csv` - SQL queries
- `sys.query_store_wait_stats.csv` - Wait statistics
- `sys.query_store_query.csv` - Query metadata
- `sys.query_store_plan.csv` - Execution plans

## Step 3: Example Claude Prompt for Analysis

### Prompt Template 1: Identify Performance Issues

```
I have SQL Server Query Store DMV data exported as CSV files. Please analyze this data
and identify the top performance issues.

Dataset overview:
- Time period: 7 days
- Workload: Mixed OLTP/OLAP with CPU pressure
- Data files: runtime_stats, query_text, wait_stats

Please provide:

1. TOP 10 MOST EXPENSIVE QUERIES
   - Query text
   - Average duration (ms)
   - Total CPU time
   - Execution count
   - Performance impact score

2. RESOURCE BOTTLENECKS
   - CPU pressure indicators
   - I/O bottleneck signs
   - Memory pressure issues

3. WAIT STATISTICS ANALYSIS
   - Most common wait types
   - Queries with high wait times
   - Wait time patterns

4. OPTIMIZATION RECOMMENDATIONS
   For each problematic query, suggest:
   - Index recommendations
   - Query rewriting suggestions
   - Configuration changes
   - Execution plan improvements

[Attach: sys.query_store_runtime_stats.csv]
[Attach: sys.query_store_query_text.csv]
[Attach: sys.query_store_wait_stats.csv]
```

### Prompt Template 2: Specific Query Optimization

```
I need help optimizing a specific slow query from SQL Server Query Store data.

Query Details:
- Query ID: 42
- Average duration: 5000ms
- CPU time: 4500ms
- Logical reads: 500,000 pages
- Execution count: 10,000/day

[Provide query text from sys.query_store_query_text.csv]

Wait Statistics for this query:
- Buffer IO: 30%
- Parallelism: 25%
- CPU: 45%

Please analyze and suggest:
1. Why is this query slow?
2. What indexes are likely missing?
3. How can I rewrite this query to be more efficient?
4. Are there any query hints that might help?
5. Should I consider partitioning or other structural changes?

[Attach relevant rows from the CSV files]
```

### Prompt Template 3: Trend Analysis

```
Analyze these 7 days of SQL Server performance data and identify trends:

1. PERFORMANCE TRENDS
   - Is performance degrading over time?
   - Which queries show increasing duration?
   - Are execution counts growing?

2. PROBLEM PATTERNS
   - Time-of-day patterns
   - Queries that consistently perform poorly
   - New slow queries that appeared recently

3. CAPACITY PLANNING
   - Based on current trends, when will we hit resource limits?
   - Which resources (CPU/Memory/IO) are most constrained?
   - Growth projections

4. PROACTIVE RECOMMENDATIONS
   - What should we optimize first?
   - What monitoring should we implement?
   - What preventive measures should we take?

[Attach: all CSV files]
```

## Step 4: Example Analysis Workflow

### Generate Multiple Scenarios

```bash
# Baseline (normal workload)
uv run generate_synthetic_dmv.py \
  --workload mixed \
  --days 7 \
  --output ./baseline \
  --seed 42

# CPU problem
uv run generate_synthetic_dmv.py \
  --workload cpu_pressure \
  --days 7 \
  --output ./cpu_problem \
  --seed 42

# I/O problem
uv run generate_synthetic_dmv.py \
  --workload io_bottleneck \
  --days 7 \
  --output ./io_problem \
  --seed 42
```

### Compare with Claude

```
I have three datasets representing different SQL Server performance scenarios:

1. BASELINE: Normal mixed workload
2. CPU_PROBLEM: High CPU utilization scenario
3. IO_PROBLEM: I/O bottleneck scenario

Please compare these three scenarios and explain:

1. How do the key metrics differ?
   - Average query duration
   - CPU utilization
   - I/O patterns
   - Wait statistics

2. What distinguishes each scenario?
   - Unique characteristics of each problem type
   - Diagnostic indicators

3. How would you diagnose which scenario a production system is experiencing?
   - Key metrics to check
   - Diagnostic queries to run
   - Monitoring thresholds

4. What are the specific remediation steps for each scenario?

[Attach CSV files from all three scenarios]
```

## Step 5: Develop Automated Analysis System

Use Claude to help build Python scripts that automate analysis:

```python
# Example: analyze_performance.py
import pandas as pd

# Load synthetic DMV data
runtime_stats = pd.read_csv('sys.query_store_runtime_stats.csv')
query_texts = pd.read_csv('sys.query_store_query_text.csv')
wait_stats = pd.read_csv('sys.query_store_wait_stats.csv')

# Find top 10 queries by total CPU time
top_cpu = runtime_stats.nlargest(10, 'avg_cpu_time')

# Join with query text
analysis = top_cpu.merge(
    query_texts,
    left_on='plan_id',  # Simplified - you'd join through proper keys
    right_on='query_text_id'
)

print("Top 10 CPU-consuming queries:")
print(analysis[['query_sql_text', 'avg_cpu_time', 'count_executions']])
```

Then ask Claude:

```
I'm building an automated SQL Server performance analysis system.
I have this basic script that identifies top CPU-consuming queries.

Please help me enhance it to:

1. Calculate a "performance impact score" considering:
   - Total CPU time
   - Execution frequency
   - Duration variability
   - Wait time percentage

2. Categorize queries into:
   - OLTP (fast, frequent)
   - OLAP (slow, analytical)
   - Problematic (inefficient patterns)

3. Generate specific recommendations for each category

4. Output a formatted report with:
   - Executive summary
   - Detailed findings
   - Prioritized recommendations
   - SQL statements ready to run

[Include your script and sample data]
```

## Step 6: Test Different Workload Scenarios

Test your analysis system against all workload types:

```bash
#!/bin/bash
# generate_all_scenarios.sh

WORKLOADS=("oltp" "olap" "mixed" "cpu_pressure" "io_bottleneck" "memory_pressure" "blocking" "parameter_sniffing")

for workload in "${WORKLOADS[@]}"; do
  echo "Generating $workload scenario..."

  uv run generate_synthetic_dmv.py \
    --workload "$workload" \
    --days 7 \
    --queries 50 \
    --format csv \
    --output "./scenarios/$workload"

  # Run your analysis
  python analyze_performance.py "./scenarios/$workload"
done
```

Then ask Claude:

```
I've run my SQL Server analysis tool against 8 different performance scenarios.
Please review the results and tell me:

1. Does my tool correctly identify the known issues in each scenario?
2. Are the recommendations appropriate for each problem type?
3. What am I missing?
4. How can I improve the accuracy of my analysis?

[Attach analysis results for all 8 scenarios]
```

## Step 7: Build Optimization Recommendation Engine

```
Help me build a recommendation engine that:

INPUT: SQL Server Query Store DMV data (CSV files)

PROCESSING:
1. Parse and analyze runtime statistics
2. Identify performance anti-patterns in query texts
3. Correlate wait statistics with query characteristics
4. Calculate performance impact scores

OUTPUT: Structured recommendations including:
1. Missing index recommendations (with CREATE INDEX statements)
2. Query rewrite suggestions (with BEFORE/AFTER SQL)
3. Configuration changes (with specific settings)
4. Architectural recommendations

Use the synthetic DMV data I've generated to develop and test this engine.

Requirements:
- Python-based
- Modular design
- Extensible for new analysis types
- Clear, actionable recommendations
- Confidence scores for each recommendation

[Provide synthetic data files and any existing code]
```

## Expected Outcomes

Using this approach, you can develop:

1. **Automated Performance Analysis**
   - Identify slow queries automatically
   - Categorize performance issues
   - Calculate impact scores

2. **Intelligent Recommendations**
   - Index suggestions
   - Query rewrites
   - Configuration tuning
   - Architecture improvements

3. **Trend Analysis**
   - Performance degradation detection
   - Capacity planning
   - Proactive problem identification

4. **Validated System**
   - Tested against 8 known scenarios
   - Reproducible results
   - Known ground truth for validation

## Benefits of Using Synthetic Data

1. **Safe Development** - No production data exposure
2. **Reproducible** - Same data every time (with seed)
3. **Comprehensive** - All 8 problem scenarios covered
4. **Scalable** - Generate as much data as needed
5. **Realistic** - Statistical patterns match real SQL Server

## Next Steps

1. Generate your scenarios
2. Test prompts with Claude
3. Refine your analysis approach
4. Build automated tools
5. Validate against all scenarios
6. Deploy to production with confidence

---

**Start now:**

```bash
# Generate first scenario
uv run generate_synthetic_dmv.py --workload cpu_pressure --days 7 --format csv

# Open Claude and start analyzing!
```
