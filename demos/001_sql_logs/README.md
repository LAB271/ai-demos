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

- `logfile_generator.py` - Generates synthetic SQL Server logs with embedded anomalies
- `anomaly_detector.py` - ML-based anomaly detection using Isolation Forest
- `sql_server_log.txt` - Sample log file (1000 entries)
- `anomaly_results.csv` - Detection results (generated after running)

## Setup

### Install Dependencies

```bash
# Using uv (recommended)
uv pip install pandas numpy scikit-learn scipy

# Or using pip
pip install pandas numpy scikit-learn scipy
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

## Next Steps (Phase 2)

1. **Generate more data** - 10,000+ logs for better training
2. **Add supervised learning** - Label anomalies for Random Forest/XGBoost
3. **Implement autoencoder** - Deep learning approach for complex patterns
4. **Real-time detection** - Stream processing with alerting
5. **Feature expansion** - User behavior baselines, query pattern analysis
6. **Evaluation metrics** - Precision, recall, F2-score with labeled test set

## Limitations

- **Small dataset** - Only 1000 logs, ~2 anomalies
- **No ground truth validation** - Can't measure accuracy without labels
- **Static threshold** - Contamination parameter is fixed
- **No temporal sequences** - Doesn't model log sequences over time
- **Simple features** - Could benefit from entity extraction, query parsing

## References

- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Log Anomaly Detection Survey](https://arxiv.org/abs/2009.07376)
