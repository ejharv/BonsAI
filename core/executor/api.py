"""
Anthropic API executor backend.
Calls Claude directly via Python SDK.
Requires ANTHROPIC_API_KEY env var.
Provides precise token tracking.
"""

from __future__ import annotations
import os
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


class APIExecutor(BaseExecutor):
    """
    Executor that calls Anthropic API
    directly via Python SDK.
    Requires ANTHROPIC_API_KEY
    environment variable.
    Provides exact token counts for
    precise budget tracking.
    Model: claude-sonnet-4-20250514
    Always use this model string.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    @property
    def backend(self) -> ExecutorBackend:
        raise NotImplementedError(
            "Phase 5 implementation"
        )

    def is_available(self) -> bool:
        """
        Check if ANTHROPIC_API_KEY
        is set in environment.
        Do not validate the key —
        just check it exists and
        is non-empty.
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
        Call Anthropic API with
        the prompt as user message.
        Extract text from response.
        Parse roots updates from output.
        Track tokens from usage field.
        Return ExecutorResult.

        If anthropic SDK not installed
        return ExecutorResult with
        status FAILED and error:
        "anthropic SDK not installed.
        Run: pip install anthropic"
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
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate budget units from
        exact token counts.
        Formula:
        input_cost =
            input_tokens / 1000 * 0.1
        output_cost =
            output_tokens / 1000 * 0.3
        return input_cost + output_cost
        Output tokens weighted 3x
        because generation is more
        expensive than input processing.
        """
        raise NotImplementedError(
            "Phase 5 implementation"
        )
