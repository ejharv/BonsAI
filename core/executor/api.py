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
        return ExecutorBackend.API

    def is_available(self) -> bool:
        """
        Check if ANTHROPIC_API_KEY
        is set in environment.
        Do not validate the key —
        just check it exists and
        is non-empty.
        """
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        return bool(key.strip())

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
        """
        try:
            import anthropic
        except ImportError:
            return ExecutorResult(
                status=ExecutorStatus.FAILED,
                raw_output="",
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.API,
                    wall_time_seconds=0,
                    output_length_chars=0,
                    tokens_used=None,
                    budget_consumed=0,
                ),
                roots_updates={},
                error=(
                    "anthropic SDK not installed."
                    " Run: pip install anthropic"
                ),
            )

        start_time = time.time()
        prompt_text = self.build_prompt_text(prompt)

        try:
            client = anthropic.Anthropic()

            message = client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt_text,
                }],
            )

            raw_output = message.content[0].text
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            wall_time = time.time() - start_time

            return ExecutorResult(
                status=ExecutorStatus.SUCCESS,
                raw_output=raw_output,
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.API,
                    wall_time_seconds=wall_time,
                    output_length_chars=len(raw_output),
                    tokens_used=input_tokens + output_tokens,
                    budget_consumed=self._calculate_budget(
                        input_tokens, output_tokens
                    ),
                ),
                roots_updates=_parse_roots_updates(raw_output),
                error=None,
            )

        except Exception as e:
            wall_time = time.time() - start_time
            return ExecutorResult(
                status=ExecutorStatus.FAILED,
                raw_output="",
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.API,
                    wall_time_seconds=wall_time,
                    output_length_chars=0,
                    tokens_used=None,
                    budget_consumed=0,
                ),
                roots_updates={},
                error=str(e),
            )

    def _parse_roots_updates(
        self,
        raw_output: str,
    ) -> dict[str, str]:
        """
        Delegates to module-level
        _parse_roots_updates in base.py.
        """
        return _parse_roots_updates(raw_output)

    def _calculate_budget(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate budget units from
        exact token counts.
        Formula:
        input_cost = input_tokens / 1000 * 0.1
        output_cost = output_tokens / 1000 * 0.3
        Output tokens weighted 3x because
        generation is more expensive than
        input processing.
        """
        input_cost = input_tokens / 1000 * 0.1
        output_cost = output_tokens / 1000 * 0.3
        return round(input_cost + output_cost, 4)
