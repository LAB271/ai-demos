"""Main synthetic DMV data generator."""

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from ..config import GeneratorConfig, SQL_SERVER_VERSION, WaitCategory, ExecutionType
from ..models.intervals import RuntimeStatsInterval
from ..models.query_text import QueryText
from ..models.query import Query
from ..models.plan import ExecutionPlan
from ..models.runtime_stats import RuntimeStats
from ..models.wait_stats import WaitStats
from .base_generator import BaseGenerator
from .workload_patterns import WorkloadScenario, get_workload_by_name


class SyntheticDMVGenerator(BaseGenerator):
    """Main generator for synthetic Query Store DMV data."""

    def __init__(self, config: GeneratorConfig, workload_scenario: WorkloadScenario | None = None):
        """
        Initialize generator.

        Args:
            config: Generator configuration
            workload_scenario: Optional workload scenario (default: based on config.workload_type)
        """
        super().__init__(config)
        self.faker = Faker()
        Faker.seed(config.random_seed)

        # Determine workload scenario
        if workload_scenario is None:
            workload_scenario = get_workload_by_name(config.workload_type)
        self.workload = workload_scenario

        # Storage for generated entities
        self.intervals = []
        self.query_texts = []
        self.queries = []
        self.plans = []
        self.runtime_stats = []
        self.wait_stats = []

    def generate(self):
        """Generate complete synthetic DMV dataset."""
        print(f"Generating synthetic DMV data with {self.workload.name} workload...")
        print(f"  Pressure factors - CPU: {self.workload.cpu_pressure}x, "
              f"I/O: {self.workload.io_pressure}x, Memory: {self.workload.memory_pressure}x")

        # Step 1: Generate time intervals
        print("\n[1/6] Generating time intervals...")
        self._generate_intervals()
        print(f"  Generated {len(self.intervals)} intervals")

        # Step 2: Generate query texts
        print("\n[2/6] Generating query texts...")
        self._generate_query_texts()
        print(f"  Generated {len(self.query_texts)} unique queries")

        # Step 3: Generate queries
        print("\n[3/6] Generating query metadata...")
        self._generate_queries()
        print(f"  Generated {len(self.queries)} query instances")

        # Step 4: Generate execution plans
        print("\n[4/6] Generating execution plans...")
        self._generate_plans()
        print(f"  Generated {len(self.plans)} execution plans")

        # Step 5: Generate runtime statistics
        print("\n[5/6] Generating runtime statistics...")
        self._generate_runtime_statistics()
        print(f"  Generated {len(self.runtime_stats)} runtime stat records")

        # Step 6: Generate wait statistics
        print("\n[6/6] Generating wait statistics...")
        self._generate_wait_statistics()
        print(f"  Generated {len(self.wait_stats)} wait stat records")

        print("\n✓ Generation complete!")

    def _generate_intervals(self):
        """Generate time intervals."""
        interval_tuples = self._generate_time_intervals()
        for interval_id, start_time, end_time in interval_tuples:
            self.intervals.append(RuntimeStatsInterval(interval_id, start_time, end_time, None))

    def _generate_query_texts(self):
        """Generate synthetic SQL query texts."""
        for i in range(self.config.num_unique_queries):
            query_text_id = self.id_gen.next_id("query_text")

            # Assign query type based on workload proportions
            query_profile = self._select_query_profile()

            # Generate SQL based on profile
            sql_text = self._generate_sql_for_profile(query_profile)

            self.query_texts.append(QueryText(query_text_id, sql_text))
            self.relationships.add_query_text(query_text_id)

    def _generate_queries(self):
        """Generate query metadata."""
        for query_text in self.query_texts:
            # Most queries have 1 query instance, some have multiple (parameter variations)
            num_queries = self.rng.integers(1, 3)

            for _ in range(num_queries):
                query_id = self.id_gen.next_id("query")

                query = Query(
                    query_id=query_id,
                    query_text_id=query_text.query_text_id,
                    context_settings_id=1,
                    object_id=0,
                    batch_sql_handle=self._generate_hash(32) if self.rng.random() < 0.5 else None,
                    query_hash=self._generate_hash(16),
                    is_internal_query=0,
                    query_parameterization_type=0 if self.rng.random() < 0.7 else 1,
                    query_parameterization_type_desc="None" if self.rng.random() < 0.7 else "User",
                )

                self.queries.append(query)
                self.relationships.add_query(query_id, query_text.query_text_id)

    def _generate_plans(self):
        """Generate execution plans."""
        for query in self.queries:
            # Generate 1-3 plans per query (plan recompiles, parameter sniffing, etc.)
            num_plans = self.rng.integers(*self.config.num_plans_per_query_range)

            for _ in range(num_plans):
                plan_id = self.id_gen.next_id("plan")

                # Plan characteristics
                is_parallel = self.rng.random() < 0.3  # 30% parallel plans
                is_trivial = self.rng.random() < 0.1  # 10% trivial plans

                base_time = self.config.start_time + timedelta(
                    seconds=self.rng.uniform(0, (self.config.end_time - self.config.start_time).total_seconds())
                )

                plan = ExecutionPlan(
                    plan_id=plan_id,
                    query_id=query.query_id,
                    plan_group_id=0,
                    engine_version=SQL_SERVER_VERSION,
                    compatibility_level=150,
                    query_plan_hash=self._generate_hash(16),
                    query_plan=None,
                    is_online_index_plan=0,
                    is_trivial_plan=1 if is_trivial else 0,
                    is_parallel_plan=1 if is_parallel else 0,
                    is_forced_plan=0,
                    is_natively_compiled=0,
                    force_failure_count=0,
                    last_force_failure_reason=0,
                    last_force_failure_reason_desc="NONE",
                    count_compiles=self.rng.integers(1, 10),
                    initial_compile_start_time=base_time,
                    last_compile_start_time=base_time + timedelta(hours=self.rng.uniform(0, 24)),
                    last_execution_time=base_time + timedelta(hours=self.rng.uniform(1, 48)),
                    avg_compile_duration=float(self.rng.uniform(100, 10000)),
                    last_compile_duration=int(self.rng.uniform(100, 10000)),
                )

                self.plans.append(plan)
                self.relationships.add_plan(plan_id, query.query_id)

    def _generate_runtime_statistics(self):
        """Generate runtime statistics for each plan in each interval."""
        for plan in self.plans:
            # Get query type profile for this plan's query
            query = next(q for q in self.queries if q.query_id == plan.query_id)
            query_text = next(qt for qt in self.query_texts if qt.query_text_id == query.query_text_id)
            profile = self._infer_profile_from_sql(query_text.query_sql_text)

            # Decide which intervals this plan executes in
            # Popular queries execute in all intervals, others in subset
            execution_probability = self.rng.uniform(0.3, 1.0)

            for interval in self.intervals:
                if self.rng.random() > execution_probability:
                    continue  # Skip this interval

                runtime_stats_id = self.id_gen.next_id("runtime_stats")

                # Generate execution count for this interval
                exec_count = max(1, int(self.sampler.poisson(profile.execution_frequency).item()))

                # Generate performance metrics based on profile + pressure factors
                duration_samples = self._generate_duration_samples(profile, exec_count)
                cpu_samples = self.correlator.cpu_from_duration(duration_samples)
                logical_reads = self.correlator.logical_reads_from_duration(duration_samples)
                physical_reads = self.correlator.physical_reads_from_logical(
                    logical_reads, cache_hit_ratio=0.95 / self.workload.io_pressure
                )

                # Apply pressure factors
                duration_samples *= self.workload.cpu_pressure * self.workload.io_pressure
                cpu_samples *= self.workload.cpu_pressure

                # Generate row counts
                row_samples = np.maximum(
                    1, self.sampler.log_normal(profile.avg_rows, profile.rows_stddev, exec_count)
                ).astype(int)

                # Memory usage (8KB pages)
                memory_samples = np.maximum(
                    1,
                    (logical_reads * self.workload.memory_pressure * self.rng.uniform(0.1, 0.3, exec_count)).astype(
                        int
                    ),
                )

                # Execution times
                first_exec, last_exec = self._generate_execution_times(
                    interval.start_time, interval.end_time, exec_count
                )

                # Create runtime stats
                stats = RuntimeStats(
                    runtime_stats_id=runtime_stats_id,
                    plan_id=plan.plan_id,
                    runtime_stats_interval_id=interval.runtime_stats_interval_id,
                    execution_type_id=0,
                    execution_type="Regular",
                    first_execution_time=first_exec,
                    last_execution_time=last_exec,
                    count_executions=exec_count,
                    # Duration (microseconds)
                    avg_duration=float(np.mean(duration_samples)),
                    last_duration=float(duration_samples[-1]),
                    min_duration=float(np.min(duration_samples)),
                    max_duration=float(np.max(duration_samples)),
                    # CPU (microseconds)
                    avg_cpu_time=float(np.mean(cpu_samples)),
                    last_cpu_time=float(cpu_samples[-1]),
                    min_cpu_time=float(np.min(cpu_samples)),
                    max_cpu_time=float(np.max(cpu_samples)),
                    # Logical reads
                    avg_logical_io_reads=float(np.mean(logical_reads)),
                    last_logical_io_reads=float(logical_reads[-1]),
                    min_logical_io_reads=float(np.min(logical_reads)),
                    max_logical_io_reads=float(np.max(logical_reads)),
                    # Logical writes (much less common)
                    avg_logical_io_writes=0,
                    last_logical_io_writes=0,
                    min_logical_io_writes=0,
                    max_logical_io_writes=0,
                    # Physical reads
                    avg_physical_io_reads=float(np.mean(physical_reads)),
                    last_physical_io_reads=float(physical_reads[-1]),
                    min_physical_io_reads=float(np.min(physical_reads)),
                    max_physical_io_reads=float(np.max(physical_reads)),
                    # CLR time (usually 0 for most queries)
                    avg_clr_time=0,
                    last_clr_time=0,
                    min_clr_time=0,
                    max_clr_time=0,
                    # Memory
                    avg_query_max_used_memory=float(np.mean(memory_samples)),
                    last_query_max_used_memory=float(memory_samples[-1]),
                    min_query_max_used_memory=float(np.min(memory_samples)),
                    max_query_max_used_memory=float(np.max(memory_samples)),
                    # Row count
                    avg_rowcount=float(np.mean(row_samples)),
                    last_rowcount=float(row_samples[-1]),
                    min_rowcount=float(np.min(row_samples)),
                    max_rowcount=float(np.max(row_samples)),
                )

                self.runtime_stats.append(stats)
                self.relationships.add_plan_interval(plan.plan_id, interval.runtime_stats_interval_id)

    def _generate_wait_statistics(self):
        """Generate wait statistics for runtime stats."""
        wait_categories = list(WaitCategory)

        for stats in self.runtime_stats:
            # Generate 1-4 wait categories per query execution
            num_wait_categories = self.rng.integers(1, 5)
            selected_categories = self.rng.choice(wait_categories, size=num_wait_categories, replace=False)

            for wait_cat in selected_categories:
                # Wait time should be related to query duration
                # For problematic queries, waits can be substantial
                wait_time_ratio = self.rng.uniform(0.05, 0.4)  # 5-40% of duration in waits
                avg_wait = stats.avg_duration * wait_time_ratio / 1000  # Convert to milliseconds

                # Apply pressure factors
                if "IO" in wait_cat.value:
                    avg_wait *= self.workload.io_pressure
                elif "Memory" in wait_cat.value:
                    avg_wait *= self.workload.memory_pressure

                # Generate wait samples
                wait_samples = np.maximum(
                    1, self.sampler.log_normal(avg_wait, avg_wait * 0.3, stats.count_executions)
                )

                wait_stat = WaitStats(
                    plan_id=stats.plan_id,
                    runtime_stats_interval_id=stats.runtime_stats_interval_id,
                    wait_category_id=wait_cat.value.__hash__() % 20,  # Simplified ID
                    wait_category=wait_cat.value,
                    total_query_wait_time_ms=float(np.sum(wait_samples)),
                    avg_query_wait_time_ms=float(np.mean(wait_samples)),
                    last_query_wait_time_ms=float(wait_samples[-1]),
                    min_query_wait_time_ms=float(np.min(wait_samples)),
                    max_query_wait_time_ms=float(np.max(wait_samples)),
                    stdev_query_wait_time_ms=float(np.std(wait_samples)),
                )

                self.wait_stats.append(wait_stat)

    def _select_query_profile(self):
        """Select a query profile based on workload distribution."""
        profiles, proportions = zip(*self.workload.query_profiles)
        return self.rng.choice(profiles, p=proportions)

    def _generate_duration_samples(self, profile, count: int) -> np.ndarray:
        """Generate duration samples based on profile."""
        # Use log-normal distribution for realistic query durations
        durations = self.sampler.log_normal(profile.avg_duration_ms * 1000, profile.duration_stddev * 1000, count)
        return np.maximum(1, durations)  # Ensure positive

    def _generate_sql_for_profile(self, profile) -> str:
        """Generate realistic SQL text based on query profile."""
        # Randomly choose from various query types for more variety
        query_types = []

        if profile.name == "OLTP":
            query_types = [
                ("oltp", 0.4),
                ("stored_proc", 0.2),
                ("insert_bulk", 0.15),
                ("select_into", 0.15),
                ("delete_daterange", 0.1),
            ]
        elif profile.name == "OLAP":
            query_types = [
                ("olap", 0.3),
                ("cte", 0.25),
                ("dynamic_pivot", 0.15),
                ("window_function", 0.15),
                ("temp_table", 0.15),
            ]
        else:
            query_types = [("problematic", 1.0)]

        types, weights = zip(*query_types)
        selected_type = self.rng.choice(types, p=weights)

        # Generate query based on selected type
        generator_map = {
            "oltp": self._generate_oltp_query,
            "olap": self._generate_olap_query,
            "problematic": self._generate_problematic_query,
            "stored_proc": self._generate_stored_proc_query,
            "insert_bulk": self._generate_insert_bulk_query,
            "select_into": self._generate_select_into_query,
            "delete_daterange": self._generate_delete_daterange_query,
            "cte": self._generate_cte_query,
            "dynamic_pivot": self._generate_dynamic_pivot_query,
            "window_function": self._generate_window_function_query,
            "temp_table": self._generate_temp_table_query,
        }

        return generator_map[selected_type]()

    def _generate_oltp_query(self) -> str:
        """Generate OLTP-style query."""
        query_type = self.rng.choice(["select_by_id", "insert", "update", "delete"], p=[0.6, 0.2, 0.15, 0.05])

        table_name = self.faker.word().capitalize() + "s"
        id_val = self.rng.integers(1, 1000000)

        if query_type == "select_by_id":
            return f"SELECT * FROM {table_name} WHERE Id = {id_val}"
        elif query_type == "insert":
            return f"INSERT INTO {table_name} (Name, Value, CreatedDate) VALUES (@p0, @p1, GETDATE())"
        elif query_type == "update":
            return f"UPDATE {table_name} SET Status = @p0, ModifiedDate = GETDATE() WHERE Id = {id_val}"
        else:
            return f"DELETE FROM {table_name} WHERE Id = {id_val}"

    def _generate_olap_query(self) -> str:
        """Generate OLAP-style query."""
        table1 = self.faker.word().capitalize() + "s"
        table2 = self.faker.word().capitalize() + "s"
        table3 = self.faker.word().capitalize() + "s"

        field1 = self.faker.word()
        field2 = self.faker.word()
        field3 = self.faker.word()

        # Return single-line query (matching original format)
        return f"SELECT t1.{field1}_id, COUNT(*) as total_count, SUM(t2.amount) as total_amount, AVG(t2.value) as avg_value FROM {table1} t1 INNER JOIN {table2} t2 ON t1.id = t2.{field2}_id LEFT JOIN {table3} t3 ON t2.id = t3.{field3}_id WHERE t1.date >= DATEADD(month, -6, GETDATE()) GROUP BY t1.{field1}_id ORDER BY total_amount DESC"

    def _generate_problematic_query(self) -> str:
        """Generate problematic query (missing indexes, scans, etc.)."""
        table1 = self.faker.word().capitalize() + "s"
        table2 = self.faker.word().capitalize() + "s"

        # Problematic patterns: LIKE with leading wildcard, function on column, no WHERE clause
        problem_type = self.rng.choice(["like_leading", "function_on_column", "no_filter", "cross_join"])

        if problem_type == "like_leading":
            return f"SELECT * FROM {table1} WHERE Name LIKE '%{self.faker.word()}%'"
        elif problem_type == "function_on_column":
            return f"SELECT * FROM {table1} WHERE YEAR(CreatedDate) = {self.rng.integers(2020, 2025)}"
        elif problem_type == "no_filter":
            return f"SELECT * FROM {table1} ORDER BY CreatedDate DESC"
        else:
            return f"SELECT * FROM {table1} t1 CROSS JOIN {table2} t2 WHERE t1.value > t2.value"

    def _generate_stored_proc_query(self) -> str:
        """Generate parameterized query (stored procedure call pattern)."""
        table = self.faker.word().capitalize() + "s"
        num_params = self.rng.integers(2, 8)
        param_list = ", ".join([f"@Param{i:06d} varchar(100)" for i in range(4, 4 + num_params)])
        value_list = ", ".join([f"@Param{i:06d}" for i in range(4, 4 + num_params)])
        columns = ["Server", "DatabaseName", "ObjectName", "Status", "CreatedDate", "ModifiedBy", "Category", "Priority"][:num_params]
        column_list = ", ".join([f"[{col}]" for col in columns])
        return f"({param_list})INSERT [dbo].[{table}]({column_list}) VALUES({value_list})"

    def _generate_insert_bulk_query(self) -> str:
        """Generate bulk insert query pattern."""
        table = self.faker.word().capitalize() + "Data"
        columns = [
            "[Server] nvarchar(128) collate SQL_Latin1_General_CP1_CI_AS",
            "[DatabaseName] nvarchar(128) collate SQL_Latin1_General_CP1_CI_AS",
            "[ObjectName] nvarchar(256) collate SQL_Latin1_General_CP1_CI_AS",
            "[Status] varchar(50) collate SQL_Latin1_General_CP1_CI_AS",
            "[CreatedDate] datetime",
            "[ModifiedDate] datetime",
            "[RecordCount] bigint",
            "[SizeMB] decimal(18,2)",
        ]
        num_cols = self.rng.integers(4, len(columns) + 1)
        selected_cols = columns[:num_cols]
        col_def = ",".join(selected_cols)
        return f"insert bulk [dbo].[{table}]({col_def})with(TABLOCK,CHECK_CONSTRAINTS)"

    def _generate_select_into_query(self) -> str:
        """Generate SELECT INTO query pattern."""
        source_table = "@" + self.faker.word() + "s"
        dest_table = "#" + self.faker.word()
        columns = self.rng.choice(["query_server, usage, query_disk", "Server, DatabaseName, Status", "ObjectName, CreatedDate, SizeMB"])
        condition = self.rng.choice([
            f"WHERE usage = 'Data'",
            f"WHERE Status = 'Active'",
            f"WHERE CreatedDate > DATEADD(day, -30, GETDATE())",
        ])
        return f"SELECT {columns} INTO {dest_table} FROM {source_table} {condition}"

    def _generate_delete_daterange_query(self) -> str:
        """Generate DELETE with date range pattern."""
        schema = self.rng.choice(["dbo", "DBA_Repository", "staging"])
        table = self.faker.word().capitalize() + self.rng.choice(["History", "Log", "Archive", "Temp"])
        date_field = self.rng.choice(["Datum", "CreatedDate", "LogDate", "Timestamp"])
        interval = self.rng.choice([("yy", -1), ("m", -6), ("m", -3), ("d", -90)])
        return f"DELETE FROM {schema}.{table} WHERE {date_field} < DATEADD({interval[0]}, {interval[1]}, GETDATE())"

    def _generate_cte_query(self) -> str:
        """Generate CTE (Common Table Expression) query."""
        cte_name = "cte_" + self.faker.word() + "s"
        table1 = self.faker.word().capitalize() + "s"
        table2 = self.faker.word().capitalize() + "s"
        field1 = self.faker.word()
        field2 = self.faker.word()
        return f"WITH {cte_name} AS ( SELECT {field1}, {field2} FROM {table1} UNION SELECT {field1}, {field2} FROM {table2} ) SELECT srv.{field1}, COUNT(*) as total FROM {cte_name} srv GROUP BY srv.{field1} ORDER BY total DESC"

    def _generate_dynamic_pivot_query(self) -> str:
        """Generate dynamic query with string concatenation."""
        var_name = "@" + self.faker.word()
        table = self.faker.word().capitalize() + "s"
        field = self.faker.word()
        return f"({var_name} nvarchar(max))SELECT {var_name} = {var_name} + N'<td>'+ isnull(cast([{field}] as nvarchar(max)), '&nbsp;') + '</td>'+ FROM {table}"

    def _generate_window_function_query(self) -> str:
        """Generate query with window functions."""
        table = self.faker.word().capitalize() + "s"
        partition_field = self.faker.word() + "_id"
        order_field = self.rng.choice(["CreatedDate", "ModifiedDate", "Timestamp"])
        return f"SELECT {partition_field}, ROW_NUMBER() OVER (PARTITION BY {partition_field} ORDER BY {order_field} DESC) as row_num, LAG({order_field}) OVER (PARTITION BY {partition_field} ORDER BY {order_field}) as prev_date FROM {table} WHERE {order_field} >= DATEADD(month, -3, GETDATE())"

    def _generate_temp_table_query(self) -> str:
        """Generate temp table manipulation query."""
        temp_var = "@" + self.faker.word().capitalize()
        table_id_var = "@TempTableID int"
        return f"({table_id_var})INSERT {temp_var} SELECT name FROM tempdb.sys.columns AS c WHERE c.object_id = @TempTableID"

    def _infer_profile_from_sql(self, sql: str):
        """Infer query profile from SQL text."""
        sql_lower = sql.lower()

        # Simple heuristics
        if "join" in sql_lower and ("group by" in sql_lower or "sum(" in sql_lower or "avg(" in sql_lower):
            # Analytical query
            profile, _ = [(p, prop) for p, prop in self.workload.query_profiles if p.name == "OLAP"][0]
            return profile
        elif "cross join" in sql_lower or "like '%" in sql_lower or "year(" in sql_lower:
            # Problematic query
            for p, _ in self.workload.query_profiles:
                if p.name == "Problematic":
                    return p
            # Fallback to OLAP if no problematic profile
            return [(p, prop) for p, prop in self.workload.query_profiles if p.name == "OLAP"][0][0]
        else:
            # OLTP query
            profile, _ = [(p, prop) for p, prop in self.workload.query_profiles if p.name == "OLTP"][0]
            return profile
