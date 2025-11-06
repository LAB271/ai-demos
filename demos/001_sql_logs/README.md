# SQL Server Log Anomaly Detection & LLM Demo

This demo showcases how to detect security anomalies in SQL Server logs using machine learning, and how to leverage Large Language Models (LLMs) to generate human-readable analysis and recommendations from the results.

## Overview

- **Goal:** Identify potential security threats in SQL Server logs and generate actionable insights using AI.
- **Approach:** Use Isolation Forest algorithm to detect anomalies, then process results with LLMs for detailed security analysis.

## Main Features

- **Log Generation:** Create synthetic SQL Server logs with embedded security anomalies.
- **ML Detection:** Unsupervised anomaly detection using Isolation Forest algorithm.
- **LLM Analysis:** Automatically generate security insights and recommendations using LLMs.
- **Multiple Integrations:** Support for OpenAI, Anthropic, and local LLMs.

## Files

- `logfile_generator.py` — Generates synthetic SQL Server logs with embedded anomalies.
- `anomaly_detector.py` — ML-based anomaly detection using Isolation Forest.
- `llm_processor.py` — Processes results for LLM analysis with multiple output formats.
- `llm_examples.py` — Five different approaches for LLM integration.
- `RESULTS.md` — Detailed Phase 1 analysis and performance metrics.

## Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  logfile_        │    │  anomaly_        │    │  llm_            │
│  generator.py    │───▶│  detector.py     │───▶│  processor.py    │
│                  │    │                  │    │                  │
│ Generate logs    │    │ ML Detection     │    │ LLM Analysis     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Example Workflow



1. **Generate Log Data:**
   ```bash
   python logfile_generator.py
   ```

2. **Run Anomaly Detection:**
   ```bash
   python anomaly_detector.py
   ```

3. **Process for LLM Analysis:**
   ```bash
   python llm_processor.py
   python llm_examples.py
   ```

4. **Review Output:**
   - Anomaly detection results in `anomaly_results.csv`
   - LLM-ready prompts in `llm_prompt.txt`
   - Structured data in `llm_analysis_data.json`

## Use Cases

- Database security monitoring
- Threat detection and analysis
- Automated security reporting
- Educational demo for AI-driven cybersecurity

## Requirements

- Python 3.14+
- pandas, numpy, scikit-learn, scipy
- OpenAI API key (for LLM analysis, if using GPT-4)

## Next Steps

- Add supervised learning with labeled anomalies
- Implement real-time detection with streaming
- Enhance feature engineering for better accuracy
- Integrate with SIEM platforms

---

This demo is part of the `ai-demos` project, illustrating practical AI and data analysis workflows for cloud and security teams.
