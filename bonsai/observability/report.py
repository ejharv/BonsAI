"""
Generates human readable reports
from run history. Reports are printed
to terminal or written to markdown
files in roots/reports/.
"""

from __future__ import annotations
from pathlib import Path
from bonsai.observability.store import (
    RunStore,
    RunSummary,
)
from core.orchestrator.models import (
    RunResult,
    NodeResult,
    NodeStatus,
)


class ReportGenerator:
    """
    Generates reports from run history.
    All output methods return strings.
    Callers decide whether to print
    or write to file.
    """

    def __init__(
        self,
        store: RunStore,
    ):
        self.store = store

    def run_summary_report(
        self,
        limit: int = 10,
    ) -> str:
        """
        Generate a summary of recent
        runs as a formatted string.
        """
        summaries = self.store.list_runs(
            limit=limit
        )
        if not summaries:
            return (
                "# Recent Runs\n\n"
                "No runs recorded yet.\n"
                "Run `bonsai run` or "
                "`bonsai run-multi` first.\n"
            )

        rate = self.store.success_rate(
            limit=limit
        )

        lines = [
            "# Recent Runs\n\n",
            "| Run | Task | Timestamp |"
            " Success | Nodes | Budget |\n",
            "|-----|------|-----------|"
            "---------|-------|--------|\n",
        ]

        for s in summaries:
            icon = "✓" if s.success else "✗"
            task_short = s.task[:35]
            if len(s.task) > 35:
                task_short += "..."
            lines.append(
                f"| {s.run_id[:8]} |"
                f" {task_short} |"
                f" {s.timestamp[:16]} |"
                f" {icon} |"
                f" {s.total_nodes} |"
                f" {s.budget_consumed:.2f}"
                f" |\n"
            )

        total_budget = sum(
            s.budget_consumed
            for s in summaries
        )
        success_count = sum(
            1 for s in summaries
            if s.success
        )

        lines.append(
            f"\nSuccess rate: "
            f"{rate:.0%} "
            f"({success_count}/"
            f"{len(summaries)} runs)\n"
        )
        lines.append(
            f"Total budget: "
            f"{total_budget:.2f} units\n"
        )

        return "".join(lines)

    def budget_report(
        self,
        limit: int = 20,
    ) -> str:
        """
        Generate budget consumption
        report by agent type.
        """
        by_agent = self.store.budget_by_agent(
            limit=limit
        )
        total = sum(by_agent.values())

        if total == 0:
            return (
                "# Budget Report\n\n"
                "No budget data yet.\n"
            )

        lines = [
            f"# Budget by Agent"
            f" (last {limit} runs)\n\n",
            "| Agent | Budget | % of Total |\n",
            "|-------|--------|------------|\n",
        ]

        for agent, budget in sorted(
            by_agent.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            pct = budget / total * 100
            lines.append(
                f"| {agent} |"
                f" {budget:.2f} |"
                f" {pct:.0f}% |\n"
            )

        lines.append(
            f"\nTotal: {total:.2f} units"
            f" across last {limit} runs\n"
        )

        return "".join(lines)

    def tree_report(
        self,
        run_id: str,
    ) -> str:
        """
        Generate a detailed tree report
        for a specific run.
        """
        run = self.store.load_run(run_id)
        if run is None:
            return (
                f"# Run Not Found\n\n"
                f"No run with ID: {run_id}\n"
            )

        tree_str = self._format_node_tree(
            run.root_result
        )

        return (
            f"# Run {run.run_id[:8]}\n\n"
            f"**Task:** {run.task}\n"
            f"**Time:** {run.timestamp}\n"
            f"**Duration:** "
            f"{run.duration_seconds:.1f}s\n"
            f"**Success:** "
            f"{'✓' if run.success else '✗'}"
            f"\n\n"
            f"## Execution Tree\n\n"
            f"```\n{tree_str}```\n\n"
            f"## Summary\n\n"
            f"{run.summary}\n"
        )

    def health_report(
        self,
        limit: int = 20,
    ) -> str:
        """
        Generate a health overview
        combining run history with
        roots/ quality data.
        """
        rate = self.store.success_rate()
        summaries = self.store.list_runs()

        avg_budget = (
            sum(s.budget_consumed
                for s in summaries) /
            max(len(summaries), 1)
        )
        avg_nodes = (
            sum(s.total_nodes
                for s in summaries) /
            max(len(summaries), 1)
        )
        total_pruned = sum(
            s.pruned_nodes
            for s in summaries
        )

        lines = [
            "# Bonsai Health Report\n\n",
            "## Run Health\n\n",
            f"Success rate: {rate:.0%}\n",
            f"Avg budget per run: "
            f"{avg_budget:.2f} units\n",
            f"Avg nodes per run: "
            f"{avg_nodes:.1f}\n",
            f"Total pruned nodes: "
            f"{total_pruned}\n\n",
            "## Recommendations\n\n",
        ]

        if rate < 0.7:
            lines.append(
                "- Success rate below 70% "
                "— review agent prompts "
                "and task specificity\n"
            )
        if avg_budget > 20.0:
            lines.append(
                "- High average budget — "
                "consider breaking tasks "
                "into smaller units\n"
            )
        if total_pruned > len(summaries):
            lines.append(
                "- High pruning rate — "
                "agents may be receiving "
                "tasks outside their domain\n"
            )
        if not any([
            rate < 0.7,
            avg_budget > 20.0,
            total_pruned > len(summaries),
        ]):
            lines.append(
                "- System health looks good\n"
            )

        return "".join(lines)

    def _format_node_tree(
        self,
        node: dict,
        prefix: str = "",
        is_last: bool = True,
    ) -> str:
        """
        Recursive tree formatter.
        Returns formatted string.
        """
        status = node.get("status", "?")
        node_id = node.get(
            "node_id", "?"
        )[:8]
        depth = node.get("depth", 0)
        budget = (
            node.get("budget_usage") or {}
        ).get("budget_consumed", 0.0)
        score = (
            node.get("signal") or {}
        ).get("contribution_score", 0.0)

        connector = (
            "└── " if is_last else "├── "
        )
        line_prefix = (
            prefix + connector
            if prefix else ""
        )

        result = (
            f"{line_prefix}"
            f"[{status}] {node_id} "
            f"depth={depth}\n"
        )
        child_prefix = prefix + (
            "    " if is_last else "│   "
        )
        result += (
            f"{child_prefix}"
            f"  budget: {budget:.2f} |"
            f" score: {score:.2f}\n"
        )

        children = node.get(
            "child_results", []
        )
        for i, child in enumerate(children):
            result += self._format_node_tree(
                child,
                child_prefix,
                i == len(children) - 1,
            )
        return result
