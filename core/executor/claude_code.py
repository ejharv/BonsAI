"""
Claude Code executor backend.
Runs agents via claude --print
subprocess. Uses Max plan
authentication. No API key needed.
"""

from __future__ import annotations
import itertools
import subprocess
import sys
import threading
import time
from core.executor.base import (
    BaseExecutor,
    _parse_roots_updates,
    _parse_file_writes,
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
        timeout_seconds: int = 300,
    ) -> ExecutorResult:
        """
        Build prompt text.
        Run: claude --print "{prompt_text}"
        in a background thread while a
        spinner runs on the main thread.
        Capture stdout as raw_output.
        Parse roots updates from output.
        Track wall time and output length.
        Return ExecutorResult.
        """
        start_time = time.time()
        prompt_text = self.build_prompt_text(prompt)

        result_container: dict = {"result": None}
        error_container: dict = {"error": None}

        def run_subprocess() -> None:
            try:
                result_container["result"] = subprocess.run(
                    ["claude", "--print", prompt_text],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                error_container["error"] = "timeout"
            except Exception as e:
                error_container["error"] = str(e)

        thread = threading.Thread(
            target=run_subprocess,
            daemon=True,
        )
        thread.start()

        spinner = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        elapsed = 0.0
        while thread.is_alive():
            frame = next(spinner)
            elapsed = time.time() - start_time
            sys.stdout.write(
                f"\r  {frame} Agent thinking... {elapsed:.0f}s"
            )
            sys.stdout.flush()
            thread.join(timeout=0.1)

        sys.stdout.write(
            f"\r  ✓ Agent responded in {elapsed:.0f}s          \n"
        )
        sys.stdout.flush()

        wall_time = time.time() - start_time

        if error_container["error"] == "timeout":
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
                file_writes={},
                error=(
                    f"Execution timed out after {timeout_seconds}s."
                    f" Try: --timeout 300"
                ),
            )

        if error_container["error"]:
            return ExecutorResult(
                status=ExecutorStatus.FAILED,
                raw_output="",
                budget_usage=BudgetUsage(
                    backend=ExecutorBackend.CLAUDE_CODE,
                    wall_time_seconds=wall_time,
                    output_length_chars=0,
                    tokens_used=None,
                    budget_consumed=0.0,
                ),
                roots_updates={},
                file_writes={},
                error=error_container["error"],
            )

        proc = result_container["result"]
        raw_output = proc.stdout

        return ExecutorResult(
            status=(
                ExecutorStatus.SUCCESS
                if proc.returncode == 0
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
            file_writes=_parse_file_writes(raw_output),
            error=(
                None if proc.returncode == 0 else proc.stderr
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
