# Azure Cost Analysis & LLM Demo

This demo showcases how to analyze Azure cloud cost and usage data using Python, and how to leverage Large Language Models (LLMs) to generate human-readable summaries and insights from the results.

## Overview

- **Goal:** Help users understand their Azure spending, identify cost drivers, and generate actionable recommendations using AI.
- **Approach:** Parse and analyze Azure cost/usage data, then use an LLM to summarize findings and suggest optimizations.

## Main Features

- **Data Ingestion:** Load and process Azure cost and usage data from sample files.
- **Cost Analysis:** Identify top services, cost spikes, and trends.
- **LLM Summarization:** Automatically generate executive summaries and recommendations using an LLM (e.g., GPT-4).
- **Extensible:** Easily adapt to other cloud providers or custom datasets.

## Files

- `azure_data.py` — Loads and structures Azure cost/usage data.
- `simple_data.py` — Provides a minimal example dataset for testing.
- `analyze_azure_costs.py` — Main analysis script; computes cost breakdowns and trends.
- `generate_llm_summary.py` — Uses an LLM to create human-readable summaries and recommendations.

## Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  azure_data.py   │    │  analyze_azure_  │    │  generate_llm_   │    │  LLM             │
│  simple_data.py  │───▶│  costs.py        │───▶│  summary.py      │───▶│  Interpretation  │
│                  │    │                  │    │                  │    │                  │
│ Generate data    │    │ Cost Analysis    │    │ LLM Summary      │    │ Human Insights   │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Example Workflow



1. **Prepare Data:** Place your Azure cost/usage CSV or JSON file in the project directory.
2. **Run Analysis:**
   ```bash
   python analyze_azure_costs.py
   ```
3. **Generate LLM Summary:**
   ```bash
   python generate_llm_summary.py
   ```
4. **Review Output:**
   - Cost breakdowns and trends (printed or saved)
   - LLM-generated summary and recommendations

## Use Cases

- Cloud cost optimization
- Executive reporting
- Automated recommendations for cloud savings
- Educational demo for AI-driven analytics

## Requirements

- Python 3.8+
- OpenAI API key (for LLM summary, if using GPT-4)
- pandas, numpy (for data analysis)

## Next Steps

- Integrate with real Azure billing exports
- Add support for other cloud providers (AWS, GCP)
- Enhance LLM prompt engineering for more tailored recommendations
- Visualize cost trends with charts

---

This demo is part of the `ai-demos` project, illustrating practical AI and data analysis workflows for cloud and security teams.
