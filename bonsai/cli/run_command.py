"""
Implementation of bonsai run.
Routes a task to the appropriate
agent, constructs an AgentPrompt,
executes via configured backend,
applies roots updates, and reports
results to the developer.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from core.executor.base import (
    BaseExecutor
)
from core.executor.models import (
    AgentPrompt,
    AgentContext,
    ExecutorResult,
    ExecutorStatus,
)
from root_manager.manager import (
    RootManager
)


def run_task(args) -> bool:
    """
    Execute bonsai run command.
    Returns True on success,
    False on failure.

    Steps:
    1. Load .bonsai config
    2. Validate project is initialized
    3. Select executor backend
    4. Read relevant agent definition
    5. Load relevant roots context
    6. Build AgentPrompt
    7. Execute via executor
    8. Apply roots updates
    9. Report results
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )


def _load_bonsai_config(
    project_path: Path,
) -> dict:
    """
    Read .bonsai config file.
    Return dict of key=value pairs.
    Return empty dict if file
    not found.
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )


def _select_executor(
    config: dict,
    forced_backend: Optional[str],
) -> BaseExecutor:
    """
    Choose executor based on config
    and --executor flag.
    forced_backend overrides config.
    If neither specified default to
    claude_code if available,
    fall back to api if not.
    Raise ValueError if neither
    backend is available.
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )


def _route_task(
    task: str,
    config: dict,
    root_manager: RootManager,
) -> str:
    """
    Determine which agent should
    handle this task.
    Read roster from config.
    Simple keyword routing for now:
    - mentions of test/spec/coverage
      → tester agent
    - mentions of quality/duplicate/
      prune/refactor → quality agent
    - mentions of evaluate/simulate/
      persona → evaluator agent
    - everything else → builder agent
    Return agent name string.
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )


def _load_agent_context(
    agent_name: str,
    task: str,
    root_manager: RootManager,
) -> AgentContext:
    """
    Build AgentContext for execution.
    Read agent definition from
    roots/agents/{agent_name}.md
    Read these roots for all agents:
    - roots/project/state.md
    - roots/context/codebase.md
    - roots/context/patterns.md
    Read these additionally per agent:
    builder: dependencies.md
    tester: failures.md
    quality: quality/repetition.md,
             quality/patterns.md
    evaluator: flows/ index
    Return AgentContext.
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )


def _apply_roots_updates(
    updates: dict[str, str],
    project_path: Path,
    root_manager: RootManager,
) -> list[str]:
    """
    Apply roots updates from executor.
    For each path in updates:
    - Validate path starts with roots/
    - Write content to file
    - Mark file dirty in root_manager
    Return list of paths updated.
    Silently skip any path that does
    not start with roots/ — agents
    cannot write outside roots/
    via this mechanism.
    """
    raise NotImplementedError(
        "Phase 5 implementation"
    )
