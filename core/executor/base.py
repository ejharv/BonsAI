"""
Abstract base class for all executor
backends. Any new executor must
implement this interface. The rest
of Bonsai only speaks BaseExecutor.
"""

from __future__ import annotations
import re
from abc import ABC, abstractmethod
from core.executor.models import (
    AgentPrompt,
    ExecutorResult,
    ExecutorBackend,
)


def _parse_roots_updates(
    raw_output: str,
) -> dict[str, str]:
    """
    Parse <root_update> XML tags
    from raw output.
    Extract path attribute and
    content between tags.
    Return dict mapping path
    to content string.
    Return empty dict if no
    tags found.
    Shared by all executor backends.
    """
    pattern = re.compile(
        r'<root_update\s+path="([^"]+)">(.*?)</root_update>',
        re.DOTALL,
    )
    return {
        match.group(1): match.group(2)
        for match in pattern.finditer(raw_output)
    }


def _parse_file_writes(
    raw_output: str,
) -> dict[str, str]:
    """
    Parse <file_write> XML tags from
    agent output.
    Extract path attribute and content.
    Return dict mapping path to content.
    Only paths that do NOT start with
    roots/ are included here.
    roots/ paths go to roots_updates.
    Return empty dict if no tags found.
    Shared by all executor backends.
    """
    pattern = re.compile(
        r'<file_write\s+path="([^"]+)">(.*?)</file_write>',
        re.DOTALL,
    )
    return {
        match.group(1).strip(): match.group(2).strip()
        for match in pattern.finditer(raw_output)
        if not match.group(1).strip().startswith("roots/")
    }


class BaseExecutor(ABC):
    """
    Abstract executor. Receives an
    AgentPrompt, runs the agent,
    returns an ExecutorResult.
    Never raises — all errors are
    captured in ExecutorResult.
    """

    @property
    @abstractmethod
    def backend(self) -> ExecutorBackend:
        """
        Which backend this executor uses.
        """

    @abstractmethod
    def execute(
        self,
        prompt: AgentPrompt,
        timeout_seconds: int = 120,
    ) -> ExecutorResult:
        """
        Execute an agent prompt.
        Never raises exceptions —
        catch all errors and return
        ExecutorResult with status
        FAILED and error message.
        timeout_seconds: hard limit
        on execution time. Return
        ExecutorResult with status
        TIMEOUT if exceeded.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this executor backend
        is available and configured.
        claude_code: checks if claude
            CLI is on PATH
        api: checks if
            ANTHROPIC_API_KEY is set
        Returns True if ready to use.
        Does not raise.
        """

    def build_prompt_text(
        self,
        prompt: AgentPrompt,
    ) -> str:
        """
        Convert AgentPrompt to a
        plain text prompt string.
        Shared by both backends.
        Not abstract — both backends
        use the same prompt format.
        """
        ctx = prompt.context
        parts = []

        parts.append("# Bonsai Agent Execution")
        parts.append("")
        parts.append("## Your Identity")
        parts.append(ctx.agent_definition)
        parts.append("")
        parts.append("## Project Context")
        parts.append("")

        for path, content in ctx.relevant_roots.items():
            parts.append(f"### {path}")
            parts.append(content)
            parts.append("")

        parts.append("## Your Task")
        parts.append(ctx.task)
        parts.append("")

        parts.append("## Parent Intent")
        if prompt.seed_depth > 0 and prompt.parent_intent:
            parts.append(prompt.parent_intent)
        else:
            parts.append("This is a root level task.")
        parts.append("")

        parts.append("## Success Criteria")
        parts.append(prompt.success_criteria)
        parts.append("")

        parts.append("## Output Format")
        parts.append(ctx.output_format)
        parts.append("")

        parts.append("## Roots to Update")
        parts.append(
            "After completing your task update these roots/ files "
            "by providing complete new content between XML tags:"
        )
        parts.append("")
        for path in ctx.roots_to_update:
            parts.append(f'<root_update path="{path}">')
            parts.append("[provide complete file content]")
            parts.append("</root_update>")
            parts.append("")

        parts.append(
            "For changes to source code files outside roots/ provide the "
            "complete file content between file tags:\n\n"
            '<file_write path="core/example/file.py">\n'
            "complete file content here\n"
            "</file_write>\n\n"
            "Bonsai will write these files directly after execution."
        )
        parts.append("")

        parts.append("## Budget Awareness")
        parts.append(
            f"You have {prompt.budget_allocated} budget units for this task. "
            "Be efficient. Do not pad output. Complete the task and stop."
        )

        return "\n".join(parts)
