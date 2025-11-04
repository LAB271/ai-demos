import random
import datetime
from faker import Faker

# Initialise Faker
fake = Faker()

# Configuration
total_logs = 20000            # Total number of log entries
security_ratio = 0.02         # Proportion of security anomalies (0.0 - 1.0)
log_file = "sql_server_log.txt"

# Generate dynamic elements
def random_user():
    return fake.user_name()

def random_ip():
    return fake.ipv4_public()

def random_db():
    return fake.word().capitalize() + "DB"

def random_query():
    tables = ["CustomerData", "Orders", "Payments", "AuditLogs", "sys.syslogins"]
    actions = ["SELECT * FROM", "DROP TABLE", "ALTER TABLE", "UPDATE", "INSERT INTO"]
    return f"{random.choice(actions)} {random.choice(tables)}"

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

# Normal log messages with placeholders
normal_templates = [
    "Backup completed successfully for database '{db}'.",
    "CHECKDB found 0 allocation errors and 0 consistency errors in '{db}'.",
    "Database '{db}' started successfully.",
    "Login succeeded for user '{user}'.",
    "Transaction committed in database '{db}'."
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
        query=random_query(),
        table=random.choice(["CustomerData", "Orders", "Payments", "AuditLogs"]),
        server=fake.domain_name(),
        session_id=random.randint(1000, 9999)
    )

def generate_log_entry(is_security=False):
    if is_security:
        # Security anomalies should be WARNING or ERROR
        severity = random.choice(["WARNING", "ERROR"])
        category = random.choice(list(anomaly_templates.keys()))
        message = fill_template(random.choice(anomaly_templates[category]))
    else:
        # Normal operations should mostly be INFO, occasionally WARNING
        severity = random.choices(["INFO", "WARNING"], weights=[0.8, 0.2])[0]
        message = fill_template(random.choice(normal_templates))
    return f"{generate_timestamp()} | {severity} | {message}"

def generate_logs():
    security_logs_count = int(total_logs * security_ratio)
    normal_logs_count = total_logs - security_logs_count

    logs = []
    for _ in range(security_logs_count):
        logs.append(generate_log_entry(is_security=True))
    for _ in range(normal_logs_count):
        logs.append(generate_log_entry(is_security=False))

    random.shuffle(logs)
    return logs

# Write logs to file
logs = generate_logs()
with open(log_file, "w") as f:
    for log in logs:
        f.write(log + "\n")

print(f"Generated {total_logs} log entries in '{log_file}' with {int(total_logs * security_ratio)} security anomalies.")
