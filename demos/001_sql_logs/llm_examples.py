"""
Example Usage: How to Feed Anomaly Detection Results to an LLM

This script demonstrates different approaches for sending anomaly detection results
to an LLM for analysis and explanation.
"""

import json
from llm_processor import AnomalyLLMProcessor


def example_1_simple_prompt():
    """Example 1: Simple prompt with top anomalies"""
    print("=== Example 1: Simple Prompt ===")
    
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    
    # Get top 3 most suspicious anomalies
    high_conf = processor.get_high_confidence_anomalies()
    top_3 = high_conf.head(3)
    
    prompt = """Analyze these SQL Server log anomalies and explain why they might be suspicious:

"""
    
    for idx, row in top_3.iterrows():
        prompt += f"""
Anomaly {idx + 1}:
- Timestamp: {row['timestamp']}
- Severity: {row['severity']}
- Message: {row['message']}
- Anomaly Score: {row['anomaly_score']:.6f}
- Raw Log: {row['raw']}

"""
    
    prompt += """
For each anomaly, please explain:
1. Why it was flagged as anomalous
2. Potential security implications
3. Recommended actions
"""
    
    print(f"Prompt length: {len(prompt)} characters")
    print("First 500 characters:")
    print(prompt[:500] + "...")
    return prompt


def example_2_structured_json():
    """Example 2: Structured JSON data for LLM APIs"""
    print("\n=== Example 2: Structured JSON for API ===")
    
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    anomalies = processor.get_anomalies_for_llm(limit=5, include_context=True)
    
    # Format for OpenAI/Anthropic API
    system_message = """You are a cybersecurity analyst specializing in SQL Server log analysis. 
    Analyze the provided anomalous log entries and explain why they were flagged as suspicious."""
    
    user_message = f"""Please analyze these {len(anomalies)} anomalous SQL Server log entries:

{json.dumps(anomalies, indent=2)}

For each anomaly, provide:
1. Classification of anomaly type
2. Technical explanation of why it's suspicious  
3. Risk assessment (Low/Medium/High/Critical)
4. Recommended investigation steps
"""
    
    api_payload = {
        "model": "gpt-4",  # or claude-3-sonnet, etc.
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }
    
    print(f"API payload size: {len(json.dumps(api_payload))} characters")
    print("System message:", system_message[:100] + "...")
    return api_payload


def example_3_batch_analysis():
    """Example 3: Batch analysis with statistical context"""
    print("\n=== Example 3: Batch Analysis with Context ===")
    
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    
    # Get comprehensive analysis
    summary = processor.get_anomalies_summary()
    patterns = processor.analyze_patterns()
    top_anomalies = processor.get_anomalies_for_llm(limit=10)
    
    context_prompt = f"""# SQL Server Security Analysis Report

## Dataset Overview
- **Total Log Entries**: {summary['total_logs']:,}
- **Anomalies Detected**: {summary['total_anomalies']}
- **Detection Rate**: {summary['anomaly_rate']:.3f}%
- **Time Period**: {summary['time_range']['start']} to {summary['time_range']['end']}

## Pattern Analysis
**Message Patterns in Anomalies**:
{json.dumps(patterns['message_patterns'], indent=2)}

**Time Distribution**:
{json.dumps(patterns['hour_distribution'], indent=2)}

## Top 10 Anomalies Requiring Analysis
{json.dumps(top_anomalies, indent=2)}

## Analysis Request
As a senior cybersecurity analyst, please provide a comprehensive analysis covering:

### 1. Threat Assessment
- Overall risk level for the organization
- Most concerning anomalies and why
- Potential attack vectors indicated

### 2. Pattern Analysis  
- Common characteristics among anomalies
- Unusual timing patterns
- Severity level distributions

### 3. Prioritized Response Plan
- Immediate actions required
- Medium-term investigation steps  
- Long-term security improvements

### 4. False Positive Assessment
- Which anomalies might be false positives
- Recommendations for tuning detection thresholds

Please structure your response with clear headings and actionable recommendations.
"""
    
    print(f"Comprehensive prompt length: {len(context_prompt)} characters")
    return context_prompt


def example_4_streaming_analysis():
    """Example 4: Process anomalies in chunks for streaming analysis"""
    print("\n=== Example 4: Streaming/Chunked Analysis ===")
    
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    
    # Get all anomalies and process in chunks
    all_anomalies = processor.get_anomalies_for_llm(limit=None, include_context=False)
    chunk_size = 5
    
    chunks = []
    for i in range(0, len(all_anomalies), chunk_size):
        chunk = all_anomalies[i:i + chunk_size]
        
        chunk_prompt = f"""Analyze this batch of {len(chunk)} SQL Server log anomalies (Batch {i//chunk_size + 1}):

{json.dumps(chunk, indent=2)}

Provide:
1. Quick risk assessment for each (Low/Medium/High/Critical)
2. Most suspicious entry in this batch
3. Any patterns you notice across the batch
4. Immediate actions needed

Keep response concise for streaming analysis.
"""
        chunks.append(chunk_prompt)
    
    print(f"Created {len(chunks)} chunks of max {chunk_size} anomalies each")
    print(f"Average chunk size: {len(chunks[0]) if chunks else 0} characters")
    
    return chunks


def example_5_specific_threat_hunting():
    """Example 5: Focused analysis for specific threat types"""
    print("\n=== Example 5: Threat-Specific Analysis ===")
    
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    processor.load_data()
    
    # Filter for specific types of potential threats
    all_anomalies = processor.df[processor.df['is_anomaly']].copy()
    
    # Example: Focus on CHECKDB anomalies (potential privilege escalation)
    checkdb_anomalies = all_anomalies[
        all_anomalies['message'].str.contains('CHECKDB', case=False)
    ]
    
    threat_prompt = f"""THREAT HUNTING: SQL Server CHECKDB Anomalies

## Context
CHECKDB operations appearing as anomalies may indicate:
- Privilege escalation attempts
- Unauthorized database integrity checks
- Malicious admin activity
- Compliance violations

## Anomalous CHECKDB Operations ({len(checkdb_anomalies)} detected)
"""
    
    for idx, row in checkdb_anomalies.head(10).iterrows():
        threat_prompt += f"""
**Anomaly #{idx}**
- Time: {row['timestamp']}
- Severity: {row['severity']} 
- Score: {row['anomaly_score']:.6f}
- Message: {row['message']}
- Database: {row['message'].split("'")[1] if "'" in row['message'] else 'Unknown'}
"""
    
    threat_prompt += """
## Analysis Required
1. **Privilege Escalation Assessment**: Could these indicate unauthorized admin access?
2. **Timing Analysis**: Are these operations happening at unusual times?
3. **Database Targeting**: Are specific databases being targeted?
4. **Severity Correlation**: Why are some CHECKDB operations WARNING vs INFO?
5. **Investigation Priority**: Which ones need immediate attention?

Provide specific hunting queries and indicators to look for.
"""
    
    print(f"Threat hunting prompt length: {len(threat_prompt)} characters")
    print(f"Found {len(checkdb_anomalies)} CHECKDB anomalies to analyze")
    
    return threat_prompt


def main():
    """Demonstrate all examples"""
    print("SQL Server Anomaly Detection - LLM Integration Examples")
    print("=" * 60)
    
    # Run all examples
    examples = [
        example_1_simple_prompt,
        example_2_structured_json, 
        example_3_batch_analysis,
        example_4_streaming_analysis,
        example_5_specific_threat_hunting
    ]
    
    results = {}
    for example_func in examples:
        try:
            result = example_func()
            results[example_func.__name__] = result
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: Ready-to-use prompts generated")
    print("=" * 60)
    
    print("\n1. **Simple Prompt**: Use for quick analysis of top anomalies")
    print("2. **JSON API**: Use with OpenAI/Anthropic APIs for structured analysis") 
    print("3. **Batch Analysis**: Use for comprehensive security reports")
    print("4. **Streaming**: Use for real-time analysis of large datasets")
    print("5. **Threat Hunting**: Use for focused investigation of specific threats")
    
    print(f"\nAll prompts and data are ready to send to your chosen LLM!")
    
    return results


if __name__ == "__main__":
    main()