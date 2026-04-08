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
    """
    from bonsai.cli.display import (
        print_header,
        print_step,
        print_success,
        print_error,
        print_warning,
    )

    print_header("Running Task")

    project_path = Path(".").resolve()

    # Step 1 — Load config
    print_step(1, 5, "Loading project config...")
    config = _load_bonsai_config(project_path)
    if not config:
        print_error(
            "No .bonsai config found. "
            "Run bonsai init first."
        )
        return False
    print_success("Config loaded")

    # Step 2 — Select executor
    print_step(2, 5, "Selecting executor backend...")
    try:
        executor = _select_executor(
            config,
            getattr(args, "executor", None),
        )
        print_success(
            f"Using {executor.backend.name} executor"
        )
    except ValueError as e:
        print_error(str(e))
        return False

    # Step 3 — Route and load context
    print_step(3, 5, "Routing task to agent...")

    roots_path = project_path / "roots"
    try:
        root_manager = RootManager(roots_path)
    except Exception as e:
        print_error(f"Could not load root manager: {e}")
        return False

    agent_name = (
        getattr(args, "agent", None)
        or _route_task(args.task, config, root_manager)
    )
    print_success(f"Routed to: {agent_name}")

    context = _load_agent_context(
        agent_name,
        args.task,
        root_manager,
    )

    # Step 4 — Build and execute
    print_step(4, 5, f"Executing via {executor.backend.name}...")

    prompt = AgentPrompt(
        context=context,
        seed_depth=0,
        budget_allocated=getattr(args, "budget", 10.0),
        parent_intent="",
        success_criteria=f"Task completed: {args.task}",
    )

    result = executor.execute(prompt, timeout_seconds=180)

    if result.status == ExecutorStatus.TIMEOUT:
        print_error("Task timed out after 180s")
        return False

    if result.status == ExecutorStatus.FAILED:
        print_error(f"Task failed: {result.error}")
        print()
        if result.raw_output:
            print("Partial output:")
            print(result.raw_output[:500])
        return False

    # Step 5 — Apply updates and report
    print_step(5, 5, "Applying roots updates...")

    applied = _apply_roots_updates(
        result.roots_updates,
        project_path,
        root_manager,
    )

    print_success("Task complete")
    print()
    print(
        f"Budget consumed: "
        f"{result.budget_usage.budget_consumed:.4f} units"
    )
    if result.budget_usage.tokens_used:
        print(f"Tokens used: {result.budget_usage.tokens_used:,}")
    print(f"Time: {result.budget_usage.wall_time_seconds:.1f}s")
    if applied:
        print(f"Roots updated: {', '.join(applied)}")
    print()
    print("Agent output:")
    print("─" * 50)
    print(result.raw_output)

    return True


def _load_bonsai_config(
    project_path: Path,
) -> dict:
    """
    Read .bonsai config file.
    Return dict of key=value pairs.
    Return empty dict if file not found.
    """
    config_path = project_path / ".bonsai"
    if not config_path.exists():
        return {}

    result = {}
    for line in config_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def _select_executor(
    config: dict,
    forced_backend: Optional[str],
) -> BaseExecutor:
    """
    Choose executor based on config and --executor flag.
    forced_backend overrides config.
    If neither specified default to claude_code if available,
    fall back to api if not.
    Raise ValueError if neither backend is available.
    """
    from core.executor.claude_code import ClaudeCodeExecutor
    from core.executor.api import APIExecutor

    backend = forced_backend or config.get("executor", "")

    if backend == "api":
        executor = APIExecutor()
        if not executor.is_available():
            raise ValueError(
                "API executor selected but "
                "ANTHROPIC_API_KEY not set"
            )
        return executor

    if backend == "claude_code":
        executor = ClaudeCodeExecutor()
        if not executor.is_available():
            raise ValueError(
                "claude_code executor selected but "
                "claude CLI not found on PATH"
            )
        return executor

    # Auto-select
    cc = ClaudeCodeExecutor()
    if cc.is_available():
        return cc
    api = APIExecutor()
    if api.is_available():
        return api

    raise ValueError(
        "No executor available. "
        "Install Claude Code CLI or "
        "set ANTHROPIC_API_KEY."
    )


def _route_task(
    task: str,
    config: dict,
    root_manager: RootManager,
) -> str:
    """
    Determine which agent should handle this task.
    Simple keyword routing.
    """
    task_lower = task.lower()

    test_keywords = ["test", "spec", "coverage", "unittest", "pytest"]
    quality_keywords = [
        "quality", "duplicate", "prune", "refactor",
        "repetition", "consolidate",
    ]
    eval_keywords = ["evaluate", "simulate", "persona", "synthetic", "assessment"]

    for kw in test_keywords:
        if kw in task_lower:
            return "tester"
    for kw in quality_keywords:
        if kw in task_lower:
            return "quality"
    for kw in eval_keywords:
        if kw in task_lower:
            return "evaluator"

    return "builder"


def _load_agent_context(
    agent_name: str,
    task: str,
    root_manager: RootManager,
) -> AgentContext:
    """
    Build AgentContext for execution.
    """
    agent_def_result = root_manager.reader.read_agent_definition(agent_name)
    agent_definition = (
        agent_def_result.data
        if agent_def_result.success
        else f"Agent: {agent_name}"
    )

    relevant_roots: dict[str, str] = {}

    def _safe_read(path_key: str, read_fn):
        result = read_fn()
        if result.success:
            relevant_roots[path_key] = str(result.data)

    _safe_read("project/state.md", root_manager.reader.read_project_state)
    _safe_read("context/codebase.md", root_manager.reader.read_codebase_map)
    _safe_read("context/patterns.md", root_manager.reader.read_patterns)

    if agent_name == "builder":
        _safe_read("context/dependencies.md", root_manager.reader.read_dependencies)
    elif agent_name == "tester":
        _safe_read("context/failures.md", root_manager.reader.read_failures)

    roots_to_update = [
        "roots/project/state.md",
        "roots/context/codebase.md",
    ]

    output_format = (
        "Provide your response in plain text. "
        "After completing the task provide roots updates using "
        "<root_update> XML tags as instructed. Be concise."
    )

    return AgentContext(
        agent_name=agent_name,
        agent_definition=agent_definition,
        relevant_roots=relevant_roots,
        task=task,
        output_format=output_format,
        roots_to_update=roots_to_update,
    )


def _apply_roots_updates(
    updates: dict[str, str],
    project_path: Path,
    root_manager: RootManager,
) -> list[str]:
    """
    Apply roots updates from executor.
    Only paths starting with roots/ are written.
    """
    applied = []
    for path, content in updates.items():
        if not path.startswith("roots/"):
            continue
        full_path = project_path / path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            region = path.split("/")[1]
            filename = path.split("/")[-1]
            root_manager.writer.mark_file_dirty(region, filename)
            applied.append(path)
        except Exception as e:
            print(f"Warning: could not apply update to {path}: {e}")
    return applied
