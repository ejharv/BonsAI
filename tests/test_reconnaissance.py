"""
Tests for the ReconnaissanceAgent implementation.
Uses only Python stdlib (no pytest).

Run with:
    python -m unittest tests/test_reconnaissance.py -v
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from root_manager.manager import RootManager
from agents.reconnaissance.models import (
    ConfidenceLevel,
    GapSeverity,
    ReconnaissanceInput,
    ReconnaissanceOutput,
)
from agents.reconnaissance.agent import ReconnaissanceAgent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_fake_project(base: Path) -> Path:
    """
    Create a minimal fake project tree under base/project/.

    fake_project/
    ├── src/
    │   ├── auth/
    │   │   ├── __init__.py
    │   │   └── service.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── routes.py
    │   └── utils/
    │       └── helpers.py
    ├── tests/
    │   └── test_auth.py
    ├── requirements.txt  (content: fastapi\njwt\nbcrypt)
    └── pyproject.toml    (minimal content)
    """
    project = base / "project"

    _write(project / "src" / "auth" / "__init__.py", "")
    _write(project / "src" / "auth" / "service.py", "# auth service\n")
    _write(project / "src" / "api" / "__init__.py", "")
    _write(project / "src" / "api" / "routes.py", "# api routes\n")
    _write(project / "src" / "utils" / "helpers.py", "# helpers\n")
    _write(project / "tests" / "test_auth.py", "# tests\n")
    _write(project / "requirements.txt", "fastapi\njwt\nbcrypt\n")
    _write(
        project / "pyproject.toml",
        '[project]\nname = "fake"\nversion = "0.1.0"\n',
    )

    return project


def _make_roots(base: Path) -> Path:
    """Create a minimal roots/ directory that RootWriter accepts."""
    roots = base / "roots"
    roots.mkdir(parents=True, exist_ok=True)
    return roots


def _make_agent(project: Path, roots: Path) -> ReconnaissanceAgent:
    manager = RootManager(roots)
    return ReconnaissanceAgent(manager, project)


def _make_input(project: Path, **kwargs) -> ReconnaissanceInput:
    defaults = dict(
        project_path=str(project),
        use_graphify=False,
        graphify_report_path=None,
        trust_git_history=False,
        involvement_preference="high",
        existing_bonsai=False,
    )
    defaults.update(kwargs)
    return ReconnaissanceInput(**defaults)


# ---------------------------------------------------------------------------
# TestScanProjectStructure
# ---------------------------------------------------------------------------


class TestScanProjectStructure(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)
        self.agent = _make_agent(self.project, self.roots)
        self.result = self.agent.scan_project_structure()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_finds_top_level_folders(self):
        self.assertIn("src", self.result["top_level_folders"])

    def test_finds_config_files(self):
        config_names = [Path(f).name for f in self.result["config_files"]]
        self.assertIn("requirements.txt", config_names)

    def test_excludes_git_from_walk(self):
        # __pycache__ and .git are excluded from traversal entirely
        for folder in self.result["folders"]:
            self.assertNotIn(".git", folder)
            self.assertNotIn("__pycache__", folder)

    def test_finds_tests_folder_in_folders(self):
        # Scan records tests/ in folders — identify_domains excludes it from
        # domain candidates, but scan itself should find it.
        self.assertIn("tests", self.result["folders"])

    def test_reads_requirements(self):
        reqs = self.result["manifest_contents"].get("requirements", [])
        self.assertIn("fastapi", reqs)
        self.assertIn("jwt", reqs)
        self.assertIn("bcrypt", reqs)

    def test_files_by_extension_has_py(self):
        self.assertIn(".py", self.result["files_by_extension"])


# ---------------------------------------------------------------------------
# TestIdentifyDomains
# ---------------------------------------------------------------------------


class TestIdentifyDomains(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)
        self.agent = _make_agent(self.project, self.roots)
        self.structure = self.agent.scan_project_structure()
        self.domains = self.agent.identify_domains(self.structure, {})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_finds_auth_domain(self):
        names = [d.name for d in self.domains]
        self.assertIn("auth", names)

    def test_finds_api_domain(self):
        names = [d.name for d in self.domains]
        self.assertIn("api", names)

    def test_excludes_tests_from_domains(self):
        names = [d.name for d in self.domains]
        self.assertNotIn("tests", names)

    def test_confidence_from_signals(self):
        # auth gets: folder signal + jwt + bcrypt = 3 signals → HIGH
        auth_domain = next((d for d in self.domains if d.name == "auth"), None)
        self.assertIsNotNone(auth_domain, "auth domain not found")
        self.assertNotEqual(auth_domain.confidence, ConfidenceLevel.LOW)

    def test_domains_are_not_empty(self):
        self.assertGreater(len(self.domains), 0)

    def test_evidence_is_populated(self):
        auth_domain = next((d for d in self.domains if d.name == "auth"), None)
        self.assertIsNotNone(auth_domain)
        self.assertGreater(len(auth_domain.evidence), 0)


# ---------------------------------------------------------------------------
# TestDetectPatterns
# ---------------------------------------------------------------------------


class TestDetectPatterns(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)
        self.agent = _make_agent(self.project, self.roots)
        self.structure = self.agent.scan_project_structure()
        self.patterns = self.agent.detect_patterns(self.structure)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_init_py_not_flagged_as_repetition(self):
        # __init__.py is in _CONVENTIONAL_FILENAMES — must never appear as
        # is_repetition=True even though it appears in multiple folders.
        for p in self.patterns:
            if p.name == "__init__.py":
                self.assertFalse(
                    p.is_repetition,
                    "__init__.py should not be flagged as unintentional repetition",
                )

    def test_returns_list(self):
        self.assertIsInstance(self.patterns, list)

    def test_oversized_file_not_repetition(self):
        # Oversized file patterns should have is_repetition=False
        for p in self.patterns:
            if p.pattern_type == "oversized_file":
                self.assertFalse(p.is_repetition)


# ---------------------------------------------------------------------------
# TestIdentifyGaps
# ---------------------------------------------------------------------------


class TestIdentifyGaps(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)
        self.agent = _make_agent(self.project, self.roots)
        self.structure = self.agent.scan_project_structure()
        self.domains = self.agent.identify_domains(self.structure, {})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_always_has_purpose_gap(self):
        gaps = self.agent.identify_gaps(self.domains, self.structure)
        blocking = [g for g in gaps if g.severity == GapSeverity.BLOCKING]
        self.assertGreater(len(blocking), 0)

    def test_low_involvement_only_blocking(self):
        self.agent._involvement_preference = "low"
        gaps = self.agent.identify_gaps(self.domains, self.structure)
        for g in gaps:
            self.assertEqual(g.severity, GapSeverity.BLOCKING)

    def test_medium_involvement_no_optional(self):
        self.agent._involvement_preference = "medium"
        gaps = self.agent.identify_gaps(self.domains, self.structure)
        for g in gaps:
            self.assertNotEqual(g.severity, GapSeverity.OPTIONAL)

    def test_high_involvement_includes_optional(self):
        self.agent._involvement_preference = "high"
        gaps = self.agent.identify_gaps(self.domains, self.structure)
        optional = [g for g in gaps if g.severity == GapSeverity.OPTIONAL]
        self.assertGreater(len(optional), 0)

    def test_gaps_ordered_blocking_first(self):
        gaps = self.agent.identify_gaps(self.domains, self.structure)
        if len(gaps) < 2:
            return
        _order = {GapSeverity.BLOCKING: 0, GapSeverity.IMPORTANT: 1, GapSeverity.OPTIONAL: 2}
        for i in range(len(gaps) - 1):
            self.assertLessEqual(
                _order[gaps[i].severity],
                _order[gaps[i + 1].severity],
            )


# ---------------------------------------------------------------------------
# TestProposeRoster
# ---------------------------------------------------------------------------


class TestProposeRoster(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)
        self.agent = _make_agent(self.project, self.roots)
        self.structure = self.agent.scan_project_structure()
        self.domains = self.agent.identify_domains(self.structure, {})
        self.roster = self.agent.propose_roster(self.domains)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_always_includes_quality(self):
        self.assertIn("quality", self.roster)

    def test_always_includes_evaluator(self):
        self.assertIn("evaluator", self.roster)

    def test_one_agent_per_domain(self):
        # auth and api should both be HIGH/MEDIUM — each gets an agent
        domain_agents = [
            r for r in self.roster if r not in ("quality", "evaluator")
        ]
        self.assertGreaterEqual(len(domain_agents), 2)

    def test_returns_list_of_strings(self):
        for name in self.roster:
            self.assertIsInstance(name, str)


# ---------------------------------------------------------------------------
# TestRunPipeline
# ---------------------------------------------------------------------------


class TestRunPipeline(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.project = _make_fake_project(self.tmp)
        self.roots = _make_roots(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_run_returns_output(self):
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        self.assertIsInstance(result, ReconnaissanceOutput)

    def test_run_ready_to_proceed_is_false(self):
        # Always False because the project purpose gap is BLOCKING
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        self.assertFalse(result.ready_to_proceed)

    def test_run_never_raises(self):
        # Point agent at a nonexistent project path — must not raise
        nonexistent = self.tmp / "does_not_exist"
        agent = _make_agent(nonexistent, self.roots)
        recon_input = _make_input(nonexistent)
        try:
            result = agent.run(recon_input)
        except Exception as exc:
            self.fail(f"run() raised an exception: {exc}")
        self.assertFalse(result.ready_to_proceed)

    def test_run_writes_codebase_entries(self):
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        # codebase.md should exist and contain domain entries
        codebase_file = self.roots / "context" / "codebase.md"
        if len(result.observed_domains) > 0:
            self.assertTrue(codebase_file.exists())

    def test_run_writes_agent_files(self):
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        agents_dir = self.roots / "agents"
        self.assertTrue(agents_dir.exists())
        # quality and evaluator files should be written
        self.assertTrue((agents_dir / "quality.md").exists())
        self.assertTrue((agents_dir / "evaluator.md").exists())

    def test_run_populates_domains(self):
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        self.assertGreater(len(result.observed_domains), 0)

    def test_run_populates_roster(self):
        agent = _make_agent(self.project, self.roots)
        recon_input = _make_input(self.project)
        result = agent.run(recon_input)
        self.assertIn("quality", result.proposed_roster)
        self.assertIn("evaluator", result.proposed_roster)


if __name__ == "__main__":
    unittest.main()
