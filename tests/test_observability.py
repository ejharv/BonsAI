"""
Tests for Phase 7 observability layer.
Covers RunStore and ReportGenerator.
"""

import json
import unittest
import tempfile
import uuid
from pathlib import Path

from core.orchestrator.models import (
    RunResult,
    NodeResult,
    NodeStatus,
)
from core.executor.models import (
    BudgetUsage,
    ExecutorBackend,
)
from core.seed.seed import Signal
from bonsai.observability.store import (
    RunStore,
    RunSummary,
    StoredRun,
)
from bonsai.observability.report import (
    ReportGenerator,
)


def make_run_result(
    run_id: str = None,
    success: bool = True,
    task: str = "test task",
) -> RunResult:
    """
    Build a minimal RunResult for testing.
    """
    rid = run_id or str(uuid.uuid4())
    signal = Signal(
        contribution_score=0.8,
        confidence=0.9,
    )
    budget = BudgetUsage(
        backend=ExecutorBackend.CLAUDE_CODE,
        wall_time_seconds=10.0,
        output_length_chars=500,
        tokens_used=None,
        budget_consumed=2.5,
    )
    node = NodeResult(
        node_id=rid,
        status=NodeStatus.COMPLETE,
        output="Test output",
        signal=signal,
        closure=None,
        child_results=[],
        budget_usage=budget,
        depth=0,
    )
    return RunResult(
        run_id=rid,
        task=task,
        root_result=node,
        total_budget_consumed=2.5,
        total_nodes=1,
        pruned_nodes=0,
        max_depth_reached=0,
        success=success,
        summary="Test run summary",
    )


class TestRunStore(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self.roots_path = Path(self._tmpdir)

    def test_save_creates_json_file(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        path = store.save_run(result, 10.0)
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, ".json")

    def test_save_creates_index_entry(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 10.0)
        index = (
            self.roots_path / "runs" /
            "index.md"
        )
        self.assertTrue(index.exists())
        content = index.read_text()
        self.assertIn(
            result.run_id[:8], content
        )

    def test_list_runs_returns_summaries(self):
        store = RunStore(self.roots_path)
        store.save_run(make_run_result(), 5.0)
        store.save_run(make_run_result(), 7.0)
        runs = store.list_runs()
        self.assertEqual(len(runs), 2)

    def test_list_runs_respects_limit(self):
        store = RunStore(self.roots_path)
        for _ in range(5):
            store.save_run(
                make_run_result(), 1.0
            )
        runs = store.list_runs(limit=3)
        self.assertLessEqual(len(runs), 3)

    def test_success_rate_all_success(self):
        store = RunStore(self.roots_path)
        for _ in range(4):
            store.save_run(
                make_run_result(success=True),
                1.0,
            )
        rate = store.success_rate()
        self.assertAlmostEqual(rate, 1.0)

    def test_success_rate_mixed(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(success=True),
            1.0,
        )
        store.save_run(
            make_run_result(success=False),
            1.0,
        )
        rate = store.success_rate()
        self.assertAlmostEqual(rate, 0.5)

    def test_success_rate_empty_returns_zero(self):
        store = RunStore(self.roots_path)
        rate = store.success_rate()
        self.assertEqual(rate, 0.0)

    def test_load_run_returns_stored_run(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        loaded = store.load_run(result.run_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded.run_id, result.run_id
        )
        self.assertTrue(loaded.success)

    def test_load_run_missing_returns_none(self):
        store = RunStore(self.roots_path)
        loaded = store.load_run("nonexistent-id")
        self.assertIsNone(loaded)

    def test_load_run_by_prefix(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        # Load using 8-char prefix
        prefix = result.run_id[:8]
        loaded = store.load_run(prefix)
        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded.run_id, result.run_id
        )

    def test_runs_for_task_pattern(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(
                task="implement auth module"
            ),
            1.0,
        )
        store.save_run(
            make_run_result(
                task="write unit tests"
            ),
            1.0,
        )
        results = store.runs_for_task_pattern(
            "auth"
        )
        self.assertEqual(len(results), 1)
        self.assertIn("auth", results[0].task)

    def test_runs_for_task_pattern_case_insensitive(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(task="Implement AUTH"),
            1.0,
        )
        results = store.runs_for_task_pattern(
            "auth"
        )
        self.assertEqual(len(results), 1)

    def test_budget_by_agent_returns_dict(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(), 5.0
        )
        by_agent = store.budget_by_agent()
        self.assertIsInstance(by_agent, dict)
        self.assertGreater(
            sum(by_agent.values()), 0
        )

    def test_result_to_dict_roundtrip(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        d = store._result_to_dict(result, 5.0)
        self.assertEqual(d["run_id"], result.run_id)
        self.assertEqual(d["success"], True)
        self.assertIn("root_result", d)
        self.assertIn("timestamp", d)
        # Enum serialized as string
        budget = d["root_result"]["budget_usage"]
        self.assertEqual(
            budget["backend"], "CLAUDE_CODE"
        )

    def test_index_prepends_most_recent(self):
        store = RunStore(self.roots_path)
        r1 = make_run_result(task="first task")
        r2 = make_run_result(task="second task")
        store.save_run(r1, 1.0)
        store.save_run(r2, 1.0)
        runs = store.list_runs()
        # Most recent (r2) should be first
        self.assertEqual(len(runs), 2)
        self.assertIn("second", runs[0].task)

    def test_runs_path_created_on_init(self):
        store = RunStore(self.roots_path)
        self.assertTrue(
            (self.roots_path / "runs").exists()
        )


class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self.roots_path = Path(self._tmpdir)

    def test_run_summary_report_no_runs(self):
        store = RunStore(self.roots_path)
        report = ReportGenerator(store)
        content = report.run_summary_report()
        self.assertIn("No runs", content)

    def test_run_summary_report_with_runs(self):
        store = RunStore(self.roots_path)
        store.save_run(make_run_result(), 5.0)
        report = ReportGenerator(store)
        content = report.run_summary_report()
        self.assertIn("Recent Runs", content)
        self.assertIn("Success rate", content)

    def test_run_summary_report_shows_checkmark(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(success=True), 5.0
        )
        report = ReportGenerator(store)
        content = report.run_summary_report()
        self.assertIn("✓", content)

    def test_budget_report_no_data(self):
        store = RunStore(self.roots_path)
        report = ReportGenerator(store)
        content = report.budget_report()
        self.assertIn("No budget data", content)

    def test_budget_report_with_data(self):
        store = RunStore(self.roots_path)
        store.save_run(make_run_result(), 5.0)
        report = ReportGenerator(store)
        content = report.budget_report()
        self.assertIn("Budget by Agent", content)
        self.assertIn("Total:", content)

    def test_tree_report_missing_run(self):
        store = RunStore(self.roots_path)
        report = ReportGenerator(store)
        content = report.tree_report(
            "nonexistent-run-id"
        )
        self.assertIn("Not Found", content)

    def test_tree_report_valid_run(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        report = ReportGenerator(store)
        content = report.tree_report(
            result.run_id
        )
        self.assertIn("Execution Tree", content)
        self.assertIn(result.run_id[:8], content)

    def test_tree_report_shows_summary(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        report = ReportGenerator(store)
        content = report.tree_report(
            result.run_id
        )
        self.assertIn("Summary", content)
        self.assertIn("Test run summary", content)

    def test_health_report_returns_string(self):
        store = RunStore(self.roots_path)
        report = ReportGenerator(store)
        content = report.health_report()
        self.assertIn("Health Report", content)
        self.assertIn("Recommendations", content)

    def test_health_report_with_data(self):
        store = RunStore(self.roots_path)
        store.save_run(
            make_run_result(success=True), 5.0
        )
        report = ReportGenerator(store)
        content = report.health_report()
        self.assertIn("Success rate", content)
        self.assertIn("100%", content)

    def test_health_report_good_health(self):
        store = RunStore(self.roots_path)
        for _ in range(3):
            store.save_run(
                make_run_result(success=True),
                5.0,
            )
        report = ReportGenerator(store)
        content = report.health_report()
        self.assertIn("looks good", content)

    def test_format_node_tree_returns_string(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        report = ReportGenerator(store)
        loaded = store.load_run(result.run_id)
        tree_str = report._format_node_tree(
            loaded.root_result
        )
        self.assertIsInstance(tree_str, str)
        self.assertIn("COMPLETE", tree_str)

    def test_tree_report_by_prefix(self):
        store = RunStore(self.roots_path)
        result = make_run_result()
        store.save_run(result, 5.0)
        report = ReportGenerator(store)
        # Use 8-char prefix as returned by list_runs
        prefix = result.run_id[:8]
        content = report.tree_report(prefix)
        self.assertIn("Execution Tree", content)


if __name__ == "__main__":
    unittest.main()
