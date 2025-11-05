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
    'Trader': ['OMS', 'PMS'],
    'Portfolio Manager': ['PMS', 'OMS'],
    'Risk Manager': ['Risk Platform', 'Compliance Monitoring'],
    'Compliance Officer': ['Compliance Monitoring'],
    'Fund Accountant': ['Fund Accounting System'],
    'Cloud Engineer': ['Cloud Infrastructure', 'Monitoring'],
    'IAM Admin': ['IAM System']
}

departments = {
    'Trader': 'Front Office',
    'Portfolio Manager': 'Front Office',
    'Risk Manager': 'Middle Office',
    'Compliance Officer': 'Middle Office',
    'Fund Accountant': 'Back Office',
    'Cloud Engineer': 'IT',
    'IAM Admin': 'IT'
}

# Employee distribution percentages
distribution_percentages = {
    'Trader': 0.25,             # 25% - Front Office
    'Portfolio Manager': 0.18,  # 18% - Front Office
    'Risk Manager': 0.10,       # 10% - Middle Office
    'Compliance Officer': 0.05, # 5% - Middle Office
    'Fund Accountant': 0.16,    # 16% - Back Office
    'Cloud Engineer': 0.16,     # 16% - IT
    'IAM Admin': 0.10           # 10% - IT
}

# Calculate employee distribution based on EMPLOYEES constant
employee_distribution = {
    role: int(EMPLOYEES * percentage) 
    for role, percentage in distribution_percentages.items()
}

# Adjust for rounding to ensure total equals EMPLOYEES
total_distributed = sum(employee_distribution.values())
if total_distributed < EMPLOYEES:
    # Add remaining employees to the largest role
    employee_distribution['Trader'] += EMPLOYEES - total_distributed
elif total_distributed > EMPLOYEES:
    # Remove excess from the largest role
    employee_distribution['Trader'] -= total_distributed - EMPLOYEES

print(f"Configuration: {EMPLOYEES} employees, {ACCESS_REQUESTS} access requests")

locations = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Singapore']  # Singapore = anomaly

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
        
        employees.append({
            'EmployeeID': employee_id,
            'Name': name,
            'Role': role,
            'Department': department,
            'Birthday': birthday.strftime('%Y-%m-%d')
        })
        employee_id_counter += 1

# Create Employee DataFrame
employees_df = pd.DataFrame(employees)

# Display employee distribution summary
print("\nEmployee Distribution Summary:")
print(employees_df['Role'].value_counts().sort_index())
print(f"\nTotal Employees: {len(employees_df)}")

# STEP 2: Export Employee List
print("\n" + "=" * 60)
print("STEP 2: Exporting Employee List")
print("=" * 60)

employees_df.to_csv('employees.csv', index=False)
print(f"✓ Employee list exported to 'employees.csv'")
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
    employee_id = employee['EmployeeID']
    role = employee['Role']
    department = employee['Department']
    
    # Normal system access based on role
    system = random.choice(roles[role])
    
    # Introduce anomalies (10% chance)
    if random.random() < 0.1:
        # Anomaly: requesting access to system not typical for their role
        all_systems = ['Fund Accounting System', 'OMS', 'IAM System', 'Cloud Infrastructure', 
                       'PMS', 'Risk Platform', 'Compliance Monitoring', 'Monitoring']
        system = random.choice([s for s in all_systems if s not in roles[role]])
    
    # Timestamp (mostly business hours, some anomalies)
    timestamp = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(6, 22))
    if random.random() < 0.05:  # anomaly: very late night
        timestamp = start_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 3))
    
    # Location (mostly Amsterdam, some anomalies)
    location = random.choice(locations) if random.random() < 0.1 else 'Amsterdam'
    
    access_requests.append({
        'RequestID': f"R{i:04d}",
        'EmployeeID': employee_id,
        'EmployeeName': employee['Name'],
        'Role': role,
        'Department': department,
        'SystemAccessRequested': system,
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'Location': location
    })

# Create Access Requests DataFrame
access_requests_df = pd.DataFrame(access_requests)

# Save to CSV
access_requests_df.to_csv('access_requests.csv', index=False)
print(f"✓ Access requests exported to 'access_requests.csv'")
print(f"  Columns: {', '.join(access_requests_df.columns)}")
print(f"  Records: {len(access_requests_df)}")

# Display sample access requests
print("\nSample Access Requests:")
print(access_requests_df.head(10).to_string(index=False))

# Display statistics
print("\n" + "=" * 60)
print("STATISTICS")
print("=" * 60)
print(f"\nRequests per Role:")
print(access_requests_df['Role'].value_counts())
print(f"\nRequests per System:")
print(access_requests_df['SystemAccessRequested'].value_counts())
print(f"\nRequests per Location:")
print(access_requests_df['Location'].value_counts())

print("\n" + "=" * 60)
print("✓ All datasets generated successfully!")
print("=" * 60)
print(f"  - employees.csv ({len(employees_df)} records)")
print(f"  - access_requests.csv ({len(access_requests_df)} records)")
