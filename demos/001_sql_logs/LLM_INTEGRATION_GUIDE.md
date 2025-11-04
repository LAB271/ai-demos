# Processing Anomaly Detection Results for LLM Analysis

This guide explains how to take the output from your SQL Server log anomaly detector and prepare it for LLM (Large Language Model) analysis and explanation.

## Overview

Your `anomaly_results.csv` contains the following structure:
```csv
timestamp,severity,message,raw,is_anomaly,anomaly_score
2025-11-04 17:08:08,INFO,Login succeeded for user 'heather10'.,2025-11-04 17:08:08 | INFO | Login succeeded...,False,0.149
2025-11-04 00:43:49,INFO,CHECKDB found 0 allocation errors...,2025-11-04 00:43:49 | INFO | CHECKDB found...,True,-0.003205
```

Where:
- `is_anomaly`: Boolean flag (True = anomalous)
- `anomaly_score`: Negative scores indicate higher anomaly confidence
- `timestamp`, `severity`, `message`: Original log data
- `raw`: Complete raw log entry

## Files Created

1. **`llm_processor.py`** - Main processor class with multiple output formats
2. **`llm_examples.py`** - Five different approaches for LLM integration
3. **`llm_prompt.txt`** - Ready-to-use prompt for manual LLM analysis
4. **`llm_analysis_data.json`** - Structured data for API integration

## Usage Approaches

### 1. Quick Analysis (Simple Prompt)

For immediate analysis of the most suspicious anomalies:

```python
from llm_processor import AnomalyLLMProcessor

processor = AnomalyLLMProcessor("anomaly_results.csv")
high_conf = processor.get_high_confidence_anomalies()

# Get top 3 most suspicious
top_3 = high_conf.head(3)
# Send to your LLM of choice
```

**When to use**: Quick triage, daily security reviews

### 2. API Integration (Structured JSON)

For integration with LLM APIs (OpenAI, Anthropic, etc.):

```python
processor = AnomalyLLMProcessor("anomaly_results.csv")
anomalies = processor.get_anomalies_for_llm(limit=5, include_context=True)

# Ready for API calls
api_payload = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are a cybersecurity analyst..."},
        {"role": "user", "content": f"Analyze these anomalies: {json.dumps(anomalies)}"}
    ]
}
```

**When to use**: Automated analysis, integration with security tools

### 3. Comprehensive Analysis (Full Context)

For detailed security reports with statistical context:

```python
processor = AnomalyLLMProcessor("anomaly_results.csv")
prompt = processor.create_llm_prompt(processor.get_anomalies_for_llm(limit=10))

# Includes:
# - Dataset summary and statistics
# - Pattern analysis
# - Context around each anomaly
# - Structured analysis request
```

**When to use**: Weekly security reports, incident analysis, compliance reporting

### 4. Streaming Analysis (Chunked Processing)

For processing large numbers of anomalies in batches:

```python
all_anomalies = processor.get_anomalies_for_llm(limit=None)
chunk_size = 5

for i in range(0, len(all_anomalies), chunk_size):
    chunk = all_anomalies[i:i + chunk_size]
    # Process each chunk separately
```

**When to use**: Real-time monitoring, large datasets, resource-constrained environments

### 5. Threat Hunting (Focused Analysis)

For investigating specific types of security threats:

```python
# Focus on specific anomaly patterns
checkdb_anomalies = processor.df[
    (processor.df['is_anomaly']) & 
    (processor.df['message'].str.contains('CHECKDB', case=False))
]

# Create targeted threat hunting prompts
```

**When to use**: Incident response, targeted investigations, compliance audits

## LLM Prompt Structure

The generated prompts include:

### Dataset Context
- Total log entries and anomaly counts
- Time range and severity distributions
- Anomaly rate and patterns

### Individual Anomaly Analysis
For each anomaly:
- Timestamp and severity
- Anomaly confidence score
- Full message and raw log
- Surrounding log context (2 entries before/after)

### Analysis Framework
Structured requests for:
1. **Pattern Analysis** - Why flagged as anomalous
2. **Security Implications** - Potential risks
3. **False Positive Assessment** - Likelihood of false positives
4. **Recommendations** - Specific actions to take

## Running the Processor

### Generate All Formats
```bash
python llm_processor.py
```

This creates:
- Summary statistics
- Pattern analysis
- High-confidence anomaly identification
- Multiple output formats (JSON, TXT)

### Try Different Approaches
```bash
python llm_examples.py
```

This demonstrates all five integration approaches with your data.

## Output Files

### `llm_prompt.txt`
Ready-to-paste prompt for manual LLM analysis. Includes:
- 5-10 top anomalies with context
- Structured analysis request
- Expected response format

### `llm_analysis_data.json`
Structured data including:
```json
{
  "metadata": {
    "generated_at": "2025-11-04T19:11:37.462142",
    "total_anomalies": 10,
    "summary": { ... }
  },
  "anomalies": [ ... ],
  "llm_prompt": "..."
}
```

## Integration Examples

### OpenAI API
```python
import openai

client = openai.OpenAI(api_key="your-key")
processor = AnomalyLLMProcessor("anomaly_results.csv")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a cybersecurity analyst..."},
        {"role": "user", "content": processor.create_llm_prompt(anomalies)}
    ]
)
```

### Anthropic Claude
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")
processor = AnomalyLLMProcessor("anomaly_results.csv")

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[
        {"role": "user", "content": processor.create_llm_prompt(anomalies)}
    ]
)
```

### Local LLM (Ollama)
```python
import requests

processor = AnomalyLLMProcessor("anomaly_results.csv")
prompt = processor.create_llm_prompt(processor.get_anomalies_for_llm(limit=5))

response = requests.post('http://localhost:11434/api/generate', 
    json={
        "model": "llama3",
        "prompt": prompt
    }
)
```

## Customization Options

### Filter by Confidence
```python
# Only high-confidence anomalies (more negative = more anomalous)
high_conf = processor.get_high_confidence_anomalies(score_threshold=-0.01)
```

### Focus on Specific Patterns
```python
# Filter by message content
suspicious_logins = processor.df[
    (processor.df['is_anomaly']) & 
    (processor.df['message'].str.contains('Login', case=False))
]
```

### Adjust Context Window
```python
# Include more/less context around anomalies
anomalies = processor.get_anomalies_for_llm(
    limit=10, 
    include_context=True  # Set False to exclude surrounding logs
)
```

## Expected LLM Response Format

The prompts request structured responses including:

1. **Anomaly Type**: Classification (authentication, privilege escalation, etc.)
2. **Technical Analysis**: Why the ML model flagged it
3. **Risk Assessment**: Security risk level (Low/Medium/High/Critical)
4. **Explanation**: Detailed issue explanation
5. **Recommended Actions**: Specific investigation/remediation steps
6. **False Positive Likelihood**: Assessment of false positive probability

## Best Practices

### For Production Use
1. **Start Small**: Begin with top 5-10 highest confidence anomalies
2. **Include Context**: Always include surrounding logs for better analysis
3. **Batch Processing**: Use chunked approach for large datasets
4. **Regular Updates**: Re-run analysis as new anomalies are detected

### For Investigation
1. **Focus Analysis**: Use threat-specific filtering for targeted investigations
2. **Cross-Reference**: Compare LLM analysis with known attack patterns
3. **Validate Findings**: Use LLM output to guide manual investigation
4. **Document Results**: Save LLM analysis for compliance and reporting

## Troubleshooting

### Common Issues

**No anomalies found**: Check if `is_anomaly` column contains any `True` values
```python
print(f"Anomalies found: {len(processor.df[processor.df['is_anomaly']])}")
```

**Empty output files**: Ensure anomaly_results.csv is in the correct format
```python
print(processor.df.columns.tolist())  # Should show expected columns
```

**Large prompt sizes**: Reduce limit parameter or use chunked processing
```python
anomalies = processor.get_anomalies_for_llm(limit=5)  # Smaller batches
```

Your anomaly detection results are now ready for LLM analysis! Choose the approach that best fits your use case and security workflow.