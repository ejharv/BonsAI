"""
All write operations against the roots/
file system. Writers never read. Every
method returns a RootManagerResult.
After every write the writer marks the
file dirty in the region index so
dependent agents know to re-read.
"""

import datetime
from pathlib import Path
from root_manager.models import (
    RootManagerResult,
    ProjectState,
    DecisionEntry,
    CodebaseEntry,
    DependencyEntry,
    FileStatus,
)


class RootWriter:
    """
    Provides structured write access to
    the roots/ file system. All
    serialization of typed structures
    back to .md format happens here.
    Agents pass typed objects, never
    raw markdown strings.
    After every successful write, the
    writer marks the affected file as
    DIRTY in the region index.
    """

    def __init__(self, roots_path: Path):
        self.roots_path = Path(roots_path)
        if not self.roots_path.exists():
            raise ValueError(
                f"roots/ directory does not exist: {self.roots_path}"
            )

    def _write_file(
        self,
        relative_path: str,
        content: str,
    ) -> RootManagerResult:
        """
        Write content to roots_path/relative_path.
        Creates parent directories if needed.
        Ensures file ends with a newline.
        """
        full_path = self.roots_path / relative_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if not content.endswith("\n"):
                content += "\n"
            full_path.write_text(content, encoding="utf-8")
            return RootManagerResult.ok(relative_path)
        except OSError as e:
            return RootManagerResult.fail(relative_path, str(e))

    def _read_raw(self, relative_path: str) -> str:
        """
        Read file at relative_path.
        Returns empty string if file does not exist yet.
        """
        full_path = self.roots_path / relative_path
        if not full_path.exists():
            return ""
        return full_path.read_text(encoding="utf-8")

    def update_project_state(
        self,
        state: ProjectState,
    ) -> RootManagerResult:
        """
        Write updated state to
        roots/project/state.md.
        Called at end of every agent
        session to record progress.
        Marks state.md as DIRTY.
        """
        content = _serialize_project_state(state)
        result = self._write_file("project/state.md", content)
        if result.success:
            self.mark_file_dirty("project", "state.md")
        return result

    def append_decision(
        self,
        decision: DecisionEntry,
    ) -> RootManagerResult:
        """
        Append a new entry to
        roots/project/decisions.md.
        Called whenever an architectural
        decision is made that future
        agents should know about.
        Never overwrites existing entries.
        Marks decisions.md as DIRTY.
        """
        path = "project/decisions.md"
        content = self._read_raw(path)
        entry_block = (
            f"\n### Decision: \"{decision.decision}\"\n"
            f"**Date:** {decision.date}\n"
            f"**Rationale:** {decision.rationale}\n"
            f"**Alternatives considered:** {decision.alternatives}\n"
        )
        new_content = content.rstrip("\n") + "\n" + entry_block
        result = self._write_file(path, new_content)
        if result.success:
            self.mark_file_dirty("project", "decisions.md")
        return result

    def update_codebase_entry(
        self,
        entry: CodebaseEntry,
    ) -> RootManagerResult:
        """
        Add or update a module entry in
        roots/context/codebase.md.
        Called by builder after creating
        or significantly modifying a module.
        Marks codebase.md as DIRTY.
        """
        path = "context/codebase.md"
        content = self._read_raw(path)
        new_row = (
            f"| `{entry.module}` | {entry.purpose} | "
            f"{entry.owner_agent} | `{entry.status}` | "
            f"{entry.last_modified} |"
        )
        content = _upsert_in_content(
            content,
            "## Module Registry",
            entry.module,
            new_row,
        )
        result = self._write_file(path, content)
        if result.success:
            self.mark_file_dirty("context", "codebase.md")
        return result

    def update_dependency_entry(
        self,
        entry: DependencyEntry,
    ) -> RootManagerResult:
        """
        Add or update a dependency entry
        in roots/context/dependencies.md.
        Called by architect when new
        relationships between modules
        are established.
        Marks dependencies.md as DIRTY.
        """
        path = "context/dependencies.md"
        content = self._read_raw(path)
        depends_str = ", ".join(entry.depends_on)
        depended_str = ", ".join(entry.depended_on_by)
        new_row = (
            f"| `{entry.component}` | {depends_str} | "
            f"{depended_str} | `{entry.criticality}` |"
        )
        content = _upsert_in_content(
            content,
            "## Dependency Registry",
            entry.component,
            new_row,
        )
        result = self._write_file(path, content)
        if result.success:
            self.mark_file_dirty("context", "dependencies.md")
        return result

    def mark_file_dirty(
        self,
        region: str,
        filename: str,
    ) -> RootManagerResult:
        """
        Mark a specific file as DIRTY
        in its region index.md.
        Called automatically after every
        write operation.
        Signals to dependent agents that
        they must re-read before acting.
        """
        return self._update_file_status(region, filename, "dirty")

    def mark_file_clean(
        self,
        region: str,
        filename: str,
    ) -> RootManagerResult:
        """
        Mark a specific file as CLEAN
        in its region index.md.
        Called after an agent has
        successfully re-read a dirty file
        and acknowledged the update.
        """
        return self._update_file_status(region, filename, "clean")

    def _update_file_status(
        self,
        region: str,
        filename: str,
        status: str,
    ) -> RootManagerResult:
        """
        Core implementation shared by
        mark_file_dirty and mark_file_clean.
        Does NOT recursively mark the
        index itself as dirty.
        """
        index_path = f"{region}/index.md"
        content = self._read_raw(index_path)
        if not content:
            return RootManagerResult.fail(
                index_path,
                f"Index file not found: {index_path}",
            )
        new_content, found = _update_status_in_content(
            content, filename, status
        )
        if not found:
            return RootManagerResult.fail(
                index_path,
                f"{filename} not found in {index_path} status table",
            )
        return self._write_file(index_path, new_content)

    def append_failure(
        self,
        what_was_tried: str,
        why_it_failed: str,
        what_was_learned: str,
    ) -> RootManagerResult:
        """
        Append a new entry to
        roots/context/failures.md.
        Called by any agent when an
        approach fails so future agents
        do not repeat the same mistake.
        Marks failures.md as DIRTY.
        """
        path = "context/failures.md"
        content = self._read_raw(path)
        today = datetime.date.today().isoformat()
        new_row = (
            f"| {today} | {what_was_tried} | "
            f"{why_it_failed} | {what_was_learned} |"
        )
        content = _append_in_content(
            content, "## Failure Log", new_row
        )
        result = self._write_file(path, content)
        if result.success:
            self.mark_file_dirty("context", "failures.md")
        return result

    def append_pattern(
        self,
        component_name: str,
        purpose: str,
        interface_shape: str,
        location: str,
    ) -> RootManagerResult:
        """
        Add or update a pattern entry
        in roots/context/patterns.md.
        Called by builder after creating
        any reusable component.
        If component already exists,
        increments instance count and
        adds location to list.
        If instance count exceeds 1,
        also writes to
        roots/quality/repetition.md.
        Marks patterns.md as DIRTY.
        """
        path = "context/patterns.md"
        content = self._read_raw(path)

        existing = _find_pattern_row(content, component_name)

        if existing is not None:
            old_locations, old_count = existing
            new_locations = (
                old_locations + ", " + location
                if old_locations
                else location
            )
            new_count = old_count + 1
            pruning = "watch" if new_count > 1 else "no"
            new_row = (
                f"| {component_name} | {purpose} | "
                f"{interface_shape} | {new_locations} | "
                f"{new_count} | {pruning} |"
            )
            content = _upsert_in_content(
                content,
                "## Component Registry",
                component_name,
                new_row,
            )
        else:
            new_count = 1
            new_locations = location
            new_row = (
                f"| {component_name} | {purpose} | "
                f"{interface_shape} | {location} | 1 | no |"
            )
            content = _append_in_content(
                content, "## Component Registry", new_row
            )

        result = self._write_file(path, content)
        if result.success:
            self.mark_file_dirty("context", "patterns.md")
            if new_count > 1:
                self._flag_repetition(
                    component_name, new_locations, new_count
                )
        return result

    def _flag_repetition(
        self,
        component_name: str,
        locations: str,
        count: int,
    ) -> None:
        """
        Record detected duplication in
        quality/repetition.md.
        If component already listed:
            update count and locations.
        If not listed:
            append new row.
        Marks repetition.md as DIRTY.
        """
        path = "quality/repetition.md"
        content = self._read_raw(path)
        new_row = (
            f"| {component_name} | {locations} | {count} | "
            f"extract to shared utility | open |"
        )
        if _find_repetition_row(content, component_name):
            content = _upsert_in_content(
                content,
                "## Active Duplication",
                component_name,
                new_row,
            )
        else:
            content = _append_in_content(
                content, "## Active Duplication", new_row
            )
        self._write_file(path, content)
        self.mark_file_dirty("quality", "repetition.md")


# ---------------------------------------------------------------------------
# Module-level helpers for table manipulation
# ---------------------------------------------------------------------------


def _split_at_table(
    content: str,
    section_marker: str,
) -> tuple[list[str], list[str], list[str]]:
    """
    Find the markdown table under section_marker.
    Returns (pre, table_lines, post).

    pre  — every line up to and including the
           section header, plus any non-| lines
           between the header and the table
    table_lines — the consecutive | lines that
                  form the table
    post — everything after the table
    """
    lines = content.splitlines()
    phase = "before"  # before | in_section | in_table | after
    pre: list[str] = []
    table: list[str] = []
    post: list[str] = []

    for line in lines:
        if phase == "before":
            pre.append(line)
            if section_marker in line:
                phase = "in_section"
        elif phase == "in_section":
            if line.strip().startswith("|"):
                phase = "in_table"
                table.append(line)
            else:
                pre.append(line)
        elif phase == "in_table":
            if line.strip().startswith("|"):
                table.append(line)
            else:
                phase = "after"
                post.append(line)
        else:  # after
            post.append(line)

    return pre, table, post


def _rejoin(
    pre: list[str],
    table: list[str],
    post: list[str],
) -> str:
    return "\n".join(pre + table + post)


def _upsert_table_row(
    table_lines: list[str],
    match_value: str,
    new_row: str,
) -> list[str]:
    """
    Replace the row where the first column
    (stripped of backticks) == match_value.
    If not found, append new_row.
    Removes | — | placeholder rows in either case.
    """
    if not table_lines:
        return [new_row]

    header = table_lines[0]
    separator = table_lines[1] if len(table_lines) > 1 else ""
    data_rows = table_lines[2:]

    found = False
    new_data: list[str] = []
    for row in data_rows:
        cols = [c.strip() for c in row.split("|") if c.strip()]
        if not cols:
            new_data.append(row)
            continue
        col0 = cols[0].strip("`")
        if col0 == "—":
            continue  # drop placeholder
        elif col0 == match_value:
            new_data.append(new_row)
            found = True
        else:
            new_data.append(row)

    if not found:
        new_data.append(new_row)

    result = [header]
    if separator:
        result.append(separator)
    result.extend(new_data)
    return result


def _append_table_row(
    table_lines: list[str],
    new_row: str,
) -> list[str]:
    """
    Append new_row, removing any | — | placeholder rows.
    """
    if not table_lines:
        return [new_row]

    header = table_lines[0]
    separator = table_lines[1] if len(table_lines) > 1 else ""
    data_rows = table_lines[2:]

    new_data: list[str] = []
    for row in data_rows:
        cols = [c.strip() for c in row.split("|") if c.strip()]
        if cols and cols[0] == "—":
            continue  # drop placeholder
        new_data.append(row)
    new_data.append(new_row)

    result = [header]
    if separator:
        result.append(separator)
    result.extend(new_data)
    return result


def _upsert_in_content(
    content: str,
    section_marker: str,
    match_value: str,
    new_row: str,
) -> str:
    pre, table, post = _split_at_table(content, section_marker)
    new_table = _upsert_table_row(table, match_value, new_row)
    return _rejoin(pre, new_table, post)


def _append_in_content(
    content: str,
    section_marker: str,
    new_row: str,
) -> str:
    pre, table, post = _split_at_table(content, section_marker)
    new_table = _append_table_row(table, new_row)
    return _rejoin(pre, new_table, post)


def _update_status_in_content(
    content: str,
    filename: str,
    new_status: str,
) -> tuple[str, bool]:
    """
    Find the row in a Status Table where
    the first column == filename, then
    replace the second column with new_status.
    Returns (updated_content, was_found).
    """
    lines = content.splitlines()
    found = False
    result: list[str] = []

    for line in lines:
        if "|" in line:
            parts = line.split("|")
            # parts[1] is the filename column,
            # parts[2] is the status column.
            if len(parts) >= 4 and parts[1].strip() == filename:
                parts[2] = f" {new_status} "
                line = "|".join(parts)
                found = True
        result.append(line)

    return "\n".join(result), found


def _find_pattern_row(
    content: str,
    component_name: str,
) -> tuple[str, int] | None:
    """
    Search the Component Registry table for
    a row matching component_name.
    Returns (locations_str, instance_count)
    if found, None if not.
    """
    found_section = False
    in_table = False

    for line in content.splitlines():
        if "## Component Registry" in line:
            found_section = True
            continue

        if not found_section:
            continue

        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table and stripped:
                break  # table ended
            continue

        cols = [c.strip() for c in stripped.split("|") if c.strip()]
        if not cols:
            continue

        # Skip header, separator, placeholder
        if "Component Name" in cols[0]:
            continue
        if cols[0] == "—":
            continue
        if all(
            not c.replace("-", "").replace(":", "").strip()
            for c in cols
        ):
            continue

        in_table = True

        if cols[0] == component_name:
            locations = cols[3] if len(cols) > 3 else ""
            try:
                count = int(cols[4]) if len(cols) > 4 else 1
            except ValueError:
                count = 1
            return locations, count

    return None


def _find_repetition_row(
    content: str,
    component_name: str,
) -> bool:
    """
    Return True if component_name already
    has a row in the repetition.md table.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cols = [c.strip() for c in stripped.split("|") if c.strip()]
            if cols and cols[0] == component_name:
                return True
    return False


def _serialize_project_state(state: ProjectState) -> str:
    """
    Serialize a ProjectState back to the
    exact .md format that reader.py expects.
    """
    today = datetime.date.today().isoformat()

    def fmt_list(items: list[str], empty_msg: str) -> str:
        if not items:
            return f"_{empty_msg}_"
        return "\n".join(f"- {item}" for item in items)

    completed = fmt_list(state.completed, "Nothing yet.")
    in_progress = fmt_list(state.in_progress, "Nothing.")
    blockers = fmt_list(state.blockers, "None.")

    return (
        "# Project State\n\n"
        "> Snapshot of current work."
        " Updated at the start and end of every session.\n\n"
        "---\n\n"
        "## Current Phase\n\n"
        f"{state.phase}\n\n"
        "---\n\n"
        "## Completed\n\n"
        f"{completed}\n\n"
        "---\n\n"
        "## In Progress\n\n"
        f"{in_progress}\n\n"
        "---\n\n"
        "## Next\n\n"
        f"{state.next_priority}\n\n"
        "---\n\n"
        "## Blockers\n\n"
        f"{blockers}\n\n"
        "---\n\n"
        "## Last Session Summary\n\n"
        f"{state.last_session_summary}\n\n"
        "---\n\n"
        f"_Last updated: {today}_\n"
    )
