#!/usr/bin/env python3
"""
Azure LLM-Friendly Cost Summary Generator

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import json
from datetime import datetime


def generate_llm_summary(csv_file="./azure_compute_usage_6months.csv", output_file="azure_cost_summary.json"):
    """
    Generate a compact, LLM-friendly summary of Azure cost data.

    This summary is designed to be fed to an LLM (like GPT-4, Claude, etc.) for:
    - Cost analysis and optimization recommendations
    - Answering questions about spending patterns
    - Identifying anomalies and trends
    - Providing insights without needing the full dataset
    """

    print("Loading Azure cost data...")
    df = pd.read_csv(csv_file)

    # Basic Overview
    overview = {
        "total_records": len(df),
        "date_range": {"start": df["date"].min(), "end": df["date"].max(), "days": df["date"].nunique()},
        "total_cost_usd": round(df["cost_usd"].sum(), 2),
        "daily_average_cost": round(df.groupby("date")["cost_usd"].sum().mean(), 2),
        "unique_resources": df["resource_id"].nunique(),
    }

    # Resource Type Breakdown
    resource_types = []
    for resource_type in df["resource_type"].unique():
        subset = df[df["resource_type"] == resource_type]
        resource_types.append(
            {
                "type": resource_type,
                "count": len(subset),
                "unique_resources": subset["resource_id"].nunique(),
                "total_cost": round(subset["cost_usd"].sum(), 2),
                "percentage_of_total": round(subset["cost_usd"].sum() / df["cost_usd"].sum() * 100, 2),
            }
        )
    resource_types.sort(key=lambda x: x["total_cost"], reverse=True)

    # Geographic Distribution
    regions = []
    for region in df["region"].unique():
        subset = df[df["region"] == region]
        regions.append(
            {
                "region": region,
                "total_cost": round(subset["cost_usd"].sum(), 2),
                "unique_resources": subset["resource_id"].nunique(),
                "percentage_of_total": round(subset["cost_usd"].sum() / df["cost_usd"].sum() * 100, 2),
            }
        )
    regions.sort(key=lambda x: x["total_cost"], reverse=True)

    # Department Breakdown
    departments = []
    for dept in df["department"].dropna().unique():
        subset = df[df["department"] == dept]
        departments.append(
            {
                "department": dept,
                "total_cost": round(subset["cost_usd"].sum(), 2),
                "unique_resources": subset["resource_id"].nunique(),
                "percentage_of_total": round(subset["cost_usd"].sum() / df["cost_usd"].sum() * 100, 2),
            }
        )

    # Untagged resources
    untagged = df[df["department"].isna()]
    if len(untagged) > 0:
        departments.append(
            {
                "department": "Untagged",
                "total_cost": round(untagged["cost_usd"].sum(), 2),
                "unique_resources": untagged["resource_id"].nunique(),
                "percentage_of_total": round(untagged["cost_usd"].sum() / df["cost_usd"].sum() * 100, 2),
                "note": "Resources without department tags - cost allocation issue",
            }
        )

    departments.sort(key=lambda x: x["total_cost"], reverse=True)

    # Environment Breakdown
    environments = []
    for env in df["environment"].dropna().unique():
        subset = df[df["environment"] == env]
        environments.append(
            {
                "environment": env,
                "total_cost": round(subset["cost_usd"].sum(), 2),
                "unique_resources": subset["resource_id"].nunique(),
                "percentage_of_total": round(subset["cost_usd"].sum() / df["cost_usd"].sum() * 100, 2),
            }
        )
    environments.sort(key=lambda x: x["total_cost"], reverse=True)

    # Monthly Trends
    monthly = []
    for month in sorted(df["billing_period"].unique()):
        subset = df[df["billing_period"] == month]
        monthly.append(
            {
                "month": month,
                "total_cost": round(subset["cost_usd"].sum(), 2),
                "daily_average": round(subset.groupby("date")["cost_usd"].sum().mean(), 2),
                "unique_resources": subset["resource_id"].nunique(),
            }
        )

    # VM SKU Distribution (if VMs exist)
    vm_skus = []
    vm_data = df[df["resource_type"] == "Microsoft.Compute/virtualMachines"]
    if len(vm_data) > 0:
        for sku in vm_data["sku"].unique():
            subset = vm_data[vm_data["sku"] == sku]
            vm_skus.append(
                {
                    "sku": sku,
                    "count": subset["resource_name"].nunique(),
                    "total_cost": round(subset["cost_usd"].sum(), 2),
                    "avg_utilization": round(subset["cpu_utilization"].mean(), 2),
                }
            )
        vm_skus.sort(key=lambda x: x["total_cost"], reverse=True)

    # Optimization Opportunities
    optimization = {"underutilized_vms": {}, "stopped_vms": {}, "untagged_resources": {}, "dev_test_ri_opportunity": {}}

    # Underutilized VMs
    vm_records = df[df["resource_type"] == "Microsoft.Compute/virtualMachines"]
    underutilized = vm_records[vm_records["cpu_utilization"] < 15]
    if len(underutilized) > 0:
        optimization["underutilized_vms"] = {
            "unique_resources": underutilized["resource_name"].nunique(),
            "total_cost": round(underutilized["cost_usd"].sum(), 2),
            "potential_savings": round(
                underutilized["cost_usd"].sum() * 0.5, 2
            ),  # Assume 50% savings from right-sizing
            "description": "VMs with <15% CPU utilization - candidates for right-sizing or shutdown",
            "recommendation": "Downsize to smaller SKUs or implement auto-scaling",
        }

    # Stopped VMs
    stopped_vms = vm_records[vm_records["uptime_hours"] == 0]
    if len(stopped_vms) > 0:
        optimization["stopped_vms"] = {
            "unique_resources": stopped_vms["resource_name"].nunique(),
            "wasted_cost": round(stopped_vms["cost_usd"].sum(), 2),
            "description": "VMs stopped but not deallocated - still incurring storage charges",
            "recommendation": "Deallocate VMs or implement auto-shutdown policies",
        }

    # Untagged resources
    if len(untagged) > 0:
        optimization["untagged_resources"] = {
            "unique_resources": untagged["resource_name"].nunique(),
            "unallocated_cost": round(untagged["cost_usd"].sum(), 2),
            "description": "Resources without department tags - cost allocation problem",
            "recommendation": "Implement tagging policy and Azure Policy for enforcement",
        }

    # Dev/Test RI opportunity
    dev_test = df[df["environment"].isin(["dev", "test"])]
    if len(dev_test) > 0:
        optimization["dev_test_ri_opportunity"] = {
            "unique_resources": dev_test["resource_name"].nunique(),
            "current_cost": round(dev_test["cost_usd"].sum(), 2),
            "potential_savings": round(dev_test["cost_usd"].sum() * 0.40, 2),  # 40% savings with 3-year RI
            "description": "Dev/Test workloads that could benefit from Reserved Instances",
            "recommendation": "Purchase 1-year or 3-year Reserved Instances for consistent workloads",
        }

    # Top 20 Most Expensive Resources
    top_resources = (
        df.groupby(["resource_name", "resource_type", "sku"])
        .agg({"cost_usd": "sum", "cpu_utilization": "mean", "uptime_hours": "mean"})
        .sort_values("cost_usd", ascending=False)
        .head(20)
    )

    expensive_resources = []
    for (resource_name, resource_type, sku), row in top_resources.iterrows():
        expensive_resources.append(
            {
                "resource_name": resource_name,
                "resource_type": resource_type.split("/")[-1] if "/" in resource_type else resource_type,
                "sku": sku,
                "total_cost": round(row["cost_usd"], 2),
                "avg_cpu_utilization": round(row["cpu_utilization"], 2) if pd.notna(row["cpu_utilization"]) else None,
                "avg_uptime_hours": round(row["uptime_hours"], 2) if pd.notna(row["uptime_hours"]) else None,
            }
        )

    # Sample Records (for context)
    sample_records = df.sample(min(10, len(df))).to_dict("records")
    for record in sample_records:
        # Simplify for readability
        record["cost_usd"] = round(record["cost_usd"], 4)
        if pd.notna(record.get("cpu_utilization")):
            record["cpu_utilization"] = round(record["cpu_utilization"], 2)
        if pd.notna(record.get("memory_usage_gb")):
            record["memory_usage_gb"] = round(record["memory_usage_gb"], 2)
        if pd.notna(record.get("uptime_hours")):
            record["uptime_hours"] = round(record["uptime_hours"], 2)

    # Cost Anomalies (days with unusually high/low costs)
    daily_costs = df.groupby("date")["cost_usd"].sum()
    mean_cost = daily_costs.mean()
    std_cost = daily_costs.std()

    anomalies = {"high_cost_days": [], "low_cost_days": []}

    for date, cost in daily_costs.items():
        if cost > mean_cost + 2 * std_cost:
            anomalies["high_cost_days"].append(
                {
                    "date": date,
                    "cost": round(cost, 2),
                    "deviation_from_average": round(((cost - mean_cost) / mean_cost) * 100, 2),
                }
            )
        elif cost < mean_cost - 2 * std_cost:
            anomalies["low_cost_days"].append(
                {
                    "date": date,
                    "cost": round(cost, 2),
                    "deviation_from_average": round(((cost - mean_cost) / mean_cost) * 100, 2),
                }
            )

    # Compile the complete summary
    summary = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_file": csv_file,
            "description": "Azure cost data summary for LLM analysis",
            "purpose": "This summary provides aggregated Azure cost insights for analysis without requiring the full dataset",
        },
        "overview": overview,
        "breakdown": {
            "by_resource_type": resource_types,
            "by_region": regions,
            "by_department": departments,
            "by_environment": environments,
            "by_vm_sku": vm_skus,
        },
        "time_series": {
            "monthly_trends": monthly,
            "cost_statistics": {
                "mean_daily_cost": round(daily_costs.mean(), 2),
                "median_daily_cost": round(daily_costs.median(), 2),
                "std_deviation": round(daily_costs.std(), 2),
                "min_daily_cost": round(daily_costs.min(), 2),
                "max_daily_cost": round(daily_costs.max(), 2),
            },
        },
        "optimization_opportunities": optimization,
        "top_expensive_resources": expensive_resources,
        "cost_anomalies": anomalies,
        "sample_records": sample_records,
    }

    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Summary generated: {output_file}")
    print(f"  File size: {len(json.dumps(summary)) / 1024:.1f} KB")
    print("  Ready to feed to LLM for analysis!")

    return summary


def print_llm_usage_guide():
    """Print guidance on how to use the summary with an LLM."""

    guide = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    HOW TO USE WITH AN LLM                                ║
╚══════════════════════════════════════════════════════════════════════════╝

1. LOAD THE SUMMARY
   Copy the contents of 'azure_cost_summary.json' and paste it into your
   LLM conversation with a prompt like:

   "I have Azure cost data summarized in JSON format. Please analyze it and
    provide insights on spending patterns, optimization opportunities, and
    recommendations."

2. EXAMPLE QUESTIONS TO ASK THE LLM

   Cost Analysis:
   • "Which department has the highest cloud spending?"
   • "What are the main cost drivers in our Azure environment?"
   • "How does spending compare across different regions?"
   • "What is the trend of our monthly costs?"

   Optimization:
   • "What are the top 5 cost optimization opportunities?"
   • "How much can we save by addressing underutilized VMs?"
   • "Should we purchase Reserved Instances? What's the ROI?"
   • "Which resources should we prioritize for cost reduction?"

   Specific Queries:
   • "Find all untagged resources and estimate the cost allocation issue"
   • "What percentage of our costs are from production vs dev/test?"
   • "Identify the most expensive resources and their utilization"
   • "Are there any cost anomalies or unusual spending patterns?"

3. ADVANCED ANALYSIS PROMPTS

   • "Create a cost optimization roadmap prioritized by potential savings"
   • "Generate a monthly executive summary of cloud spending"
   • "Compare costs across departments and suggest fair chargeback model"
   • "Identify resources that violate our cost efficiency policies"
   • "Forecast next month's spending based on current trends"

4. USING WITH COPILOT/CHATGPT/CLAUDE

   For Copilot:
   @workspace "Analyze the azure_cost_summary.json file and provide 
   cost optimization recommendations"

   For ChatGPT/Claude:
   Simply paste the JSON content with your question

5. TIPS FOR BETTER RESULTS

   • Be specific with your questions
   • Ask for actionable recommendations
   • Request calculations and comparisons
   • Ask for prioritization based on business impact
   • Request follow-up analysis on specific findings

═══════════════════════════════════════════════════════════════════════════
"""
    print(guide)


if __name__ == "__main__":
    import sys

    # Get CSV file path from command line or use default
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "./azure_compute_usage_6months.csv"

    # Generate summary
    summary = generate_llm_summary(csv_file)

    # Print usage guide
    print_llm_usage_guide()
