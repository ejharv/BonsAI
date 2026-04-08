"""
Terminal dashboard for bonsai status
command. Shows live project health,
recent runs, and budget trends in
a single terminal view.
"""

from __future__ import annotations
from pathlib import Path
from bonsai.observability.store import (
    RunStore,
)
from bonsai.observability.report import (
    ReportGenerator,
)
from root_manager.manager import (
    RootManager,
)


class Dashboard:
    """
    Renders a terminal dashboard
    showing current project state.
    Called by bonsai status command.
    """

    def __init__(
        self,
        store: RunStore,
        report: ReportGenerator,
        root_manager: RootManager,
    ):
        self.store = store
        self.report = report
        self.root_manager = root_manager

    def render(self) -> None:
        """
        Print full dashboard to terminal.

        Sections in order:
        1. Header with project name
           and current phase
        2. Recent runs table (last 5)
        3. Budget by agent (last 20)
        4. Quality health summary
        5. Next priority from state.md
        """
        self._render_header()
        self._render_recent_runs()
        self._render_budget_summary()
        self._render_quality_health()
        self._render_next_priority()

    def _render_header(self) -> None:
        """
        Print project header.
        Read phase from state.md.
        """
        state_result = (
            self.root_manager.reader
            .read_project_state()
        )
        phase = "Unknown"
        if state_result.success:
            phase = (
                state_result.data.phase
            )
        inner = 48
        phase_line = f"  {phase}"[:inner].ljust(inner)
        print(f"╔{'═' * inner}╗")
        print(f"║{'  Bonsai Status':<{inner}}║")
        print(f"║{phase_line}║")
        print(f"╚{'═' * inner}╝")
        print()

    def _render_recent_runs(
        self,
        limit: int = 5,
    ) -> None:
        """
        Print last N runs as a
        compact table.
        """
        summaries = self.store.list_runs(
            limit=limit
        )
        print("── Recent Runs ──")
        if not summaries:
            print(
                "  No runs yet. "
                "Run bonsai run first."
            )
            print()
            return
        print(
            f"{'Run':<10}"
            f"{'Success':<10}"
            f"{'Nodes':<8}"
            f"{'Budget':<10}"
            f"Task"
        )
        print("─" * 60)
        for s in summaries:
            icon = (
                "✓" if s.success else "✗"
            )
            task = s.task[:25]
            if len(s.task) > 25:
                task += "..."
            print(
                f"{s.run_id[:8]:<10}"
                f"{icon:<10}"
                f"{s.total_nodes:<8}"
                f"{s.budget_consumed:<10.2f}"
                f"{task}"
            )
        print()

    def _render_budget_summary(
        self,
    ) -> None:
        """
        Print budget by agent as
        a compact table.
        """
        by_agent = self.store.budget_by_agent()
        total = sum(by_agent.values())
        print("── Budget by Agent ──")
        if total == 0:
            print("  No budget data yet.")
            print()
            return
        for agent, budget in sorted(
            by_agent.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            pct = budget / total * 100
            bar_len = int(pct / 5)
            bar = "█" * bar_len
            print(
                f"  {agent:<15}"
                f"{budget:>7.2f} units"
                f"  {bar} {pct:.0f}%"
            )
        print(
            f"\n  Total: {total:.2f} units"
        )
        print()

    def _render_quality_health(
        self,
    ) -> None:
        """
        Print quality health summary.
        Read roots/quality/repetition.md
        and roots/quality/debt.md
        Count open items in each.
        """
        print("── Quality Health ──")

        rep_path = (
            self.root_manager.roots_path
            / "quality"
            / "repetition.md"
        )
        debt_path = (
            self.root_manager.roots_path
            / "quality"
            / "debt.md"
        )

        def count_open(path: Path) -> int:
            if not path.exists():
                return 0
            content = path.read_text()
            rows = [
                ln for ln in
                content.splitlines()
                if ln.startswith("|")
                and not ln.startswith("|--")
                and "open" in ln.lower()
            ]
            return max(0, len(rows) - 1)

        rep_count = count_open(rep_path)
        debt_count = count_open(debt_path)

        print(
            f"  Open repetitions: "
            f"{rep_count}"
        )
        print(
            f"  Open debt items:  "
            f"{debt_count}"
        )

        if rep_count > 3:
            print(
                "  ⚠ High repetition count"
                " — consider pruning"
            )
        print()

    def _render_next_priority(
        self,
    ) -> None:
        """
        Print next priority from
        roots/project/state.md.
        """
        state_result = (
            self.root_manager.reader
            .read_project_state()
        )
        print("── Next Priority ──")
        if state_result.success:
            next_p = (
                state_result.data
                .next_priority
            )
            print(f"  {next_p}")
        else:
            print("  Could not read state.md")
        print()
