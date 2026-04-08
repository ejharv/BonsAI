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

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "init":
        success = run_init(args)
        sys.exit(0 if success else 1)
    elif args.command == "run":
        from bonsai.cli.run_command \
            import run_task
        success = run_task(args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
