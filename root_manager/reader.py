"""
All read operations against the roots/
file system. Readers never write.
Every method returns a RootManagerResult.
Agents call readers to understand
project state before acting.
"""

from pathlib import Path
from root_manager.models import (
    RootManagerResult,
    ProjectState,
    DecisionEntry,
    CodebaseEntry,
    DependencyEntry,
    FileStatus,
)


class RootReader:
    """
    Provides structured read access to
    the roots/ file system. All parsing
    of .md content into typed structures
    happens here. Agents receive typed
    objects, never raw markdown strings.
    """

    VALID_AGENTS = {
        "architect",
        "builder",
        "tester",
        "quality",
        "evaluator",
    }
    VALID_REGIONS = {
        "project",
        "agents",
        "context",
        "quality",
        "flows",
    }

    def __init__(self, roots_path: Path):
        """
        roots_path: absolute path to
        the roots/ directory.
        Raises ValueError if the directory
        does not exist — missing roots/ is
        a configuration error, not runtime.
        """
        self.roots_path = Path(roots_path)
        if not self.roots_path.exists():
            raise ValueError(
                f"roots/ directory does not exist: {self.roots_path}"
            )

    def _read_file(self, relative_path: str) -> str:
        """
        Read file at roots_path/relative_path.
        Raises FileNotFoundError if missing.
        """
        full_path = self.roots_path / relative_path
        if not full_path.exists():
            raise FileNotFoundError(
                f"File not found: {relative_path}"
            )
        return full_path.read_text(encoding="utf-8")

    def read_root_index(self) -> RootManagerResult:
        """
        Read ROOT.md and return the
        master project index.
        Always the first call in any
        agent session.
        Returns: RootManagerResult with
        data as raw string — ROOT.md
        is too varied to fully type.
        """
        path = "ROOT.md"
        try:
            content = self._read_file(path)
            return RootManagerResult.ok(path, data=content)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )

    def read_project_state(self) -> RootManagerResult:
        """
        Read roots/project/state.md
        and return a typed ProjectState.
        Called at start of every session
        to understand current position.
        """
        path = "project/state.md"
        try:
            content = self._read_file(path)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )
        state = _parse_project_state(content)
        return RootManagerResult.ok(path, data=state)

    def read_decisions(self) -> RootManagerResult:
        """
        Read roots/project/decisions.md
        and return list of DecisionEntry.
        Called before any architectural
        decision to avoid contradicting
        established choices.

        Parses ### Decision: header format.
        Existing table-format entries
        (written before this system) are
        not parsed and return empty list.
        """
        path = "project/decisions.md"
        try:
            content = self._read_file(path)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )
        entries = _parse_decisions(content)
        return RootManagerResult.ok(path, data=entries)

    def read_codebase_map(self) -> RootManagerResult:
        """
        Read roots/context/codebase.md
        and return list of CodebaseEntry.
        Called by builder before creating
        anything new to understand what
        already exists.
        """
        path = "context/codebase.md"
        try:
            content = self._read_file(path)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )
        entries = _parse_table(
            content,
            "## Module Registry",
            _row_to_codebase_entry,
        )
        return RootManagerResult.ok(path, data=entries)

    def read_dependencies(self) -> RootManagerResult:
        """
        Read roots/context/dependencies.md
        and return list of DependencyEntry.
        Called by quality agent before
        any pruning proposal to assess
        blast radius.
        """
        path = "context/dependencies.md"
        try:
            content = self._read_file(path)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )
        entries = _parse_table(
            content,
            "## Dependency Registry",
            _row_to_dependency_entry,
        )
        return RootManagerResult.ok(path, data=entries)

    def read_patterns(self) -> RootManagerResult:
        """
        Read roots/context/patterns.md
        and return raw content.
        Called by builder before creating
        any new component to check if
        it already exists.
        """
        path = "context/patterns.md"
        try:
            content = self._read_file(path)
            return RootManagerResult.ok(path, data=content)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )

    def read_agent_definition(
        self,
        agent_name: str,
    ) -> RootManagerResult:
        """
        Read a specific agent definition
        from roots/agents/{agent_name}.md
        Called when an agent needs to
        understand another agent's domain
        before handing off work.
        agent_name: one of architect,
        builder, tester, quality, evaluator
        """
        if agent_name not in self.VALID_AGENTS:
            return RootManagerResult.fail(
                f"agents/{agent_name}.md",
                f"Unknown agent: {agent_name}",
            )
        path = f"agents/{agent_name}.md"
        try:
            content = self._read_file(path)
            return RootManagerResult.ok(path, data=content)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )

    def read_region_index(
        self,
        region: str,
    ) -> RootManagerResult:
        """
        Read a region's index.md and
        return raw string — region indexes
        are orientation documents, not
        parsed into typed structures.
        region: project, agents, context,
        quality, or flows
        """
        if region not in self.VALID_REGIONS:
            return RootManagerResult.fail(
                f"{region}/index.md",
                f"Unknown region: {region}",
            )
        path = f"{region}/index.md"
        try:
            content = self._read_file(path)
            return RootManagerResult.ok(path, data=content)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )

    def read_failures(self) -> RootManagerResult:
        """
        Read roots/context/failures.md
        and return raw content.
        Called before attempting any
        approach that might have been
        tried before.
        """
        path = "context/failures.md"
        try:
            content = self._read_file(path)
            return RootManagerResult.ok(path, data=content)
        except FileNotFoundError:
            return RootManagerResult.fail(
                path, f"File not found: {path}"
            )


# ---------------------------------------------------------------------------
# Module-level parse helpers
# These are functions, not methods, so writer.py can import them if needed.
# ---------------------------------------------------------------------------


def _split_cols(line: str) -> list[str]:
    """Split a | table row into stripped non-empty column values."""
    return [c.strip() for c in line.split("|") if c.strip()]


def _is_separator(cols: list[str]) -> bool:
    """Return True if this is a markdown table separator row (---|---)."""
    return bool(cols) and all(
        not c.replace("-", "").replace(":", "").strip()
        for c in cols
    )


def _parse_table(
    content: str,
    section_marker: str,
    row_fn,
) -> list:
    """
    Generic table parser.
    Finds the table under section_marker,
    skips the header and separator rows,
    calls row_fn on each data row.
    Returns list of results, skipping
    None returns from row_fn.
    """
    results = []
    in_section = False
    in_table = False

    for line in content.splitlines():
        if section_marker in line:
            in_section = True
            continue

        if not in_section:
            continue

        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break  # table ended
            continue

        cols = _split_cols(stripped)
        if not cols:
            continue

        if not in_table:
            # First | line is the header row — skip it
            in_table = True
            continue

        if _is_separator(cols):
            continue

        if cols[0] == "—":
            continue  # placeholder row

        entry = row_fn(cols)
        if entry is not None:
            results.append(entry)

    return results


def _row_to_codebase_entry(cols: list[str]):
    if len(cols) < 5:
        return None
    return CodebaseEntry(
        module=cols[0].strip("`"),
        purpose=cols[1],
        owner_agent=cols[2],
        status=cols[3].strip("`"),
        last_modified=cols[4],
    )


def _row_to_dependency_entry(cols: list[str]):
    if len(cols) < 4:
        return None
    depends_on = [
        x.strip().strip("`")
        for x in cols[1].split(",")
        if x.strip()
    ]
    depended_on_by = [
        x.strip().strip("`")
        for x in cols[2].split(",")
        if x.strip()
    ]
    return DependencyEntry(
        component=cols[0].strip("`"),
        depends_on=depends_on,
        depended_on_by=depended_on_by,
        criticality=cols[3].strip("`"),
    )


def _parse_project_state(content: str) -> ProjectState:
    """Parse state.md content into a ProjectState dataclass."""
    # Collect lines per section
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_section is not None:
                sections[current_section] = current_lines
            current_section = line[3:].strip()
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = current_lines

    def to_list(section_name: str) -> list[str]:
        """Extract bullet items (- or *) from a section."""
        items = []
        for line in sections.get(section_name, []):
            s = line.strip()
            if s.startswith("- ") or s.startswith("* "):
                items.append(s[2:].strip())
        return items

    def to_text(section_name: str) -> str:
        """Extract non-empty, non-divider text lines from a section."""
        kept = []
        for line in sections.get(section_name, []):
            s = line.strip()
            if s and s != "---" and not s.startswith("_Last"):
                kept.append(s)
        return "\n".join(kept).strip()

    def to_phase() -> str:
        # Phase is often wrapped in ** bold markers; strip them
        return to_text("Current Phase").strip("*").strip()

    # Support both "Next" and "Next Priority" as section names
    next_key = (
        "Next Priority"
        if "Next Priority" in sections
        else "Next"
    )

    return ProjectState(
        phase=to_phase(),
        completed=to_list("Completed"),
        in_progress=to_list("In Progress"),
        next_priority=to_text(next_key),
        blockers=to_list("Blockers"),
        last_session_summary=to_text("Last Session Summary"),
    )


def _parse_decisions(content: str) -> list[DecisionEntry]:
    """
    Parse ### Decision: header format entries.
    Each entry looks like:
        ### Decision: "text"
        **Date:** value
        **Rationale:** value
        **Alternatives considered:** value

    Table-format entries from before this
    system are silently skipped.
    """
    entries: list[DecisionEntry] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("### Decision:"):
            decision_text = (
                line[len("### Decision:"):].strip().strip('"')
            )
            date = rationale = alternatives = ""
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(
                "### Decision:"
            ):
                l = lines[i].strip()
                if l.startswith("**Date:**"):
                    date = l[len("**Date:**"):].strip()
                elif l.startswith("**Rationale:**"):
                    rationale = l[len("**Rationale:**"):].strip()
                elif l.startswith("**Alternatives considered:**"):
                    alternatives = l[
                        len("**Alternatives considered:**"):
                    ].strip()
                i += 1
            entries.append(
                DecisionEntry(
                    date=date,
                    decision=decision_text,
                    rationale=rationale,
                    alternatives=alternatives,
                )
            )
        else:
            i += 1
    return entries
