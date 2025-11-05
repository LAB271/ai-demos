#!/usr/bin/env python3
"""
IAM Access Request Data Generation Script

Generates synthetic IAM access request datasets for financial services organizations,
including realistic employee profiles and access requests with embedded security anomalies
for testing access validation systems and machine learning models.

ORGANIZATION STRUCTURE:
• Financial Services firm with 250 employees across 4 departments
• 7 distinct business roles with specific system access patterns
• Realistic employee distribution reflecting industry standards

BUSINESS ROLES & SYSTEM ACCESS:
• Front Office (43%):
  - Traders (25%): Access to OMS (Order Management), PMS (Portfolio Management)
  - Portfolio Managers (18%): Access to PMS, OMS
• Middle Office (15%):
  - Risk Managers (10%): Access to Risk Platform, Compliance Monitoring
  - Compliance Officers (5%): Access to Compliance Monitoring only
• Back Office (16%):
  - Fund Accountants (16%): Access to Fund Accounting System
• IT Department (26%):
  - Cloud Engineers (16%): Access to Cloud Infrastructure, Monitoring
  - IAM Admins (10%): Access to IAM System

ANOMALY PATTERNS IMPLEMENTED:
• System Access Anomalies (10% of requests):
  - Traders requesting IAM System access (privilege escalation)
  - Portfolio Managers requesting Cloud Infrastructure (inappropriate access)
  - Fund Accountants requesting OMS access (segregation of duties violation)
  - Any role requesting systems outside their normal scope
• Temporal Anomalies (5% of requests):
  - Access requests during very late night hours (00:00-03:00)
  - Outside normal business hours patterns
  - Potential insider threat indicators
• Location Anomalies (10% of requests):
  - Requests from Singapore (designated anomaly location)
  - Requests from non-primary office locations
  - Geographically suspicious access patterns

SECURITY TESTING SCENARIOS:
• Toxic Combinations: Role-system pairs that violate security policies
• Privilege Escalation: Lower-privilege roles requesting admin systems
• Segregation of Duties: Front office accessing back office systems
• Insider Threats: Off-hours access from unusual locations
• Compliance Violations: Access patterns that breach regulatory requirements

DATA QUALITY FEATURES:
• Reproducible generation with fixed random seed (SEED = 42)
• Realistic age distribution (25-65 years old employees)
• Business hours bias (6 AM - 10 PM for normal requests)
• Location distribution (90% Amsterdam main office)
• Proper ID formatting (E001-E250, R0001-R5000)

GENERATED OUTPUT:
• employees.csv: Employee master data with demographics and roles
• access_requests.csv: Access request transactions with anomaly flags

USE CASES:
• IAM policy validation and enforcement testing
• Machine learning model training for anomaly detection
• Security awareness training scenarios
• Compliance monitoring and reporting demonstrations
• Rule-based validation system development

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

EMPLOYEES = 250
ACCESS_REQUESTS = 5000
start_date = datetime(2025, 11, 1)
SEED = 42

# Initialize Faker
fake = Faker()
Faker.seed(SEED)  # For reproducibility
random.seed(SEED)

# Define roles and systems
roles = {
    "Trader": ["OMS", "PMS"],
    "Portfolio Manager": ["PMS", "OMS"],
    "Risk Manager": ["Risk Platform", "Compliance Monitoring"],
    "Compliance Officer": ["Compliance Monitoring"],
    "Fund Accountant": ["Fund Accounting System"],
    "Cloud Engineer": ["Cloud Infrastructure", "Monitoring"],
    "IAM Admin": ["IAM System"],
}

departments = {
    "Trader": "Front Office",
    "Portfolio Manager": "Front Office",
    "Risk Manager": "Middle Office",
    "Compliance Officer": "Middle Office",
    "Fund Accountant": "Back Office",
    "Cloud Engineer": "IT",
    "IAM Admin": "IT",
}

# Employee distribution percentages
distribution_percentages = {
    "Trader": 0.25,  # 25% - Front Office
    "Portfolio Manager": 0.18,  # 18% - Front Office
    "Risk Manager": 0.10,  # 10% - Middle Office
    "Compliance Officer": 0.05,  # 5% - Middle Office
    "Fund Accountant": 0.16,  # 16% - Back Office
    "Cloud Engineer": 0.16,  # 16% - IT
    "IAM Admin": 0.10,  # 10% - IT
}

# Calculate employee distribution based on EMPLOYEES constant
employee_distribution = {role: int(EMPLOYEES * percentage) for role, percentage in distribution_percentages.items()}

# Adjust for rounding to ensure total equals EMPLOYEES
total_distributed = sum(employee_distribution.values())
if total_distributed < EMPLOYEES:
    # Add remaining employees to the largest role
    employee_distribution["Trader"] += EMPLOYEES - total_distributed
elif total_distributed > EMPLOYEES:
    # Remove excess from the largest role
    employee_distribution["Trader"] -= total_distributed - EMPLOYEES

print(f"Configuration: {EMPLOYEES} employees, {ACCESS_REQUESTS} access requests")

locations = ["Amsterdam", "Rotterdam", "Utrecht", "Singapore"]  # Singapore = anomaly

# STEP 1: Generate Employees
print("=" * 60)
print("STEP 1: Generating Employees")
print("=" * 60)

employees = []
employee_id_counter = 1

for role, count in employee_distribution.items():
    for _ in range(count):
        employee_id = f"E{employee_id_counter:03d}"
        name = fake.name()
        department = departments[role]
        # Generate birthday for ages between 25-65 years old
        birthday = fake.date_of_birth(minimum_age=25, maximum_age=65)

        employees.append(
            {
                "EmployeeID": employee_id,
                "Name": name,
                "Role": role,
                "Department": department,
                "Birthday": birthday.strftime("%Y-%m-%d"),
            }
        )
        employee_id_counter += 1

# Create Employee DataFrame
employees_df = pd.DataFrame(employees)

# Display employee distribution summary
print("\nEmployee Distribution Summary:")
print(employees_df["Role"].value_counts().sort_index())
print(f"\nTotal Employees: {len(employees_df)}")

# STEP 2: Export Employee List
print("\n" + "=" * 60)
print("STEP 2: Exporting Employee List")
print("=" * 60)

employees_df.to_csv("employees.csv", index=False)
print("✓ Employee list exported to 'employees.csv'")
print(f"  Columns: {', '.join(employees_df.columns)}")
print(f"  Records: {len(employees_df)}")

# Display sample employees
print("\nSample Employees:")
print(employees_df.head(10).to_string(index=False))

# STEP 3: Generate Access Requests using actual employees
print("\n" + "=" * 60)
print("STEP 3: Generating Access Requests")
print("=" * 60)

access_requests = []

for i in range(1, ACCESS_REQUESTS + 1):
    # Select a random employee
    employee = employees_df.sample(n=1).iloc[0]
    employee_id = employee["EmployeeID"]
    role = employee["Role"]
    department = employee["Department"]

    # Normal system access based on role
    system = random.choice(roles[role])

    # Introduce anomalies (10% chance)
    if random.random() < 0.1:
        # Anomaly: requesting access to system not typical for their role
        all_systems = [
            "Fund Accounting System",
            "OMS",
            "IAM System",
            "Cloud Infrastructure",
            "PMS",
            "Risk Platform",
            "Compliance Monitoring",
            "Monitoring",
        ]
        system = random.choice([s for s in all_systems if s not in roles[role]])

    # Timestamp (mostly business hours, some anomalies)
    timestamp = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(6, 22))
    if random.random() < 0.05:  # anomaly: very late night
        timestamp = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 3))

    # Location (mostly Amsterdam, some anomalies)
    location = random.choice(locations) if random.random() < 0.1 else "Amsterdam"

    access_requests.append(
        {
            "RequestID": f"R{i:04d}",
            "EmployeeID": employee_id,
            "EmployeeName": employee["Name"],
            "Role": role,
            "Department": department,
            "SystemAccessRequested": system,
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Location": location,
        }
    )

# Create Access Requests DataFrame
access_requests_df = pd.DataFrame(access_requests)

# Save to CSV
access_requests_df.to_csv("access_requests.csv", index=False)
print("✓ Access requests exported to 'access_requests.csv'")
print(f"  Columns: {', '.join(access_requests_df.columns)}")
print(f"  Records: {len(access_requests_df)}")

# Display sample access requests
print("\nSample Access Requests:")
print(access_requests_df.head(10).to_string(index=False))

# Display statistics
print("\n" + "=" * 60)
print("STATISTICS")
print("=" * 60)
print("\nRequests per Role:")
print(access_requests_df["Role"].value_counts())
print("\nRequests per System:")
print(access_requests_df["SystemAccessRequested"].value_counts())
print("\nRequests per Location:")
print(access_requests_df["Location"].value_counts())

print("\n" + "=" * 60)
print("✓ All datasets generated successfully!")
print("=" * 60)
print(f"  - employees.csv ({len(employees_df)} records)")
print(f"  - access_requests.csv ({len(access_requests_df)} records)")
