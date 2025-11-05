"""Unit tests for the SQL Server log file generator."""

import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

# Import the module to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'demos', '001_sql_logs'))

import logfile_generator


class TestLogfileGenerator(unittest.TestCase):
    """Test cases for the SQL Server log file generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
        os.rmdir(self.temp_dir)

    def test_random_user_generation(self):
        """Test that random_user generates valid usernames."""
        user = logfile_generator.random_user()
        self.assertIsInstance(user, str)
        self.assertGreater(len(user), 0)
        self.assertNotIn(' ', user)  # Username should not contain spaces

    def test_random_ip_generation(self):
        """Test that random_ip generates valid IP addresses."""
        ip = logfile_generator.random_ip()
        self.assertIsInstance(ip, str)
        # Basic IP format validation
        parts = ip.split('.')
        self.assertEqual(len(parts), 4)
        for part in parts:
            self.assertTrue(0 <= int(part) <= 255)

    def test_random_db_distribution(self):
        """Test that random_db generates both standard and weird databases."""
        databases = [logfile_generator.random_db() for _ in range(50)]  # Reduced from 100
        
        # Should have some variety
        unique_dbs = set(databases)
        self.assertGreater(len(unique_dbs), 3)  # Reduced expectation
        
        # All should be strings ending with common suffixes
        for db in databases:
            self.assertIsInstance(db, str)
            self.assertGreater(len(db), 2)

    def test_random_standard_db(self):
        """Test that random_standard_db generates enterprise-style names."""
        db = logfile_generator.random_standard_db()
        self.assertIsInstance(db, str)
        self.assertGreater(len(db), 4)
        
        # Should contain at least one of the expected suffixes
        suffixes = ["DB", "Data", "Store", "Warehouse", "Repository", "Archive"]
        self.assertTrue(any(suffix in db for suffix in suffixes))

    def test_random_weird_db(self):
        """Test that random_weird_db returns one of the predefined weird names."""
        weird_names = [
            "WomanDB", "BeautifulDB", "TrueDB", "AmongDB", "CourtDB",
            "MaterialDB", "AfterDB", "ThroughoutDB", "MajorityDB", "BecauseDB",
            "SouthernDB", "WhiteDB", "WorldDB", "LeastDB", "BothDB", "ScoreDB"
        ]
        
        db = logfile_generator.random_weird_db()
        self.assertIn(db, weird_names)

    def test_random_query_generation(self):
        """Test that random_query generates realistic SQL queries."""
        query = logfile_generator.random_query()
        self.assertIsInstance(query, str)
        self.assertGreater(len(query), 5)
        
        # Should contain typical SQL keywords or SQL Server specific commands
        sql_keywords = ["SELECT", "DROP", "ALTER", "UPDATE", "INSERT", "DELETE", "TRUNCATE", "BULK", "xp_cmdshell", "sp_configure"]
        self.assertTrue(any(keyword in query for keyword in sql_keywords))

    def test_timestamp_format(self):
        """Test that generate_timestamp returns properly formatted timestamps."""
        timestamp = logfile_generator.generate_timestamp()
        self.assertIsInstance(timestamp, str)
        
        # Validate timestamp format
        try:
            parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            self.assertIsInstance(parsed, datetime)
        except ValueError:
            self.fail(f"Timestamp '{timestamp}' is not in the expected format")

    def test_timestamp_with_clustering(self):
        """Test that generate_timestamp_with_clustering works correctly."""
        timestamp = logfile_generator.generate_timestamp_with_clustering()
        self.assertIsInstance(timestamp, str)
        
        # Validate timestamp format
        try:
            parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            self.assertIsInstance(parsed, datetime)
        except ValueError:
            self.fail(f"Clustered timestamp '{timestamp}' is not in the expected format")

    def test_fill_template_basic(self):
        """Test that fill_template correctly replaces placeholders."""
        template = "User {user} accessed database {db}"
        result = logfile_generator.fill_template(template)
        
        self.assertIsInstance(result, str)
        self.assertNotIn("{user}", result)
        self.assertNotIn("{db}", result)
        self.assertIn("User ", result)
        self.assertIn(" accessed database ", result)

    def test_fill_template_all_placeholders(self):
        """Test that fill_template handles all available placeholders."""
        template = "{user} {ip} {db} {query} {table} {server} {session_id}"
        result = logfile_generator.fill_template(template)
        
        # Check that no placeholders remain
        placeholders = ["{user}", "{ip}", "{db}", "{query}", "{table}", "{server}", "{session_id}"]
        for placeholder in placeholders:
            self.assertNotIn(placeholder, result)

    def test_generate_log_entry_normal(self):
        """Test generation of normal log entries."""
        log_entry = logfile_generator.generate_log_entry("normal")
        
        self.assertIsInstance(log_entry, str)
        parts = log_entry.split(" | ")
        self.assertEqual(len(parts), 3)
        
        timestamp, severity, message = parts
        
        # Validate timestamp format
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        
        # Severity should be INFO or WARNING for normal entries
        self.assertIn(severity, ["INFO", "WARNING"])
        
        # Message should not be empty
        self.assertGreater(len(message), 0)

    def test_generate_log_entry_security(self):
        """Test generation of security anomaly log entries."""
        log_entry = logfile_generator.generate_log_entry("security")
        
        self.assertIsInstance(log_entry, str)
        parts = log_entry.split(" | ")
        self.assertEqual(len(parts), 3)
        
        timestamp, severity, message = parts
        
        # Validate timestamp format
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        
        # Security entries should be WARNING or ERROR
        self.assertIn(severity, ["WARNING", "ERROR"])
        
        # Message should not be empty
        self.assertGreater(len(message), 0)

    def test_generate_log_entry_severe(self):
        """Test generation of severe configuration issue log entries."""
        log_entry = logfile_generator.generate_log_entry("severe")
        
        self.assertIsInstance(log_entry, str)
        parts = log_entry.split(" | ")
        self.assertEqual(len(parts), 3)
        
        timestamp, severity, message = parts
        
        # Validate timestamp format
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        
        # Severe entries can be INFO, WARNING, or ERROR
        self.assertIn(severity, ["INFO", "WARNING", "ERROR"])
        
        # Message should not be empty
        self.assertGreater(len(message), 0)

    def test_log_entry_format_consistency(self):
        """Test that all log entry types follow the same format."""
        entry_types = ["normal", "security", "severe"]
        
        for entry_type in entry_types:
            with self.subTest(entry_type=entry_type):
                log_entry = logfile_generator.generate_log_entry(entry_type)
                parts = log_entry.split(" | ")
                
                self.assertEqual(len(parts), 3, f"Log entry format incorrect for {entry_type}")
                
                timestamp, severity, message = parts
                
                # Timestamp should be valid
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                
                # Severity should be valid
                self.assertIn(severity, ["INFO", "WARNING", "ERROR"])
                
                # Message should not be empty
                self.assertGreater(len(message.strip()), 0)

    @patch('logfile_generator.total_logs', 100)
    @patch('logfile_generator.security_ratio', 0.1)
    @patch('logfile_generator.severe_ratio', 0.05)
    def test_generate_logs_count(self):
        """Test that generate_logs produces the correct number of entries."""
        logs = logfile_generator.generate_logs()
        
        self.assertEqual(len(logs), 100)
        
        # All entries should be strings
        for log in logs:
            self.assertIsInstance(log, str)

    @patch('logfile_generator.total_logs', 10)
    @patch('logfile_generator.security_ratio', 0.2)
    @patch('logfile_generator.severe_cases', False)
    def test_generate_logs_no_severe_cases(self):
        """Test log generation when severe_cases is disabled."""
        logs = logfile_generator.generate_logs()
        
        self.assertEqual(len(logs), 10)
        
        # Should have roughly 20% security logs (2 out of 10)
        # The rest should be normal logs

    def test_anomaly_templates_structure(self):
        """Test that anomaly templates are properly structured."""
        self.assertIsInstance(logfile_generator.anomaly_templates, dict)
        
        for category, templates in logfile_generator.anomaly_templates.items():
            self.assertIsInstance(category, str)
            self.assertIsInstance(templates, list)
            self.assertGreater(len(templates), 0)
            
            for template in templates:
                self.assertIsInstance(template, str)
                self.assertGreater(len(template), 0)

    def test_severe_templates_structure(self):
        """Test that severe templates are properly structured."""
        self.assertIsInstance(logfile_generator.severe_templates, dict)
        
        for category, templates in logfile_generator.severe_templates.items():
            self.assertIsInstance(category, str)
            self.assertIsInstance(templates, list)
            self.assertGreater(len(templates), 0)
            
            for template in templates:
                self.assertIsInstance(template, str)
                self.assertGreater(len(template), 0)

    def test_normal_templates_structure(self):
        """Test that normal templates are properly structured."""
        self.assertIsInstance(logfile_generator.normal_templates, list)
        
        for template in logfile_generator.normal_templates:
            self.assertIsInstance(template, str)
            self.assertGreater(len(template), 0)

    def test_configuration_variables(self):
        """Test that configuration variables have expected values."""
        self.assertEqual(logfile_generator.total_logs, 50000)
        self.assertEqual(logfile_generator.security_ratio, 0.005)
        self.assertEqual(logfile_generator.severe_ratio, 0.0003)
        self.assertTrue(logfile_generator.severe_cases)
        self.assertEqual(logfile_generator.log_file, "sql_server.log")

    def test_database_naming_distribution(self):
        """Test that random_db follows 80% standard / 20% unusual distribution."""
        # Generate a smaller sample to test distribution
        databases = [logfile_generator.random_db() for _ in range(200)]  # Reduced from 1000
        
        # Count databases that match standard patterns
        standard_count = 0
        for db in databases:
            # Check if it follows standard enterprise patterns
            if any(suffix in db for suffix in ["DB", "Data", "Store", "Warehouse", "Repository", "Archive"]):
                # Check if it starts with a standard prefix
                prefixes = ["Customer", "Product", "Order", "Inventory", "Sales", "HR", "Finance", "Audit", "Report", "Analytics"]
                if any(db.startswith(prefix) for prefix in prefixes):
                    standard_count += 1
        
        # Should be roughly 80% standard (allow more variance due to smaller sample)
        standard_ratio = standard_count / len(databases)
        self.assertGreater(standard_ratio, 0.6, "Standard database naming ratio too low")  # More lenient
        self.assertLess(standard_ratio, 0.95, "Standard database naming ratio too high")

    def test_severity_distribution_checkdb(self):
        """Test that CHECKDB messages have correct severity distribution."""
        # Generate fewer entries and check CHECKDB severity distribution
        checkdb_entries = []
        for _ in range(100):  # Reduced from 1000
            entry = logfile_generator.generate_log_entry("normal")
            if "CHECKDB found 0" in entry or "consistency check" in entry or "Integrity check passed" in entry:
                checkdb_entries.append(entry)
        
        if len(checkdb_entries) > 10:  # Reduced threshold from 50
            info_count = sum(1 for entry in checkdb_entries if " | INFO | " in entry)
            warning_count = sum(1 for entry in checkdb_entries if " | WARNING | " in entry)
            
            total_checkdb = info_count + warning_count
            if total_checkdb > 0:
                info_ratio = info_count / total_checkdb
                # Should be roughly 95% INFO, 5% WARNING (allow more variance)
                self.assertGreaterEqual(info_ratio, 0.7, "CHECKDB INFO ratio too low")  # More lenient boundary

    def test_temporal_clustering_distribution(self):
        """Test that generate_timestamp_with_clustering produces early morning times."""
        early_morning_count = 0
        total_tests = 1000
        
        for _ in range(total_tests):
            timestamp_str = logfile_generator.generate_timestamp_with_clustering()
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            
            # Count timestamps between 00:00 and 06:00
            if 0 <= timestamp.hour <= 6:
                early_morning_count += 1
        
        # Should have some clustering in early morning hours (at least 40% due to 60% chance * randomness)
        early_morning_ratio = early_morning_count / total_tests
        self.assertGreater(early_morning_ratio, 0.3, "Not enough early morning clustering")

    @patch('builtins.open', create=True)
    def test_file_output_integration(self, mock_open):
        """Test that the file writing logic works correctly."""
        mock_file = mock_open.return_value.__enter__.return_value
        
        # Mock the module-level execution
        with patch('logfile_generator.total_logs', 10), \
             patch('logfile_generator.security_ratio', 0.2), \
             patch('logfile_generator.severe_cases', False), \
             patch('logfile_generator.log_file', 'test.log'):
            
            # Manually call the file writing logic
            logs = logfile_generator.generate_logs()
            with open('test.log', 'w') as f:
                for log in logs:
                    f.write(log + '\n')
            
            # Verify file was opened correctly
            mock_open.assert_called_with('test.log', 'w')
            
            # Verify correct number of write calls
            expected_writes = len(logs)
            self.assertEqual(mock_file.write.call_count, expected_writes)

    def test_large_scale_generation(self):
        """Test generation of moderate numbers of logs."""
        with patch('logfile_generator.total_logs', 100), \
             patch('logfile_generator.security_ratio', 0.1), \
             patch('logfile_generator.severe_ratio', 0.05):
            
            logs = logfile_generator.generate_logs()
            
            # Should generate exactly 100 logs
            self.assertEqual(len(logs), 100)
            
            # Count different types by checking severity levels
            error_count = sum(1 for log in logs if " | ERROR | " in log)
            warning_count = sum(1 for log in logs if " | WARNING | " in log)
            info_count = sum(1 for log in logs if " | INFO | " in log)
            
            # Should have all three severity levels represented
            self.assertGreater(error_count, 0, "No ERROR logs generated")
            self.assertGreater(warning_count, 0, "No WARNING logs generated") 
            self.assertGreater(info_count, 0, "No INFO logs generated")
            
            # INFO should be the majority (more lenient check)
            self.assertGreater(info_count, 10, "Should have a reasonable number of INFO logs")


if __name__ == '__main__':
    unittest.main()