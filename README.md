# AI Demos

A collection of practical AI and machine learning demonstrations focusing on cybersecurity applications and anomaly detection.

## Project Overview

This repository contains AI/ML demonstrations that showcase real-world applications in cybersecurity, particularly around log analysis and anomaly detection. The project is built with modern Python tooling and includes comprehensive examples of machine learning workflows integrated with Large Language Models (LLMs).

## Features

- **SQL Server Log Anomaly Detection**: Complete ML pipeline using Isolation Forest algorithm
- **LLM Integration**: Multiple approaches for feeding ML results to Large Language Models
- **Production-Ready Code**: Comprehensive testing, linting, and dependency management
- **Comprehensive Documentation**: Detailed guides and results analysis

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/LAB271/ai-demos.git
cd ai-demos

# Set up development environment
make env

# Activate virtual environment
source .venv/bin/activate
```

### Basic Usage

```bash
# Run the main demo
python main.py

# Generate SQL logs and detect anomalies
cd demos/001_sql_logs
python logfile_generator.py
python anomaly_detector.py

# Process results for LLM analysis
python llm_processor.py
python llm_examples.py
```

## Demos

### 001: SQL Server Log Anomaly Detection

**Location**: `demos/001_sql_logs/`

A complete implementation of anomaly detection for SQL Server logs featuring:

#### Core Components
- **`logfile_generator.py`** - Generates synthetic SQL logs with embedded security anomalies
- **`anomaly_detector.py`** - ML-based detection using Isolation Forest algorithm
- **`llm_processor.py`** - Processes results for LLM analysis
- **`llm_examples.py`** - Five different LLM integration approaches

#### Key Features
- **50,000 log entries** with realistic SQL Server operations
- **Isolation Forest algorithm** for unsupervised anomaly detection
- **TF-IDF + temporal features** for pattern recognition
- **LLM integration ready** with structured output formats
- **Comprehensive analysis** including false positive assessment

#### Security Threats Detected
- Authentication failures and suspicious logins
- Privilege escalation attempts (ALTER SERVER ROLE)
- Malicious queries (DROP TABLE, xp_cmdshell)
- Audit log manipulation
- Performance anomalies indicating attacks
- Off-hours database access patterns

#### Output Formats
- **CSV Results**: `anomaly_results.csv` with scores and classifications
- **LLM-Ready JSON**: `llm_analysis_data.json` for API integration
- **Analysis Prompts**: `llm_prompt.txt` for manual review
- **Statistical Reports**: Comprehensive performance metrics

#### Documentation
- **`README.md`** - Complete setup and usage guide
- **`RESULTS.md`** - Detailed analysis of Phase 1 results
- **`LLM_INTEGRATION_GUIDE.md`** - Comprehensive LLM integration guide

## Architecture

### Dependencies
- **pandas** & **numpy** - Data manipulation and analysis
- **scikit-learn** - Machine learning algorithms (Isolation Forest)
- **scipy** - Statistical computations
- **faker** - Synthetic data generation

### Development Tools
- **uv** - Fast Python package manager
- **ruff** - Linting and code formatting
- **pytest** - Testing framework
- **Makefile** - Development workflow automation

## Usage Examples

### Basic Anomaly Detection

```python
from demos.001_sql_logs.anomaly_detector import LogAnomalyDetector

# Initialize detector
detector = LogAnomalyDetector()

# Load and analyze logs
detector.load_data("sql_server_log.txt")
detector.train()
anomalies = detector.detect_anomalies()

# Display results
detector.display_anomalies()
```

### LLM Integration

```python
from demos.001_sql_logs.llm_processor import AnomalyLLMProcessor

# Process results for LLM analysis
processor = AnomalyLLMProcessor("anomaly_results.csv")
anomalies = processor.get_anomalies_for_llm(limit=10, include_context=True)

# Generate structured prompt
prompt = processor.create_llm_prompt(anomalies)
```

### API Integration

```python
import json

# Load structured data for API calls
with open("llm_analysis_data.json", "r") as f:
    data = json.load(f)

# Ready for OpenAI, Anthropic, or local LLM APIs
api_payload = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are a cybersecurity analyst..."},
        {"role": "user", "content": data["llm_prompt"]}
    ]
}
```

## Development

### Available Commands

```bash
# Development environment setup
make env          # Set up virtual environment and dependencies
make check        # Validate development dependencies

# Code quality
make lint         # Run linting and formatting checks
make format       # Format code with ruff
make lint-fix     # Fix linting issues automatically

# Testing
make test         # Run test suite

# Cleanup
make clean        # Clean up environment and cache files
```

### Project Structure

```
ai-demos/
├── demos/
│   └── 001_sql_logs/           # SQL log anomaly detection demo
│       ├── anomaly_detector.py # Core ML algorithm
│       ├── logfile_generator.py # Synthetic data generation
│       ├── llm_processor.py    # LLM integration processor
│       ├── llm_examples.py     # Integration examples
│       ├── README.md           # Demo documentation
│       ├── RESULTS.md          # Analysis results
│       └── LLM_INTEGRATION_GUIDE.md # LLM guide
├── main.py                     # Main entry point
├── pyproject.toml             # Project configuration
├── Makefile                   # Development commands
└── README.md                  # This file
```

## Results & Performance

### Phase 1 Results (Latest Run)
- **Dataset Size**: 50,000 log entries
- **Detection Rate**: 93 anomalies (0.186%)
- **Processing Time**: < 5 seconds
- **False Positive Rate**: Requires tuning (detected mostly rare patterns)

### Key Insights
- ✅ Successfully identifies statistical outliers in log patterns
- ✅ Fast, scalable processing for large datasets
- ✅ Comprehensive LLM integration capabilities
- ⚠️ Needs security-specific feature engineering for real threats
- ⚠️ Requires labeled data for validation and tuning

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Phase 2 (Planned)
- [ ] Semi-supervised learning with labeled anomalies
- [ ] Deep learning autoencoder for complex patterns
- [ ] Real-time streaming anomaly detection
- [ ] Integration with SIEM platforms
- [ ] User behavior analytics

### Phase 3 (Future)
- [ ] Multi-modal feature engineering
- [ ] Active learning with analyst feedback
- [ ] Explainable AI for anomaly explanations
- [ ] Production deployment examples

## Acknowledgments

- Built with modern Python tooling (uv, ruff, pytest)
- Inspired by real-world cybersecurity challenges
- Designed for educational and demonstration purposes
