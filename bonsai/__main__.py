import argparse
import sys
from bonsai.cli.init_command import (
    run_init
)

def main():
    parser = argparse.ArgumentParser(
        prog="bonsai",
        description=(
            "Bonsai — adaptive agent "
            "orchestration framework"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="command"
    )

    # bonsai run
    run_parser = subparsers.add_parser(
        "run",
        help=(
            "Run a task against an "
            "initialized project."
        )
    )
    run_parser.add_argument(
        "task",
        help=(
            "Task description in plain "
            "english. Be specific. "
            "Example: 'implement the "
            "budget conservation "
            "invariant in core/"
            "invariants/invariants.py'"
        )
    )
    run_parser.add_argument(
        "--executor",
        choices=[
            "claude_code", "api"
        ],
        default=None,
        help=(
            "Force a specific executor "
            "backend. Overrides .bonsai "
            "config. Default: auto-select"
        )
    )
    run_parser.add_argument(
        "--agent",
        default=None,
        help=(
            "Force a specific agent. "
            "Overrides auto-routing. "
            "Example: --agent builder"
        )
    )
    run_parser.add_argument(
        "--budget",
        type=float,
        default=10.0,
        help=(
            "Budget units for this task. "
            "Default: 10.0"
        )
    )
    run_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help=(
            "Timeout in seconds per "
            "agent execution. "
            "Default: 300. "
            "Increase for complex tasks."
        )
    )

    # bonsai init
    init_parser = subparsers.add_parser(
        "init",
        help=(
            "Initialize Bonsai on a "
            "project. Runs reconnaissance "
            "and sets up roots/."
        )
    )
    init_parser.add_argument(
        "project_path",
        help=(
            "Path to the project to "
            "initialize. Use . for "
            "current directory."
        )
    )
    init_parser.add_argument(
        "--involvement",
        choices=["high", "medium", "low"],
        default="medium",
        help=(
            "How much to involve you "
            "in decisions. "
            "high: ask everything. "
            "medium: ask important only. "
            "low: ask blocking only. "
            "Default: medium"
        )
    )
    init_parser.add_argument(
        "--graphify",
        metavar="REPORT_PATH",
        help=(
            "Path to graphify "
            "GRAPH_REPORT.md if you "
            "ran graphify before init."
        )
    )
    init_parser.add_argument(
        "--trust-git",
        action="store_true",
        default=True,
        help=(
            "Use git history as signal "
            "for domain detection. "
            "Default: True"
        )
    )

    # bonsai status
    status_parser = subparsers.add_parser(
        "status",
        help=(
            "Show project dashboard — "
            "recent runs, budget trends, "
            "quality health."
        )
    )
    status_parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of recent runs to show."
    )

    # bonsai report
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a run report."
    )
    report_parser.add_argument(
        "type",
        choices=[
            "runs", "budget",
            "health", "tree"
        ],
        help="Type of report to generate."
    )
    report_parser.add_argument(
        "--run-id",
        help=(
            "Run ID for tree report. "
            "Required when type is tree."
        )
    )
    report_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of runs to include."
    )
    report_parser.add_argument(
        "--output",
        help=(
            "Write report to this file "
            "instead of printing."
        )
    )

    # bonsai run-multi
    multi_parser = subparsers.add_parser(
        "run-multi",
        help=(
            "Run a task with full "
            "multi-agent orchestration. "
            "Supports agent-driven "
            "branching and child spawning."
        )
    )
    multi_parser.add_argument(
        "task",
        help="Task description."
    )
    multi_parser.add_argument(
        "--executor",
        choices=["claude_code", "api"],
        default=None,
    )
    multi_parser.add_argument(
        "--agent",
        default="builder",
    )
    multi_parser.add_argument(
        "--budget",
        type=float,
        default=20.0,
    )
    multi_parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
    )
    multi_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help=(
            "Timeout in seconds per "
            "node execution. "
            "Default: 300."
        )
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "init":
        success = run_init(args)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        from bonsai.cli.status_command \
            import run_status
        success = run_status(args)
        sys.exit(0 if success else 1)
    elif args.command == "report":
        from bonsai.cli.report_command \
            import run_report
        success = run_report(args)
        sys.exit(0 if success else 1)
    elif args.command == "run":
        from bonsai.cli.run_command \
            import run_task
        success = run_task(args)
        sys.exit(0 if success else 1)
    elif args.command == "run-multi":
        from bonsai.cli.multi_command \
            import run_multi
        success = run_multi(args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
