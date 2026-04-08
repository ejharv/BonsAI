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
        raise NotImplementedError(
            "Phase 7 implementation"
        )

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

        Each section separated by
        a horizontal rule.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _render_header(self) -> None:
        """
        Print project header.
        Read phase from state.md.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _render_recent_runs(
        self,
        limit: int = 5,
    ) -> None:
        """
        Print last N runs as a
        compact table.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _render_budget_summary(
        self,
    ) -> None:
        """
        Print budget by agent as
        a compact table.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _render_quality_health(
        self,
    ) -> None:
        """
        Print quality health summary.
        Read roots/quality/repetition.md
        and roots/quality/debt.md
        Count open items in each.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )

    def _render_next_priority(
        self,
    ) -> None:
        """
        Print next priority from
        roots/project/state.md.
        """
        raise NotImplementedError(
            "Phase 7 implementation"
        )
