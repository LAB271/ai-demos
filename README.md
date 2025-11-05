# AI Demos

A collection of practical AI and machine learning demonstrations showcasing real-world applications in cybersecurity and data analysis.

## Purpose

This project demonstrates how AI and machine learning can be applied to solve common challenges in cybersecurity and IT operations. Each demo uses synthetic data to illustrate practical workflows that can be adapted for production environments.

The demos focus on:
- **Security Monitoring** - Anomaly detection in logs and access patterns
- **Cost Optimization** - AI-driven analysis of cloud spending
- **Access Management** - Automated validation and risk assessment

## Demos

| Demo | Description | Focus Area | README |
|------|-------------|------------|---------|
| **001** | SQL Server Log Anomaly Detection & LLM | Cybersecurity | [View README](demos/001_sql_logs/README.md) |
| **002** | Azure Cost Analysis & LLM | Cloud Operations | [View README](demos/002_azure/README.md) |
| **003** | IAM Access Request Analysis & Validation | Identity Management | [View README](demos/003_iam_recommendation/README.md) |

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LAB271/ai-demos.git
   cd ai-demos
   ```

2. **Set up environment:**
   ```bash
   make env
   source .venv/bin/activate
   ```

3. **Choose a demo and follow its README:**
   - Each demo is self-contained with its own instructions
   - Synthetic data is generated automatically
   - No external dependencies or APIs required to get started

## Why Synthetic Data?

These demos use synthetic data to:
- **Ensure Privacy** - No real customer or security data is exposed
- **Enable Learning** - Anyone can run the demos without access to production systems
- **Demonstrate Patterns** - Controlled datasets show clear examples of the techniques
- **Facilitate Testing** - Predictable data makes it easy to validate the AI models

## Next Steps

Each demo can be extended to work with real data sources:
- Connect to actual log management systems
- Integrate with cloud billing APIs  
- Link to enterprise IAM platforms

The synthetic examples provide the foundation for understanding the techniques before applying them to production environments.
