"""
Tests for the Bonsai CLI — _initialize_roots, display functions,
_write_bonsai_config, and run_init integration.
"""

import sys
import unittest
import unittest.mock as mock
from pathlib import Path
import tempfile
import os

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bonsai.cli.init_command import (
    _initialize_roots,
    _write_bonsai_config,
    run_init,
)
from bonsai.cli.display import (
    print_header,
    print_roster_summary,
    print_domain_summary,
)
from agents.reconnaissance.models import (
    ObservedDomain,
    ConfidenceLevel,
)


# ---------------------------------------------------------------------------
# TestInitializeRoots
# ---------------------------------------------------------------------------


class TestInitializeRoots(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.roots_path = Path(self.tmp) / "roots"

    def test_creates_all_regions(self):
        _initialize_roots(self.roots_path)
        for region in ["project", "agents", "context", "quality", "flows"]:
            self.assertTrue(
                (self.roots_path / region).is_dir(),
                f"Missing region directory: {region}",
            )

    def test_creates_index_files(self):
        _initialize_roots(self.roots_path)
        for region in ["project", "agents", "context", "quality", "flows"]:
            index = self.roots_path / region / "index.md"
            self.assertTrue(
                index.exists(),
                f"Missing index.md in {region}/",
            )

    def test_creates_root_md(self):
        _initialize_roots(self.roots_path)
        self.assertTrue((self.roots_path / "ROOT.md").exists())

    def test_safe_to_call_twice(self):
        _initialize_roots(self.roots_path)
        # Write a sentinel into an index file
        sentinel = "SENTINEL_DO_NOT_OVERWRITE"
        index = self.roots_path / "project" / "index.md"
        original = index.read_text()
        index.write_text(original + sentinel)

        # Second call must not raise and must not overwrite existing files
        try:
            _initialize_roots(self.roots_path)
        except Exception as exc:
            self.fail(f"Second call raised: {exc}")

        content = index.read_text()
        self.assertIn(sentinel, content, "Second call overwrote existing index.md")


# ---------------------------------------------------------------------------
# TestDisplay
# ---------------------------------------------------------------------------


class TestDisplay(unittest.TestCase):

    def test_print_header_no_crash(self):
        try:
            print_header("Test")
        except Exception as exc:
            self.fail(f"print_header raised: {exc}")

    def test_print_roster_summary_no_crash(self):
        try:
            print_roster_summary(["auth_agent", "api_agent", "quality", "evaluator"])
        except Exception as exc:
            self.fail(f"print_roster_summary raised: {exc}")

    def test_print_domain_summary_no_crash(self):
        domains = [
            ObservedDomain(
                name="auth",
                purpose="Handles authentication",
                confidence=ConfidenceLevel.HIGH,
                evidence=["src/auth/ exists"],
                file_paths=["src/auth/auth.py"],
                dependencies=[],
            ),
            ObservedDomain(
                name="api",
                purpose="REST API endpoints",
                confidence=ConfidenceLevel.MEDIUM,
                evidence=["src/api/ exists"],
                file_paths=["src/api/views.py"],
                dependencies=["auth"],
            ),
        ]
        try:
            print_domain_summary(domains)
        except Exception as exc:
            self.fail(f"print_domain_summary raised: {exc}")

    def test_print_roster_summary_empty(self):
        try:
            print_roster_summary([])
        except Exception as exc:
            self.fail(f"print_roster_summary([]) raised: {exc}")

    def test_print_domain_summary_long_purpose_truncated(self):
        """Purpose longer than 24 chars should not crash and should truncate."""
        domains = [
            ObservedDomain(
                name="longdomain",
                purpose="A" * 40,
                confidence=ConfidenceLevel.LOW,
                evidence=[],
                file_paths=[],
                dependencies=[],
            )
        ]
        try:
            print_domain_summary(domains)
        except Exception as exc:
            self.fail(f"print_domain_summary with long purpose raised: {exc}")


# ---------------------------------------------------------------------------
# TestWriteBonsaiConfig
# ---------------------------------------------------------------------------


class TestWriteBonsaiConfig(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project_path = Path(self.tmp)

    def test_creates_config_file(self):
        _write_bonsai_config(self.project_path, "medium", ["auth_agent"])
        self.assertTrue((self.project_path / ".bonsai").exists())

    def test_config_contains_involvement(self):
        _write_bonsai_config(self.project_path, "high", ["auth_agent"])
        content = (self.project_path / ".bonsai").read_text()
        self.assertIn("involvement=high", content)

    def test_config_contains_roster(self):
        _write_bonsai_config(
            self.project_path, "medium", ["auth_agent", "quality"]
        )
        content = (self.project_path / ".bonsai").read_text()
        self.assertIn("auth_agent", content)

    def test_config_initialized_flag(self):
        _write_bonsai_config(self.project_path, "low", [])
        content = (self.project_path / ".bonsai").read_text()
        self.assertIn("initialized=True", content)


# ---------------------------------------------------------------------------
# TestRunInitIntegration
# ---------------------------------------------------------------------------


class _MockArgs:
    """Minimal stand-in for argparse Namespace."""

    def __init__(self, project_path, involvement="low", graphify=None, trust_git=False):
        self.project_path = project_path
        self.involvement = involvement
        self.graphify = graphify
        self.trust_git = trust_git


class TestRunInitIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project_dir = Path(self.tmp)

    def test_run_init_creates_roots(self):
        args = _MockArgs(
            project_path=str(self.project_dir),
            involvement="low",
            graphify=None,
            trust_git=False,
        )
        with mock.patch("builtins.input", return_value=""):
            run_init(args)
        self.assertTrue(
            (self.project_dir / "roots").is_dir(),
            "run_init did not create roots/ directory",
        )

    def test_run_init_returns_bool(self):
        args = _MockArgs(
            project_path=str(self.project_dir),
            involvement="low",
            graphify=None,
            trust_git=False,
        )
        with mock.patch("builtins.input", return_value=""):
            result = run_init(args)
        self.assertIsInstance(result, bool)

    def test_run_init_invalid_path_returns_false(self):
        args = _MockArgs(
            project_path="/nonexistent/path/that/does/not/exist",
            involvement="low",
        )
        result = run_init(args)
        self.assertFalse(result)

    def test_run_init_creates_bonsai_config_on_confirm(self):
        """When user confirms roster (empty string = Y), .bonsai should be written."""
        args = _MockArgs(
            project_path=str(self.project_dir),
            involvement="low",
            graphify=None,
            trust_git=False,
        )
        with mock.patch("builtins.input", return_value=""):
            run_init(args)
        # .bonsai written only if roster confirmed — empty roster auto-confirms
        config = self.project_dir / ".bonsai"
        self.assertTrue(
            config.exists(),
            ".bonsai config not written after successful init",
        )

    def test_run_init_declined_roster_returns_false(self):
        """When user declines roster confirmation, run_init returns False."""
        args = _MockArgs(
            project_path=str(self.project_dir),
            involvement="low",
            graphify=None,
            trust_git=False,
        )
        # First input() calls are for gap questions (return ""), last is roster confirm (return "n")
        inputs = iter(["", "n"])
        with mock.patch("builtins.input", side_effect=inputs):
            result = run_init(args)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
