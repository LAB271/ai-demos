"""
SQL Server Log Anomaly Detection - Phase 1: Baseline Implementation
Using Isolation Forest with TF-IDF features

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime


class LogAnomalyDetector:
    """Simple anomaly detector for SQL Server logs using Isolation Forest"""

    def __init__(self, contamination=0.002):
        """
        Initialize the anomaly detector

        Args:
            contamination (float): Expected proportion of anomalies in dataset
        """
        self.contamination = contamination
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2), min_df=1, stop_words="english")
        self.model = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)

    def parse_log_file(self, filepath):
        """
        Parse SQL Server log file into structured format

        Args:
            filepath (str): Path to log file

        Returns:
            pd.DataFrame: Parsed log entries
        """
        logs = []
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse format: timestamp | severity | message
                parts = line.split("|", 2)
                if len(parts) == 3:
                    timestamp_str = parts[0].strip()
                    severity = parts[1].strip()
                    message = parts[2].strip()

                    # Parse timestamp
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        timestamp = None

                    logs.append({"timestamp": timestamp, "severity": severity, "message": message, "raw": line})

        df = pd.DataFrame(logs)
        return df

    def extract_features(self, df):
        """
        Extract features from log entries

        Args:
            df (pd.DataFrame): Parsed log entries

        Returns:
            np.ndarray: Feature matrix
        """
        # Extract TF-IDF features from messages
        tfidf_features = self.vectorizer.fit_transform(df["message"])

        # Create additional features
        severity_map = {"INFO": 0, "WARNING": 1, "ERROR": 2}
        severity_encoded = df["severity"].map(severity_map).fillna(0).values.reshape(-1, 1)

        # Extract hour of day (suspicious if outside business hours)
        hours = df["timestamp"].apply(lambda x: x.hour if x else 12).values.reshape(-1, 1)

        # Combine features
        from scipy.sparse import hstack, csr_matrix

        additional_features = csr_matrix(np.hstack([severity_encoded, hours]))
        features = hstack([tfidf_features, additional_features])

        return features

    def fit_predict(self, df):
        """
        Train model and predict anomalies

        Args:
            df (pd.DataFrame): Parsed log entries

        Returns:
            np.ndarray: Predictions (-1 for anomaly, 1 for normal)
        """
        # Extract features
        X = self.extract_features(df)

        # Fit and predict
        predictions = self.model.fit_predict(X)

        # Get anomaly scores (lower = more anomalous)
        scores = self.model.decision_function(X)

        return predictions, scores

    def get_top_suspicious_keywords(self, df, predictions, top_n=20):
        """
        Identify keywords most associated with anomalies

        Args:
            df (pd.DataFrame): Log entries
            predictions (np.ndarray): Anomaly predictions
            top_n (int): Number of top keywords to return

        Returns:
            list: Top suspicious keywords
        """
        anomaly_messages = df[predictions == -1]["message"].tolist()

        if not anomaly_messages:
            return []

        # Extract keywords from anomalies
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words="english")
        vectorizer.fit(anomaly_messages)

        return vectorizer.get_feature_names_out().tolist()


def main():
    """Main execution function"""

    print("=" * 80)
    print("SQL Server Log Anomaly Detection - Phase 1 Demo")
    print("=" * 80)
    print()

    # Initialize detector
    print("📊 Initializing Isolation Forest detector...")
    detector = LogAnomalyDetector(contamination=0.002)

    # Load and parse logs
    print("📂 Loading log file...")
    log_file = "sql_server.log"
    df = detector.parse_log_file(log_file)
    print(f"   Loaded {len(df)} log entries")
    print()

    # Show severity distribution
    print("📈 Log Severity Distribution:")
    severity_counts = df["severity"].value_counts()
    for severity, count in severity_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {severity:8s}: {count:4d} ({percentage:5.2f}%)")
    print()

    # Detect anomalies
    print("🔍 Training model and detecting anomalies...")
    predictions, scores = detector.fit_predict(df)

    # Add predictions to dataframe
    df["is_anomaly"] = predictions == -1
    df["anomaly_score"] = scores

    # Count anomalies
    n_anomalies = (predictions == -1).sum()
    print(f"   Detected {n_anomalies} potential anomalies ({(n_anomalies / len(df) * 100):.2f}%)")
    print()

    # Show detected anomalies
    if n_anomalies > 0:
        print("🚨 Detected Anomalies (sorted by score):")
        print("-" * 80)
        anomalies = df[df["is_anomaly"]].sort_values("anomaly_score")

        for idx, row in anomalies.head(20).iterrows():
            print(f"\n[{idx + 1}] Score: {row['anomaly_score']:.4f}")
            print(f"    Time: {row['timestamp']}")
            print(f"    Severity: {row['severity']}")
            print(f"    Message: {row['message'][:120]}...")
        print()

        # Identify suspicious keywords
        print("🔑 Top Suspicious Keywords in Anomalies:")
        keywords = detector.get_top_suspicious_keywords(df, predictions, top_n=15)
        for i, keyword in enumerate(keywords, 1):
            print(f"   {i:2d}. {keyword}")
        print()
    else:
        print("✅ No significant anomalies detected in this dataset")
        print()

    # Show normal samples for comparison
    print("✅ Sample Normal Log Entries (for comparison):")
    print("-" * 80)
    normal_logs = df[~df["is_anomaly"]].sample(min(5, len(df[~df["is_anomaly"]])))
    for idx, row in normal_logs.iterrows():
        print(f"\n[{idx + 1}] Score: {row['anomaly_score']:.4f}")
        print(f"    Severity: {row['severity']}")
        print(f"    Message: {row['message'][:120]}...")
    print()

    # Summary statistics
    print("📊 Anomaly Score Statistics:")
    print(f"   Mean: {scores.mean():.4f}")
    print(f"   Std:  {scores.std():.4f}")
    print(f"   Min:  {scores.min():.4f} (most anomalous)")
    print(f"   Max:  {scores.max():.4f} (most normal)")
    print()

    # Save results
    output_file = "anomaly_results.csv"
    df.to_csv(output_file, index=False)
    print(f"💾 Results saved to: {output_file}")
    print()

    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
