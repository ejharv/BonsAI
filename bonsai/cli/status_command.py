"""
Implementation of bonsai status.
Wires Dashboard to the CLI.
"""

from pathlib import Path
from bonsai.observability.store import (
    RunStore,
)
from bonsai.observability.report import (
    ReportGenerator,
)
from bonsai.observability.dashboard import (
    Dashboard,
)
from root_manager.manager import RootManager
from bonsai.cli.display import print_error


def run_status(args) -> bool:
    """
    Execute bonsai status command.
    Returns True on success.
    """
    project_path = Path(".").resolve()
    roots_path = project_path / "roots"

    if not roots_path.exists():
        print_error(
            "No roots/ directory found. "
            "Run bonsai init first."
        )
        return False

    try:
        root_manager = RootManager(
            roots_path
        )
        store = RunStore(roots_path)
        report = ReportGenerator(store)
        dashboard = Dashboard(
            store, report, root_manager
        )
        dashboard.render()
        return True
    except Exception as e:
        print_error(
            f"Dashboard error: {e}"
        )
        return False
