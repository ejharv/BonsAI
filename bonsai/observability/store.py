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
        self.roots_path = roots_path
        self.runs_path = roots_path / "runs"
        self.runs_path.mkdir(
            parents=True,
            exist_ok=True,
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
        import json
        d = self._result_to_dict(
            result, duration_seconds
        )
        run_file = (
            self.runs_path /
            f"{result.run_id}.json"
        )
        run_file.write_text(
            json.dumps(d, indent=2)
        )
        summary = RunSummary(
            run_id=result.run_id,
            task=result.task[:80],
            timestamp=d["timestamp"],
            success=result.success,
            total_nodes=result.total_nodes,
            pruned_nodes=result.pruned_nodes,
            max_depth=result.max_depth_reached,
            budget_consumed=(
                result.total_budget_consumed
            ),
            duration_seconds=duration_seconds,
        )
        self._update_index(summary)
        return run_file

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
        import json
        # Try exact match first
        run_file = (
            self.runs_path /
            f"{run_id}.json"
        )
        if not run_file.exists():
            # Prefix match for 8-char IDs
            # from index
            matches = list(
                self.runs_path.glob(
                    f"{run_id}*.json"
                )
            )
            if not matches:
                return None
            run_file = matches[0]

        try:
            d = json.loads(
                run_file.read_text()
            )
        except Exception:
            return None

        return StoredRun(
            run_id=d.get("run_id", run_id),
            task=d.get("task", ""),
            timestamp=d.get("timestamp", ""),
            duration_seconds=d.get(
                "duration_seconds", 0.0
            ),
            success=d.get("success", False),
            summary=d.get("summary", ""),
            total_nodes=d.get(
                "total_nodes", 0
            ),
            pruned_nodes=d.get(
                "pruned_nodes", 0
            ),
            max_depth_reached=d.get(
                "max_depth_reached", 0
            ),
            total_budget_consumed=d.get(
                "total_budget_consumed", 0.0
            ),
            root_result=d.get(
                "root_result", {}
            ),
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
        index_path = self.runs_path / "index.md"
        if not index_path.exists():
            return []

        content = index_path.read_text()
        summaries = []

        for line in content.splitlines():
            if not line.startswith("|"):
                continue
            # Skip header and separator rows
            stripped = line.strip()
            if stripped.startswith("|--") or stripped.startswith("| Run"):
                continue
            parts = [
                p.strip()
                for p in line.split("|")
            ]
            # Remove empty strings from
            # leading/trailing pipes
            parts = [p for p in parts if p]
            if len(parts) < 7:
                continue
            try:
                run_id = parts[0]
                task = parts[1]
                timestamp = parts[2]
                success = parts[3] == "✓"
                total_nodes = int(parts[4])
                budget = float(parts[5])
                duration_str = (
                    parts[6].rstrip("s")
                )
                duration = float(duration_str)
                summaries.append(RunSummary(
                    run_id=run_id,
                    task=task,
                    timestamp=timestamp,
                    success=success,
                    total_nodes=total_nodes,
                    pruned_nodes=0,
                    max_depth=0,
                    budget_consumed=budget,
                    duration_seconds=duration,
                ))
            except (ValueError, IndexError):
                continue

        return summaries[:limit]

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
        summaries = self.list_runs(
            limit=1000
        )
        return [
            s for s in summaries
            if pattern.lower() in
            s.task.lower()
        ]

    def budget_by_agent(
        self,
        limit: int = 20,
    ) -> dict[str, float]:
        """
        Return total budget consumed
        per agent type across recent runs.
        Phase 7: returns single entry
        {"all_agents": total} from
        summary data. Agent-level
        breakdown deferred to Phase 8.
        """
        summaries = self.list_runs(
            limit=limit
        )
        total = sum(
            s.budget_consumed
            for s in summaries
        )
        return {"all_agents": total}

    def success_rate(
        self,
        limit: int = 20,
    ) -> float:
        """
        Return fraction of recent runs
        that succeeded.
        Read from index only.
        Returns 0.0 if no runs exist.
        """
        summaries = self.list_runs(
            limit=limit
        )
        if not summaries:
            return 0.0
        successes = sum(
            1 for s in summaries
            if s.success
        )
        return successes / len(summaries)

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
        """
        def node_to_dict(
            nr: NodeResult,
        ) -> dict:
            budget = None
            if nr.budget_usage:
                budget = {
                    "backend": (
                        nr.budget_usage
                        .backend.name
                    ),
                    "wall_time_seconds": (
                        nr.budget_usage
                        .wall_time_seconds
                    ),
                    "output_length_chars": (
                        nr.budget_usage
                        .output_length_chars
                    ),
                    "tokens_used": (
                        nr.budget_usage
                        .tokens_used
                    ),
                    "budget_consumed": (
                        nr.budget_usage
                        .budget_consumed
                    ),
                }
            closure = None
            if nr.closure:
                closure = {
                    "partial_output": (
                        nr.closure.partial_output
                    ),
                    "termination_reason": (
                        nr.closure
                        .termination_reason
                    ),
                    "budget_returned": (
                        nr.closure.budget_returned
                    ),
                    "pattern_record": (
                        nr.closure.pattern_record
                    ),
                }
            return {
                "node_id": nr.node_id,
                "status": nr.status.name,
                "output": nr.output,
                "agent_name": "unknown",
                "signal": {
                    "contribution_score": (
                        nr.signal
                        .contribution_score
                    ),
                    "complexity_delta": (
                        nr.signal.complexity_delta
                    ),
                    "confidence": (
                        nr.signal.confidence
                    ),
                    "value_efficiency": (
                        nr.signal.value_efficiency
                    ),
                },
                "closure": closure,
                "child_results": [
                    node_to_dict(c)
                    for c in nr.child_results
                ],
                "budget_usage": budget,
                "depth": nr.depth,
            }

        from datetime import datetime
        return {
            "run_id": result.run_id,
            "task": result.task,
            "timestamp": (
                datetime.now().isoformat()
            ),
            "duration_seconds": (
                duration_seconds
            ),
            "root_result": node_to_dict(
                result.root_result
            ),
            "total_budget_consumed": (
                result.total_budget_consumed
            ),
            "total_nodes": result.total_nodes,
            "pruned_nodes": result.pruned_nodes,
            "max_depth_reached": (
                result.max_depth_reached
            ),
            "success": result.success,
            "summary": result.summary,
        }

    def _dict_to_summary(
        self,
        d: dict,
    ) -> RunSummary:
        """
        Convert a stored run dict
        to a RunSummary.
        """
        return RunSummary(
            run_id=d.get("run_id", ""),
            task=d.get("task", "")[:80],
            timestamp=d.get("timestamp", ""),
            success=d.get("success", False),
            total_nodes=d.get(
                "total_nodes", 0
            ),
            pruned_nodes=d.get(
                "pruned_nodes", 0
            ),
            max_depth=d.get(
                "max_depth_reached", 0
            ),
            budget_consumed=d.get(
                "total_budget_consumed", 0.0
            ),
            duration_seconds=d.get(
                "duration_seconds", 0.0
            ),
        )

    def _update_index(
        self,
        summary: RunSummary,
    ) -> None:
        """
        Prepend a new row to
        roots/runs/index.md.
        Create index.md with header
        if it does not exist.
        Most recent run appears first.
        """
        index_path = (
            self.runs_path / "index.md"
        )

        header = (
            "# Run Index\n\n"
            "| Run ID | Task | Timestamp |"
            " Success | Nodes | Budget |"
            " Duration |\n"
            "|--------|------|-----------|"
            "---------|-------|--------|"
            "----------|\n"
        )

        new_row = (
            f"| {summary.run_id[:8]} |"
            f" {summary.task[:40]} |"
            f" {summary.timestamp[:19]} |"
            f" {'✓' if summary.success else '✗'} |"
            f" {summary.total_nodes} |"
            f" {summary.budget_consumed:.2f} |"
            f" {summary.duration_seconds:.1f}s |\n"
        )

        if index_path.exists():
            content = index_path.read_text()
            lines = content.splitlines(
                keepends=True
            )
            header_lines = []
            data_lines = []
            in_header = True
            for line in lines:
                if in_header and (
                    line.startswith("|--")
                ):
                    header_lines.append(line)
                    in_header = False
                elif in_header:
                    header_lines.append(line)
                else:
                    data_lines.append(line)
            existing = (
                "".join(header_lines) +
                new_row +
                "".join(data_lines)
            )
        else:
            existing = header + new_row

        index_path.write_text(existing)
