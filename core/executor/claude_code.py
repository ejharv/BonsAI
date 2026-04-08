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
        return ExecutorBackend.CLAUDE_CODE

    def is_available(self) -> bool:
        """
        Check if claude CLI is on PATH.
        Run: claude --version
        Return True if exit code 0.
        """
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

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
        start_time = time.time()
        prompt_text = self.build_prompt_text(prompt)

        try:
            result = subprocess.run(
                ["claude", "--print", prompt_text],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return ExecutorResult(
                status=ExecutorStatus.TIMEOUT,
                raw_output="",
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.CLAUDE_CODE,
                    wall_time_seconds=float(timeout_seconds),
                    output_length_chars=0,
                    tokens_used=None,
                    budget_consumed=self._calculate_budget(
                        float(timeout_seconds), 0
                    ),
                ),
                roots_updates={},
                error=f"Execution timed out after {timeout_seconds}s",
            )
        except Exception as e:
            wall_time = time.time() - start_time
            return ExecutorResult(
                status=ExecutorStatus.FAILED,
                raw_output="",
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.CLAUDE_CODE,
                    wall_time_seconds=wall_time,
                    output_length_chars=0,
                    tokens_used=None,
                    budget_consumed=self._calculate_budget(wall_time, 0),
                ),
                roots_updates={},
                error=str(e),
            )

        wall_time = time.time() - start_time
        raw_output = result.stdout

        return ExecutorResult(
            status=(
                ExecutorStatus.SUCCESS
                if result.returncode == 0
                else ExecutorStatus.FAILED
            ),
            raw_output=raw_output,
            budget_usage=BudgetUsage(
                backend=ExecutorBackend.CLAUDE_CODE,
                wall_time_seconds=wall_time,
                output_length_chars=len(raw_output),
                tokens_used=None,
                budget_consumed=self._calculate_budget(
                    wall_time, len(raw_output)
                ),
            ),
            roots_updates=_parse_roots_updates(raw_output),
            error=(
                None if result.returncode == 0 else result.stderr
            ),
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
        """
        base = wall_time * 0.1
        output_factor = output_length / 1000 * 0.05
        return round(base + output_factor, 4)
