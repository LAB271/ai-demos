"""Correlation and relationship management utilities."""

from dataclasses import dataclass


@dataclass
class EntityRelationships:
    """Tracks relationships between DMV entities."""

    query_text_to_query: dict[int, list[int]]  # query_text_id -> [query_ids]
    query_to_plans: dict[int, list[int]]  # query_id -> [plan_ids]
    plan_to_intervals: dict[int, list[int]]  # plan_id -> [interval_ids]

    def __init__(self):
        """Initialize empty relationship dictionaries."""
        self.query_text_to_query = {}
        self.query_to_plans = {}
        self.plan_to_intervals = {}

    def add_query_text(self, query_text_id: int):
        """Register a new query text."""
        if query_text_id not in self.query_text_to_query:
            self.query_text_to_query[query_text_id] = []

    def add_query(self, query_id: int, query_text_id: int):
        """Register a query linked to query text."""
        if query_text_id not in self.query_text_to_query:
            self.query_text_to_query[query_text_id] = []
        self.query_text_to_query[query_text_id].append(query_id)

        if query_id not in self.query_to_plans:
            self.query_to_plans[query_id] = []

    def add_plan(self, plan_id: int, query_id: int):
        """Register a plan linked to a query."""
        if query_id not in self.query_to_plans:
            self.query_to_plans[query_id] = []
        self.query_to_plans[query_id].append(plan_id)

        if plan_id not in self.plan_to_intervals:
            self.plan_to_intervals[plan_id] = []

    def add_plan_interval(self, plan_id: int, interval_id: int):
        """Register that a plan was executed in an interval."""
        if plan_id not in self.plan_to_intervals:
            self.plan_to_intervals[plan_id] = []
        if interval_id not in self.plan_to_intervals[plan_id]:
            self.plan_to_intervals[plan_id].append(interval_id)

    def get_queries_for_text(self, query_text_id: int) -> list[int]:
        """Get all query IDs for a query text."""
        return self.query_text_to_query.get(query_text_id, [])

    def get_plans_for_query(self, query_id: int) -> list[int]:
        """Get all plan IDs for a query."""
        return self.query_to_plans.get(query_id, [])

    def get_intervals_for_plan(self, plan_id: int) -> list[int]:
        """Get all interval IDs where a plan was executed."""
        return self.plan_to_intervals.get(plan_id, [])


class IdGenerator:
    """Generates sequential IDs for different entity types."""

    def __init__(self):
        """Initialize ID counters."""
        self.counters = {}

    def next_id(self, entity_type: str) -> int:
        """Get the next ID for an entity type."""
        if entity_type not in self.counters:
            self.counters[entity_type] = 1
        else:
            self.counters[entity_type] += 1
        return self.counters[entity_type]

    def current_id(self, entity_type: str) -> int:
        """Get the current ID for an entity type."""
        return self.counters.get(entity_type, 0)
