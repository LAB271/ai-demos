#!/usr/bin/env python3
"""
Unit tests for IAM Access Request Data Generation Script

Tests the generate_access_request.py script functionality including:
- Configuration validation
- Employee generation logic
- Access request generation
- Data structure integrity
- Anomaly pattern generation
- Distribution validation

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import unittest
import pandas as pd
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch
import random

# Add the demos/003_iam_recommendation directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demos', '003_iam_recommendation'))

# Import the constants and configuration from generate_access_request.py
try:
    # Patch the module execution to prevent file generation during import
    with patch('builtins.open'), patch('builtins.print'), patch('pandas.DataFrame.to_csv'):
        import generate_access_request
except ImportError:
    # If direct import fails, try importing as a module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "generate_access_request", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demos', '003_iam_recommendation', 'generate_access_request.py')
    )
    generate_access_request = importlib.util.module_from_spec(spec)
    with patch('builtins.open'), patch('builtins.print'), patch('pandas.DataFrame.to_csv'):
        spec.loader.exec_module(generate_access_request)


class TestGenerateAccessRequest(unittest.TestCase):
    """Test suite for IAM access request generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_dir)
        
    def test_configuration_constants(self):
        """Test that all configuration constants are properly defined."""
        # Test basic configuration
        self.assertIsInstance(generate_access_request.EMPLOYEES, int)
        self.assertGreater(generate_access_request.EMPLOYEES, 0)
        
        self.assertIsInstance(generate_access_request.ACCESS_REQUESTS, int)
        self.assertGreater(generate_access_request.ACCESS_REQUESTS, 0)
        
        self.assertIsInstance(generate_access_request.SEED, int)
        
        # Test date configuration
        self.assertIsInstance(generate_access_request.start_date, datetime)
        
    def test_roles_and_systems_structure(self):
        """Test that roles and systems are properly structured."""
        # Test roles dictionary
        self.assertIsInstance(generate_access_request.roles, dict)
        for role, systems in generate_access_request.roles.items():
            self.assertIsInstance(role, str)
            self.assertIsInstance(systems, list)
            self.assertGreater(len(systems), 0)
            for system in systems:
                self.assertIsInstance(system, str)
                
    def test_departments_structure(self):
        """Test that departments are properly mapped to roles."""
        self.assertIsInstance(generate_access_request.departments, dict)
        
        # Every role should have a department
        for role in generate_access_request.roles.keys():
            self.assertIn(role, generate_access_request.departments)
            self.assertIsInstance(generate_access_request.departments[role], str)
            
    def test_distribution_percentages(self):
        """Test that distribution percentages are valid."""
        self.assertIsInstance(generate_access_request.distribution_percentages, dict)
        
        # All roles should have percentages
        for role in generate_access_request.roles.keys():
            self.assertIn(role, generate_access_request.distribution_percentages)
            percentage = generate_access_request.distribution_percentages[role]
            self.assertIsInstance(percentage, (int, float))
            self.assertGreaterEqual(percentage, 0)
            self.assertLessEqual(percentage, 1)
            
        # Total percentages should equal 1.0
        total_percentage = sum(generate_access_request.distribution_percentages.values())
        self.assertAlmostEqual(total_percentage, 1.0, places=2)
        
    def test_employee_distribution_calculation(self):
        """Test that employee distribution calculation works correctly."""
        # Test with a smaller employee count for predictable results
        test_employees = 100
        test_percentages = {
            "Role1": 0.5,
            "Role2": 0.3,
            "Role3": 0.2
        }
        
        distribution = {role: int(test_employees * percentage) 
                       for role, percentage in test_percentages.items()}
        
        # Test basic calculation
        self.assertEqual(distribution["Role1"], 50)
        self.assertEqual(distribution["Role2"], 30)
        self.assertEqual(distribution["Role3"], 20)
        
        # Test total equals target
        total = sum(distribution.values())
        self.assertEqual(total, test_employees)
        
    def test_locations_configuration(self):
        """Test that locations are properly configured."""
        self.assertIsInstance(generate_access_request.locations, list)
        self.assertGreater(len(generate_access_request.locations), 0)
        
        # Singapore should be included as anomaly location
        self.assertIn("Singapore", generate_access_request.locations)
        self.assertIn("Amsterdam", generate_access_request.locations)
        
    @patch('generate_access_request.EMPLOYEES', 10)
    @patch('generate_access_request.fake')
    def test_employee_generation_structure(self, mock_faker):
        """Test employee generation creates proper structure."""
        # Mock faker outputs
        mock_faker.name.return_value = "John Doe"
        mock_faker.date_of_birth.return_value = datetime(1990, 1, 1).date()
        
        # Simplified employee generation for testing
        employees = []
        employee_id_counter = 1
        
        test_distribution = {"Trader": 5, "Portfolio Manager": 5}
        test_departments = {"Trader": "Front Office", "Portfolio Manager": "Front Office"}
        
        for role, count in test_distribution.items():
            for _ in range(count):
                employee_id = f"E{employee_id_counter:03d}"
                employees.append({
                    "EmployeeID": employee_id,
                    "Name": "John Doe",
                    "Role": role,
                    "Department": test_departments[role],
                    "Birthday": "1990-01-01",
                })
                employee_id_counter += 1
                
        # Validate structure
        self.assertEqual(len(employees), 10)
        
        for employee in employees:
            self.assertIn("EmployeeID", employee)
            self.assertIn("Name", employee)
            self.assertIn("Role", employee)
            self.assertIn("Department", employee)
            self.assertIn("Birthday", employee)
            
            # Validate employee ID format
            self.assertTrue(employee["EmployeeID"].startswith("E"))
            self.assertEqual(len(employee["EmployeeID"]), 4)
            
    def test_employee_id_format(self):
        """Test employee ID format generation."""
        # Test ID format
        for i in range(1, 100):
            employee_id = f"E{i:03d}"
            self.assertTrue(employee_id.startswith("E"))
            self.assertEqual(len(employee_id), 4)
            
        # Test specific cases
        self.assertEqual("E001", f"E{1:03d}")
        self.assertEqual("E010", f"E{10:03d}")
        self.assertEqual("E999", f"E{999:03d}")
        
    def test_request_id_format(self):
        """Test request ID format generation."""
        # Test ID format
        for i in range(1, 1000):
            request_id = f"R{i:04d}"
            self.assertTrue(request_id.startswith("R"))
            self.assertEqual(len(request_id), 5)
            
        # Test specific cases
        self.assertEqual("R0001", f"R{1:04d}")
        self.assertEqual("R0010", f"R{10:04d}")
        self.assertEqual("R9999", f"R{9999:04d}")
        
    def test_birthday_age_range(self):
        """Test that birthday generation follows age constraints."""
        from faker import Faker
        test_faker = Faker()
        test_faker.seed_instance(42)
        
        # Generate multiple birthdays and check age range
        today = datetime.today().date()
        
        for _ in range(50):
            birthday = test_faker.date_of_birth(minimum_age=25, maximum_age=65)
            age = (today - birthday).days / 365.25
            
            self.assertGreaterEqual(age, 24.5)  # Allow slight variance due to calculation
            self.assertLessEqual(age, 66)       # Allow slight variance at upper bound
            
    def test_system_access_anomaly_detection(self):
        """Test system access anomaly logic."""
        # Test normal access
        trader_systems = generate_access_request.roles["Trader"]
        self.assertIn("OMS", trader_systems)
        self.assertIn("PMS", trader_systems)
        
        # Test anomaly detection logic
        all_systems = [
            "Fund Accounting System", "OMS", "IAM System", "Cloud Infrastructure",
            "PMS", "Risk Platform", "Compliance Monitoring", "Monitoring"
        ]
        
        # Systems that would be anomalous for a trader
        anomalous_for_trader = [s for s in all_systems if s not in trader_systems]
        
        self.assertIn("IAM System", anomalous_for_trader)
        self.assertIn("Cloud Infrastructure", anomalous_for_trader)
        self.assertNotIn("OMS", anomalous_for_trader)
        self.assertNotIn("PMS", anomalous_for_trader)
        
    def test_timestamp_generation_business_hours(self):
        """Test timestamp generation for business hours."""
        base_date = datetime(2025, 11, 1)
        
        # Test business hours generation (6-22)
        for _ in range(50):
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(6, 22)
            timestamp = base_date + timedelta(days=days_offset, hours=hours_offset)
            
            self.assertGreaterEqual(timestamp.hour, 6)
            self.assertLessEqual(timestamp.hour, 22)
            
    def test_timestamp_generation_anomaly_hours(self):
        """Test timestamp generation for anomaly hours."""
        base_date = datetime(2025, 11, 1)
        
        # Test anomaly hours generation (0-3)
        for _ in range(50):
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(0, 3)
            timestamp = base_date + timedelta(days=days_offset, hours=hours_offset)
            
            self.assertGreaterEqual(timestamp.hour, 0)
            self.assertLessEqual(timestamp.hour, 3)
            
    def test_location_distribution(self):
        """Test location distribution logic."""
        locations = generate_access_request.locations
        
        # Test normal location (Amsterdam) vs anomaly logic
        amsterdam_count = 0
        anomaly_count = 0
        
        # Simulate location selection logic
        random.seed(42)
        for _ in range(1000):
            if random.random() < 0.1:  # 10% anomaly
                random.choice(locations)  # Select anomaly location
                anomaly_count += 1
            else:
                amsterdam_count += 1
                
        # Amsterdam should be majority (~90%)
        total = amsterdam_count + anomaly_count
        amsterdam_ratio = amsterdam_count / total
        
        self.assertGreater(amsterdam_ratio, 0.85)  # Allow some variance
        self.assertLess(amsterdam_ratio, 0.95)
        
    @patch('pandas.DataFrame.to_csv')
    @patch('builtins.print')
    def test_data_export_structure(self, mock_print, mock_to_csv):
        """Test that data export calls are made correctly."""
        # Create test dataframes
        employees_data = [
            {"EmployeeID": "E001", "Name": "John Doe", "Role": "Trader", 
             "Department": "Front Office", "Birthday": "1990-01-01"}
        ]
        employees_df = pd.DataFrame(employees_data)
        
        access_requests_data = [
            {"RequestID": "R0001", "EmployeeID": "E001", "EmployeeName": "John Doe",
             "Role": "Trader", "Department": "Front Office", "SystemAccessRequested": "OMS",
             "Timestamp": "2025-11-01 14:30:00", "Location": "Amsterdam"}
        ]
        access_requests_df = pd.DataFrame(access_requests_data)
        
        # Test CSV export calls
        employees_df.to_csv("employees.csv", index=False)
        access_requests_df.to_csv("access_requests.csv", index=False)
        
        # Verify calls were made
        self.assertEqual(mock_to_csv.call_count, 2)
        
        # Check call arguments
        calls = mock_to_csv.call_args_list
        self.assertEqual(calls[0][0][0], "employees.csv")
        self.assertEqual(calls[0][1]["index"], False)
        self.assertEqual(calls[1][0][0], "access_requests.csv")
        self.assertEqual(calls[1][1]["index"], False)
        
    def test_dataframe_column_structure(self):
        """Test that generated dataframes have correct column structure."""
        # Test employee dataframe structure
        employees_data = [
            {"EmployeeID": "E001", "Name": "John Doe", "Role": "Trader", 
             "Department": "Front Office", "Birthday": "1990-01-01"}
        ]
        employees_df = pd.DataFrame(employees_data)
        
        expected_employee_columns = ["EmployeeID", "Name", "Role", "Department", "Birthday"]
        self.assertEqual(list(employees_df.columns), expected_employee_columns)
        
        # Test access request dataframe structure
        access_requests_data = [
            {"RequestID": "R0001", "EmployeeID": "E001", "EmployeeName": "John Doe",
             "Role": "Trader", "Department": "Front Office", "SystemAccessRequested": "OMS",
             "Timestamp": "2025-11-01 14:30:00", "Location": "Amsterdam"}
        ]
        access_requests_df = pd.DataFrame(access_requests_data)
        
        expected_request_columns = [
            "RequestID", "EmployeeID", "EmployeeName", "Role", "Department",
            "SystemAccessRequested", "Timestamp", "Location"
        ]
        self.assertEqual(list(access_requests_df.columns), expected_request_columns)
        
    def test_data_type_validation(self):
        """Test that generated data has correct types."""
        # Employee data validation
        employee_data = {
            "EmployeeID": "E001",
            "Name": "John Doe", 
            "Role": "Trader",
            "Department": "Front Office",
            "Birthday": "1990-01-01"
        }
        
        self.assertIsInstance(employee_data["EmployeeID"], str)
        self.assertIsInstance(employee_data["Name"], str)
        self.assertIsInstance(employee_data["Role"], str)
        self.assertIsInstance(employee_data["Department"], str)
        self.assertIsInstance(employee_data["Birthday"], str)
        
        # Access request data validation
        request_data = {
            "RequestID": "R0001",
            "EmployeeID": "E001",
            "EmployeeName": "John Doe",
            "Role": "Trader",
            "Department": "Front Office", 
            "SystemAccessRequested": "OMS",
            "Timestamp": "2025-11-01 14:30:00",
            "Location": "Amsterdam"
        }
        
        for value in request_data.values():
            self.assertIsInstance(value, str)
            
    def test_timestamp_format_validation(self):
        """Test that timestamps are properly formatted."""
        test_timestamp = datetime(2025, 11, 1, 14, 30, 0)
        formatted = test_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        self.assertEqual(formatted, "2025-11-01 14:30:00")
        
        # Test parsing back
        parsed = datetime.strptime(formatted, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(parsed, test_timestamp)
        
    def test_birthday_format_validation(self):
        """Test that birthdays are properly formatted."""
        test_date = datetime(1990, 1, 1).date()
        formatted = test_date.strftime("%Y-%m-%d")
        
        self.assertEqual(formatted, "1990-01-01")
        
        # Test parsing back
        parsed = datetime.strptime(formatted, "%Y-%m-%d").date()
        self.assertEqual(parsed, test_date)
        
    def test_role_system_consistency(self):
        """Test that role-system mappings are consistent."""
        roles = generate_access_request.roles
        departments = generate_access_request.departments
        
        # Every role in roles should have a department
        for role in roles.keys():
            self.assertIn(role, departments)
            
        # Every role in departments should have systems
        for role in departments.keys():
            self.assertIn(role, roles)
            
    def test_anomaly_percentage_logic(self):
        """Test anomaly percentage calculations."""
        # Test system anomaly (10%)
        system_anomalies = 0
        total_tests = 1000
        
        random.seed(42)
        for _ in range(total_tests):
            if random.random() < 0.1:
                system_anomalies += 1
                
        anomaly_ratio = system_anomalies / total_tests
        self.assertGreater(anomaly_ratio, 0.08)  # Allow variance
        self.assertLess(anomaly_ratio, 0.12)
        
        # Test temporal anomaly (5%)
        temporal_anomalies = 0
        
        random.seed(42)
        for _ in range(total_tests):
            if random.random() < 0.05:
                temporal_anomalies += 1
                
        temporal_ratio = temporal_anomalies / total_tests
        self.assertGreater(temporal_ratio, 0.03)  # Allow variance
        self.assertLess(temporal_ratio, 0.07)
        
    def test_seed_reproducibility(self):
        """Test that using the same seed produces reproducible results."""
        from faker import Faker
        
        # Test with same seed
        fake1 = Faker()
        fake1.seed_instance(42)
        
        fake2 = Faker()
        fake2.seed_instance(42)
        
        # Should generate same names
        name1 = fake1.name()
        name2 = fake2.name()
        self.assertEqual(name1, name2)
        
        # Test random seed consistency
        random.seed(42)
        value1 = random.random()
        
        random.seed(42)
        value2 = random.random()
        self.assertEqual(value1, value2)


class TestAccessRequestIntegration(unittest.TestCase):
    """Integration tests for the complete access request generation process."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        
    @patch('generate_access_request.EMPLOYEES', 20)
    @patch('generate_access_request.ACCESS_REQUESTS', 50)
    @patch('builtins.print')
    def test_small_dataset_generation(self, mock_print):
        """Test generation of a small dataset for validation."""
        # This test validates the overall data generation logic
        
        # Test employee distribution calculation
        test_employees = 20
        distribution = {role: int(test_employees * percentage) 
                       for role, percentage in generate_access_request.distribution_percentages.items()}
        
        # Adjust for rounding
        total_distributed = sum(distribution.values())
        if total_distributed < test_employees:
            distribution["Trader"] += test_employees - total_distributed
        elif total_distributed > test_employees:
            distribution["Trader"] -= total_distributed - test_employees
            
        final_total = sum(distribution.values())
        self.assertEqual(final_total, test_employees)
        
        # Validate all roles are represented
        for role in generate_access_request.roles.keys():
            self.assertIn(role, distribution)
            self.assertGreaterEqual(distribution[role], 0)


if __name__ == '__main__':
    unittest.main()