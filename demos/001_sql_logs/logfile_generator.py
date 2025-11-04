"""
Enhanced SQL Server Log Generator

This script generates realistic SQL Server log entries for anomaly detection testing.

IMPROVEMENTS BASED ON LLM ANALYSIS:
1. Added 'severe_cases' switch to generate configuration and system issues
2. FIXED: CHECKDB success messages now predominantly logged as INFO (95%) with rare WARNING (5%)
3. FIXED: Severe configuration issues now use realistic probability distributions
4. Added temporal clustering for anomalies (early morning hours)
5. Enhanced database naming with both standard and unusual patterns
6. Added system-level anomalies (deadlocks, memory issues, disk space)
7. Added temporal anomalies (off-hours operations)
8. Improved severity level accuracy based on anomaly report findings

CURRENT FAIL CASES:
- Authentication: Login failures, suspicious IPs, off-hours access
- Privilege Escalation: Adding users to sysadmin, elevated privileges
- Suspicious Queries: DROP TABLE, large SELECT on sensitive tables
- Audit Manipulation: Turning off audits, deleting audit logs
- Malware Indicators: xp_cmdshell execution, unusual connections
- Performance Anomalies: CPU spikes, blocking sessions
- Configuration Issues: Rare severity misconfigurations (now more realistic)
- System Anomalies: Memory failures, deadlocks, disk issues
- Temporal Anomalies: Operations outside maintenance windows
- Naming Convention Issues: Unusual database names (reduced frequency)

FIXES IMPLEMENTED:
- CHECKDB success messages now 95% INFO, 5% WARNING (was 100% WARNING)
- Added proper database naming distribution (80% standard, 20% unusual)
- Reduced severe case ratio from 0.0005 to 0.0003 for more realistic anomaly rates
- Enhanced template system for more varied log patterns
"""

import random
import datetime
from faker import Faker

# Initialise Faker
fake = Faker()

# Configuration
total_logs = 50000            # Total number of log entries
security_ratio = 0.0015       # Proportion of security anomalies (0.0 - 1.0)
severe_cases = True           # Generate configuration and system issues
severe_ratio = 0.0003         # Reduced proportion of severe configuration issues (was 0.0005)
log_file = "sql_server_log.txt"

# Generate dynamic elements
def random_user():
    return fake.user_name()

def random_ip():
    return fake.ipv4_public()

def random_db():
    # 80% chance of standard naming, 20% chance of weird naming
    if random.random() < 0.8:
        return random_standard_db()
    else:
        return fake.word().capitalize() + "DB"

def random_weird_db():
    """Generate databases with unusual naming patterns that might trigger anomaly detection"""
    weird_names = [
        "WomanDB", "BeautifulDB", "TrueDB", "AmongDB", "CourtDB", 
        "MaterialDB", "AfterDB", "ThroughoutDB", "MajorityDB", "BecauseDB",
        "SouthernDB", "WhiteDB", "WorldDB", "LeastDB", "BothDB", "ScoreDB"
    ]
    return random.choice(weird_names)

def random_standard_db():
    """Generate databases with standard enterprise naming patterns"""
    prefixes = ["Customer", "Product", "Order", "Inventory", "Sales", "HR", "Finance", "Audit", "Report", "Analytics"]
    suffixes = ["DB", "Data", "Store", "Warehouse", "Repository", "Archive"]
    return random.choice(prefixes) + random.choice(suffixes)

def random_query():
    tables = ["CustomerData", "Orders", "Payments", "AuditLogs", "sys.syslogins"]
    actions = ["SELECT * FROM", "DROP TABLE", "ALTER TABLE", "UPDATE", "INSERT INTO"]
    return f"{random.choice(actions)} {random.choice(tables)}"

def generate_timestamp_with_clustering():
    """Generate timestamps with clustering for severe cases (early morning hours)"""
    now = datetime.datetime.now()
    if random.random() < 0.6:  # 60% chance of early morning clustering
        # Generate times between 00:00 and 06:00
        hour = random.randint(0, 6)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        random_date = now - datetime.timedelta(days=random.randint(0, 1))
        timestamp = random_date.replace(hour=hour, minute=minute, second=second)
    else:
        # Normal random timestamp
        random_offset = datetime.timedelta(seconds=random.randint(0, 86400))
        timestamp = now - random_offset
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

# Anomaly categories with placeholders
anomaly_templates = {
    "Authentication": [
        "Login failed for user '{user}'. Reason: Password did not match.",
        "Login attempt from unknown IP: {ip}",
        "Login succeeded outside normal hours for user '{user}'."
    ],
    "Privilege Escalation": [
        "ALTER SERVER ROLE sysadmin ADD MEMBER '{user}'",
        "New login '{user}' created with elevated privileges."
    ],
    "Suspicious Queries": [
        "{query} executed by user '{user}'.",
        "Large SELECT query on sensitive table '{table}'.",
        "DROP TABLE detected on '{table}'."
    ],
    "Audit Manipulation": [
        "ALTER SERVER AUDIT state changed to OFF by '{user}'.",
        "Audit log file manually deleted by user '{user}'."
    ],
    "Malware Indicators": [
        "xp_cmdshell executed: 'powershell -EncodedCommand ...' by '{user}'.",
        "Unusual linked server connection to '{server}'."
    ],
    "Performance Anomalies": [
        "CPU usage spiked to 95% during query execution by '{user}'.",
        "Blocking session detected: Session ID {session_id}."
    ]
}

# Severe configuration and system issue templates
severe_templates = {
    "Configuration Issues": [
        "CHECKDB found 0 allocation errors and 0 consistency errors in '{db}'.",  # Occasionally logged as WARNING (configuration issue)
        "Backup completed successfully for database '{db}'.",  # Rarely logged as WARNING (configuration issue)
        "Database '{db}' started successfully.",  # Occasionally logged as WARNING/ERROR (configuration issue)
    ],
    "System Anomalies": [
        "Memory allocation failed for database '{db}'. Retrying...",
        "Deadlock detected between sessions {session_id} and {session_id2}.",
        "Transaction log full for database '{db}'. Waiting for log backup.",
        "Page checksum mismatch detected in database '{db}', page {page_id}.",
        "Login timeout exceeded for user '{user}' from {ip}.",
        "Database '{db}' recovery pending due to unexpected shutdown.",
        "Disk space critically low on drive hosting '{db}' ({space_mb}MB remaining)."
    ],
    "Temporal Anomalies": [
        "Scheduled maintenance job failed: Database integrity check for '{db}'.",
        "Automated backup job started outside maintenance window for '{db}'.",
        "Index rebuild operation initiated during peak hours on '{db}'.",
        "Database mail configuration changed outside business hours by '{user}'."
    ],
    "Naming Convention Issues": [
        "Database '{weird_db}' created with non-standard naming convention.",
        "Suspicious database name detected: '{weird_db}' created by '{user}'.",
        "Database '{weird_db}' shows unusual activity patterns."
    ]
}

# Normal log messages with placeholders
normal_templates = [
    "Backup completed successfully for database '{db}'.",
    "CHECKDB found 0 allocation errors and 0 consistency errors in '{db}'.",  # This should normally be INFO
    "Database '{db}' started successfully.",
    "Login succeeded for user '{user}'.",
    "Transaction committed in database '{db}'."
]

# Additional normal CHECKDB templates to ensure proper severity distribution
checkdb_success_templates = [
    "CHECKDB found 0 allocation errors and 0 consistency errors in '{db}'.",
    "Database consistency check completed successfully for '{db}'.",
    "Integrity check passed for database '{db}' - no errors found.",
]

def generate_timestamp():
    now = datetime.datetime.now()
    random_offset = datetime.timedelta(seconds=random.randint(0, 86400))
    return (now - random_offset).strftime("%Y-%m-%d %H:%M:%S")

def fill_template(template):
    return template.format(
        user=random_user(),
        ip=random_ip(),
        db=random_db(),
        standard_db=random_standard_db(),
        weird_db=random_weird_db(),
        query=random_query(),
        table=random.choice(["CustomerData", "Orders", "Payments", "AuditLogs"]),
        server=fake.domain_name(),
        session_id=random.randint(1000, 9999),
        session_id2=random.randint(1000, 9999),
        page_id=random.randint(1, 999999),
        space_mb=random.randint(50, 500)
    )

def generate_log_entry(entry_type="normal"):
    """
    Generate log entry based on type:
    - normal: Regular operations
    - security: Security anomalies  
    - severe: Configuration issues and system problems
    """
    timestamp = generate_timestamp()
    
    if entry_type == "security":
        # Security anomalies should be WARNING or ERROR
        severity = random.choice(["WARNING", "ERROR"])
        category = random.choice(list(anomaly_templates.keys()))
        message = fill_template(random.choice(anomaly_templates[category]))
        
    elif entry_type == "severe":
        # Severe cases: configuration issues and system problems
        category = random.choice(list(severe_templates.keys()))
        template = random.choice(severe_templates[category])
        
        if category == "Configuration Issues":
            # Configuration issue: CHECKDB success sometimes logged as WARNING (should be INFO)
            if "CHECKDB found 0" in template:
                # 70% chance it's correctly logged as INFO, 30% as WARNING (the anomaly)
                severity = "WARNING" if random.random() < 0.3 else "INFO"
                # Use weird database names more often for these anomalies
                template = template.replace("{db}", "{weird_db}")
            else:
                # Other configuration issues occasionally logged as WARNING
                severity = "WARNING" if random.random() < 0.2 else "INFO"
            timestamp = generate_timestamp_with_clustering()  # Cluster in early morning
        elif category == "System Anomalies":
            severity = random.choice(["ERROR", "WARNING"])
        elif category == "Temporal Anomalies":
            severity = "WARNING"
            # Generate during off-hours for temporal anomalies
            timestamp = generate_timestamp_with_clustering()
        else:  # Naming Convention Issues
            severity = random.choice(["WARNING", "INFO"])
            
        message = fill_template(template)
        
    else:  # normal
        # For normal operations, ensure CHECKDB success is predominantly INFO
        template = random.choice(normal_templates + checkdb_success_templates)
        
        if "CHECKDB found 0" in template:
            # Normal CHECKDB operations should be 95% INFO, 5% WARNING (rare misconfiguration)
            severity = "WARNING" if random.random() < 0.05 else "INFO"
        else:
            # Other normal operations should mostly be INFO, occasionally WARNING
            severity = random.choices(["INFO", "WARNING"], weights=[0.8, 0.2])[0]
            
        message = fill_template(template)
    
    return f"{timestamp} | {severity} | {message}"

def generate_logs():
    security_logs_count = int(total_logs * security_ratio)
    severe_logs_count = int(total_logs * severe_ratio) if severe_cases else 0
    normal_logs_count = total_logs - security_logs_count - severe_logs_count

    logs = []
    
    # Generate security anomalies
    for _ in range(security_logs_count):
        logs.append(generate_log_entry("security"))
    
    # Generate severe configuration and system issues
    if severe_cases:
        for _ in range(severe_logs_count):
            logs.append(generate_log_entry("severe"))
    
    # Generate normal logs
    for _ in range(normal_logs_count):
        logs.append(generate_log_entry("normal"))

    random.shuffle(logs)
    return logs

# Write logs to file
logs = generate_logs()
with open(log_file, "w") as f:
    for log in logs:
        f.write(log + "\n")

severe_info = f" and {int(total_logs * severe_ratio)} severe configuration issues" if severe_cases else ""
print(f"Generated {total_logs} log entries in '{log_file}' with {int(total_logs * security_ratio)} security anomalies{severe_info}.")
