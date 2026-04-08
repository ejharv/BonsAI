"""
Claude Code executor backend.
Runs agents via claude --print
subprocess. Uses Max plan
authentication. No API key needed.
"""

from __future__ import annotations
import subprocess
import time
from core.executor.base import (
    BaseExecutor,
    _parse_roots_updates,
)
from core.executor.models import (
    AgentPrompt,
    ExecutorResult,
    ExecutorStatus,
    ExecutorBackend,
    BudgetUsage,
)


class ClaudeCodeExecutor(BaseExecutor):
    """
    Executor that uses Claude Code CLI
    via subprocess with --print flag.
    Requires: claude CLI installed
    and authenticated with Max plan.
    """

    @property
    def backend(self) -> ExecutorBackend:
        raise NotImplementedError(
            "Phase 5 implementation"
        )

    def is_available(self) -> bool:
        """
        Check if claude CLI is on PATH.
        Run: claude --version
        Return True if exit code 0.
        """
        raise NotImplementedError(
            "Phase 5 implementation"
        )

    def execute(
        self,
        prompt: AgentPrompt,
        timeout_seconds: int = 120,
    ) -> ExecutorResult:
        """
        Build prompt text.
        Run: claude --print "{prompt_text}"
        Capture stdout as raw_output.
        Parse roots updates from output.
        Track wall time and output length.
        Return ExecutorResult.
        """
        raise NotImplementedError(
            "Phase 5 implementation"
        )

    def _parse_roots_updates(
        self,
        raw_output: str,
    ) -> dict[str, str]:
        """
        Parse <root_update> XML tags
        from raw output.
        Delegates to module-level
        _parse_roots_updates in base.py.
        """
        raise NotImplementedError(
            "Phase 5 implementation"
        )

    def _calculate_budget(
        self,
        wall_time: float,
        output_length: int,
    ) -> float:
        """
        Calculate budget units consumed
        from wall time and output length.
        Formula:
        base = wall_time_seconds * 0.1
        output_factor =
            output_length / 1000 * 0.05
        return base + output_factor
        This is approximate — claude_code
        mode cannot measure tokens.
        """
        raise NotImplementedError(
            "Phase 5 implementation"
        )
