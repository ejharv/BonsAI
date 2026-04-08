"""
Implementation of bonsai run-multi.
Wires the Orchestrator to the CLI.
Provides rich output showing the
full execution tree as it runs.
"""

from pathlib import Path
from core.orchestrator.orchestrator import Orchestrator
from core.orchestrator.models import (
    OrchestratorConfig,
    RunResult,
    NodeResult,
    NodeStatus,
)
from bonsai.cli.run_command import (
    _load_bonsai_config,
    _select_executor,
)
from bonsai.cli.display import (
    print_header,
    print_step,
    print_success,
    print_error,
    print_warning,
)
from root_manager.manager import RootManager


def run_multi(args) -> bool:
    """
    Execute bonsai run-multi command.
    Returns True on success.
    """
    print_header("Running Multi-Agent Task")

    project_path = Path(".").resolve()

    print_step(1, 4, "Loading project config...")
    config = _load_bonsai_config(project_path)
    if not config:
        print_error("No .bonsai config found. Run bonsai init first.")
        return False
    print_success("Config loaded")

    print_step(2, 4, "Selecting executor backend...")
    try:
        executor = _select_executor(
            config,
            getattr(args, "executor", None),
        )
        print_success(f"Using {executor.backend.name} executor")
    except ValueError as e:
        print_error(str(e))
        return False

    print_step(3, 4, "Initializing orchestrator...")
    roots_path = project_path / "roots"
    try:
        root_manager = RootManager(roots_path)
    except Exception as e:
        print_error(f"Could not load root manager: {e}")
        return False

    max_depth = getattr(args, "max_depth", 3)
    orch_config = OrchestratorConfig(
        min_branch_size=1.0,
        max_depth=max_depth,
        prune_threshold=0.2,
        warn_threshold=0.4,
        synthesis_budget_fraction=0.15,
        timeout_per_node_seconds=getattr(
            args, "timeout", 300
        ),
    )

    orchestrator = Orchestrator(
        executor=executor,
        root_manager=root_manager,
        config=orch_config,
    )
    print_success(f"Orchestrator ready (max_depth={max_depth})")

    print_step(4, 4, f"Executing: {args.task[:60]}...")

    result = orchestrator.run(
        task=args.task,
        agent_name=getattr(args, "agent", "builder"),
        budget=getattr(args, "budget", 20.0),
    )

    print()
    print_run_result(result)

    return result.success


def print_run_result(result: RunResult) -> None:
    """
    Print a rich summary of a RunResult.
    """
    print("── Run Complete ──")
    print(f"Task: {result.task}")
    print()
    print("Execution Tree:")
    _print_node_tree(result.root_result, prefix="", is_last=True)
    print()
    print(
        f"Total: {result.total_nodes} node"
        f"{'s' if result.total_nodes != 1 else ''}, "
        f"{result.pruned_nodes} pruned"
    )
    print(f"Budget: {result.total_budget_consumed:.4f} units consumed")
    print(f"Max depth: {result.max_depth_reached}")
    print(f"Success: {result.success}")
    print()
    print(result.summary)


def _print_node_tree(
    result: NodeResult,
    prefix: str = "",
    is_last: bool = True,
) -> None:
    """
    Recursive tree printer helper.
    """
    connector = "└── " if is_last else "├── "
    indent = "    " if is_last else "│   "

    budget = result.budget_usage.budget_consumed if result.budget_usage else 0.0
    score = result.signal.contribution_score if result.signal else 0.0

    label = f"[{result.status.name}] depth={result.depth}"
    print(f"{prefix}{connector if prefix else ''}{label}")
    print(f"{prefix}{indent if prefix else '  '}budget: {budget:.4f} units")
    print(f"{prefix}{indent if prefix else '  '}score:  {score:.2f}")

    children = result.child_results or []
    for i, child in enumerate(children):
        child_is_last = i == len(children) - 1
        child_prefix = prefix + (indent if prefix else "  ")
        _print_node_tree(child, prefix=child_prefix, is_last=child_is_last)
