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
        raise NotImplementedError(
            "Phase 2 implementation"
        )

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
        raise NotImplementedError(
            "Phase 2 implementation"
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
        raise NotImplementedError(
            "Phase 2 implementation"
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
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    @property
    def reader(self) -> RootReader:
        """
        Access the reader directly for
        read operations.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    @property
    def writer(self) -> RootWriter:
        """
        Access the writer directly for
        write operations.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )
