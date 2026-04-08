"""
Typed representations of every
meaningful structure in the roots/
file system. The Root Manager speaks
in these types — never in raw strings
or untyped dicts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto


class FileStatus(Enum):
    """
    CLEAN: content is current,
        safe to read without re-fetching
    DIRTY: content was recently written,
        dependent agents must re-read
    STALE: content has not been updated
        within its freshness window,
        treat with caution
    """

    CLEAN = auto()
    DIRTY = auto()
    STALE = auto()


class Freshness(Enum):
    """
    STATIC: changes rarely if ever,
        vision.md, decisions.md
    SLOW: changes between phases,
        agent definitions, flow contracts
    FAST: changes between sessions,
        codebase.md, dependencies.md
    REALTIME: changes within a session,
        state.md, repetition.md
    """

    STATIC = auto()
    SLOW = auto()
    FAST = auto()
    REALTIME = auto()


@dataclass
class RootFile:
    """
    region: which roots/ region
        this file belongs to
    filename: the .md filename
    path: full path from repo root
    status: current dirty/clean state
    freshness: how quickly this
        file becomes stale
    owner_agent: which agent is
        responsible for this file
    last_updated: ISO timestamp
        of last write
    dependents: list of agent names
        that must re-read when dirty
    """

    region: str
    filename: str
    path: str
    status: FileStatus
    freshness: Freshness
    owner_agent: str
    last_updated: str
    dependents: list[str] = field(
        default_factory=list
    )


@dataclass
class RegionIndex:
    """
    region: name matching roots/
        subdirectory
    purpose: one sentence describing
        what this region is for
    files: all RootFile entries
        in this region
    last_updated: most recent write
        across all files in region
    """

    region: str
    purpose: str
    files: list[RootFile]
    last_updated: str


@dataclass
class ProjectState:
    phase: str
    completed: list[str]
    in_progress: list[str]
    next_priority: str
    blockers: list[str]
    last_session_summary: str


@dataclass
class DecisionEntry:
    date: str
    decision: str
    rationale: str
    alternatives: str


@dataclass
class CodebaseEntry:
    module: str
    purpose: str
    owner_agent: str
    status: str
    last_modified: str


@dataclass
class DependencyEntry:
    """
    criticality: low, medium,
        high, or critical —
        used by pruning agent to
        assess blast radius
    """

    component: str
    depends_on: list[str]
    depended_on_by: list[str]
    criticality: str


@dataclass
class RootManagerResult:
    """
    success: whether operation succeeded
    path: which file was operated on
    data: parsed content if read operation
    error: description if success is False
    """

    success: bool
    path: str
    data: Optional[any] = None
    error: Optional[str] = None

    @classmethod
    def ok(
        cls,
        path: str,
        data: any = None,
    ) -> "RootManagerResult":
        """Convenience constructor for successful results."""
        return cls(success=True, path=path, data=data)

    @classmethod
    def fail(
        cls,
        path: str,
        error: str,
    ) -> "RootManagerResult":
        """Convenience constructor for failed results."""
        return cls(success=False, path=path, error=error)
