"""
Unit tests for the executor layer.
No real Claude Code CLI or API calls —
all external calls are mocked.
"""

import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from core.executor.models import (
    AgentContext,
    AgentPrompt,
    ExecutorBackend,
    ExecutorStatus,
)
from core.executor.claude_code import ClaudeCodeExecutor
from core.executor.api import APIExecutor
from bonsai.cli.run_command import (
    _load_bonsai_config,
    _route_task,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_prompt() -> AgentPrompt:
    """Build the simplest valid AgentPrompt for testing."""
    ctx = AgentContext(
        agent_name="builder",
        agent_definition="You are Builder.",
        relevant_roots={},
        task="Do something",
        output_format="Plain text",
        roots_to_update=[],
    )
    return AgentPrompt(
        context=ctx,
        seed_depth=0,
        budget_allocated=5.0,
        parent_intent="",
        success_criteria="Task done",
    )


# ---------------------------------------------------------------------------
# ClaudeCodeExecutor tests
# ---------------------------------------------------------------------------

class TestClaudeCodeExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = ClaudeCodeExecutor()

    def test_is_available_returns_bool(self):
        # Should return a bool without raising regardless of claude presence
        result = self.executor.is_available()
        self.assertIsInstance(result, bool)

    def test_calculate_budget(self):
        result = self.executor._calculate_budget(10.0, 500)
        self.assertGreater(result, 0)
        self.assertLess(result, 5.0)
        # Expected: 10.0 * 0.1 + 500/1000 * 0.05 = 1.0 + 0.025 = 1.025
        self.assertAlmostEqual(result, 1.025, places=4)

    def test_parse_roots_updates_empty(self):
        result = self.executor._parse_roots_updates("")
        self.assertEqual(result, {})

    def test_parse_roots_updates_finds_tag(self):
        raw = (
            'Some text\n'
            '<root_update path="roots/project/state.md">'
            '\n# State\ncontent here\n'
            '</root_update>\n'
            'More text'
        )
        result = self.executor._parse_roots_updates(raw)
        self.assertIn("roots/project/state.md", result)
        self.assertIn("content here", result["roots/project/state.md"])

    def test_execute_timeout_returns_result(self):
        prompt = _make_minimal_prompt()
        with mock.patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("claude", 1)
            result = self.executor.execute(prompt, timeout_seconds=1)
        self.assertEqual(result.status, ExecutorStatus.TIMEOUT)
        self.assertIsNotNone(result.error)
        self.assertIn("timed out", result.error)

    def test_execute_failure_returns_result(self):
        prompt = _make_minimal_prompt()
        mock_completed = subprocess.CompletedProcess(
            args=["claude", "--print", "x"],
            returncode=1,
            stdout="partial output",
            stderr="error message",
        )
        with mock.patch("subprocess.run", return_value=mock_completed):
            result = self.executor.execute(prompt)
        self.assertEqual(result.status, ExecutorStatus.FAILED)

    def test_execute_success_returns_result(self):
        prompt = _make_minimal_prompt()
        mock_completed = subprocess.CompletedProcess(
            args=["claude", "--print", "x"],
            returncode=0,
            stdout="Good output from agent",
            stderr="",
        )
        with mock.patch("subprocess.run", return_value=mock_completed):
            result = self.executor.execute(prompt)
        self.assertEqual(result.status, ExecutorStatus.SUCCESS)
        self.assertEqual(result.raw_output, "Good output from agent")
        self.assertIsNone(result.error)
        self.assertIsNone(result.budget_usage.tokens_used)
        self.assertEqual(result.budget_usage.backend, ExecutorBackend.CLAUDE_CODE)

    def test_backend_property(self):
        self.assertEqual(self.executor.backend, ExecutorBackend.CLAUDE_CODE)


# ---------------------------------------------------------------------------
# APIExecutor tests
# ---------------------------------------------------------------------------

class TestAPIExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = APIExecutor()

    def test_is_available_false_without_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(self.executor.is_available())

    def test_is_available_true_with_key(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            self.assertTrue(self.executor.is_available())

    def test_is_available_false_with_empty_key(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "  "}):
            self.assertFalse(self.executor.is_available())

    def test_calculate_budget(self):
        result = self.executor._calculate_budget(1000, 500)
        # input_cost = 1000/1000 * 0.1 = 0.1
        # output_cost = 500/1000 * 0.3 = 0.15
        # total = 0.25
        self.assertAlmostEqual(result, 0.25, places=4)

    def test_execute_without_sdk_fails(self):
        prompt = _make_minimal_prompt()
        with mock.patch.dict("sys.modules", {"anthropic": None}):
            result = self.executor.execute(prompt)
        self.assertEqual(result.status, ExecutorStatus.FAILED)
        self.assertIsNotNone(result.error)
        self.assertIn("not installed", result.error)

    def test_backend_property(self):
        self.assertEqual(self.executor.backend, ExecutorBackend.API)

    def test_execute_api_success(self):
        prompt = _make_minimal_prompt()

        # Build mock anthropic response
        mock_content = mock.MagicMock()
        mock_content.text = "API agent output"

        mock_usage = mock.MagicMock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 50

        mock_message = mock.MagicMock()
        mock_message.content = [mock_content]
        mock_message.usage = mock_usage

        mock_client = mock.MagicMock()
        mock_client.messages.create.return_value = mock_message

        mock_anthropic_module = mock.MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        with mock.patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
            result = self.executor.execute(prompt)

        self.assertEqual(result.status, ExecutorStatus.SUCCESS)
        self.assertEqual(result.raw_output, "API agent output")
        self.assertEqual(result.budget_usage.tokens_used, 150)
        self.assertEqual(result.budget_usage.backend, ExecutorBackend.API)


# ---------------------------------------------------------------------------
# _load_bonsai_config tests
# ---------------------------------------------------------------------------

class TestLoadBonsaiConfig(unittest.TestCase):

    def test_loads_key_value_pairs(self):
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".bonsai"
            config_path.write_text(
                "executor=claude_code\n"
                "involvement=medium\n"
            )
            result = _load_bonsai_config(Path(tmpdir))
        self.assertEqual(result["executor"], "claude_code")
        self.assertEqual(result["involvement"], "medium")

    def test_empty_if_no_file(self):
        with TemporaryDirectory() as tmpdir:
            result = _load_bonsai_config(Path(tmpdir))
        self.assertEqual(result, {})

    def test_ignores_comments(self):
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".bonsai"
            config_path.write_text(
                "# this is a comment\n"
                "executor=api\n"
            )
            result = _load_bonsai_config(Path(tmpdir))
        self.assertNotIn("#", result)
        self.assertEqual(result["executor"], "api")

    def test_ignores_blank_lines(self):
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".bonsai"
            config_path.write_text(
                "\n"
                "executor=claude_code\n"
                "\n"
            )
            result = _load_bonsai_config(Path(tmpdir))
        self.assertEqual(result["executor"], "claude_code")


# ---------------------------------------------------------------------------
# _route_task tests
# ---------------------------------------------------------------------------

class TestRouteTask(unittest.TestCase):

    def test_routes_test_keywords(self):
        result = _route_task("write tests for auth module", {}, None)
        self.assertEqual(result, "tester")

    def test_routes_spec_keyword(self):
        result = _route_task("create spec for the payment flow", {}, None)
        self.assertEqual(result, "tester")

    def test_routes_quality_keywords(self):
        result = _route_task("refactor duplicate code in utils", {}, None)
        self.assertEqual(result, "quality")

    def test_routes_prune_keyword(self):
        result = _route_task("prune unused modules", {}, None)
        self.assertEqual(result, "quality")

    def test_routes_evaluator_keywords(self):
        result = _route_task("evaluate the API using a persona", {}, None)
        self.assertEqual(result, "evaluator")

    def test_defaults_to_builder(self):
        result = _route_task(
            "implement user login endpoint", {}, None
        )
        self.assertEqual(result, "builder")

    def test_defaults_to_builder_for_unknown(self):
        result = _route_task(
            "add a new feature to the dashboard", {}, None
        )
        self.assertEqual(result, "builder")


if __name__ == "__main__":
    unittest.main()
