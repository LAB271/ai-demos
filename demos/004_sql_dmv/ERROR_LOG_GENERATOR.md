# SQL Server Error Log Generator

The synthetic DMV generator has been extended to also generate realistic SQL Server Error Log files that match the format of the original files.

## What Was Added

### New Components

1. **Error Log Model** ([models/errorlog.py](synthetic_dmv_generator/models/errorlog.py))
   - `ErrorLogEntry` dataclass representing a single log entry
   - Fields: date, source, severity, message, and optional metadata

2. **Error Log Generator** ([generators/errorlog_generator.py](synthetic_dmv_generator/generators/errorlog_generator.py))
   - Generates realistic error log entries based on time period
   - Includes common SQL Server log patterns:
     - Policy violation checks (every 30 minutes)
     - Certificate checks (every 60 minutes)
     - Informational messages
     - Error messages
     - Warning messages
     - Server startup messages

3. **Error Log Exporter** ([exporters/errorlog_exporter.py](synthetic_dmv_generator/exporters/errorlog_exporter.py))
   - Exports error log entries to UTF-16 LE CSV format with BOM
   - Matches the exact format of SQL Server ERRORLOG files
   - 10 columns: Date, Source, Severity, Message, Log ID, Process ID, Mail Item ID, Account ID, Last Modified, Last Modified By

### Integration

The error log generator is automatically invoked when running [generate_synthetic_dmv.py](generate_synthetic_dmv.py:1):

```bash
# Generate DMV data with error log
uv run python generate_synthetic_dmv.py --workload mixed --days 7 --queries 100
```

This will create:
- All DMV files (sys.query_store_*.txt)
- **New:** `sqlserver_log.txt` - SQL Server error log in UTF-16 LE format

## Generated Error Log Characteristics

### File Format
- **Encoding:** UTF-16 LE with BOM (FF FE)
- **Format:** CSV with comma delimiters
- **Line endings:** Windows (CRLR\n)
- **Sorted:** Newest entries first (descending by date)

### Log Entry Types

1. **Policy Violations** (every 30 minutes)
   - Windows Authentication policy
   - SQL login policy checks
   - Password policy
   - Password expiration
   - Each violation followed by Error 34052

2. **Certificate Checks** (every 60 minutes, offset by 30 min)
   - Dutch language messages (matching original)
   - Certificate validation status
   - Expiration date

3. **Informational Messages** (~1 per day)
   - SQL Server startup
   - Database backups
   - Recovery complete
   - Service Broker status
   - Clearing tempdb

4. **Error Messages** (2-5 per day)
   - Login failures (Error 18456)
   - Deadlocks (Error 1205)
   - I/O errors (Error 825)
   - SSPI handshake failures (Error 17806)

5. **Warning Messages** (1-3 per day)
   - Lock resource exhaustion
   - Autogrow timeouts
   - Slow I/O warnings

### Example Output

```csv
Date,Source,Severity,Message,Log ID,Process ID,Mail Item ID,Account ID,Last Modified,Last Modified By
11/08/2025 07:39:25,spid66,Unknown,Policy 'PGGM SQL - Password Policy' has been violated.,,,,,
11/08/2025 07:39:25,spid66,Unknown,Error: 34052<c/> Severity: 16<c/> State: 1.,,,,,
11/08/2025 06:40:02,spid115,Unknown,Certificaatscript Module dbatools geinstalleerd...,,,,,
```

## File Size Comparison

| Time Period | Error Log Entries | File Size |
|-------------|-------------------|-----------|
| 2 days      | ~254 entries      | ~70 KB    |
| 7 days      | ~887 entries      | ~243 KB   |
| Real data   | 3,687 entries     | ~983 KB   |

## Usage for LLM Analysis

The error log complements DMV data by providing:
- **Security events** - Policy violations, authentication issues
- **Operational events** - Startup, backups, configuration
- **Error context** - Correlate performance issues with errors
- **Compliance data** - Certificate checks, policy enforcement

### Combined Analysis Example

When analyzing SQL Server performance with an LLM, you can now provide:
1. **DMV data** - Query performance, wait stats, execution plans
2. **Error log** - Errors, warnings, operational events during the same time period

This allows for richer analysis like:
- "Did policy violations coincide with performance degradation?"
- "Were there any errors or warnings during the slow query period?"
- "What operational events occurred before the performance spike?"

## Technical Details

### UTF-16 LE Encoding

The error log uses UTF-16 LE (Little Endian) encoding with BOM, which is the standard format for SQL Server ERRORLOG files. This ensures compatibility with SQL Server management tools.

**BOM Verification:**
```bash
od -N 2 -t x1 synthetic_output/sqlserver_log.txt
# Output: 0000000  ff  fe  (correct BOM)
```

### Customization

To modify error log generation behavior, edit [errorlog_generator.py](synthetic_dmv_generator/generators/errorlog_generator.py:1):

- Adjust frequency of policy checks
- Add new error message patterns
- Change severity levels
- Customize certificate messages
- Add database-specific events

## Benefits

1. **Realistic testing data** - Mimic real SQL Server environments
2. **Comprehensive analysis** - Combine performance + operational logs
3. **Format compatibility** - Matches real SQL Server ERRORLOG format
4. **Temporal correlation** - Error log entries align with DMV time periods
5. **Security context** - Include policy violations and compliance events
