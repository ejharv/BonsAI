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
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def run_summary_report(
        self,
        limit: int = 10,
    ) -> str:
        """
        Generate a summary of recent
        runs as a formatted string.

        Format:
        # Recent Runs

        | Run | Task | Time | Success |
        | Nodes | Budget |
        |-----|------|------|---------|
        |-------|--------|
        | abc123 | implement... |
        | 12:34 | ✓ | 3 | 4.2 |

        Footer:
        Success rate: 85% (17/20 runs)
        Total budget: 42.3 units
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def budget_report(
        self,
        limit: int = 20,
    ) -> str:
        """
        Generate budget consumption
        report by agent type.

        Format:
        # Budget by Agent (last N runs)

        | Agent | Budget | % of Total |
        |-------|--------|------------|
        | builder | 34.2 | 72% |
        | tester  | 8.1  | 17% |
        | quality | 5.4  | 11% |

        Total: 47.7 units across N runs
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def tree_report(
        self,
        run_id: str,
    ) -> str:
        """
        Generate a detailed tree report
        for a specific run.

        Format:
        # Run {run_id[:8]}
        Task: {task}
        Time: {timestamp}
        Duration: {duration}s
        Success: {success}

        ## Execution Tree

        [COMPLETE] root (builder)
          budget: 5.2 | score: 0.85
          ├── [COMPLETE] child (builder)
          │     budget: 2.1 | score: 0.9
          └── [COMPLETE] child (tester)
                budget: 1.8 | score: 0.8

        ## Summary
        {summary text}
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def health_report(
        self,
        limit: int = 20,
    ) -> str:
        """
        Generate a health overview
        combining run history with
        roots/ quality data.

        Format:
        # Bonsai Health Report

        ## Run Health
        Success rate: 85%
        Avg budget per run: 12.3 units
        Avg nodes per run: 2.1
        Most pruned agent: builder (3)

        ## Quality Health
        Open repetitions: 4
        Open debt items: 2
        Patterns tracked: 8

        ## Recommendations
        - builder agent pruned 3 times
          consider refining its prompts
        - 4 open repetitions suggest
          consolidation opportunity
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _format_node_tree(
        self,
        node: dict,
        prefix: str = "",
        is_last: bool = True,
    ) -> str:
        """
        Recursive tree formatter.
        Returns formatted string
        not prints it.
        Same visual style as
        multi_command._print_node_tree
        but returns string.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )
