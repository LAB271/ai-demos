#!/usr/bin/env python3
"""
Azure Resource Data Generation Script

Generates 6 months of synthetic Azure billing data for 2,350 resources across 4 types:
- Virtual Machines (2,000): 5 SKU types with region-specific pricing
- Container Instances (200): CPU/memory-based billing with burst patterns  
- Storage Accounts (100): Hot/cool/archive tiers with monthly billing
- SQL Databases (50): Service tier-based 24/7 billing

Features realistic optimization scenarios:
- Underutilized VMs (20%): Low CPU usage candidates for right-sizing
- Stopped VMs (10%): Still charging when not properly deallocated
- Untagged resources (5%): Missing department/environment tags
- Environment patterns: Prod (24/7) vs dev/test (business hours)

Covers 5 Azure regions, 5 subscriptions, 5 departments, 4 environments.
Outputs CSV with daily usage metrics, costs, and optimization opportunities.
Includes summary statistics and potential savings analysis.

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Configuration
num_vms = 2000
num_containers = 200
num_storage_accounts = 100
num_sql_databases = 50
days = 180  # 6 months
start_date = datetime.today() - timedelta(days=days)

# Azure-compliant configuration
REGIONS = ["eastus", "westus", "northeurope", "southeastasia", "australiaeast"]
SUBSCRIPTION_IDS = [fake.uuid4() for _ in range(5)]  # 5 subscriptions
DEPARTMENTS = ["Finance", "HR", "Engineering", "Marketing", "Sales"]
ENVIRONMENTS = ["prod", "dev", "test", "staging"]

# Resource Groups (Azure naming conventions)
RESOURCE_GROUPS = [
    f"rg-{dept.lower()}-{env}-{region}"
    for dept in DEPARTMENTS
    for env in ENVIRONMENTS
    for region in random.sample(REGIONS, 2)
]

# VM SKU pricing (USD per hour) by region
VM_SKU_PRICING = {
    "Standard_B2s": {
        "eastus": 0.042,
        "westus": 0.045,
        "northeurope": 0.048,
        "southeastasia": 0.050,
        "australiaeast": 0.052,
    },
    "Standard_D4s_v3": {
        "eastus": 0.192,
        "westus": 0.205,
        "northeurope": 0.210,
        "southeastasia": 0.220,
        "australiaeast": 0.225,
    },
    "Standard_E8s_v3": {
        "eastus": 0.504,
        "westus": 0.538,
        "northeurope": 0.550,
        "southeastasia": 0.575,
        "australiaeast": 0.590,
    },
    "Standard_D2s_v4": {
        "eastus": 0.096,
        "westus": 0.102,
        "northeurope": 0.105,
        "southeastasia": 0.110,
        "australiaeast": 0.115,
    },
    "Standard_F4s_v2": {
        "eastus": 0.169,
        "westus": 0.180,
        "northeurope": 0.185,
        "southeastasia": 0.195,
        "australiaeast": 0.200,
    },
}

# Container pricing (USD per vCPU-hour and GB-hour)
CONTAINER_PRICING = {
    "cpu_per_hour": 0.0000125,  # Per vCPU second * 3600
    "memory_per_hour": 0.0000014,  # Per GB second * 3600
}

# Storage pricing (USD per GB-month)
STORAGE_PRICING = {"hot": 0.0184, "cool": 0.01, "archive": 0.002}

# SQL Database pricing tiers (USD per hour)
SQL_PRICING = {"Basic": 0.0068, "S0": 0.0206, "S1": 0.0412, "S2": 0.1644, "P1": 0.6849}

# Generate consistent resource configurations
vm_configs = []
for i in range(num_vms):
    subscription_id = random.choice(SUBSCRIPTION_IDS)
    resource_group = random.choice(RESOURCE_GROUPS)
    region = resource_group.split("-")[-1]  # Extract region from RG name
    department = resource_group.split("-")[1].capitalize()
    environment = resource_group.split("-")[2]
    sku = random.choice(list(VM_SKU_PRICING.keys()))
    vm_name = f"vm-{department.lower()}-{environment}-{i + 1:04d}"

    # Create optimization scenarios
    # 20% of VMs are underutilized (candidates for right-sizing)
    is_underutilized = random.random() < 0.20
    # 10% of VMs are stopped but not deallocated
    is_stopped_not_deallocated = random.random() < 0.10
    # 5% are missing tags
    has_tags = random.random() > 0.05
    # Dev/test vs prod usage patterns
    is_production = environment == "prod"

    vm_configs.append(
        {
            "resource_id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
            "resource_name": vm_name,
            "resource_type": "Microsoft.Compute/virtualMachines",
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "region": region,
            "department": department if has_tags else None,
            "environment": environment if has_tags else None,
            "sku": sku,
            "is_underutilized": is_underutilized,
            "is_stopped_not_deallocated": is_stopped_not_deallocated,
            "is_production": is_production,
        }
    )

container_configs = []
for i in range(num_containers):
    subscription_id = random.choice(SUBSCRIPTION_IDS)
    resource_group = random.choice(RESOURCE_GROUPS)
    region = resource_group.split("-")[-1]
    department = resource_group.split("-")[1].capitalize()
    environment = resource_group.split("-")[2]
    container_name = f"aci-{department.lower()}-{environment}-{i + 1:04d}"
    has_tags = random.random() > 0.05

    container_configs.append(
        {
            "resource_id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ContainerInstance/containerGroups/{container_name}",
            "resource_name": container_name,
            "resource_type": "Microsoft.ContainerInstance/containerGroups",
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "region": region,
            "department": department if has_tags else None,
            "environment": environment if has_tags else None,
            "cpu_cores": random.choice([1, 2, 4]),
            "memory_gb": random.choice([1, 2, 4, 8]),
        }
    )

storage_configs = []
for i in range(num_storage_accounts):
    subscription_id = random.choice(SUBSCRIPTION_IDS)
    resource_group = random.choice(RESOURCE_GROUPS)
    region = resource_group.split("-")[-1]
    department = resource_group.split("-")[1].capitalize()
    environment = resource_group.split("-")[2]
    storage_name = f"st{department.lower()}{environment}{i + 1:04d}".replace("-", "")[:24]
    has_tags = random.random() > 0.05
    tier = random.choice(["hot", "cool", "archive"])

    storage_configs.append(
        {
            "resource_id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_name}",
            "resource_name": storage_name,
            "resource_type": "Microsoft.Storage/storageAccounts",
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "region": region,
            "department": department if has_tags else None,
            "environment": environment if has_tags else None,
            "storage_tier": tier,
            "storage_size_gb": random.randint(100, 10000),
        }
    )

sql_configs = []
for i in range(num_sql_databases):
    subscription_id = random.choice(SUBSCRIPTION_IDS)
    resource_group = random.choice(RESOURCE_GROUPS)
    region = resource_group.split("-")[-1]
    department = resource_group.split("-")[1].capitalize()
    environment = resource_group.split("-")[2]
    sql_server = f"sql-{department.lower()}-{environment}-{region}"
    db_name = f"db-{department.lower()}-{environment}-{i + 1:04d}"
    has_tags = random.random() > 0.05
    tier = random.choice(list(SQL_PRICING.keys()))

    sql_configs.append(
        {
            "resource_id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Sql/servers/{sql_server}/databases/{db_name}",
            "resource_name": db_name,
            "resource_type": "Microsoft.Sql/servers/databases",
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "region": region,
            "department": department if has_tags else None,
            "environment": environment if has_tags else None,
            "service_tier": tier,
        }
    )

# Generate daily records with realistic usage patterns
records = []
print("Generating synthetic Azure cost data...")

for day in range(days):
    date = start_date + timedelta(days=day)
    is_weekday = date.weekday() < 5

    # VMs
    for vm_config in vm_configs:
        # Determine uptime and utilization based on patterns
        if vm_config["is_stopped_not_deallocated"]:
            uptime_hours = 0
            cpu_utilization = 0
            memory_usage_gb = 0
            # Still charged for storage when stopped but not deallocated
            daily_cost = VM_SKU_PRICING[vm_config["sku"]][vm_config["region"]] * 24 * 0.1
        elif vm_config["is_underutilized"]:
            # Underutilized resources (consistent low usage)
            uptime_hours = 24
            cpu_utilization = round(random.uniform(2, 15), 2)
            memory_usage_gb = round(random.uniform(1, 10), 2)
            daily_cost = VM_SKU_PRICING[vm_config["sku"]][vm_config["region"]] * uptime_hours
        elif vm_config["is_production"]:
            # Production: 24/7 with higher utilization
            uptime_hours = 24
            cpu_utilization = round(random.uniform(40, 85), 2)
            memory_usage_gb = round(random.uniform(20, 64), 2)
            daily_cost = VM_SKU_PRICING[vm_config["sku"]][vm_config["region"]] * uptime_hours
        else:
            # Dev/Test: Business hours pattern
            if is_weekday:
                uptime_hours = round(random.uniform(10, 14), 2)
                cpu_utilization = round(random.uniform(15, 60), 2)
                memory_usage_gb = round(random.uniform(8, 32), 2)
            else:
                uptime_hours = round(random.uniform(0, 4), 2)
                cpu_utilization = round(random.uniform(5, 20), 2)
                memory_usage_gb = round(random.uniform(2, 16), 2)
            daily_cost = VM_SKU_PRICING[vm_config["sku"]][vm_config["region"]] * uptime_hours

        records.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "resource_id": vm_config["resource_id"],
                "resource_name": vm_config["resource_name"],
                "resource_type": vm_config["resource_type"],
                "meter_category": "Virtual Machines",
                "meter_subcategory": "Compute",
                "meter_name": f"{vm_config['sku']} - {vm_config['region']}",
                "subscription_id": vm_config["subscription_id"],
                "resource_group": vm_config["resource_group"],
                "region": vm_config["region"],
                "service_name": "Virtual Machines",
                "sku": vm_config["sku"],
                "cpu_utilization": cpu_utilization,
                "memory_usage_gb": memory_usage_gb,
                "uptime_hours": uptime_hours,
                "cost_usd": round(daily_cost, 4),
                "currency": "USD",
                "department": vm_config["department"],
                "environment": vm_config["environment"],
                "billing_period": date.strftime("%Y-%m"),
            }
        )

    # Containers
    for container_config in container_configs:
        # Containers typically have burst patterns
        if is_weekday:
            uptime_hours = round(random.uniform(8, 20), 2)
            cpu_utilization = round(random.uniform(30, 75), 2)
        else:
            uptime_hours = round(random.uniform(2, 8), 2)
            cpu_utilization = round(random.uniform(10, 40), 2)

        memory_usage_gb = container_config["memory_gb"] * (cpu_utilization / 100)
        cpu_cost = CONTAINER_PRICING["cpu_per_hour"] * container_config["cpu_cores"] * uptime_hours
        memory_cost = CONTAINER_PRICING["memory_per_hour"] * container_config["memory_gb"] * uptime_hours
        daily_cost = cpu_cost + memory_cost

        records.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "resource_id": container_config["resource_id"],
                "resource_name": container_config["resource_name"],
                "resource_type": container_config["resource_type"],
                "meter_category": "Container Instances",
                "meter_subcategory": "Container Groups",
                "meter_name": f"{container_config['cpu_cores']} vCPU, {container_config['memory_gb']} GB Memory",
                "subscription_id": container_config["subscription_id"],
                "resource_group": container_config["resource_group"],
                "region": container_config["region"],
                "service_name": "Container Instances",
                "sku": f"{container_config['cpu_cores']}vCPU-{container_config['memory_gb']}GB",
                "cpu_utilization": cpu_utilization,
                "memory_usage_gb": round(memory_usage_gb, 2),
                "uptime_hours": uptime_hours,
                "cost_usd": round(daily_cost, 4),
                "currency": "USD",
                "department": container_config["department"],
                "environment": container_config["environment"],
                "billing_period": date.strftime("%Y-%m"),
            }
        )

    # Storage Accounts (monthly cost, but reported daily)
    if date.day == 1:  # Report on first day of month
        for storage_config in storage_configs:
            monthly_cost = storage_config["storage_size_gb"] * STORAGE_PRICING[storage_config["storage_tier"]]
            daily_cost = monthly_cost / 30

            records.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "resource_id": storage_config["resource_id"],
                    "resource_name": storage_config["resource_name"],
                    "resource_type": storage_config["resource_type"],
                    "meter_category": "Storage",
                    "meter_subcategory": "Blob Storage",
                    "meter_name": f"{storage_config['storage_tier'].capitalize()} Storage",
                    "subscription_id": storage_config["subscription_id"],
                    "resource_group": storage_config["resource_group"],
                    "region": storage_config["region"],
                    "service_name": "Storage Accounts",
                    "sku": storage_config["storage_tier"],
                    "cpu_utilization": None,
                    "memory_usage_gb": None,
                    "uptime_hours": 720,  # Full month
                    "cost_usd": round(monthly_cost, 4),
                    "currency": "USD",
                    "department": storage_config["department"],
                    "environment": storage_config["environment"],
                    "billing_period": date.strftime("%Y-%m"),
                }
            )

    # SQL Databases
    for sql_config in sql_configs:
        # SQL databases are charged 24/7
        daily_cost = SQL_PRICING[sql_config["service_tier"]] * 24

        records.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "resource_id": sql_config["resource_id"],
                "resource_name": sql_config["resource_name"],
                "resource_type": sql_config["resource_type"],
                "meter_category": "SQL Database",
                "meter_subcategory": "Single Database",
                "meter_name": f"{sql_config['service_tier']} Tier",
                "subscription_id": sql_config["subscription_id"],
                "resource_group": sql_config["resource_group"],
                "region": sql_config["region"],
                "service_name": "Azure SQL Database",
                "sku": sql_config["service_tier"],
                "cpu_utilization": round(random.uniform(20, 70), 2),
                "memory_usage_gb": None,
                "uptime_hours": 24,
                "cost_usd": round(daily_cost, 4),
                "currency": "USD",
                "department": sql_config["department"],
                "environment": sql_config["environment"],
                "billing_period": date.strftime("%Y-%m"),
            }
        )

    if (day + 1) % 30 == 0:
        print(f"Generated {day + 1}/{days} days...")

print("\nData generation complete.\n")

# Create DataFrame and save to CSV
df = pd.DataFrame(records)
df.to_csv("azure_compute_usage_6months.csv", index=False)

# Generate summary statistics
print("=" * 60)
print("DATASET SUMMARY")
print("=" * 60)
print(f"Total records: {len(df):,}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total cost: ${df['cost_usd'].sum():,.2f}")
print("\nResource breakdown:")
print(df["resource_type"].value_counts())
print("\nRegion breakdown:")
print(df["region"].value_counts())
print("\nDepartment breakdown:")
print(df["department"].value_counts())
print("\nEnvironment breakdown:")
print(df["environment"].value_counts())
print(f"\nResources without tags: {df['department'].isna().sum():,}")

# Optimization opportunities
print("\n" + "=" * 60)
print("OPTIMIZATION OPPORTUNITIES")
print("=" * 60)

vm_records = df[df["resource_type"] == "Microsoft.Compute/virtualMachines"]
underutilized = vm_records[vm_records["cpu_utilization"] < 15]
print(f"Underutilized VMs (<15% CPU): {underutilized['resource_name'].nunique()} resources")
print(f"  Potential savings: ${underutilized['cost_usd'].sum():,.2f}")

stopped_vms = vm_records[vm_records["uptime_hours"] == 0]
if len(stopped_vms) > 0:
    print(f"\nStopped VMs (still charging): {stopped_vms['resource_name'].nunique()} resources")
    print(f"  Wasted costs: ${stopped_vms['cost_usd'].sum():,.2f}")

untagged = df[df["department"].isna()]
print(f"\nUntagged resources: {untagged['resource_name'].nunique()} resources")
print(f"  Unallocated costs: ${untagged['cost_usd'].sum():,.2f}")

dev_test = df[df["environment"].isin(["dev", "test"])]
print(f"\nDev/Test resources: {dev_test['resource_name'].nunique()} resources")
print(f"  Potential Reserved Instance savings: ${dev_test['cost_usd'].sum() * 0.40:,.2f} (40% with 3-year RI)")

print("\n" + "=" * 60)
print("Synthetic dataset 'azure_compute_usage_6months.csv' generated successfully!")
print("=" * 60)
