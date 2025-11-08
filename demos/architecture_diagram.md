# AI Demos - Architecture Block Diagram

## Overview
This repository contains three AI demonstration workflows for different use cases: SQL Log Analysis, Azure Cost Analysis, and IAM Access Request Management.

## System Architecture

```mermaid
graph TB
    %% Main entry point
    main[main.py<br/>Entry Point]
    
    %% Demo 001: SQL Logs
    subgraph demo001[Demo 001: SQL Log Analysis & Anomaly Detection]
        loggen[logfile_generator.py<br/>Generates synthetic SQL logs]
        sqlnb[sql_log_generator_study.ipynb<br/>Interactive analysis & visualization]
        anomdet[anomaly_detector.py<br/>ML-based anomaly detection]
        llmproc[llm_processor.py<br/>Processes results for LLM]
        llmex[llm_examples.py<br/>Usage examples for LLMs]
        
        %% Data flows for Demo 001
        loggen --> sqlnb
        sqlnb --> anomdet
        anomdet --> llmproc
        llmproc --> llmex
        
        %% Data files for Demo 001
        sqllog[(SQL Log Files<br/>.log format)]
        anomres[(anomaly_results.csv)]
        llmprompt[(llm_prompt.txt)]
        llmjson[(llm_analysis_data.json)]
        
        loggen --> sqllog
        anomdet --> anomres
        llmproc --> llmprompt
        llmproc --> llmjson
        llmex -.-> llmjson
    end
    
    %% Demo 002: Azure Analysis
    subgraph demo002[Demo 002: Azure Cost Analysis]
        simpledata[simple_data.py<br/>Simple synthetic data generator]
        azuredata[azure_data.py<br/>Advanced Azure data generator]
        azureanalyze[analyze_azure_costs.py<br/>Cost analysis & insights]
        azurellm[generate_llm_summary.py<br/>LLM-ready summaries]
        
        %% Data flows for Demo 002
        simpledata --> azureanalyze
        azuredata --> azureanalyze
        azureanalyze --> azurellm
        
        %% Data files for Demo 002
        azurecsv[(azure_compute_usage_6months.csv)]
        azuresummary[(azure_cost_summary.json)]
        
        simpledata --> azurecsv
        azuredata --> azurecsv
        azureanalyze -.-> azurecsv
        azurellm --> azuresummary
    end
    
    %% Demo 003: IAM Recommendations
    subgraph demo003[Demo 003: IAM Access Request Management]
        genreq[generate_access_request.py<br/>Generates synthetic IAM requests]
        validatereq[validate_access_requests.py<br/>Validates against policies]
        anomiam[anomaly_detection.py<br/>ML-based access anomalies]
        
        %% Data flows for Demo 003
        genreq --> validatereq
        validatereq --> anomiam
        
        %% Data files for Demo 003
        employees[(employees.csv)]
        accessreq[(access_requests.csv)]
        validated[(access_requests_validated.csv)]
        
        genreq --> employees
        genreq --> accessreq
        validatereq --> validated
        anomiam -.-> validated
    end
    
    %% Testing infrastructure
    subgraph testing[Testing Infrastructure]
        testgen[test_generate_access_request.py<br/>Tests IAM generation]
        testazure[test_azure_data.py<br/>Tests Azure data generation]
        testlog[test_logfile_generator.py<br/>Tests log generation]
        
        %% Test relationships
        testgen -.-> genreq
        testazure -.-> azuredata
        testlog -.-> loggen
    end
    
    %% Configuration and build
    subgraph config[Configuration & Build]
        pyproject[pyproject.toml<br/>Python project config]
        makefile[Makefile<br/>Build & clean tasks]
        readme[README.md<br/>Documentation]
        license[LICENSE<br/>Apache 2.0]
    end
    
    %% External dependencies (shown as hexagons)
    pandas{{pandas<br/>Data manipulation}}
    sklearn{{scikit-learn<br/>ML algorithms}}
    faker{{faker<br/>Synthetic data}}
    matplotlib{{matplotlib<br/>Visualization}}
    
    %% Dependencies flow to modules
    pandas -.-> demo001
    pandas -.-> demo002
    pandas -.-> demo003
    sklearn -.-> anomdet
    sklearn -.-> anomiam
    faker -.-> loggen
    faker -.-> azuredata
    faker -.-> genreq
    matplotlib -.-> sqlnb
    matplotlib -.-> anomiam
    
    %% Styling
    classDef dataFile fill:#e1f5fe,stroke:#01579b,color:#000
    classDef pythonFile fill:#fff3e0,stroke:#e65100,color:#000
    classDef notebook fill:#f3e5f5,stroke:#4a148c,color:#000
    classDef dependency fill:#e8f5e8,stroke:#2e7d32,color:#000
    classDef config fill:#fafafa,stroke:#424242,color:#000
    
    class sqllog,anomres,llmprompt,llmjson,azurecsv,azuresummary,employees,accessreq,validated dataFile
    class loggen,anomdet,llmproc,llmex,simpledata,azuredata,azureanalyze,azurellm,genreq,validatereq,anomiam,testgen,testazure,testlog,main pythonFile
    class sqlnb notebook
    class pandas,sklearn,faker,matplotlib dependency
    class pyproject,makefile,readme,license config
```

## Data Flow Summary

### Demo 001: SQL Log Analysis
1. **logfile_generator.py** creates synthetic SQL server logs
2. **sql_log_generator_study.ipynb** provides interactive analysis and visualization
3. **anomaly_detector.py** uses ML (Isolation Forest) to detect anomalies in logs
4. **llm_processor.py** formats anomaly results for LLM consumption
5. **llm_examples.py** demonstrates various ways to feed data to LLMs

**Output Files:**
- SQL log files (.log format)
- `anomaly_results.csv` - Detected anomalies with scores
- `llm_prompt.txt` - Ready-to-use prompts for LLMs
- `llm_analysis_data.json` - Structured data for LLM APIs

### Demo 002: Azure Cost Analysis
1. **simple_data.py** OR **azure_data.py** generate synthetic Azure usage data
2. **analyze_azure_costs.py** performs cost analysis and identifies optimization opportunities
3. **generate_llm_summary.py** creates LLM-ready summaries for cost optimization

**Output Files:**
- `azure_compute_usage_6months.csv` - 6 months of Azure usage data
- `azure_cost_summary.json` - Structured summary for LLM analysis

### Demo 003: IAM Access Request Management
1. **generate_access_request.py** creates synthetic employees and access requests
2. **validate_access_requests.py** validates requests against security policies
3. **anomaly_detection.py** uses ML to detect unusual access patterns

**Output Files:**
- `employees.csv` - Synthetic employee database
- `access_requests.csv` - Generated access requests
- `access_requests_validated.csv` - Validated requests with risk assessments

## Key Dependencies

- **pandas**: Data manipulation and CSV handling across all demos
- **scikit-learn**: Machine learning for anomaly detection (Isolation Forest, TF-IDF)
- **faker**: Generating realistic synthetic data (names, dates, etc.)
- **matplotlib/seaborn**: Data visualization (primarily in notebooks)

## Testing Strategy

Each major component has corresponding unit tests in the `tests/` directory that validate data generation, processing logic, and output format integrity.

## Build System

- **Makefile**: Provides commands for setup, testing, cleaning, and dependency management
- **pyproject.toml**: Python project configuration with dependencies and metadata