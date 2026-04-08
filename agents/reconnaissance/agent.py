"""
The reconnaissance agent is the first agent to run on any brownfield project.
It reads the existing codebase, integrates graphify output if available,
identifies domain boundaries, detects patterns, surfaces gaps, and produces
a ReconnaissanceOutput that drives roster creation and root population.

It is read-only with respect to the project codebase. It never modifies
source files. It only writes to roots/ via RootManager.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from root_manager.manager import RootManager
from agents.reconnaissance.models import (
    ReconnaissanceInput,
    ReconnaissanceOutput,
    ObservedDomain,
    DetectedPattern,
    DeveloperGap,
    ConfidenceLevel,
    GapSeverity,
)


class ReconnaissanceAgent:
    """
    Reads an existing codebase and produces a structured understanding
    of its domain boundaries, patterns, and gaps.

    Never modifies source files.
    Writes only to roots/ via RootManager.
    Asks developer only what it cannot determine from the codebase itself.
    """

    def __init__(
        self,
        root_manager: RootManager,
        project_path: Path,
    ):
        """
        root_manager: initialized RootManager pointed at the project's roots/
        project_path: absolute path to the project root
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def run(
        self,
        input: ReconnaissanceInput,
    ) -> ReconnaissanceOutput:
        """
        Main entry point. Runs the full reconnaissance pipeline in this order:

        1. begin_session via root_manager
        2. load_graphify_report if input.use_graphify is True
        3. scan_project_structure
        4. identify_domains
        5. detect_patterns
        6. analyze_git_history if input.trust_git_history
        7. identify_gaps
        8. propose_roster
        9. write_to_roots
        10. end_session via root_manager

        Returns ReconnaissanceOutput.
        Never raises — catches all errors and returns output with
        ready_to_proceed=False and the error in confidence_summary.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def load_graphify_report(
        self,
        report_path: Path,
    ) -> dict:
        """
        Read and parse GRAPH_REPORT.md produced by graphify.
        Returns parsed content as dict with keys: god_nodes, communities,
        connections, surprising_links.
        If file not found or unparseable returns empty dict and logs
        warning — graphify integration is optional not required.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def scan_project_structure(
        self,
    ) -> dict:
        """
        Walk the project directory tree.
        Collect: folder structure, file extensions present, config files found,
        entry points detected, package manifest contents.
        Returns raw structural data that identify_domains uses.
        Respects .gitignore patterns.
        Never reads file contents beyond config and manifest files at this
        stage — that is identify_domains responsibility.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def identify_domains(
        self,
        structure: dict,
        graphify_data: dict,
    ) -> list[ObservedDomain]:
        """
        Derive domain boundaries from structural data and graphify output
        combined. Each domain becomes one agent in the proposed roster.
        Assign ConfidenceLevel per domain based on strength of evidence.
        A domain needs at least two independent signals to reach HIGH
        confidence. One signal is MEDIUM. Guessed from name alone is LOW.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def detect_patterns(
        self,
        structure: dict,
    ) -> list[DetectedPattern]:
        """
        Find repeated structures in the codebase.
        Look for: similar file names across directories, duplicate class or
        function names, copy-pasted file structures.
        Mark is_repetition=True when the same pattern appears in multiple
        locations without evidence of intentional variation.
        These pre-populate quality/repetition.md.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def analyze_git_history(
        self,
    ) -> dict:
        """
        Read git log to extract signals.
        Collect: commit frequency per directory, co-change patterns (files
        that always change together), recent activity concentration.
        Co-change patterns are the most valuable signal — files that always
        change together are coupled regardless of folder structure.
        Returns dict of signals that identify_domains can use to refine
        domain boundaries.
        If git history unavailable returns empty dict gracefully.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def identify_gaps(
        self,
        domains: list[ObservedDomain],
        structure: dict,
    ) -> list[DeveloperGap]:
        """
        Determine what cannot be inferred from the codebase alone.
        Always check for these gaps:
        - Project purpose and direction (never in code)
        - Intentional vs accidental duplication
        - Deprecated vs active modules with low git activity
        - Compliance or security constraints
        - Planned but unbuilt areas
        Order gaps by GapSeverity.
        Respect involvement_preference — LOW preference means only BLOCKING
        gaps become questions, others get defaulted silently.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def propose_roster(
        self,
        domains: list[ObservedDomain],
    ) -> list[str]:
        """
        Derive agent names from domains.
        One agent per HIGH or MEDIUM confidence domain.
        LOW confidence domains get merged into nearest HIGH domain or flagged
        as a gap question.
        Always include quality agent regardless of domains found.
        Returns list of agent name strings that become agent .md files
        in roots/agents/.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )

    def write_to_roots(
        self,
        output: ReconnaissanceOutput,
    ) -> None:
        """
        Write reconnaissance findings to roots/ via RootManager.
        Writes in this order:
        1. context/codebase.md — one entry per domain
        2. context/dependencies.md — from domain dependencies
        3. context/patterns.md — all detected patterns
        4. quality/repetition.md — patterns where is_repetition is True
        5. project/state.md — update phase and next priority
        6. roots/agents/ — one .md file per proposed roster entry using
           standard agent template
        Never overwrites existing entries if existing_bonsai is True —
        merges instead.
        """
        raise NotImplementedError(
            "Phase 3 implementation"
        )
