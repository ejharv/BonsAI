"""
Typed inputs and outputs for the reconnaissance agent. These structures
define what the agent receives, what it produces, and what questions it
asks the developer to fill gaps.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto


class ConfidenceLevel(Enum):
    """
    How certain the reconnaissance agent is about an observed domain.

    HIGH: directly observed from code structure, config files, or
        explicit documentation
    MEDIUM: inferred from patterns, naming conventions, or
        git history signals
    LOW: guessed from minimal signal, requires developer confirmation
    """

    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class GapSeverity(Enum):
    """
    How critical it is to fill a developer gap before proceeding.

    BLOCKING: cannot derive agent roster or begin work without this
    IMPORTANT: significantly affects roster quality if missing
    OPTIONAL: nice to have, system proceeds with reasonable default
    """

    BLOCKING = auto()
    IMPORTANT = auto()
    OPTIONAL = auto()


@dataclass
class ObservedDomain:
    """
    A domain boundary identified by the reconnaissance agent.

    name: short identifier for this domain e.g. "authentication"
    purpose: one sentence describing what this domain does
    confidence: how certain we are this is a real domain boundary
    evidence: list of specific signals that led to this conclusion
        e.g. "src/auth/ directory exists", "AuthService imported in 4 files"
    file_paths: files that belong to this domain
    dependencies: other domain names this domain depends on
    """

    name: str
    purpose: str
    confidence: ConfidenceLevel
    evidence: list[str]
    file_paths: list[str]
    dependencies: list[str]


@dataclass
class DetectedPattern:
    """
    A structural pattern found in the codebase, including repetitions.

    name: component or pattern name
    pattern_type: component, utility, service, hook, middleware, other
    locations: file paths where found
    instance_count: how many times this pattern appears
    is_repetition: True if instance_count greater than 1 and locations
        are not intentional variations
    """

    name: str
    pattern_type: str
    locations: list[str]
    instance_count: int
    is_repetition: bool


@dataclass
class DeveloperGap:
    """
    Something the reconnaissance agent cannot determine from the codebase
    alone and must ask the developer.

    question: the specific question to ask the developer
        must be answerable in one sentence or a short list
    severity: how much this matters
    context: why Bonsai needs this, what it cannot determine alone
    default_if_skipped: what Bonsai assumes if developer does not
        answer within timeout window
    affects: list of root files or agent definitions that depend
        on the answer
    """

    question: str
    severity: GapSeverity
    context: str
    default_if_skipped: str
    affects: list[str]


@dataclass
class ReconnaissanceInput:
    """
    Everything the reconnaissance agent needs to begin a run.

    project_path: absolute path to the project being onboarded
    use_graphify: whether graphify was run before reconnaissance
    graphify_report_path: path to GRAPH_REPORT.md if use_graphify
        is True, None otherwise
    trust_git_history: whether to use commit history as signal for
        domain boundaries and ownership
    involvement_preference: high, medium, or low —
        controls how many gap questions get asked vs defaulted
    existing_bonsai: True if project already has a roots/ directory;
        agent will merge not overwrite
    """

    project_path: str
    use_graphify: bool
    graphify_report_path: Optional[str]
    trust_git_history: bool
    involvement_preference: str
    existing_bonsai: bool


@dataclass
class ReconnaissanceOutput:
    """
    Everything the reconnaissance agent produces from a single run.

    observed_domains: all domains the agent identified with confidence
    detected_patterns: patterns found including repetitions
    developer_gaps: questions that must or should be answered before
        roster is finalized; ordered by severity
    proposed_roster: list of agent names derived from observed domains;
        one agent per domain boundary
    health_observations: immediate quality issues found —
        obvious duplication, dead code, structural inconsistencies;
        these pre-populate quality/
    confidence_summary: one paragraph plain english summary of what
        was found confidently vs what is uncertain
    ready_to_proceed: True only if no BLOCKING gaps remain;
        False means developer must answer blocking questions first
    """

    observed_domains: list[ObservedDomain]
    detected_patterns: list[DetectedPattern]
    developer_gaps: list[DeveloperGap]
    proposed_roster: list[str]
    health_observations: list[str]
    confidence_summary: str
    ready_to_proceed: bool
