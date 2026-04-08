"""
Implementation of bonsai report.
Generates and outputs run reports.
"""

from pathlib import Path
from bonsai.observability.store import (
    RunStore,
)
from bonsai.observability.report import (
    ReportGenerator,
)
from bonsai.cli.display import print_error


def run_report(args) -> bool:
    """
    Execute bonsai report command.
    Returns True on success.
    """
    project_path = Path(".").resolve()
    roots_path = project_path / "roots"

    if not roots_path.exists():
        print_error(
            "No roots/ found. "
            "Run bonsai init first."
        )
        return False

    store = RunStore(roots_path)
    report = ReportGenerator(store)

    report_type = args.type
    limit = getattr(args, "limit", 20)

    if report_type == "runs":
        content = (
            report.run_summary_report(
                limit=limit
            )
        )
    elif report_type == "budget":
        content = report.budget_report(
            limit=limit
        )
    elif report_type == "health":
        content = report.health_report(
            limit=limit
        )
    elif report_type == "tree":
        run_id = getattr(
            args, "run_id", None
        )
        if not run_id:
            runs = store.list_runs(
                limit=1
            )
            if not runs:
                print_error(
                    "No runs found. "
                    "Specify --run-id."
                )
                return False
            run_id = runs[0].run_id
        content = report.tree_report(
            run_id
        )
    else:
        print_error(
            f"Unknown report type: "
            f"{report_type}"
        )
        return False

    output_path = getattr(
        args, "output", None
    )
    if output_path:
        Path(output_path).write_text(
            content
        )
        print(
            f"Report written to: "
            f"{output_path}"
        )
    else:
        print(content)

    return True
