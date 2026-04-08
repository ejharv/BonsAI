"""
Tests for the Root Manager implementation.
Uses only Python stdlib (no pytest).

Run with:
    python -m unittest tests/test_root_manager.py -v
"""

import datetime
import shutil
import tempfile
import unittest
from pathlib import Path

from root_manager.models import (
    CodebaseEntry,
    DecisionEntry,
    DependencyEntry,
    FileStatus,
    ProjectState,
)
from root_manager.reader import RootReader
from root_manager.writer import RootWriter
from root_manager.manager import RootManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _make_index(files: list[str]) -> str:
    today = datetime.date.today().isoformat()
    rows = "\n".join(
        f"| {f} | clean | Architect | {today} | fresh |"
        for f in files
    )
    return (
        "# Index\n\n"
        "## Status Table\n\n"
        "| File | Status | Owner Agent | Last Updated | Freshness |\n"
        "|------|--------|-------------|--------------|----------|\n"
        f"{rows}\n"
    )


# ---------------------------------------------------------------------------
# TestRootReader
# ---------------------------------------------------------------------------


class TestRootReader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.roots = Path(self.tmp) / "roots"
        self.roots.mkdir()
        (self.roots / "project").mkdir()
        (self.roots / "agents").mkdir()
        (self.roots / "context").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_read_project_state_parses_correctly(self):
        state_md = (
            "# Project State\n\n"
            "## Current Phase\n\nTest phase\n\n"
            "## Completed\n\n- Item one\n- Item two\n\n"
            "## In Progress\n\n_Nothing._\n\n"
            "## Next\n\nNext priority text\n\n"
            "## Blockers\n\n_None._\n\n"
            "## Last Session Summary\n\nSummary text\n"
        )
        _write(self.roots / "project" / "state.md", state_md)

        reader = RootReader(self.roots)
        result = reader.read_project_state()

        self.assertTrue(result.success)
        state = result.data
        self.assertIsInstance(state, ProjectState)
        self.assertEqual(state.phase, "Test phase")
        self.assertEqual(state.completed, ["Item one", "Item two"])
        self.assertEqual(state.in_progress, [])
        self.assertIn("Next priority text", state.next_priority)
        self.assertEqual(state.blockers, [])
        self.assertIn("Summary text", state.last_session_summary)

    def test_read_decisions_returns_list(self):
        decisions_md = (
            "# Decision Log\n\n---\n\n"
            '### Decision: "First decision"\n'
            "**Date:** 2026-01-01\n"
            "**Rationale:** Because reasons\n"
            "**Alternatives considered:** None tried\n\n"
            '### Decision: "Second decision"\n'
            "**Date:** 2026-01-02\n"
            "**Rationale:** More reasons\n"
            "**Alternatives considered:** Other things\n"
        )
        _write(self.roots / "project" / "decisions.md", decisions_md)

        reader = RootReader(self.roots)
        result = reader.read_decisions()

        self.assertTrue(result.success)
        entries = result.data
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].decision, "First decision")
        self.assertEqual(entries[0].date, "2026-01-01")
        self.assertEqual(entries[0].rationale, "Because reasons")
        self.assertEqual(entries[1].decision, "Second decision")

    def test_read_unknown_agent_fails(self):
        reader = RootReader(self.roots)
        result = reader.read_agent_definition("unknown")

        self.assertFalse(result.success)
        self.assertIn("Unknown agent", result.error)

    def test_read_missing_file_fails(self):
        # project/state.md does not exist in this test
        reader = RootReader(self.roots)
        result = reader.read_project_state()

        self.assertFalse(result.success)
        self.assertIn("File not found", result.error)

    def test_read_codebase_map_parses_table(self):
        codebase_md = (
            "# Codebase Map\n\n"
            "## Module Registry\n\n"
            "| Module Name | Purpose | Owner Agent | Status | Last Modified |\n"
            "|-------------|---------|-------------|--------|---------------|\n"
            "| `core/seed.py` | The seed | Architect | `defined` | 2026-04-07 |\n"
        )
        _write(self.roots / "context" / "codebase.md", codebase_md)

        reader = RootReader(self.roots)
        result = reader.read_codebase_map()

        self.assertTrue(result.success)
        entries = result.data
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].module, "core/seed.py")
        self.assertEqual(entries[0].status, "defined")

    def test_read_unknown_region_fails(self):
        reader = RootReader(self.roots)
        result = reader.read_region_index("nonexistent")

        self.assertFalse(result.success)
        self.assertIn("Unknown region", result.error)


# ---------------------------------------------------------------------------
# TestRootWriter
# ---------------------------------------------------------------------------


class TestRootWriter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.roots = Path(self.tmp) / "roots"
        self.roots.mkdir()
        (self.roots / "project").mkdir()
        (self.roots / "context").mkdir()
        (self.roots / "quality").mkdir()

        _write(
            self.roots / "project" / "index.md",
            _make_index(["state.md", "decisions.md"]),
        )
        _write(
            self.roots / "context" / "index.md",
            _make_index(["codebase.md", "patterns.md", "failures.md"]),
        )
        _write(
            self.roots / "quality" / "index.md",
            _make_index(["repetition.md"]),
        )
        _write(
            self.roots / "context" / "patterns.md",
            "# Pattern Registry\n\n"
            "## Component Registry\n\n"
            "| Component Name | Purpose | Interface Shape | Locations | Instance Count | Pruning Candidate |\n"
            "|----------------|---------|-----------------|-----------|----------------|-------------------|\n"
            "| — | — | — | — | — | — |\n\n"
            "## Registration Protocol\n\nSome protocol text.\n",
        )
        _write(
            self.roots / "quality" / "repetition.md",
            "# Repetition Registry\n\n"
            "## Active Duplication\n\n"
            "| Pattern Name | Locations | Instance Count | Suggested Action | Status |\n"
            "|--------------|-----------|----------------|-----------------|--------|\n"
            "| — | — | — | — | — |\n",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_append_decision_roundtrip(self):
        _write(
            self.roots / "project" / "decisions.md",
            "# Decision Log\n\n---\n",
        )
        writer = RootWriter(self.roots)
        decision = DecisionEntry(
            date="2026-01-01",
            decision="Test decision",
            rationale="Test rationale",
            alternatives="Test alternatives",
        )
        result = writer.append_decision(decision)

        self.assertTrue(result.success)
        content = _read(self.roots / "project" / "decisions.md")
        self.assertIn("Test decision", content)
        self.assertIn("Test rationale", content)
        self.assertIn("**Date:** 2026-01-01", content)
        self.assertIn("**Rationale:** Test rationale", content)

    def test_mark_file_dirty_updates_index(self):
        writer = RootWriter(self.roots)
        result = writer.mark_file_dirty("project", "state.md")

        self.assertTrue(result.success)
        content = _read(self.roots / "project" / "index.md")
        self.assertIn("dirty", content)
        # Other files should still be clean
        self.assertIn("decisions.md | clean", content)

    def test_mark_file_clean_updates_index(self):
        writer = RootWriter(self.roots)
        writer.mark_file_dirty("project", "state.md")
        result = writer.mark_file_clean("project", "state.md")

        self.assertTrue(result.success)
        content = _read(self.roots / "project" / "index.md")
        self.assertIn("state.md | clean", content)

    def test_mark_unknown_file_fails(self):
        writer = RootWriter(self.roots)
        result = writer.mark_file_dirty("project", "ghost.md")

        self.assertFalse(result.success)
        self.assertIn("ghost.md", result.error)

    def test_append_pattern_adds_row(self):
        writer = RootWriter(self.roots)
        result = writer.append_pattern(
            "MyParser",
            "Parses markdown tables",
            "takes str, returns list",
            "root_manager/reader.py",
        )

        self.assertTrue(result.success)
        content = _read(self.roots / "context" / "patterns.md")
        self.assertIn("MyParser", content)
        self.assertNotIn("| — |", content)

    def test_append_pattern_flags_repetition(self):
        writer = RootWriter(self.roots)
        writer.append_pattern(
            "TestComponent",
            "Test purpose",
            "takes string, returns bool",
            "module/a.py",
        )
        writer.append_pattern(
            "TestComponent",
            "Test purpose",
            "takes string, returns bool",
            "module/b.py",
        )

        content = _read(self.roots / "quality" / "repetition.md")
        self.assertIn("TestComponent", content)
        self.assertIn("module/a.py", content)
        self.assertIn("module/b.py", content)

    def test_append_pattern_increments_count(self):
        writer = RootWriter(self.roots)
        writer.append_pattern("Comp", "purpose", "shape", "loc/a.py")
        writer.append_pattern("Comp", "purpose", "shape", "loc/b.py")
        writer.append_pattern("Comp", "purpose", "shape", "loc/c.py")

        content = _read(self.roots / "context" / "patterns.md")
        self.assertIn("| 3 |", content)

    def test_update_codebase_entry_upsert(self):
        _write(
            self.roots / "context" / "codebase.md",
            "# Codebase Map\n\n"
            "## Module Registry\n\n"
            "| Module Name | Purpose | Owner Agent | Status | Last Modified |\n"
            "|-------------|---------|-------------|--------|---------------|\n"
            "| `core/seed.py` | Old purpose | Architect | `defined` | 2026-04-06 |\n",
        )
        writer = RootWriter(self.roots)
        entry = CodebaseEntry(
            module="core/seed.py",
            purpose="New purpose",
            owner_agent="Builder",
            status="implemented",
            last_modified="2026-04-07",
        )
        result = writer.update_codebase_entry(entry)

        self.assertTrue(result.success)
        content = _read(self.roots / "context" / "codebase.md")
        self.assertIn("New purpose", content)
        self.assertNotIn("Old purpose", content)
        # Should be exactly one row for this module
        self.assertEqual(content.count("core/seed.py"), 1)

    def test_update_project_state_roundtrip(self):
        state = ProjectState(
            phase="Test phase",
            completed=["Thing one", "Thing two"],
            in_progress=[],
            next_priority="Build more things",
            blockers=[],
            last_session_summary="Did some work.",
        )
        writer = RootWriter(self.roots)
        result = writer.update_project_state(state)

        self.assertTrue(result.success)
        content = _read(self.roots / "project" / "state.md")
        self.assertIn("Test phase", content)
        self.assertIn("Thing one", content)
        self.assertIn("Build more things", content)
        self.assertIn("Did some work.", content)


# ---------------------------------------------------------------------------
# TestRootManager
# ---------------------------------------------------------------------------


class TestRootManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.roots = Path(self.tmp) / "roots"
        self.roots.mkdir()

        for region in ("project", "agents", "context", "quality", "flows"):
            (self.roots / region).mkdir()

        today = datetime.date.today().isoformat()

        _write(
            self.roots / "ROOT.md",
            "# Bonsai Root\n\n## Current Phase\n\nTest phase\n",
        )
        _write(
            self.roots / "project" / "state.md",
            "# Project State\n\n"
            "## Current Phase\n\nTest Phase\n\n"
            "## Completed\n\n- Done thing\n\n"
            "## In Progress\n\n_Nothing._\n\n"
            "## Next\n\nBuild something\n\n"
            "## Blockers\n\n_None._\n\n"
            "## Last Session Summary\n\nPrevious summary\n",
        )

        for region in ("project", "agents", "context", "quality", "flows"):
            _write(
                self.roots / region / "index.md",
                _make_index(["state.md"]),
            )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_begin_session_returns_orientation(self):
        manager = RootManager(self.roots)
        result = manager.begin_session("builder")

        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
        self.assertIn("phase", result.data)
        self.assertIn("next_priority", result.data)
        self.assertIn("blockers", result.data)
        self.assertIn("dirty_files", result.data)
        self.assertEqual(result.data["agent"], "builder")
        self.assertEqual(result.data["phase"], "Test Phase")

    def test_begin_session_populates_cache(self):
        manager = RootManager(self.roots)
        manager.begin_session("builder")

        # Cache should have entries from all five regions
        self.assertTrue(len(manager._session_cache) > 0)

    def test_needs_reread_returns_true_for_dirty(self):
        manager = RootManager(self.roots)
        manager._session_cache["project/state.md"] = FileStatus.DIRTY
        self.assertTrue(manager.needs_reread("project", "state.md"))

    def test_needs_reread_returns_false_for_clean(self):
        manager = RootManager(self.roots)
        manager._session_cache["project/state.md"] = FileStatus.CLEAN
        self.assertFalse(manager.needs_reread("project", "state.md"))

    def test_needs_reread_returns_true_for_unknown(self):
        manager = RootManager(self.roots)
        # Key not in cache at all
        self.assertTrue(manager.needs_reread("project", "unknown.md"))

    def test_reader_property(self):
        manager = RootManager(self.roots)
        self.assertIsInstance(manager.reader, RootReader)

    def test_writer_property(self):
        manager = RootManager(self.roots)
        self.assertIsInstance(manager.writer, RootWriter)

    def test_end_session_clears_cache(self):
        manager = RootManager(self.roots)
        manager._session_cache["project/state.md"] = FileStatus.CLEAN
        manager.end_session("builder", "Completed the work.")

        self.assertEqual(len(manager._session_cache), 0)

    def test_end_session_updates_state(self):
        manager = RootManager(self.roots)
        result = manager.end_session("builder", "Did important things.")

        self.assertTrue(result.success)
        content = _read(self.roots / "project" / "state.md")
        self.assertIn("Did important things.", content)


if __name__ == "__main__":
    unittest.main()
