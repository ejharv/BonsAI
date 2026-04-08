"""
Implementation of bonsai init.
Wires together reconnaissance agent,
gap presentation, and roots/
initialization for a new or existing
project.
"""

from pathlib import Path
import sys

from agents.reconnaissance.agent import (
    ReconnaissanceAgent
)
from agents.reconnaissance.models import (
    ReconnaissanceInput,
    GapSeverity,
)
from root_manager.manager import (
    RootManager
)
from root_manager.models import (
    ProjectState
)
from bonsai.cli.display import (
    print_header,
    print_step,
    print_success,
    print_warning,
    print_error,
    print_domain_summary,
    print_gap_question,
    print_roster_summary,
    print_bonsai_complete,
)


def run_init(args) -> bool:
    """
    Execute bonsai init command.
    Returns True on success,
    False on failure.

    Steps:
    1. Validate project path
    2. Initialize roots/ directory
    3. Initialize RootManager
    4. Run ReconnaissanceAgent
    5. Display domain summary
    6. Present gap questions
    7. Display roster summary
    8. Write final state
    9. Print completion message
    """

    print_header("Initializing Project")

    # Step 1 — Validate project path
    print_step(1, 6,
        "Validating project path...")

    project_path = Path(
        args.project_path
    ).resolve()

    if not project_path.exists():
        print_error(
            f"Project path does not "
            f"exist: {project_path}"
        )
        return False

    if not project_path.is_dir():
        print_error(
            f"Project path is not a "
            f"directory: {project_path}"
        )
        return False

    print_success(
        f"Project path: {project_path}"
    )

    # Step 2 — Initialize roots/
    print_step(2, 6,
        "Initializing roots/ "
        "directory...")

    roots_path = project_path / "roots"
    existing_bonsai = roots_path.exists()

    if existing_bonsai:
        print_warning(
            "roots/ already exists — "
            "merging with existing state"
        )
    else:
        success = _initialize_roots(
            roots_path
        )
        if not success:
            return False
        print_success(
            "roots/ initialized"
        )

    # Step 3 — Initialize RootManager
    print_step(3, 6,
        "Starting root manager...")

    try:
        root_manager = RootManager(
            roots_path
        )
    except Exception as e:
        print_error(
            f"Failed to start root "
            f"manager: {e}"
        )
        return False

    print_success("Root manager ready")

    # Step 4 — Run reconnaissance
    print_step(4, 6,
        "Running reconnaissance "
        "agent...")

    recon_input = ReconnaissanceInput(
        project_path=str(project_path),
        use_graphify=bool(args.graphify),
        graphify_report_path=
            args.graphify,
        trust_git_history=
            args.trust_git,
        involvement_preference=
            args.involvement,
        existing_bonsai=existing_bonsai,
    )

    agent = ReconnaissanceAgent(
        root_manager=root_manager,
        project_path=project_path,
    )

    try:
        output = agent.run(recon_input)
    except Exception as e:
        print_error(
            f"Reconnaissance failed: {e}"
        )
        return False

    print_success(
        f"Reconnaissance complete — "
        f"{len(output.observed_domains)}"
        f" domains found"
    )

    # Step 5 — Display domain summary
    print_domain_summary(
        output.observed_domains
    )

    # Display health observations
    if output.health_observations:
        print()
        print_warning(
            "Health issues detected:"
        )
        for obs in (
            output.health_observations
        ):
            print(f"  {obs}")

    # Step 6 — Present gap questions
    print_step(5, 6,
        "Resolving knowledge gaps...")

    answers = _present_gaps(
        output.developer_gaps
    )

    # Store answers in roots
    _record_answers(
        answers,
        output.developer_gaps,
        root_manager,
        project_path,
    )

    # Step 7 — Display roster
    print_step(6, 6,
        "Finalizing agent roster...")

    print_roster_summary(
        output.proposed_roster
    )

    # Confirm roster with developer
    confirmed = _confirm_roster(
        output.proposed_roster
    )

    if not confirmed:
        print_warning(
            "Roster not confirmed — "
            "roots/ has been initialized "
            "but no agents are active. "
            "Edit roots/agents/ manually "
            "and re-run bonsai init."
        )
        return False

    # Step 8 — Write final state
    _write_bonsai_config(
        project_path,
        args.involvement,
        output.proposed_roster,
    )

    # Step 9 — Complete
    print_bonsai_complete(
        str(project_path),
        len(output.proposed_roster),
    )

    return True


def _initialize_roots(
    roots_path: Path,
) -> bool:
    """
    Create minimal roots/ structure
    for a fresh project.
    Creates all required directories
    and minimal index files.
    Returns True on success.
    """
    try:
        regions = [
            "project",
            "agents",
            "context",
            "quality",
            "flows",
        ]

        for region in regions:
            region_path = (
                roots_path / region
            )
            region_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            index_path = (
                region_path / "index.md"
            )
            if not index_path.exists():
                index_path.write_text(
                    f"# {region.title()} "
                    f"Region Index\n\n"
                    f"## Status Table\n\n"
                    f"| File | Status | "
                    f"Owner | Updated | "
                    f"Freshness |\n"
                    f"|------|--------|"
                    f"-------|---------|"
                    f"-----------|\n"
                )

        root_md = roots_path / "ROOT.md"
        if not root_md.exists():
            root_md.write_text(
                "# Bonsai Root Index\n\n"
                "## Current Phase\n"
                "Initializing\n\n"
                "## Regions\n\n"
                "| Region | Purpose | "
                "Owner |\n"
                "|--------|---------|"
                "-------|\n"
            )

        return True

    except Exception as e:
        print_error(
            f"Failed to initialize "
            f"roots/: {e}"
        )
        return False


def _present_gaps(
    gaps: list,
) -> dict:
    """
    Present each gap question to the
    developer interactively.
    Returns dict mapping gap question
    to developer answer string.
    Empty string means developer
    accepted the default.
    """
    if not gaps:
        print_success(
            "No gaps to resolve"
        )
        return {}

    answers = {}
    total = len(gaps)

    print()
    for i, gap in enumerate(gaps, 1):
        print_gap_question(
            i, total, gap
        )

        try:
            answer = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print_warning(
                "Input interrupted — "
                "using defaults for "
                "remaining gaps"
            )
            break

        if answer:
            answers[gap.question] = answer
            print_success(
                "Answer recorded"
            )
        else:
            answers[gap.question] = ""
            print_warning(
                f"Using default: "
                f"{gap.default_if_skipped}"
            )
        print()

    return answers


def _record_answers(
    answers: dict,
    gaps: list,
    root_manager: RootManager,
    project_path: Path,
) -> None:
    """
    Write developer answers to
    appropriate roots/ files.
    The purpose gap answer goes to
    project/vision.md.
    All others go to project/state.md
    as context notes.
    """
    for gap in gaps:
        answer = answers.get(
            gap.question, ""
        )

        if not answer:
            answer = gap.default_if_skipped

        if "purpose" in (
            gap.question.lower()
        ):
            vision_path = (
                root_manager.roots_path
                / "project"
                / "vision.md"
            )
            if not vision_path.exists():
                vision_path.write_text(
                    f"# Project Vision\n\n"
                    f"## Purpose\n"
                    f"{answer}\n\n"
                    f"## Status\n"
                    f"Defined during "
                    f"bonsai init\n"
                )


def _confirm_roster(
    roster: list[str],
) -> bool:
    """
    Ask developer to confirm the
    proposed roster before proceeding.
    Returns True if confirmed.
    """
    print()
    print(
        "Confirm this roster? "
        "[Y/n]: ",
        end="",
        flush=True,
    )

    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    return response in ("", "y", "yes")


def _write_bonsai_config(
    project_path: Path,
    involvement: str,
    roster: list[str],
) -> None:
    """
    Write .bonsai config file to
    project root.
    Simple key=value format.
    """
    config_path = (
        project_path / ".bonsai"
    )

    lines = [
        "# Bonsai configuration",
        f"involvement={involvement}",
        f"roster={','.join(roster)}",
        f"initialized=True",
        "",
    ]

    config_path.write_text(
        "\n".join(lines)
    )
