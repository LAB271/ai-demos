import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Configuration
num_vms = 2000
num_containers = 200
days = 180  # 6 months
start_date = datetime.today() - timedelta(days=days)

# Generate IDs
vm_ids = [f"vm_{i+1}" for i in range(num_vms)]
container_ids = [f"container_{i+1}" for i in range(num_containers)]

# Departments for tagging
departments = ["Finance", "HR", "Engineering", "Marketing", "Sales"]

# Generate synthetic records
records = []
for day in range(days):
    date = start_date + timedelta(days=day)
    
    # VMs
    for vm_id in vm_ids:
        records.append({
            "date": date.strftime('%Y-%m-%d'),
            "resource_id": vm_id,
            "resource_type": "VM",
            "cpu_utilization": round(random.uniform(5, 95), 2),
            "memory_usage_gb": round(random.uniform(1, 64), 2),
            "uptime_hours": round(random.uniform(20, 24), 2),
            "estimated_cost_usd": round(random.uniform(5, 50), 2),
            "resource_group": fake.word(),
            "subscription_id": fake.uuid4(),
            "department": random.choice(departments)
        })
    
    # Containers
    for container_id in container_ids:
        records.append({
            "date": date.strftime('%Y-%m-%d'),
            "resource_id": container_id,
            "resource_type": "Container",
            "cpu_utilization": round(random.uniform(1, 80), 2),
            "memory_usage_gb": round(random.uniform(0.5, 8), 2),
            "uptime_hours": round(random.uniform(10, 24), 2),
            "estimated_cost_usd": round(random.uniform(0.5, 10), 2),
            "resource_group": fake.word(),
            "subscription_id": fake.uuid4(),
            "department": random.choice(departments)
        })

# Create DataFrame and save to CSV
df = pd.DataFrame(records)
df.to_csv("azure_compute_usage_6months.csv", index=False)

print("Synthetic dataset 'azure_compute_usage_6months.csv' generated successfully!")