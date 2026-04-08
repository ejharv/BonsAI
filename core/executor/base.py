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
        raise NotImplementedError(
            "Phase 5 implementation"
        )
