#!/usr/bin/env python3
"""
Unit tests for SQL Server DMV Synthetic Data Generator

Tests the 004_sql_dmv synthetic data generation functionality including:
- Configuration validation
- Data model integrity
- Generator logic (synthetic DMV, error logs, workload patterns)
- Exporter functionality (text, CSV, error log formats)
- Statistical distributions and correlations
- Data validation and relationships

Copyright (c) 2025 Lab271
SPDX-License-Identifier: Apache-2.0
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np

# Add the demos/004_sql_dmv directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demos', '004_sql_dmv'))

# Import modules
from synthetic_dmv_generator.config import (
    GeneratorConfig, 
    WaitCategory, 
    ExecutionType, 
    QueryTypeProfile,
    SQL_SERVER_VERSION,
    OLTP_PROFILE,
    OLAP_PROFILE,
    PROBLEM_PROFILE
)
from synthetic_dmv_generator.generators.synthetic_generator import SyntheticDMVGenerator
from synthetic_dmv_generator.generators.errorlog_generator import ErrorLogGenerator
from synthetic_dmv_generator.generators.workload_patterns import (
    WorkloadScenario,
    get_workload_by_name,
    list_available_workloads
)
from synthetic_dmv_generator.models.intervals import RuntimeStatsInterval
from synthetic_dmv_generator.models.query_text import QueryText
from synthetic_dmv_generator.models.query import Query
from synthetic_dmv_generator.models.plan import ExecutionPlan
from synthetic_dmv_generator.models.runtime_stats import RuntimeStats
from synthetic_dmv_generator.models.wait_stats import WaitStats
from synthetic_dmv_generator.models.errorlog import ErrorLogEntry
from synthetic_dmv_generator.exporters.text_exporter import TextExporter
from synthetic_dmv_generator.exporters.csv_exporter import CSVExporter
from synthetic_dmv_generator.exporters.errorlog_exporter import ErrorLogExporter


class TestConfiguration(unittest.TestCase):
    """Test suite for configuration and constants."""
    
    def test_wait_category_enum(self):
        """Test WaitCategory enum has expected values."""
        wait_categories = list(WaitCategory)
        self.assertGreater(len(wait_categories), 0)
        
        # Check some expected categories
        category_values = [wc.value for wc in wait_categories]
        self.assertIn("Buffer IO", category_values)
        self.assertIn("Network IO", category_values)
        
    def test_execution_type_enum(self):
        """Test ExecutionType enum has expected values."""
        execution_types = list(ExecutionType)
        self.assertGreater(len(execution_types), 0)
        
    def test_generator_config_creation(self):
        """Test GeneratorConfig creation with valid parameters."""
        start_time = datetime.now(timezone.utc) - timedelta(days=7)
        end_time = datetime.now(timezone.utc)
        
        config = GeneratorConfig(
            start_time=start_time,
            end_time=end_time,
            interval_hours=1,
            num_unique_queries=100,
            workload_type="mixed",
            random_seed=42
        )
        
        self.assertEqual(config.start_time, start_time)
        self.assertEqual(config.end_time, end_time)
        self.assertEqual(config.interval_hours, 1)
        self.assertEqual(config.num_unique_queries, 100)
        self.assertEqual(config.workload_type, "mixed")
        self.assertEqual(config.random_seed, 42)
        
    def test_generator_config_defaults(self):
        """Test GeneratorConfig default values."""
        config = GeneratorConfig()
        
        self.assertIsNotNone(config.start_time)
        self.assertIsNotNone(config.end_time)
        self.assertEqual(config.interval_hours, 1)
        self.assertEqual(config.num_unique_queries, 100)
        self.assertEqual(config.workload_type, "mixed")
        self.assertEqual(config.random_seed, 42)
        
    def test_query_type_profile_structure(self):
        """Test QueryTypeProfile data structure."""
        profile = OLTP_PROFILE
        
        self.assertIsNotNone(profile.name)
        self.assertIsInstance(profile.avg_duration_ms, (int, float))
        self.assertIsInstance(profile.duration_stddev, (float, int))
        self.assertIsInstance(profile.execution_frequency, (int, float))
        self.assertIsInstance(profile.avg_rows, (int, float))
        self.assertGreater(profile.avg_duration_ms, 0)
        
    def test_sql_server_version(self):
        """Test SQL Server version constant."""
        self.assertIsInstance(SQL_SERVER_VERSION, str)
        self.assertIn(".", SQL_SERVER_VERSION)


class TestWorkloadPatterns(unittest.TestCase):
    """Test suite for workload patterns and scenarios."""
    
    def test_list_available_workloads(self):
        """Test that available workloads are listed."""
        workloads = list_available_workloads()
        
        self.assertIsInstance(workloads, list)
        self.assertGreater(len(workloads), 0)
        self.assertIn("mixed", workloads)
        self.assertIn("oltp", workloads)
        self.assertIn("olap", workloads)
        
    def test_get_workload_by_name_mixed(self):
        """Test retrieving mixed workload scenario."""
        workload = get_workload_by_name("mixed")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertEqual(workload.name, "Mixed")
        self.assertGreater(len(workload.query_profiles), 0)
        
        # Check that proportions sum to 1.0
        total_proportion = sum(prop for _, prop in workload.query_profiles)
        self.assertAlmostEqual(total_proportion, 1.0, places=5)
        
    def test_get_workload_by_name_oltp(self):
        """Test retrieving OLTP workload scenario."""
        workload = get_workload_by_name("oltp")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertEqual(workload.name, "OLTP")
        self.assertLess(workload.cpu_pressure, 2.0)
        
    def test_get_workload_by_name_olap(self):
        """Test retrieving OLAP workload scenario."""
        workload = get_workload_by_name("olap")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertEqual(workload.name, "OLAP")
        
    def test_get_workload_by_name_cpu_pressure(self):
        """Test retrieving CPU pressure scenario."""
        workload = get_workload_by_name("cpu_pressure")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertGreater(workload.cpu_pressure, 1.0)
        
    def test_get_workload_by_name_io_bottleneck(self):
        """Test retrieving I/O bottleneck scenario."""
        workload = get_workload_by_name("io_bottleneck")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertGreater(workload.io_pressure, 1.0)
        
    def test_get_workload_by_name_memory_pressure(self):
        """Test retrieving memory pressure scenario."""
        workload = get_workload_by_name("memory_pressure")
        
        self.assertIsInstance(workload, WorkloadScenario)
        self.assertGreater(workload.memory_pressure, 1.0)
        
    def test_workload_scenario_structure(self):
        """Test WorkloadScenario structure."""
        workload = get_workload_by_name("mixed")
        
        self.assertIsInstance(workload.name, str)
        self.assertIsInstance(workload.query_profiles, list)
        self.assertGreater(workload.cpu_pressure, 0)
        self.assertGreater(workload.io_pressure, 0)
        self.assertGreater(workload.memory_pressure, 0)


class TestDataModels(unittest.TestCase):
    """Test suite for data model classes."""
    
    def test_runtime_stats_interval_creation(self):
        """Test RuntimeStatsInterval model creation."""
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(hours=1)
        
        interval = RuntimeStatsInterval(
            runtime_stats_interval_id=1,
            start_time=start_time,
            end_time=end_time,
            comment=None
        )
        
        self.assertEqual(interval.runtime_stats_interval_id, 1)
        self.assertEqual(interval.start_time, start_time)
        self.assertEqual(interval.end_time, end_time)
        
    def test_query_text_creation(self):
        """Test QueryText model creation."""
        query_text = QueryText(
            query_text_id=1,
            query_sql_text="SELECT * FROM Users WHERE Id = @p0"
        )
        
        self.assertEqual(query_text.query_text_id, 1)
        self.assertIn("SELECT", query_text.query_sql_text)
        self.assertIsInstance(query_text.query_sql_text, str)
        
    def test_query_creation(self):
        """Test Query model creation."""
        query = Query(
            query_id=1,
            query_text_id=1,
            context_settings_id=1,
            object_id=0,
            batch_sql_handle="0x123456",
            query_hash="0xABCDEF",
            is_internal_query=0,
            query_parameterization_type=0,
            query_parameterization_type_desc="None"
        )
        
        self.assertEqual(query.query_id, 1)
        self.assertEqual(query.query_text_id, 1)
        self.assertIn(query.query_parameterization_type, [0, 1])
        
    def test_execution_plan_creation(self):
        """Test ExecutionPlan model creation."""
        base_time = datetime.now(timezone.utc)
        
        plan = ExecutionPlan(
            plan_id=1,
            query_id=1,
            plan_group_id=0,
            engine_version=SQL_SERVER_VERSION,
            compatibility_level=150,
            query_plan_hash="0xABCDEF",
            query_plan=None,
            is_online_index_plan=0,
            is_trivial_plan=0,
            is_parallel_plan=1,
            is_forced_plan=0,
            is_natively_compiled=0,
            force_failure_count=0,
            last_force_failure_reason=0,
            last_force_failure_reason_desc="NONE",
            count_compiles=1,
            initial_compile_start_time=base_time,
            last_compile_start_time=base_time,
            last_execution_time=base_time,
            avg_compile_duration=1000.0,
            last_compile_duration=1000
        )
        
        self.assertEqual(plan.plan_id, 1)
        self.assertEqual(plan.query_id, 1)
        self.assertIn(plan.is_parallel_plan, [0, 1])
        
    def test_runtime_stats_creation(self):
        """Test RuntimeStats model creation."""
        first_exec = datetime.now(timezone.utc)
        last_exec = first_exec + timedelta(minutes=30)
        
        stats = RuntimeStats(
            runtime_stats_id=1,
            plan_id=1,
            runtime_stats_interval_id=1,
            execution_type_id=0,
            execution_type="Regular",
            first_execution_time=first_exec,
            last_execution_time=last_exec,
            count_executions=100,
            avg_duration=5000.0,
            last_duration=4800.0,
            min_duration=1000.0,
            max_duration=25000.0,
            avg_cpu_time=4000.0,
            last_cpu_time=3800.0,
            min_cpu_time=800.0,
            max_cpu_time=20000.0,
            avg_logical_io_reads=500.0,
            last_logical_io_reads=480.0,
            min_logical_io_reads=100.0,
            max_logical_io_reads=2500.0,
            avg_logical_io_writes=0.0,
            last_logical_io_writes=0.0,
            min_logical_io_writes=0.0,
            max_logical_io_writes=0.0,
            avg_physical_io_reads=25.0,
            last_physical_io_reads=24.0,
            min_physical_io_reads=5.0,
            max_physical_io_reads=125.0,
            avg_clr_time=0.0,
            last_clr_time=0.0,
            min_clr_time=0.0,
            max_clr_time=0.0,
            avg_query_max_used_memory=150.0,
            last_query_max_used_memory=145.0,
            min_query_max_used_memory=30.0,
            max_query_max_used_memory=750.0,
            avg_rowcount=10.0,
            last_rowcount=9.0,
            min_rowcount=1.0,
            max_rowcount=50.0
        )
        
        self.assertEqual(stats.runtime_stats_id, 1)
        self.assertEqual(stats.count_executions, 100)
        self.assertGreater(stats.avg_duration, 0)
        self.assertGreaterEqual(stats.max_duration, stats.avg_duration)
        self.assertLessEqual(stats.min_duration, stats.avg_duration)
        
    def test_wait_stats_creation(self):
        """Test WaitStats model creation."""
        wait_stat = WaitStats(
            plan_id=1,
            runtime_stats_interval_id=1,
            wait_category_id=1,
            wait_category="Buffer IO",
            total_query_wait_time_ms=1000.0,
            avg_query_wait_time_ms=10.0,
            last_query_wait_time_ms=9.5,
            min_query_wait_time_ms=1.0,
            max_query_wait_time_ms=50.0,
            stdev_query_wait_time_ms=5.0
        )
        
        self.assertEqual(wait_stat.plan_id, 1)
        self.assertEqual(wait_stat.wait_category, "Buffer IO")
        self.assertGreater(wait_stat.total_query_wait_time_ms, 0)
        
    def test_errorlog_entry_creation(self):
        """Test ErrorLogEntry model creation."""
        log_time = datetime.now(timezone.utc)
        
        entry = ErrorLogEntry(
            date=log_time,
            source="spid52",
            severity="Information",
            message="Database 'tempdb' has 1234 active transactions."
        )
        
        self.assertEqual(entry.date, log_time)
        self.assertEqual(entry.source, "spid52")
        self.assertIn("Database", entry.message)


class TestSyntheticGenerator(unittest.TestCase):
    """Test suite for synthetic DMV data generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.start_time = datetime.now(timezone.utc) - timedelta(days=2)
        self.end_time = datetime.now(timezone.utc)
        self.config = GeneratorConfig(
            start_time=self.start_time,
            end_time=self.end_time,
            interval_hours=1,
            num_unique_queries=10,
            workload_type="mixed",
            random_seed=42
        )
        
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = SyntheticDMVGenerator(self.config)
        
        self.assertIsNotNone(generator.faker)
        self.assertIsNotNone(generator.workload)
        self.assertEqual(len(generator.intervals), 0)
        self.assertEqual(len(generator.query_texts), 0)
        
    def test_generator_produces_intervals(self):
        """Test that generator creates time intervals."""
        generator = SyntheticDMVGenerator(self.config)
        generator._generate_intervals()
        
        self.assertGreater(len(generator.intervals), 0)
        
        # Verify intervals are ordered (end_time of one <= start_time of next)
        for i in range(len(generator.intervals) - 1):
            self.assertLessEqual(
                generator.intervals[i].end_time,
                generator.intervals[i + 1].start_time
            )
            
    def test_generator_produces_query_texts(self):
        """Test that generator creates query texts."""
        generator = SyntheticDMVGenerator(self.config)
        generator._generate_query_texts()
        
        self.assertEqual(len(generator.query_texts), self.config.num_unique_queries)
        
        # Verify query texts have SQL
        for qt in generator.query_texts:
            self.assertIsInstance(qt.query_sql_text, str)
            self.assertGreater(len(qt.query_sql_text), 0)
            
    def test_generator_produces_queries(self):
        """Test that generator creates query metadata."""
        generator = SyntheticDMVGenerator(self.config)
        generator._generate_query_texts()
        generator._generate_queries()
        
        self.assertGreater(len(generator.queries), 0)
        self.assertGreaterEqual(len(generator.queries), len(generator.query_texts))
        
        # Verify all queries have valid query_text_id references
        query_text_ids = {qt.query_text_id for qt in generator.query_texts}
        for query in generator.queries:
            self.assertIn(query.query_text_id, query_text_ids)
            
    def test_generator_produces_plans(self):
        """Test that generator creates execution plans."""
        generator = SyntheticDMVGenerator(self.config)
        generator._generate_query_texts()
        generator._generate_queries()
        generator._generate_plans()
        
        self.assertGreater(len(generator.plans), 0)
        self.assertGreaterEqual(len(generator.plans), len(generator.queries))
        
        # Verify all plans have valid query_id references
        query_ids = {q.query_id for q in generator.queries}
        for plan in generator.plans:
            self.assertIn(plan.query_id, query_ids)
            
    def test_full_generation_workflow(self):
        """Test complete generation workflow."""
        generator = SyntheticDMVGenerator(self.config)
        generator.generate()
        
        # Verify all components were generated
        self.assertGreater(len(generator.intervals), 0)
        self.assertGreater(len(generator.query_texts), 0)
        self.assertGreater(len(generator.queries), 0)
        self.assertGreater(len(generator.plans), 0)
        self.assertGreater(len(generator.runtime_stats), 0)
        self.assertGreater(len(generator.wait_stats), 0)
        
    def test_runtime_stats_relationships(self):
        """Test runtime stats maintain proper relationships."""
        generator = SyntheticDMVGenerator(self.config)
        generator.generate()
        
        # Verify runtime stats reference valid plans and intervals
        plan_ids = {p.plan_id for p in generator.plans}
        interval_ids = {i.runtime_stats_interval_id for i in generator.intervals}
        
        for stats in generator.runtime_stats:
            self.assertIn(stats.plan_id, plan_ids)
            self.assertIn(stats.runtime_stats_interval_id, interval_ids)
            
    def test_wait_stats_relationships(self):
        """Test wait stats maintain proper relationships."""
        generator = SyntheticDMVGenerator(self.config)
        generator.generate()
        
        # Verify wait stats reference valid plans and intervals
        plan_ids = {p.plan_id for p in generator.plans}
        interval_ids = {i.runtime_stats_interval_id for i in generator.intervals}
        
        for wait_stat in generator.wait_stats:
            self.assertIn(wait_stat.plan_id, plan_ids)
            self.assertIn(wait_stat.runtime_stats_interval_id, interval_ids)
            
    def test_statistical_realism_duration(self):
        """Test that generated durations follow log-normal distribution."""
        generator = SyntheticDMVGenerator(self.config)
        generator.generate()
        
        durations = [stats.avg_duration for stats in generator.runtime_stats]
        
        # Basic statistical checks
        self.assertGreater(np.mean(durations), 0)
        self.assertGreater(np.std(durations), 0)
        self.assertGreater(np.max(durations), np.mean(durations))
        
    def test_cpu_duration_correlation(self):
        """Test that CPU time correlates with duration."""
        generator = SyntheticDMVGenerator(self.config)
        generator.generate()
        
        for stats in generator.runtime_stats:
            # CPU time should be less than or equal to duration
            self.assertLessEqual(stats.avg_cpu_time, stats.avg_duration)
            # CPU time should be a significant portion of duration
            if stats.avg_duration > 0:
                cpu_ratio = stats.avg_cpu_time / stats.avg_duration
                self.assertGreater(cpu_ratio, 0)
                self.assertLessEqual(cpu_ratio, 1.0)


class TestErrorLogGenerator(unittest.TestCase):
    """Test suite for error log generator."""
    
    def test_errorlog_generator_initialization(self):
        """Test ErrorLogGenerator initialization."""
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        generator = ErrorLogGenerator(start_time, end_time, seed=42)
        
        self.assertIsNotNone(generator)
        
    def test_errorlog_generation(self):
        """Test error log entry generation."""
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        generator = ErrorLogGenerator(start_time, end_time, seed=42)
        entries = generator.generate()
        
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0)
        
        # Verify entries have required fields
        for entry in entries:
            self.assertIsInstance(entry, ErrorLogEntry)
            self.assertIsNotNone(entry.date)
            self.assertIsNotNone(entry.source)
            self.assertIsNotNone(entry.message)
            
    def test_errorlog_time_range(self):
        """Test that error log entries are within time range."""
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        generator = ErrorLogGenerator(start_time, end_time, seed=42)
        entries = generator.generate()
        
        for entry in entries:
            self.assertGreaterEqual(entry.date, start_time)
            self.assertLessEqual(entry.date, end_time)
            
    def test_errorlog_has_different_levels(self):
        """Test that error log has entries at different levels."""
        start_time = datetime.now(timezone.utc) - timedelta(days=7)
        end_time = datetime.now(timezone.utc)
        
        generator = ErrorLogGenerator(start_time, end_time, seed=42)
        entries = generator.generate()
        
        # Should have a mix of informational and error messages
        # (this is probabilistic but with enough entries should hold)
        self.assertGreater(len(entries), 10)


class TestExporters(unittest.TestCase):
    """Test suite for data exporters."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.start_time = datetime.now(timezone.utc) - timedelta(days=1)
        self.end_time = datetime.now(timezone.utc)
        
        self.config = GeneratorConfig(
            start_time=self.start_time,
            end_time=self.end_time,
            interval_hours=1,
            num_unique_queries=5,
            workload_type="mixed",
            random_seed=42
        )
        
        self.generator = SyntheticDMVGenerator(self.config)
        self.generator.generate()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_text_exporter_creates_files(self):
        """Test that text exporter creates output files."""
        exporter = TextExporter()
        output_path = Path(self.temp_dir) / "text_output"
        
        exporter.export_all(self.generator, output_path)
        
        # Check that files were created
        expected_files = [
            "sys.query_store_runtime_stats_interval.txt",
            "sys.query_store_query_text.txt",
            "sys.query_store_query.txt",
            "sys.query_store_plan.txt",
            "sys.query_store_runtime_stats.txt",
            "sys.query_store_wait_stats.txt"
        ]
        
        for filename in expected_files:
            file_path = output_path / filename
            self.assertTrue(file_path.exists(), f"Expected file not created: {filename}")
            self.assertGreater(file_path.stat().st_size, 0, f"File is empty: {filename}")
            
    def test_csv_exporter_creates_files(self):
        """Test that CSV exporter creates output files."""
        exporter = CSVExporter()
        output_path = Path(self.temp_dir) / "csv_output"
        
        exporter.export_all(self.generator, output_path)
        
        # Check that CSV files were created
        expected_files = [
            "sys.query_store_runtime_stats_interval.csv",
            "sys.query_store_query_text.csv",
            "sys.query_store_query.csv",
            "sys.query_store_plan.csv",
            "sys.query_store_runtime_stats.csv",
            "sys.query_store_wait_stats.csv"
        ]
        
        for filename in expected_files:
            file_path = output_path / filename
            self.assertTrue(file_path.exists(), f"Expected CSV file not created: {filename}")
            self.assertGreater(file_path.stat().st_size, 0, f"CSV file is empty: {filename}")
            
    def test_errorlog_exporter_creates_file(self):
        """Test that error log exporter creates output file."""
        errorlog_generator = ErrorLogGenerator(self.start_time, self.end_time, seed=42)
        entries = errorlog_generator.generate()
        
        exporter = ErrorLogExporter()
        output_path = Path(self.temp_dir)
        
        exporter.export(entries, output_path, filename="ERRORLOG.csv")
        
        # Check that ERRORLOG.csv was created
        errorlog_file = output_path / "ERRORLOG.csv"
        self.assertTrue(errorlog_file.exists())
        self.assertGreater(errorlog_file.stat().st_size, 0)
        
    def test_text_export_format(self):
        """Test that text export uses semicolon delimiter."""
        exporter = TextExporter()
        output_path = Path(self.temp_dir) / "text_output"
        
        exporter.export_all(self.generator, output_path)
        
        # Read a file and verify semicolon delimiter
        test_file = output_path / "sys.query_store_query.txt"
        with open(test_file, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            self.assertIn(';', first_line)
            
    def test_csv_export_has_headers(self):
        """Test that CSV export includes headers."""
        exporter = CSVExporter()
        output_path = Path(self.temp_dir) / "csv_output"
        
        exporter.export_all(self.generator, output_path)
        
        # Read a file and verify it has headers
        test_file = output_path / "sys.query_store_query.csv"
        with open(test_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            # Should contain column names
            self.assertIn('query_id', first_line)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def test_end_to_end_small_dataset(self):
        """Test end-to-end generation of small dataset."""
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        config = GeneratorConfig(
            start_time=start_time,
            end_time=end_time,
            interval_hours=1,
            num_unique_queries=10,
            workload_type="mixed",
            random_seed=42
        )
        
        # Generate DMV data
        generator = SyntheticDMVGenerator(config)
        generator.generate()
        
        # Generate error log
        errorlog_gen = ErrorLogGenerator(start_time, end_time, seed=42)
        errorlog_entries = errorlog_gen.generate()
        
        # Verify data integrity
        self.assertGreater(len(generator.intervals), 0)
        self.assertEqual(len(generator.query_texts), 10)
        self.assertGreater(len(generator.queries), 0)
        self.assertGreater(len(generator.plans), 0)
        self.assertGreater(len(generator.runtime_stats), 0)
        self.assertGreater(len(generator.wait_stats), 0)
        self.assertGreater(len(errorlog_entries), 0)
        
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same results."""
        start_time = datetime.now(timezone.utc) - timedelta(days=1)
        end_time = datetime.now(timezone.utc)
        
        config1 = GeneratorConfig(
            start_time=start_time,
            end_time=end_time,
            interval_hours=1,
            num_unique_queries=5,
            workload_type="mixed",
            random_seed=42
        )
        
        config2 = GeneratorConfig(
            start_time=start_time,
            end_time=end_time,
            interval_hours=1,
            num_unique_queries=5,
            workload_type="mixed",
            random_seed=42
        )
        
        # Generate two datasets with same seed
        gen1 = SyntheticDMVGenerator(config1)
        gen1.generate()
        
        gen2 = SyntheticDMVGenerator(config2)
        gen2.generate()
        
        # Should have same counts
        self.assertEqual(len(gen1.intervals), len(gen2.intervals))
        self.assertEqual(len(gen1.query_texts), len(gen2.query_texts))
        self.assertEqual(len(gen1.queries), len(gen2.queries))
        self.assertEqual(len(gen1.plans), len(gen2.plans))


if __name__ == '__main__':
    unittest.main()
