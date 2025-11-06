# IAM Access Request Analysis & Validation Demo

This demo showcases how to analyze Identity and Access Management (IAM) access requests using rule-based validation and machine learning anomaly detection to identify potential security risks and policy violations.

## Overview

- **Goal:** Automate IAM access request validation, detect anomalous patterns, and prevent toxic role-system combinations that could pose security risks.
- **Approach:** Generate synthetic access request data, apply rule-based validation for toxic combinations, and use anomaly detection to identify suspicious patterns.

## Main Features

- **Data Generation:** Create realistic IAM access request datasets with embedded anomalies and policy violations.
- **Rule-Based Validation:** Enforce toxic combination policies (e.g., traders accessing infrastructure systems).
- **Anomaly Detection:** Use Isolation Forest to identify unusual access patterns and behaviors.
- **Risk Assessment:** Categorize requests as approved, high-risk, or rejected with detailed reasoning.

## Files

- `generate_access_request.py` — Generates synthetic employees and access request datasets with anomalies.
- `validate_access_requests.py` — Rule-based validation engine for toxic combinations and policy enforcement.
- `anomaly_detection.py` — ML-based anomaly detection using Isolation Forest algorithm.

## Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  generate_       │    │  validate_       │    │  anomaly_        │
│  access_request  │───▶│  access_requests │───▶│  detection.py    │
│  .py             │    │  .py             │    │                  │
│                  │    │                  │    │                  │
│ Generate data    │    │ Rule validation  │    │ ML Detection     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Example Workflow



1. **Generate Dataset:**
   ```bash
   python generate_access_request.py
   ```

2. **Validate Requests:**
   ```bash
   python validate_access_requests.py
   ```

3. **Run Anomaly Detection:**
   ```bash
   python anomaly_detection.py
   ```

4. **Review Output:**
   - Employee database in `employees.csv`
   - Access requests with validation results in `access_requests_validated.csv`
   - Anomaly detection results and visualizations

## Use Cases

- IAM access request automation
- Security policy enforcement
- Insider threat detection
- Compliance monitoring and reporting
- Educational demo for AI-driven security controls

## Requirements

- Python 3.8+
- pandas, numpy, scikit-learn
- matplotlib (for anomaly visualization)
- faker (for synthetic data generation)

## Next Steps

- Integrate with real IAM systems (Active Directory, Okta, etc.)
- Add temporal analysis for access pattern detection
- Implement role mining and recommendation engines
- Connect to SIEM platforms for real-time monitoring

---

This demo is part of the `ai-demos` project, illustrating practical AI and data analysis workflows for cloud and security teams.