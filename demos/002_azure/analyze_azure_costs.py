#!/usr/bin/env python3
"""
Azure Cost Analysis - Comprehensive Statistics and Optimization Opportunities

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd


def analyze_azure_costs(csv_file="azure_compute_usage_6months.csv"):
    """Analyze Azure cost data and provide comprehensive statistics."""

    print("Loading Azure cost data...")
    df = pd.read_csv(csv_file)

    # Basic Statistics
    print("\n" + "=" * 70)
    print("DATASET OVERVIEW")
    print("=" * 70)
    print(f"Total Records: {len(df):,} ({len(df) // 30:,} months of data)")
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total Cost: ${df['cost_usd'].sum():,.2f}")
    print(f"Average Daily Cost: ${df.groupby('date')['cost_usd'].sum().mean():,.2f}")

    # Resource Distribution
    print("\n" + "=" * 70)
    print("RESOURCE DISTRIBUTION")
    print("=" * 70)
    resource_counts = df["resource_type"].value_counts()
    for resource_type, count in resource_counts.items():
        resource_name = resource_type.split("/")[-1] if "/" in resource_type else resource_type
        cost = df[df["resource_type"] == resource_type]["cost_usd"].sum()
        print(f"{resource_name:30s}: {count:8,} records  |  ${cost:12,.2f} total cost")

    # Geographic Distribution
    print("\n" + "=" * 70)
    print("GEOGRAPHIC DISTRIBUTION")
    print("=" * 70)
    region_stats = (
        df.groupby("region").agg({"cost_usd": "sum", "resource_id": "count"}).sort_values("cost_usd", ascending=False)
    )

    for region, row in region_stats.iterrows():
        print(f"{region:20s}: {int(row['resource_id']):8,} records  |  ${row['cost_usd']:12,.2f} total cost")

    # Department Distribution
    print("\n" + "=" * 70)
    print("DEPARTMENT DISTRIBUTION")
    print("=" * 70)
    dept_stats = (
        df.groupby("department")
        .agg({"cost_usd": "sum", "resource_id": "count"})
        .sort_values("cost_usd", ascending=False)
    )

    for dept, row in dept_stats.iterrows():
        if pd.notna(dept):
            print(f"{dept:20s}: {int(row['resource_id']):8,} records  |  ${row['cost_usd']:12,.2f} total cost")

    untagged = df[df["department"].isna()]
    if len(untagged) > 0:
        print(f"{'Untagged':20s}: {len(untagged):8,} records  |  ${untagged['cost_usd'].sum():12,.2f} total cost")

    # Environment Distribution
    print("\n" + "=" * 70)
    print("ENVIRONMENT DISTRIBUTION")
    print("=" * 70)
    env_stats = (
        df.groupby("environment")
        .agg({"cost_usd": "sum", "resource_id": "count"})
        .sort_values("cost_usd", ascending=False)
    )

    for env, row in env_stats.iterrows():
        if pd.notna(env):
            print(f"{env:20s}: {int(row['resource_id']):8,} records  |  ${row['cost_usd']:12,.2f} total cost")

    # Unique Item Statistics
    print("\n" + "=" * 70)
    print("UNIQUE ITEM STATISTICS")
    print("=" * 70)

    unique_stats = {
        "Unique Resources": df["resource_id"].nunique(),
        "Unique Resource Names": df["resource_name"].nunique(),
        "Unique Subscriptions": df["subscription_id"].nunique(),
        "Unique Resource Groups": df["resource_group"].nunique(),
        "Unique Regions": df["region"].nunique(),
        "Unique Departments": df["department"].nunique(),
        "Unique Environments": df["environment"].nunique(),
        "Unique Resource Types": df["resource_type"].nunique(),
        "Unique Service Names": df["service_name"].nunique(),
        "Unique SKUs": df["sku"].nunique(),
        "Unique Billing Periods": df["billing_period"].nunique(),
    }

    for stat_name, count in unique_stats.items():
        print(f"{stat_name:30s}: {count:6,}")

    # SKU Distribution (for VMs)
    print("\n" + "=" * 70)
    print("VM SKU DISTRIBUTION")
    print("=" * 70)
    vm_data = df[df["resource_type"] == "Microsoft.Compute/virtualMachines"]
    if len(vm_data) > 0:
        sku_stats = (
            vm_data.groupby("sku")
            .agg({"resource_name": "nunique", "cost_usd": "sum"})
            .sort_values("cost_usd", ascending=False)
        )

        for sku, row in sku_stats.iterrows():
            print(f"{sku:20s}: {int(row['resource_name']):5} VMs  |  ${row['cost_usd']:12,.2f} total cost")

    # Optimization Opportunities
    print("\n" + "=" * 70)
    print("OPTIMIZATION OPPORTUNITIES")
    print("=" * 70)

    # Underutilized VMs
    vm_records = df[df["resource_type"] == "Microsoft.Compute/virtualMachines"]
    underutilized = vm_records[vm_records["cpu_utilization"] < 15]
    if len(underutilized) > 0:
        unique_underutilized = underutilized["resource_name"].nunique()
        potential_savings = underutilized["cost_usd"].sum()
        print("Underutilized VMs (<15% CPU):")
        print(f"  - Unique Resources: {unique_underutilized:,}")
        print(f"  - Total Records: {len(underutilized):,}")
        print(f"  - Potential Savings: ${potential_savings:,.2f}")
        print(f"  - Avg Cost per VM: ${potential_savings / unique_underutilized:,.2f}")

    # Stopped VMs
    stopped_vms = vm_records[vm_records["uptime_hours"] == 0]
    if len(stopped_vms) > 0:
        unique_stopped = stopped_vms["resource_name"].nunique()
        wasted_cost = stopped_vms["cost_usd"].sum()
        print("\nStopped VMs (still charging):")
        print(f"  - Unique Resources: {unique_stopped:,}")
        print(f"  - Total Records: {len(stopped_vms):,}")
        print(f"  - Wasted Costs: ${wasted_cost:,.2f}")

    # Untagged resources
    untagged = df[df["department"].isna()]
    if len(untagged) > 0:
        unique_untagged = untagged["resource_name"].nunique()
        unallocated_cost = untagged["cost_usd"].sum()
        print("\nUntagged Resources:")
        print(f"  - Unique Resources: {unique_untagged:,}")
        print(f"  - Total Records: {len(untagged):,}")
        print(f"  - Unallocated Costs: ${unallocated_cost:,.2f}")

    # Dev/Test workloads (Reserved Instance opportunity)
    dev_test = df[df["environment"].isin(["dev", "test"])]
    if len(dev_test) > 0:
        unique_dev_test = dev_test["resource_name"].nunique()
        dev_test_cost = dev_test["cost_usd"].sum()
        ri_savings = dev_test_cost * 0.40  # 40% savings with 3-year RI
        print("\nDev/Test Resources (RI Opportunity):")
        print(f"  - Unique Resources: {unique_dev_test:,}")
        print(f"  - Total Records: {len(dev_test):,}")
        print(f"  - Current Cost: ${dev_test_cost:,.2f}")
        print(f"  - Potential Savings (40% with 3-yr RI): ${ri_savings:,.2f}")

    # Cost Trends
    print("\n" + "=" * 70)
    print("COST TRENDS")
    print("=" * 70)

    daily_costs = df.groupby("date")["cost_usd"].sum().sort_index()
    print("Daily Cost Statistics:")
    print(f"  - Minimum Daily Cost: ${daily_costs.min():,.2f} on {daily_costs.idxmin()}")
    print(f"  - Maximum Daily Cost: ${daily_costs.max():,.2f} on {daily_costs.idxmax()}")
    print(f"  - Average Daily Cost: ${daily_costs.mean():,.2f}")
    print(f"  - Median Daily Cost: ${daily_costs.median():,.2f}")
    print(f"  - Std Deviation: ${daily_costs.std():,.2f}")

    # Monthly breakdown
    monthly_costs = df.groupby("billing_period")["cost_usd"].sum().sort_index()
    print("\nMonthly Cost Breakdown:")
    for month, cost in monthly_costs.items():
        print(f"  - {month}: ${cost:,.2f}")

    # Top 10 Most Expensive Resources
    print("\n" + "=" * 70)
    print("TOP 10 MOST EXPENSIVE RESOURCES (Total Cost)")
    print("=" * 70)
    top_resources = (
        df.groupby(["resource_name", "resource_type", "sku"])
        .agg({"cost_usd": "sum", "resource_id": "count"})
        .sort_values("cost_usd", ascending=False)
        .head(10)
    )

    for idx, (resource_info, row) in enumerate(top_resources.iterrows(), 1):
        resource_name, resource_type, sku = resource_info
        short_type = resource_type.split("/")[-1] if "/" in resource_type else resource_type
        print(f"{idx:2d}. {resource_name:40s} ({short_type:20s} {sku:15s})")
        print(f"    Cost: ${row['cost_usd']:10,.2f}  |  Records: {int(row['resource_id']):,}")

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    # Get CSV file path from command line or use default
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "./azure_compute_usage_6months.csv"

    # Run analysis
    analyze_azure_costs(csv_file)
