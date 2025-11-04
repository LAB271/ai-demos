# SQL Server Log Anomaly Detection Demo

This demo implements a Phase 1 baseline anomaly detection system for SQL Server logs using an Isolation Forest algorithm.

## Overview

The system analyzes SQL Server logs to identify potential security anomalies including:
- Authentication failures
- Privilege escalation attempts
- Suspicious queries (DROP TABLE, etc.)
- Audit manipulation
- Malware indicators
- Performance anomalies

## Files

### Core Detection System
- `logfile_generator.py` - Generates synthetic SQL Server logs with embedded anomalies
- `anomaly_detector.py` - ML-based anomaly detection using Isolation Forest
- `sql_server_log.txt` - Sample log file (up to 50,000 entries)
- `anomaly_results.csv` - Detection results with scores and classifications

### LLM Integration Components
- `llm_processor.py` - Main processor class with multiple output formats
- `llm_examples.py` - Five different approaches for LLM integration
- `llm_prompt.txt` - Ready-to-use prompt for manual LLM analysis (generated)
- `llm_analysis_data.json` - Structured data for API integration (generated)

### Documentation
- `README.md` - This comprehensive guide
- `RESULTS.md` - Detailed Phase 1 analysis and performance metrics

## Setup

### Install Dependencies

```bash
# Using uv (recommended)
uv add pandas numpy scikit-learn scipy

# Or using pip
uv pip install pandas numpy scikit-learn scipy
```

## Usage

### 1. Generate Log Data

```bash
python demos/001_sql_logs/logfile_generator.py
```

This creates `sql_server_log.txt` with 1000 log entries containing ~0.15% security anomalies.

### 2. Run Anomaly Detection

```bash
python demos/001_sql_logs/anomaly_detector.py
```

This will:
- Parse the log file
- Train an Isolation Forest model
- Detect and display anomalies
- Save results to `anomaly_results.csv`

### 3. Process Results for LLM Analysis

```bash
# Generate all LLM integration formats
python demos/001_sql_logs/llm_processor.py

# Explore different integration approaches
python demos/001_sql_logs/llm_examples.py
```

This creates:
- `llm_prompt.txt` - Ready-to-paste prompt for manual analysis
- `llm_analysis_data.json` - Structured data for API integration
- Summary statistics and pattern analysis

## How It Works

### Algorithm: Isolation Forest

**Why Isolation Forest?**
- Designed for anomaly detection in imbalanced datasets
- Doesn't require labeled anomalies for training
- Fast and efficient for high-dimensional data
- Works by isolating observations (anomalies are easier to isolate)

### Feature Engineering

The detector extracts three types of features:

1. **TF-IDF Text Features (100 features)**
   - Captures unique words and 2-grams from log messages
   - Helps identify unusual commands or patterns

2. **Severity Encoding (1 feature)**
   - INFO = 0, WARNING = 1, ERROR = 2
   - Higher severity often correlates with issues

3. **Temporal Features (1 feature)**
   - Hour of day (0-23)
   - Unusual hours may indicate suspicious activity

### Parameters

- `contamination=0.002` (0.2%) - Expected proportion of anomalies
- `n_estimators=100` - Number of trees in the forest
- `max_features=100` - Maximum TF-IDF features to extract

## Output Explanation

### Anomaly Score
- **Lower scores** = more anomalous
- **Higher scores** = more normal
- Typically ranges from -0.2 to 0.4

### Example Output

```
🚨 Detected Anomalies (sorted by score):
────────────────────────────────────────────────────────────────────────────────

[1] Score: -0.1234
    Time: 2025-11-04 08:29:19
    Severity: ERROR
    Message: CPU usage spiked to 95% during query execution by 'wagnerkayla'.
```

## Results Interpretation

### True Anomalies
The generator creates anomalies in these categories:
- Authentication failures
- Privilege escalation (ALTER SERVER ROLE)
- Suspicious queries (DROP TABLE, xp_cmdshell)
- Audit manipulation
- Performance spikes

### False Positives
May include:
- Rare but legitimate database names
- Unusual but valid usernames
- Off-hours scheduled maintenance

## Tuning the Model

### Increase Sensitivity
```python
detector = LogAnomalyDetector(contamination=0.005)  # Detect more anomalies
```

### Decrease Sensitivity
```python
detector = LogAnomalyDetector(contamination=0.001)  # Detect fewer anomalies
```

### Adjust Feature Count
```python
self.vectorizer = TfidfVectorizer(
    max_features=200,  # More detailed text analysis
    ngram_range=(1, 3)  # Include 3-grams
)
```

## LLM Integration

Once you have anomaly detection results, you can leverage Large Language Models for deeper analysis and explanation.

### CSV Output Structure

The `anomaly_results.csv` contains:
```csv
timestamp,severity,message,raw,is_anomaly,anomaly_score
2025-11-04 17:08:08,INFO,Login succeeded for user 'heather10'.,2025-11-04 17:08:08 | INFO | Login succeeded...,False,0.149
2025-11-04 00:43:49,INFO,CHECKDB found 0 allocation errors...,2025-11-04 00:43:49 | INFO | CHECKDB found...,True,-0.003205
```

Where:
- `is_anomaly`: Boolean flag (True = anomalous)  
- `anomaly_score`: Negative scores = higher anomaly confidence
- `timestamp`, `severity`, `message`: Original log data
- `raw`: Complete raw log entry

### Five LLM Integration Approaches

#### 1. Quick Analysis (Simple Prompt)
For immediate triage and daily security reviews:

```python
from llm_processor import AnomalyLLMProcessor

processor = AnomalyLLMProcessor("anomaly_results.csv")
high_conf = processor.get_high_confidence_anomalies()
top_3 = high_conf.head(3)
# Send to your LLM of choice
```

#### 2. API Integration (Structured JSON)
For automated analysis and integration with security tools:

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

#### 3. Comprehensive Analysis (Full Context)
For weekly security reports, incident analysis, and compliance reporting:

```python
processor = AnomalyLLMProcessor("anomaly_results.csv")
prompt = processor.create_llm_prompt(processor.get_anomalies_for_llm(limit=10))
# Includes dataset summary, pattern analysis, context, and structured requests
```

#### 4. Streaming Analysis (Chunked Processing)
For real-time monitoring and large datasets:

```python
all_anomalies = processor.get_anomalies_for_llm(limit=None)
chunk_size = 5

for i in range(0, len(all_anomalies), chunk_size):
    chunk = all_anomalies[i:i + chunk_size]
    # Process each chunk separately
```

#### 5. Threat Hunting (Focused Analysis)
For incident response and targeted investigations:

```python
# Focus on specific anomaly patterns
checkdb_anomalies = processor.df[
    (processor.df['is_anomaly']) & 
    (processor.df['message'].str.contains('CHECKDB', case=False))
]
```

### LLM API Integration Examples

#### OpenAI API
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

#### Anthropic Claude
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

#### Local LLM (Ollama)
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

### LLM Analysis Framework

The generated prompts request structured analysis including:

1. **Pattern Analysis** - Why flagged as anomalous
2. **Security Implications** - Potential risks  
3. **False Positive Assessment** - Likelihood of false positives
4. **Recommendations** - Specific actions to take
5. **Anomaly Type** - Classification (authentication, privilege escalation, etc.)
6. **Risk Assessment** - Security risk level (Low/Medium/High/Critical)

### Customization Options

#### Filter by Confidence
```python
# Only high-confidence anomalies (more negative = more anomalous)
high_conf = processor.get_high_confidence_anomalies(score_threshold=-0.01)
```

#### Focus on Specific Patterns
```python
# Filter by message content
suspicious_logins = processor.df[
    (processor.df['is_anomaly']) & 
    (processor.df['message'].str.contains('Login', case=False))
]
```

#### Adjust Context Window
```python
# Include more/less context around anomalies
anomalies = processor.get_anomalies_for_llm(
    limit=10, 
    include_context=True  # Set False to exclude surrounding logs
)
```

### Best Practices

#### For Production Use
1. **Start Small**: Begin with top 5-10 highest confidence anomalies
2. **Include Context**: Always include surrounding logs for better analysis
3. **Batch Processing**: Use chunked approach for large datasets
4. **Regular Updates**: Re-run analysis as new anomalies are detected

#### For Investigation
1. **Focus Analysis**: Use threat-specific filtering for targeted investigations
2. **Cross-Reference**: Compare LLM analysis with known attack patterns
3. **Validate Findings**: Use LLM output to guide manual investigation
4. **Document Results**: Save LLM analysis for compliance and reporting

## Next Steps (Phase 2)

1. **Generate more data** - 10,000+ logs for better training
2. **Add supervised learning** - Label anomalies for Random Forest/XGBoost
3. **Implement autoencoder** - Deep learning approach for complex patterns
4. **Real-time detection** - Stream processing with alerting
5. **Feature expansion** - User behavior baselines, query pattern analysis
6. **Evaluation metrics** - Precision, recall, F2-score with labeled test set

## Limitations

- **Small initial dataset** - Starts with 1000 logs, scales to 50,000
- **No ground truth validation** - Can't measure accuracy without labels
- **Static threshold** - Contamination parameter is fixed
- **No temporal sequences** - Doesn't model log sequences over time
- **Simple features** - Could benefit from entity extraction, query parsing
- **False positive tuning needed** - Currently detects rare patterns vs. security threats

## Troubleshooting

### Common Issues

**No anomalies found**: Check if `is_anomaly` column contains any `True` values
```python
processor = AnomalyLLMProcessor("anomaly_results.csv")
print(f"Anomalies found: {len(processor.df[processor.df['is_anomaly']])}")
```

**Empty output files**: Ensure anomaly_results.csv is in the correct format
```python
processor = AnomalyLLMProcessor("anomaly_results.csv")
print(processor.df.columns.tolist())  # Should show expected columns
```

**Large prompt sizes**: Reduce limit parameter or use chunked processing
```python
anomalies = processor.get_anomalies_for_llm(limit=5)  # Smaller batches
```

## References

- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Log Anomaly Detection Survey](https://arxiv.org/abs/2009.07376)
