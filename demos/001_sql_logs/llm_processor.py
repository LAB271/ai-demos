#!/usr/bin/env python3
"""
LLM Processor for SQL Server Log Anomaly Detection Results

This script demonstrates how to process anomaly detection results from anomaly_results.csv
and prepare them for feeding into an LLM for explanation and analysis.

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any


class AnomalyLLMProcessor:
    """Process anomaly detection results for LLM consumption"""
    
    def __init__(self, results_file: str = "anomaly_results.csv"):
        """
        Initialize the processor with results file
        
        Args:
            results_file (str): Path to the anomaly results CSV file
        """
        self.results_file = results_file
        self.df = None
        
    def load_data(self):
        """Load the anomaly detection results"""
        self.df = pd.read_csv(self.results_file)
        print(f"Loaded {len(self.df)} log entries")
        print(f"Found {len(self.df[self.df['is_anomaly']])} anomalies")
        
    def get_anomalies_summary(self) -> Dict[str, Any]:
        """Get a summary of detected anomalies"""
        if self.df is None:
            self.load_data()
            
        anomalies = self.df[self.df['is_anomaly']]
        
        summary = {
            "total_logs": len(self.df),
            "total_anomalies": len(anomalies),
            "anomaly_rate": len(anomalies) / len(self.df) * 100,
            "time_range": {
                "start": self.df['timestamp'].min(),
                "end": self.df['timestamp'].max()
            },
            "severity_distribution": self.df['severity'].value_counts().to_dict(),
            "anomaly_severity_distribution": anomalies['severity'].value_counts().to_dict(),
            "top_anomaly_scores": anomalies.nlargest(5, 'anomaly_score')[['timestamp', 'severity', 'message', 'anomaly_score']].to_dict('records')
        }
        
        return summary
    
    def get_anomalies_for_llm(self, limit: int = None, include_context: bool = True) -> List[Dict[str, Any]]:
        """
        Extract anomalies in a format suitable for LLM analysis
        
        Args:
            limit (int): Maximum number of anomalies to return
            include_context (bool): Whether to include surrounding normal logs for context
            
        Returns:
            List[Dict]: Formatted anomaly data for LLM
        """
        if self.df is None:
            self.load_data()
            
        anomalies = self.df[self.df['is_anomaly']].copy()
        
        if limit:
            anomalies = anomalies.head(limit)
            
        llm_data = []
        
        for idx, anomaly in anomalies.iterrows():
            anomaly_entry = {
                "id": idx,
                "timestamp": anomaly['timestamp'],
                "severity": anomaly['severity'],
                "message": anomaly['message'],
                "raw_log": anomaly['raw'],
                "anomaly_score": float(anomaly['anomaly_score']),
                "analysis_request": "Please analyze why this log entry was flagged as anomalous."
            }
            
            # Add context if requested
            if include_context:
                # Get 2 entries before and after for context
                context_start = max(0, idx - 2)
                context_end = min(len(self.df), idx + 3)
                context_entries = self.df.iloc[context_start:context_end]
                
                anomaly_entry["context"] = {
                    "surrounding_logs": [
                        {
                            "timestamp": row['timestamp'],
                            "severity": row['severity'],
                            "message": row['message'],
                            "is_anomaly": row['is_anomaly'],
                            "is_target": i == (idx - context_start)  # Mark the anomaly entry
                        }
                        for i, (_, row) in enumerate(context_entries.iterrows())
                    ]
                }
            
            llm_data.append(anomaly_entry)
            
        return llm_data
    
    def create_llm_prompt(self, anomaly_data: List[Dict[str, Any]]) -> str:
        """
        Create a structured prompt for LLM analysis
        
        Args:
            anomaly_data: List of anomaly entries from get_anomalies_for_llm()
            
        Returns:
            str: Formatted prompt for LLM
        """
        summary = self.get_anomalies_summary()
        
        prompt = f"""# SQL Server Log Anomaly Analysis Request

## Dataset Summary
- Total log entries: {summary['total_logs']:,}
- Anomalies detected: {summary['total_anomalies']}
- Anomaly rate: {summary['anomaly_rate']:.3f}%
- Time range: {summary['time_range']['start']} to {summary['time_range']['end']}

## Severity Distribution
- All logs: {summary['severity_distribution']}
- Anomalies only: {summary['anomaly_severity_distribution']}

## Analysis Task
Please analyze the following anomalous log entries and provide explanations for why each was flagged as suspicious. Consider:

1. **Pattern Analysis**: What makes each entry unusual compared to normal logs?
2. **Security Implications**: What potential security risks do these anomalies represent?
3. **False Positive Assessment**: Are any of these likely false positives?
4. **Recommendations**: What actions should be taken for each anomaly?

## Anomalous Log Entries

"""
        
        for i, anomaly in enumerate(anomaly_data, 1):
            prompt += f"### Anomaly #{i}\n"
            prompt += f"- **Timestamp**: {anomaly['timestamp']}\n"
            prompt += f"- **Severity**: {anomaly['severity']}\n"
            prompt += f"- **Anomaly Score**: {anomaly['anomaly_score']:.6f}\n"
            prompt += f"- **Message**: {anomaly['message']}\n"
            prompt += f"- **Raw Log**: `{anomaly['raw_log']}`\n"
            
            if 'context' in anomaly:
                prompt += "\n**Context (surrounding logs):**\n"
                for j, ctx in enumerate(anomaly['context']['surrounding_logs']):
                    marker = "→ **[ANOMALY]**" if ctx['is_target'] else "  "
                    prompt += f"{marker} {ctx['timestamp']} | {ctx['severity']} | {ctx['message']}\n"
            
            prompt += "\n---\n\n"
        
        prompt += """## Expected Response Format

For each anomaly, please provide:

1. **Anomaly Type**: Classification of the anomaly (e.g., authentication, privilege escalation, etc.)
2. **Technical Analysis**: Why the ML model flagged this as anomalous
3. **Risk Assessment**: Security risk level (Low/Medium/High/Critical)
4. **Explanation**: Detailed explanation of the potential issue
5. **Recommended Actions**: Specific steps to investigate or remediate
6. **False Positive Likelihood**: Assessment of whether this is likely a false positive

Please be thorough but concise in your analysis."""

        return prompt
    
    def export_for_llm(self, output_file: str = "llm_analysis_data.json", limit: int = 20):
        """
        Export anomaly data in JSON format for LLM consumption
        
        Args:
            output_file (str): Output JSON file name
            limit (int): Maximum number of anomalies to export
        """
        anomaly_data = self.get_anomalies_for_llm(limit=limit, include_context=True)
        summary = self.get_anomalies_summary()
        
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_file": self.results_file,
                "total_anomalies": len(anomaly_data),
                "summary": summary
            },
            "anomalies": anomaly_data,
            "llm_prompt": self.create_llm_prompt(anomaly_data)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"Exported {len(anomaly_data)} anomalies to {output_file}")
        return output_file
    
    def get_high_confidence_anomalies(self, score_threshold: float = -0.01) -> pd.DataFrame:
        """
        Get anomalies with high confidence scores (more negative = more anomalous)
        
        Args:
            score_threshold (float): Threshold for anomaly score (more negative = more anomalous)
            
        Returns:
            pd.DataFrame: High confidence anomalies
        """
        if self.df is None:
            self.load_data()
            
        high_confidence = self.df[
            (self.df['is_anomaly']) & 
            (self.df['anomaly_score'] <= score_threshold)
        ].copy()
        
        return high_confidence.sort_values('anomaly_score')
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the anomalies for LLM context"""
        if self.df is None:
            self.load_data()
            
        anomalies = self.df[self.df['is_anomaly']]
        
        # Extract patterns from messages
        message_patterns = {}
        for message in anomalies['message'].values:
            # Simple pattern extraction - look for key terms
            if 'CHECKDB' in message:
                message_patterns['checkdb_operations'] = message_patterns.get('checkdb_operations', 0) + 1
            elif 'Login' in message:
                message_patterns['login_operations'] = message_patterns.get('login_operations', 0) + 1
            elif 'Database' in message and 'started' in message:
                message_patterns['database_starts'] = message_patterns.get('database_starts', 0) + 1
            elif 'Transaction' in message:
                message_patterns['transactions'] = message_patterns.get('transactions', 0) + 1
            elif 'Backup' in message:
                message_patterns['backups'] = message_patterns.get('backups', 0) + 1
                
        # Time-based analysis
        anomalies['hour'] = pd.to_datetime(anomalies['timestamp']).dt.hour
        hour_distribution = anomalies['hour'].value_counts().sort_index().to_dict()
        
        return {
            "message_patterns": message_patterns,
            "hour_distribution": hour_distribution,
            "severity_patterns": anomalies['severity'].value_counts().to_dict()
        }


def main():
    """Example usage of the LLM processor"""
    print("SQL Server Log Anomaly Detection - LLM Processor")
    print("=" * 50)
    
    # Initialize processor
    processor = AnomalyLLMProcessor("anomaly_results.csv")
    processor.load_data()
    
    # Get summary
    print("\n1. Getting anomaly summary...")
    summary = processor.get_anomalies_summary()
    print(f"Found {summary['total_anomalies']} anomalies out of {summary['total_logs']} total logs")
    print(f"Anomaly rate: {summary['anomaly_rate']:.3f}%")
    
    # Analyze patterns
    print("\n2. Analyzing anomaly patterns...")
    patterns = processor.analyze_patterns()
    print("Message patterns found:")
    for pattern, count in patterns['message_patterns'].items():
        print(f"  - {pattern}: {count}")
    
    # Get high confidence anomalies
    print("\n3. High confidence anomalies:")
    high_conf = processor.get_high_confidence_anomalies()
    print(f"Found {len(high_conf)} high-confidence anomalies")
    if len(high_conf) > 0:
        print("\nTop 3 highest confidence:")
        for idx, row in high_conf.head(3).iterrows():
            print(f"  Score: {row['anomaly_score']:.6f} - {row['message']}")
    
    # Export for LLM analysis
    print("\n4. Exporting data for LLM analysis...")
    processor.export_for_llm(limit=10)
    
    # Create a focused prompt for the most suspicious anomalies
    print("\n5. Creating focused LLM prompt...")
    top_anomalies = processor.get_anomalies_for_llm(limit=5, include_context=True)
    prompt = processor.create_llm_prompt(top_anomalies)
    
    # Save the prompt to a file
    with open("llm_prompt.txt", "w", encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"Created LLM prompt in 'llm_prompt.txt' ({len(prompt)} characters)")
    print("\nReady for LLM analysis!")
    
    # Show a preview of what to send to the LLM
    print("\n" + "="*50)
    print("PREVIEW - First anomaly for LLM analysis:")
    print("="*50)
    if top_anomalies:
        anomaly = top_anomalies[0]
        print(f"Timestamp: {anomaly['timestamp']}")
        print(f"Severity: {anomaly['severity']}")
        print(f"Message: {anomaly['message']}")
        print(f"Anomaly Score: {anomaly['anomaly_score']:.6f}")
        print("\nThis data is now ready to be sent to an LLM for detailed analysis.")


if __name__ == "__main__":
    main()