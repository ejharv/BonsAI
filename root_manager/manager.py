"""
The Root Manager is the single interface
agents use to interact with the roots/
file system. It composes the reader and
writer and adds session management —
tracking which files have been read in
this session and whether they need
re-reading due to dirty flags.

No agent imports RootReader or RootWriter
directly. All access goes through
RootManager.
"""

import datetime
from pathlib import Path
from root_manager.reader import RootReader
from root_manager.writer import RootWriter
from root_manager.models import (
    RootManagerResult,
    FileStatus,
)


class RootManager:
    """
    The single interface between agents
    and the roots/ file system.
    Composes reader and writer.
    Manages session-level file status
    cache so agents know what needs
    re-reading without checking
    indexes manually.
    """

    def __init__(self, roots_path: Path):
        """
        roots_path: absolute path to
        the roots/ directory.
        Initializes reader, writer, and
        empty session cache.
        """
        self.roots_path = Path(roots_path)
        self._reader = RootReader(roots_path)
        self._writer = RootWriter(roots_path)
        self._session_cache: dict[str, FileStatus] = {}
        self._current_agent: str = ""

    def begin_session(
        self,
        agent_name: str,
    ) -> RootManagerResult:
        """
        Called at the start of every
        agent session.
        Reads ROOT.md and state.md.
        Loads region indexes to build
        session file status cache.
        Returns orientation summary —
        current phase, last completed,
        next priority.
        agent_name: which agent is
        starting this session
        """
        self._current_agent = agent_name
        self._session_cache = {}

        # Read orientation documents
        self._reader.read_root_index()
        state_result = self._reader.read_project_state()
        state = state_result.data if state_result.success else None

        # Load file statuses from all five region indexes
        regions = ["project", "agents", "context", "quality", "flows"]
        for region in regions:
            index_result = self._reader.read_region_index(region)
            if index_result.success and index_result.data:
                statuses = _parse_status_table(index_result.data)
                for filename, status in statuses.items():
                    self._session_cache[f"{region}/{filename}"] = status

        dirty_files = [
            path
            for path, status in self._session_cache.items()
            if status == FileStatus.DIRTY
        ]

        return RootManagerResult.ok(
            "ROOT.md",
            data={
                "agent": agent_name,
                "phase": state.phase if state else "",
                "next_priority": (
                    state.next_priority if state else ""
                ),
                "blockers": state.blockers if state else [],
                "dirty_files": dirty_files,
            },
        )

    def end_session(
        self,
        agent_name: str,
        summary: str,
    ) -> RootManagerResult:
        """
        Called at the end of every
        agent session.
        Updates state.md with summary.
        Ensures all writes are flushed.
        Returns confirmation of
        session close.
        summary: what was accomplished
        in this session in plain english
        """
        state_result = self._reader.read_project_state()
        if state_result.success and state_result.data:
            state = state_result.data
            today = datetime.date.today().isoformat()
            session_entry = (
                f"**Session: {today} ({agent_name})**\n\n{summary}"
            )
            if state.last_session_summary:
                state.last_session_summary = (
                    state.last_session_summary
                    + "\n\n---\n\n"
                    + session_entry
                )
            else:
                state.last_session_summary = session_entry
            self._writer.update_project_state(state)

        self._session_cache = {}
        return RootManagerResult.ok(
            "session",
            data={"closed": True, "agent": agent_name},
        )

    def needs_reread(
        self,
        region: str,
        filename: str,
    ) -> bool:
        """
        Check whether a file has been
        marked dirty since this session
        began or since last read.
        Agents call this before using
        cached knowledge of a file.
        Returns True if agent must
        re-read before acting.
        """
        key = f"{region}/{filename}"
        if key not in self._session_cache:
            return True  # unknown — assume needs reading
        return self._session_cache[key] in (
            FileStatus.DIRTY,
            FileStatus.STALE,
        )

    @property
    def reader(self) -> RootReader:
        """
        Access the reader directly for
        read operations.
        """
        return self._reader

    @property
    def writer(self) -> RootWriter:
        """
        Access the writer directly for
        write operations.
        """
        return self._writer


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _parse_status_table(
    index_content: str,
) -> dict[str, FileStatus]:
    """
    Parse a region index.md and return
    {filename: FileStatus} mapping by
    reading the ## Status Table section.
    """
    result: dict[str, FileStatus] = {}
    in_status_table = False
    rows_seen = 0  # 0=header not yet, 1=header seen, 2+=data

    for line in index_content.splitlines():
        if "## Status Table" in line:
            in_status_table = True
            rows_seen = 0
            continue

        if not in_status_table:
            continue

        stripped = line.strip()

        if not stripped.startswith("|"):
            if stripped:
                in_status_table = False
            continue

        parts = line.split("|")
        if len(parts) < 4:
            continue

        rows_seen += 1
        if rows_seen == 1:
            continue  # column header row
        if rows_seen == 2:
            continue  # separator row (---|---)

        filename = parts[1].strip()
        status_str = parts[2].strip().lower()

        if not filename or filename == "File":
            continue

        if status_str == "dirty":
            result[filename] = FileStatus.DIRTY
        elif status_str == "stale":
            result[filename] = FileStatus.STALE
        else:
            result[filename] = FileStatus.CLEAN

    return result
