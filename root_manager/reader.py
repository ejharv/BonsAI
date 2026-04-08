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
    RegionIndex,
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

    def __init__(self, roots_path: Path):
        """
        roots_path: absolute path to
        the roots/ directory
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_root_index(
        self,
    ) -> RootManagerResult:
        """
        Read ROOT.md and return the
        master project index.
        Always the first call in any
        agent session.
        Returns: RootManagerResult with
        data as raw string — ROOT.md
        is too varied to fully type.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_project_state(
        self,
    ) -> RootManagerResult:
        """
        Read roots/project/state.md
        and return a typed ProjectState.
        Called at start of every session
        to understand current position.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_decisions(
        self,
    ) -> RootManagerResult:
        """
        Read roots/project/decisions.md
        and return list of DecisionEntry.
        Called before any architectural
        decision to avoid contradicting
        established choices.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_codebase_map(
        self,
    ) -> RootManagerResult:
        """
        Read roots/context/codebase.md
        and return list of CodebaseEntry.
        Called by builder before creating
        anything new to understand what
        already exists.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_dependencies(
        self,
    ) -> RootManagerResult:
        """
        Read roots/context/dependencies.md
        and return list of DependencyEntry.
        Called by quality agent before
        any pruning proposal to assess
        blast radius.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_patterns(
        self,
    ) -> RootManagerResult:
        """
        Read roots/context/patterns.md
        and return raw content.
        Called by builder before creating
        any new component to check if
        it already exists.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
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
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_region_index(
        self,
        region: str,
    ) -> RootManagerResult:
        """
        Read a region's index.md and
        return a typed RegionIndex.
        Called to understand what files
        exist in a region and their
        current status before deciding
        what to read next.
        region: project, agents, context,
        quality, or flows
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )

    def read_failures(
        self,
    ) -> RootManagerResult:
        """
        Read roots/context/failures.md
        and return raw content.
        Called before attempting any
        approach that might have been
        tried before.
        """
        raise NotImplementedError(
            "Phase 2 implementation"
        )
