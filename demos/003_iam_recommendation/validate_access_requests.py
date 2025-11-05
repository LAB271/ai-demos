#!/usr/bin/env python3
"""
IAM Access Request Validation Script

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
from typing import Tuple

# Define toxic/no-go combinations: Role -> Systems that should NEVER be accessed
TOXIC_COMBINATIONS = {
    "Trader": {
        "Cloud Infrastructure",  # Traders should not manage infrastructure
        "IAM System",  # Traders should not manage identity/access
        "Compliance Monitoring",  # Traders should not access compliance tools
    },
    "Portfolio Manager": {
        "Cloud Infrastructure",  # PMs should not manage infrastructure
        "IAM System",  # PMs should not manage identity/access
        "Fund Accounting System",  # PMs should not access accounting systems
    },
    "Risk Manager": {
        "OMS",  # Risk should not trade (conflict of interest)
        "PMS",  # Risk should not manage portfolios
        "IAM System",  # Risk should not manage identity/access
        "Cloud Infrastructure",  # Risk should not manage infrastructure
    },
    "Compliance Officer": {
        "OMS",  # Compliance should not trade (conflict of interest)
        "PMS",  # Compliance should not manage portfolios
        "IAM System",  # Compliance should not manage identity/access
        "Cloud Infrastructure",  # Compliance should not manage infrastructure
        "Fund Accounting System",  # Compliance should not modify accounting
    },
    "Fund Accountant": {
        "OMS",  # Accountants should not trade
        "PMS",  # Accountants should not manage portfolios
        "IAM System",  # Accountants should not manage identity/access
        "Cloud Infrastructure",  # Accountants should not manage infrastructure
        "Monitoring",  # Accountants should not access monitoring
    },
    "Cloud Engineer": {
        "OMS",  # Engineers should not trade
        "PMS",  # Engineers should not manage portfolios
        "Fund Accounting System",  # Engineers should not access accounting
        "Compliance Monitoring",  # Engineers should not access compliance data
    },
    "IAM Admin": {
        "OMS",  # IAM admins should not trade
        "PMS",  # IAM admins should not manage portfolios
        "Fund Accounting System",  # IAM admins should not access accounting
        "Compliance Monitoring",  # IAM admins should not access compliance data
        "Risk Platform",  # IAM admins should not access risk data
    },
}

# Define high-risk combinations: Suspicious but not always violations
HIGH_RISK_COMBINATIONS = {
    "Trader": {
        "Risk Platform",  # Traders accessing risk data is suspicious
        "Fund Accounting System",  # Traders accessing accounting is unusual
    },
    "Portfolio Manager": {
        "Risk Platform",  # PMs should coordinate with risk, not access directly
        "Compliance Monitoring",  # PMs accessing compliance tools is unusual
    },
    "Risk Manager": {
        "Fund Accounting System"  # Risk accessing accounting needs justification
    },
    "Cloud Engineer": {
        "Risk Platform"  # Engineers accessing risk data needs review
    },
    "IAM Admin": {
        "Monitoring"  # IAM accessing monitoring is borderline
    },
}


def load_access_requests(filepath: str = "access_requests.csv") -> pd.DataFrame:
    """Load access requests from CSV file."""
    return pd.read_csv(filepath)


def validate_request(role: str, system: str) -> Tuple[str, str]:
    """
    Validate a single access request.

    Returns:
        Tuple of (status, reason)
        status: 'APPROVED', 'HIGH_RISK', or 'REJECTED'
    """
    # Check for toxic combinations
    if role in TOXIC_COMBINATIONS and system in TOXIC_COMBINATIONS[role]:
        return "REJECTED", f"Toxic combination: {role} should never access {system}"

    # Check for high-risk combinations
    if role in HIGH_RISK_COMBINATIONS and system in HIGH_RISK_COMBINATIONS[role]:
        return "HIGH_RISK", f"Suspicious combination: {role} accessing {system} requires review"

    # Default approval
    return "APPROVED", "Access request follows standard role permissions"


def validate_all_requests(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate all access requests and add validation columns.

    Args:
        df: DataFrame with access requests

    Returns:
        DataFrame with added validation columns
    """
    # Apply validation to each request
    validation_results = df.apply(lambda row: validate_request(row["Role"], row["SystemAccessRequested"]), axis=1)

    # Split the tuple results into separate columns
    df["ValidationStatus"] = validation_results.apply(lambda x: x[0])
    df["ValidationReason"] = validation_results.apply(lambda x: x[1])

    return df


def generate_validation_report(df: pd.DataFrame):
    """Generate and print validation report."""
    print("=" * 80)
    print("ACCESS REQUEST VALIDATION REPORT")
    print("=" * 80)

    # Overall statistics
    total_requests = len(df)
    rejected = len(df[df["ValidationStatus"] == "REJECTED"])
    high_risk = len(df[df["ValidationStatus"] == "HIGH_RISK"])
    approved = len(df[df["ValidationStatus"] == "APPROVED"])

    print("\nOverall Statistics:")
    print(f"  Total Requests:     {total_requests}")
    print(f"  ✓ Approved:         {approved} ({approved / total_requests * 100:.1f}%)")
    print(f"  ⚠ High Risk:        {high_risk} ({high_risk / total_requests * 100:.1f}%)")
    print(f"  ✗ Rejected:         {rejected} ({rejected / total_requests * 100:.1f}%)")

    # Rejected requests
    if rejected > 0:
        print("\n" + "=" * 80)
        print("REJECTED REQUESTS (Toxic Combinations)")
        print("=" * 80)
        rejected_df = df[df["ValidationStatus"] == "REJECTED"]

        print(f"\nTotal Violations: {len(rejected_df)}")
        print("\nViolations by Role:")
        print(rejected_df["Role"].value_counts().to_string())

        print("\nViolations by System:")
        print(rejected_df["SystemAccessRequested"].value_counts().to_string())

        print("\nSample Rejected Requests:")
        sample_size = min(10, len(rejected_df))
        print(
            rejected_df[
                ["RequestID", "EmployeeID", "EmployeeName", "Role", "SystemAccessRequested", "ValidationReason"]
            ]
            .head(sample_size)
            .to_string(index=False)
        )

    # High-risk requests
    if high_risk > 0:
        print("\n" + "=" * 80)
        print("HIGH-RISK REQUESTS (Require Review)")
        print("=" * 80)
        high_risk_df = df[df["ValidationStatus"] == "HIGH_RISK"]

        print(f"\nTotal High-Risk: {len(high_risk_df)}")
        print("\nHigh-Risk by Role:")
        print(high_risk_df["Role"].value_counts().to_string())

        print("\nHigh-Risk by System:")
        print(high_risk_df["SystemAccessRequested"].value_counts().to_string())

        print("\nSample High-Risk Requests:")
        sample_size = min(10, len(high_risk_df))
        print(
            high_risk_df[
                ["RequestID", "EmployeeID", "EmployeeName", "Role", "SystemAccessRequested", "ValidationReason"]
            ]
            .head(sample_size)
            .to_string(index=False)
        )

    # Toxic combinations found
    print("\n" + "=" * 80)
    print("TOXIC COMBINATION MATRIX")
    print("=" * 80)
    print("\nDefined toxic combinations (Role -> Forbidden Systems):")
    for role, systems in TOXIC_COMBINATIONS.items():
        print(f"\n{role}:")
        for system in sorted(systems):
            count = len(df[(df["Role"] == role) & (df["SystemAccessRequested"] == system)])
            if count > 0:
                print(f"  ✗ {system}: {count} violation(s)")
            else:
                print(f"  - {system}: no violations")

    # Location analysis for rejected requests
    if rejected > 0:
        print("\n" + "=" * 80)
        print("REJECTED REQUESTS BY LOCATION")
        print("=" * 80)
        location_violations = (
            rejected_df.groupby(["Location", "Role", "SystemAccessRequested"]).size().reset_index(name="Count")
        )
        print(location_violations.to_string(index=False))


def main():
    """Main execution function."""
    print("Loading access requests...")
    df = load_access_requests()

    print(f"Loaded {len(df)} access requests")
    print(f"Validating against {len(TOXIC_COMBINATIONS)} role definitions...")

    # Validate all requests
    validated_df = validate_all_requests(df)

    # Generate report
    generate_validation_report(validated_df)

    # Save validated results
    output_file = "access_requests_validated.csv"
    validated_df.to_csv(output_file, index=False)

    print("\n" + "=" * 80)
    print(f"✓ Validation complete! Results saved to: {output_file}")
    print("=" * 80)

    # Print summary recommendation
    rejected_count = len(validated_df[validated_df["ValidationStatus"] == "REJECTED"])
    high_risk_count = len(validated_df[validated_df["ValidationStatus"] == "HIGH_RISK"])

    print("\nRECOMMENDATIONS:")
    if rejected_count > 0:
        print(f"  ✗ REJECT {rejected_count} requests due to toxic combinations")
    if high_risk_count > 0:
        print(f"  ⚠ REVIEW {high_risk_count} high-risk requests with additional scrutiny")

    approval_rate = len(validated_df[validated_df["ValidationStatus"] == "APPROVED"]) / len(validated_df) * 100
    print(f"  ✓ AUTO-APPROVE {approval_rate:.1f}% of requests following standard permissions")


if __name__ == "__main__":
    main()
