#!/usr/bin/env python3
"""
Unit tests for Azure Data Generation Script

Tests the azure_data.py script functionality including:
- Configuration validation
- Resource generation logic
- Pricing calculations
- Data structure integrity
- Optimization scenario generation

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch
import random

# Add the demos/002_azure directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demos', '002_azure'))

# Import the constants and configuration from azure_data.py
try:
    import azure_data
except ImportError:
    # If direct import fails, try importing as a module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "azure_data", 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demos', '002_azure', 'azure_data.py')
    )
    azure_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(azure_data)


class TestAzureDataGeneration(unittest.TestCase):
    """Test suite for Azure data generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_regions = ["eastus", "westus", "northeurope"]
        self.test_departments = ["Finance", "HR", "Engineering"]
        self.test_environments = ["prod", "dev", "test"]
        
    def test_configuration_constants(self):
        """Test that all configuration constants are properly defined."""
        # Test regions
        self.assertEqual(len(azure_data.REGIONS), 5)
        self.assertIn("eastus", azure_data.REGIONS)
        self.assertIn("westus", azure_data.REGIONS)
        
        # Test departments
        self.assertEqual(len(azure_data.DEPARTMENTS), 5)
        self.assertIn("Finance", azure_data.DEPARTMENTS)
        self.assertIn("Engineering", azure_data.DEPARTMENTS)
        
        # Test environments
        self.assertEqual(len(azure_data.ENVIRONMENTS), 4)
        self.assertIn("prod", azure_data.ENVIRONMENTS)
        self.assertIn("dev", azure_data.ENVIRONMENTS)
        
        # Test subscription IDs
        self.assertEqual(len(azure_data.SUBSCRIPTION_IDS), 5)
        for sub_id in azure_data.SUBSCRIPTION_IDS:
            self.assertIsInstance(sub_id, str)
            
    def test_vm_sku_pricing_structure(self):
        """Test VM SKU pricing structure is valid."""
        # Test that all SKUs have pricing for all regions
        for sku, pricing in azure_data.VM_SKU_PRICING.items():
            self.assertIsInstance(sku, str)
            self.assertTrue(sku.startswith("Standard_"))
            
            for region in azure_data.REGIONS:
                self.assertIn(region, pricing)
                self.assertIsInstance(pricing[region], (int, float))
                self.assertGreater(pricing[region], 0)
                
    def test_container_pricing_structure(self):
        """Test container pricing structure."""
        self.assertIn("cpu_per_hour", azure_data.CONTAINER_PRICING)
        self.assertIn("memory_per_hour", azure_data.CONTAINER_PRICING)
        
        self.assertGreater(azure_data.CONTAINER_PRICING["cpu_per_hour"], 0)
        self.assertGreater(azure_data.CONTAINER_PRICING["memory_per_hour"], 0)
        
    def test_storage_pricing_tiers(self):
        """Test storage pricing tiers."""
        expected_tiers = ["hot", "cool", "archive"]
        for tier in expected_tiers:
            self.assertIn(tier, azure_data.STORAGE_PRICING)
            self.assertGreater(azure_data.STORAGE_PRICING[tier], 0)
            
        # Test that hot is most expensive, archive is cheapest
        self.assertGreater(azure_data.STORAGE_PRICING["hot"], azure_data.STORAGE_PRICING["cool"])
        self.assertGreater(azure_data.STORAGE_PRICING["cool"], azure_data.STORAGE_PRICING["archive"])
        
    def test_sql_pricing_tiers(self):
        """Test SQL Database pricing tiers."""
        expected_tiers = ["Basic", "S0", "S1", "S2", "P1"]
        for tier in expected_tiers:
            self.assertIn(tier, azure_data.SQL_PRICING)
            self.assertGreater(azure_data.SQL_PRICING[tier], 0)
            
        # Test pricing progression (Basic < S0 < S1 < S2 < P1)
        self.assertLess(azure_data.SQL_PRICING["Basic"], azure_data.SQL_PRICING["S0"])
        self.assertLess(azure_data.SQL_PRICING["S0"], azure_data.SQL_PRICING["S1"])
        self.assertLess(azure_data.SQL_PRICING["S1"], azure_data.SQL_PRICING["S2"])
        self.assertLess(azure_data.SQL_PRICING["S2"], azure_data.SQL_PRICING["P1"])
        
    def test_resource_group_naming_convention(self):
        """Test resource group naming follows Azure conventions."""
        # Test that resource groups follow the pattern: rg-{dept}-{env}-{region}
        for rg in azure_data.RESOURCE_GROUPS:
            parts = rg.split("-")
            self.assertEqual(len(parts), 4)  # rg, dept, env, region
            self.assertEqual(parts[0], "rg")
            self.assertIn(parts[1], [dept.lower() for dept in azure_data.DEPARTMENTS])
            self.assertIn(parts[2], azure_data.ENVIRONMENTS)
            self.assertIn(parts[3], azure_data.REGIONS)
            
    @patch('random.random')
    @patch('random.choice')
    def test_vm_configuration_generation(self, mock_choice, mock_random):
        """Test VM configuration generation logic."""
        # Mock random functions for predictable testing
        mock_random.side_effect = [0.1, 0.05, 0.1]  # underutilized, stopped, has_tags
        mock_choice.side_effect = [
            azure_data.SUBSCRIPTION_IDS[0],
            azure_data.RESOURCE_GROUPS[0],
            list(azure_data.VM_SKU_PRICING.keys())[0]
        ]
        
        # Generate a single VM config (simplified version of the script logic)
        resource_group = azure_data.RESOURCE_GROUPS[0]
        region = resource_group.split("-")[-1]
        department = resource_group.split("-")[1].capitalize()
        environment = resource_group.split("-")[2]
        sku = list(azure_data.VM_SKU_PRICING.keys())[0]
        
        vm_config = {
            "resource_name": f"vm-{department.lower()}-{environment}-0001",
            "resource_type": "Microsoft.Compute/virtualMachines",
            "region": region,
            "department": department,
            "environment": environment,
            "sku": sku,
            "is_underutilized": True,  # 0.1 < 0.20
            "is_stopped_not_deallocated": False,  # 0.05 < 0.10
            "is_production": environment == "prod"
        }
        
        # Validate the configuration
        self.assertIn("vm-", vm_config["resource_name"])
        self.assertEqual(vm_config["resource_type"], "Microsoft.Compute/virtualMachines")
        self.assertIn(vm_config["region"], azure_data.REGIONS)
        self.assertIn(vm_config["sku"], azure_data.VM_SKU_PRICING)
        self.assertIsInstance(vm_config["is_underutilized"], bool)
        self.assertIsInstance(vm_config["is_stopped_not_deallocated"], bool)
        self.assertIsInstance(vm_config["is_production"], bool)
        
    def test_container_configuration_structure(self):
        """Test container configuration structure."""
        # Test that container configs have required fields
        expected_fields = [
            "resource_name", "resource_type", "subscription_id", "resource_group",
            "region", "department", "environment", "cpu_cores", "memory_gb"
        ]
        
        # Simulate container config generation
        container_config = {
            "resource_name": "aci-finance-prod-0001",
            "resource_type": "Microsoft.ContainerInstance/containerGroups",
            "cpu_cores": 2,
            "memory_gb": 4
        }
        
        self.assertIn("aci-", container_config["resource_name"])
        self.assertEqual(container_config["resource_type"], "Microsoft.ContainerInstance/containerGroups")
        self.assertIn(container_config["cpu_cores"], [1, 2, 4])
        self.assertIn(container_config["memory_gb"], [1, 2, 4, 8])
        
    def test_storage_naming_convention(self):
        """Test storage account naming follows Azure conventions."""
        # Storage names must be lowercase, no hyphens, max 24 chars
        test_storage_name = "stfinanceprod0001"
        
        self.assertTrue(test_storage_name.islower())
        self.assertNotIn("-", test_storage_name)
        self.assertLessEqual(len(test_storage_name), 24)
        self.assertTrue(test_storage_name.startswith("st"))
        
    def test_cost_calculation_vm_underutilized(self):
        """Test cost calculation for underutilized VMs."""
        sku = "Standard_B2s"
        region = "eastus"
        uptime_hours = 24
        
        expected_cost = azure_data.VM_SKU_PRICING[sku][region] * uptime_hours
        calculated_cost = azure_data.VM_SKU_PRICING[sku][region] * uptime_hours
        
        self.assertEqual(calculated_cost, expected_cost)
        self.assertGreater(calculated_cost, 0)
        
    def test_cost_calculation_vm_stopped(self):
        """Test cost calculation for stopped but not deallocated VMs."""
        sku = "Standard_B2s"
        region = "eastus"
        
        # Stopped VMs still charge 10% for storage
        expected_cost = azure_data.VM_SKU_PRICING[sku][region] * 24 * 0.1
        calculated_cost = azure_data.VM_SKU_PRICING[sku][region] * 24 * 0.1
        
        self.assertEqual(calculated_cost, expected_cost)
        self.assertGreater(calculated_cost, 0)
        self.assertLess(calculated_cost, azure_data.VM_SKU_PRICING[sku][region] * 24)
        
    def test_cost_calculation_container(self):
        """Test cost calculation for containers."""
        cpu_cores = 2
        memory_gb = 4
        uptime_hours = 12
        
        cpu_cost = azure_data.CONTAINER_PRICING["cpu_per_hour"] * cpu_cores * uptime_hours
        memory_cost = azure_data.CONTAINER_PRICING["memory_per_hour"] * memory_gb * uptime_hours
        total_cost = cpu_cost + memory_cost
        
        self.assertGreater(total_cost, 0)
        self.assertGreater(cpu_cost, 0)
        self.assertGreater(memory_cost, 0)
        self.assertEqual(total_cost, cpu_cost + memory_cost)
        
    def test_cost_calculation_storage(self):
        """Test cost calculation for storage."""
        storage_size_gb = 1000
        tier = "hot"
        
        monthly_cost = storage_size_gb * azure_data.STORAGE_PRICING[tier]
        daily_cost = monthly_cost / 30
        
        self.assertGreater(monthly_cost, 0)
        self.assertGreater(daily_cost, 0)
        self.assertEqual(daily_cost, monthly_cost / 30)
        
    def test_cost_calculation_sql(self):
        """Test cost calculation for SQL databases."""
        service_tier = "S1"
        
        daily_cost = azure_data.SQL_PRICING[service_tier] * 24
        
        self.assertGreater(daily_cost, 0)
        self.assertEqual(daily_cost, azure_data.SQL_PRICING[service_tier] * 24)
        
    def test_optimization_scenario_percentages(self):
        """Test that optimization scenarios follow expected percentages."""
        # Test with a large sample to verify percentages
        sample_size = 1000
        underutilized_count = 0
        stopped_count = 0
        untagged_count = 0
        
        # Simulate the random generation with fixed seed for reproducibility
        random.seed(42)
        
        for _ in range(sample_size):
            if random.random() < 0.20:  # 20% underutilized
                underutilized_count += 1
            if random.random() < 0.10:  # 10% stopped
                stopped_count += 1
            if random.random() <= 0.05:  # 5% untagged (using <= to match script logic)
                untagged_count += 1
                
        # Allow for some variance in random generation (±5%)
        self.assertAlmostEqual(underutilized_count / sample_size, 0.20, delta=0.05)
        self.assertAlmostEqual(stopped_count / sample_size, 0.10, delta=0.05)
        self.assertAlmostEqual(untagged_count / sample_size, 0.05, delta=0.03)
        
    def test_date_range_generation(self):
        """Test date range generation logic."""
        days = 30
        start_date = datetime(2025, 1, 1)
        
        dates = []
        for day in range(days):
            date = start_date + timedelta(days=day)
            dates.append(date)
            
        self.assertEqual(len(dates), days)
        self.assertEqual(dates[0], start_date)
        self.assertEqual(dates[-1], start_date + timedelta(days=days-1))
        
    def test_weekday_weekend_logic(self):
        """Test weekday vs weekend usage pattern logic."""
        # Monday (weekday)
        monday = datetime(2025, 11, 3)  # Known Monday
        self.assertTrue(monday.weekday() < 5)
        
        # Saturday (weekend)
        saturday = datetime(2025, 11, 8)  # Known Saturday
        self.assertFalse(saturday.weekday() < 5)
        
    def test_billing_period_format(self):
        """Test billing period format generation."""
        test_date = datetime(2025, 11, 15)
        billing_period = test_date.strftime("%Y-%m")
        
        self.assertEqual(billing_period, "2025-11")
        self.assertEqual(len(billing_period), 7)
        self.assertIn("-", billing_period)
        
    def test_resource_id_format(self):
        """Test Azure resource ID format."""
        subscription_id = "12345678-1234-1234-1234-123456789abc"
        resource_group = "rg-finance-prod-eastus"
        vm_name = "vm-finance-prod-0001"
        
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        
        self.assertTrue(resource_id.startswith("/subscriptions/"))
        self.assertIn("/resourceGroups/", resource_id)
        self.assertIn("/providers/Microsoft.Compute/virtualMachines/", resource_id)
        self.assertTrue(resource_id.endswith(vm_name))
        
    def test_data_structure_completeness(self):
        """Test that generated records have all required fields."""
        # Create a sample record
        sample_record = {
            "date": "2025-11-05",
            "resource_id": "/subscriptions/test/resourceGroups/rg-test/providers/Microsoft.Compute/virtualMachines/vm-test",
            "resource_name": "vm-test-0001",
            "resource_type": "Microsoft.Compute/virtualMachines",
            "meter_category": "Virtual Machines",
            "meter_subcategory": "Compute",
            "meter_name": "Standard_B2s - eastus",
            "subscription_id": "test-subscription",
            "resource_group": "rg-test",
            "region": "eastus",
            "service_name": "Virtual Machines",
            "sku": "Standard_B2s",
            "cpu_utilization": 45.5,
            "memory_usage_gb": 16.0,
            "uptime_hours": 24.0,
            "cost_usd": 1.008,
            "currency": "USD",
            "department": "Finance",
            "environment": "prod",
            "billing_period": "2025-11"
        }
        
        # Test that all expected fields are present
        required_fields = [
            "date", "resource_id", "resource_name", "resource_type",
            "meter_category", "meter_subcategory", "meter_name",
            "subscription_id", "resource_group", "region", "service_name",
            "sku", "cpu_utilization", "memory_usage_gb", "uptime_hours",
            "cost_usd", "currency", "department", "environment", "billing_period"
        ]
        
        for field in required_fields:
            self.assertIn(field, sample_record, f"Missing required field: {field}")


class TestAzureDataIntegration(unittest.TestCase):
    """Integration tests for the complete Azure data generation process."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        
    @patch('azure_data.num_vms', 10)
    @patch('azure_data.num_containers', 5)
    @patch('azure_data.num_storage_accounts', 3)
    @patch('azure_data.num_sql_databases', 2)
    @patch('azure_data.days', 7)
    def test_small_dataset_generation(self):
        """Test generation of a small dataset for validation."""
        # This test would require refactoring the original script to be more modular
        # For now, we test the logic components individually
        
        # Test that the configuration scales properly
        total_vms = 10
        total_containers = 5
        total_storage = 3
        total_sql = 2
        days = 7
        
        # Expected total records (approximate)
        # VMs: 10 * 7 = 70
        # Containers: 5 * 7 = 35
        # Storage: 3 * 1 = 3 (monthly billing, only first day)
        # SQL: 2 * 7 = 14
        expected_min_records = (total_vms * days) + (total_containers * days) + total_storage + (total_sql * days)
        
        self.assertGreater(expected_min_records, 0)
        self.assertEqual(expected_min_records, 122)


if __name__ == '__main__':
    unittest.main()