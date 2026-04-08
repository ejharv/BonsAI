"""
Persists run results to roots/runs/
and provides query access to run
history. Every completed run is
stored as a JSON file. An index
provides fast summary access without
reading individual run files.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from core.orchestrator.models import (
    RunResult,
    NodeResult,
    NodeStatus,
)


@dataclass
class RunSummary:
    """
    Lightweight summary of a single run.
    Built from the index — does not
    require reading the full run JSON.

    run_id: unique run identifier
    task: first 80 chars of task
    timestamp: ISO format datetime
    success: whether run succeeded
    total_nodes: nodes that executed
    pruned_nodes: nodes pruned
    max_depth: deepest node reached
    budget_consumed: total units used
    duration_seconds: wall clock time
    """
    run_id: str
    task: str
    timestamp: str
    success: bool
    total_nodes: int
    pruned_nodes: int
    max_depth: int
    budget_consumed: float
    duration_seconds: float


@dataclass
class StoredRun:
    """
    A fully loaded run from disk.
    Returned by load_run().
    root_result is a raw dict —
    not a reconstructed NodeResult.
    """
    run_id: str
    task: str
    timestamp: str
    duration_seconds: float
    success: bool
    summary: str
    total_nodes: int
    pruned_nodes: int
    max_depth_reached: int
    total_budget_consumed: float
    root_result: dict


class RunStore:
    """
    Persists and queries run history.
    Writes to roots/runs/ directory.
    One JSON file per run.
    One index.md for fast summaries.
    """

    def __init__(
        self,
        roots_path: Path,
    ):
        """
        roots_path: path to roots/
        Creates roots/runs/ if needed.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def save_run(
        self,
        result: RunResult,
        duration_seconds: float,
    ) -> Path:
        """
        Persist a RunResult to disk.
        Write {run_id}.json to
        roots/runs/.
        Update roots/runs/index.md
        with a new summary row.
        Return path to saved file.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def load_run(
        self,
        run_id: str,
    ) -> Optional[StoredRun]:
        """
        Load a specific run by id.
        Read {run_id}.json from
        roots/runs/.
        Return StoredRun or None
        if not found.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def list_runs(
        self,
        limit: int = 20,
    ) -> list[RunSummary]:
        """
        Return most recent run summaries.
        Read from index.md — do not
        read individual run files.
        Return list ordered most recent
        first, limited to limit entries.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def runs_for_task_pattern(
        self,
        pattern: str,
    ) -> list[RunSummary]:
        """
        Return summaries where task
        contains pattern string.
        Case insensitive match.
        Read from index only.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def budget_by_agent(
        self,
        limit: int = 20,
    ) -> dict[str, float]:
        """
        Return total budget consumed
        per agent type across recent runs.
        Load individual run files to
        traverse node trees.
        Return dict: agent_name → total
        ordered by total descending.
        limit: how many recent runs
        to include in calculation.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def success_rate(
        self,
        limit: int = 20,
    ) -> float:
        """
        Return fraction of recent runs
        that succeeded.
        Read from index only.
        limit: how many recent runs
        to include.
        Returns 0.0 if no runs exist.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _result_to_dict(
        self,
        result: RunResult,
        duration_seconds: float,
    ) -> dict:
        """
        Convert RunResult to a JSON
        serializable dict.
        Recursively converts NodeResult
        tree including all fields.
        BudgetUsage backend stored
        as string name not enum.
        NodeStatus stored as string.
        LifecycleStage stored as string.
        Signal fields stored as floats.
        Closure stored as dict or None.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _dict_to_summary(
        self,
        d: dict,
    ) -> RunSummary:
        """
        Convert a stored run dict
        to a RunSummary.
        Used when reading index entries.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _update_index(
        self,
        summary: RunSummary,
    ) -> None:
        """
        Append a new row to
        roots/runs/index.md.
        Create index.md if it
        does not exist with header.

        Table format:
        | run_id (8 chars) | task (40) |
        | timestamp | success |
        | nodes | budget | duration |

        Prepend new rows so most
        recent appears first.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )
