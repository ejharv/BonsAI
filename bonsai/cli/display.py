"""
All terminal output for the Bonsai CLI.
Nothing outside this module prints
to stdout except display functions.
This keeps output consistent and
easy to modify without touching
command logic.
"""

import sys


def print_header(title: str) -> None:
    """
    Print a visually distinct header.

    ╔══════════════════════════════════════════════════╗
    ║  Bonsai — {title padded to fill}                 ║
    ╚══════════════════════════════════════════════════╝

    Width: 50 characters total.
    """
    inner = 48  # ╔ + 48×═ + ╗ = 50
    content = ("  Bonsai — " + title)[:inner].ljust(inner)
    print(f"╔{'═' * inner}╗")
    print(f"║{content}║")
    print(f"╚{'═' * inner}╝")


def print_step(
    step: int,
    total: int,
    message: str,
) -> None:
    """
    Print a numbered step.
    Format: [{step}/{total}] {message}
    Example: [1/4] Scanning project structure...
    """
    print(f"[{step}/{total}] {message}")


def print_success(message: str) -> None:
    """
    Print a success message.
    Format: ✓ {message}
    """
    print(f"✓ {message}")


def print_warning(message: str) -> None:
    """
    Print a warning.
    Format: ⚠ {message}
    """
    print(f"⚠ {message}")


def print_error(message: str) -> None:
    """
    Print an error to stderr.
    Format: ✗ {message}
    """
    print(f"✗ {message}", file=sys.stderr)


def print_domain_summary(domains: list) -> None:
    """
    Print a summary table of domains found by reconnaissance.

    Domains Found:
    ┌─────────────────┬────────────┬──────────────────────────┐
    │ Domain          │ Confidence │ Purpose                  │
    ├─────────────────┼────────────┼──────────────────────────┤
    │ auth            │ HIGH       │ Handles authentication   │
    │ api             │ MEDIUM     │ REST API endpoints       │
    └─────────────────┴────────────┴──────────────────────────┘

    domains is list[ObservedDomain]
    """
    # Column widths include 1-space padding each side
    c1, c2, c3 = 17, 12, 26
    w1, w2, w3 = c1 - 2, c2 - 2, c3 - 2  # content widths: 15, 10, 24

    print()
    print("Domains Found:")
    print(f"┌{'─' * c1}┬{'─' * c2}┬{'─' * c3}┐")
    print(f"│ {'Domain':<{w1}} │ {'Confidence':<{w2}} │ {'Purpose':<{w3}} │")
    print(f"├{'─' * c1}┼{'─' * c2}┼{'─' * c3}┤")

    for domain in domains:
        name = str(domain.name)[:w1].ljust(w1)
        conf = domain.confidence.name[:w2].ljust(w2)
        purpose = domain.purpose
        if len(purpose) > w3:
            purpose = purpose[:w3 - 3] + "..."
        purpose = purpose.ljust(w3)
        print(f"│ {name} │ {conf} │ {purpose} │")

    print(f"└{'─' * c1}┴{'─' * c2}┴{'─' * c3}┘")


def print_gap_question(
    index: int,
    total: int,
    gap: object,
) -> None:
    """
    Print a developer gap question.

    ── Question {index} of {total} ──
    [{severity}] {question}

    Context: {context}
    Default if skipped: {default}

    Your answer (or press Enter
    to use default):
    """
    print(f"\n── Question {index} of {total} ──")
    print(f"[{gap.severity.name}] {gap.question}")
    print()
    print(f"Context: {gap.context}")
    print(f"Default if skipped: {gap.default_if_skipped}")
    print()
    print("Your answer (or press Enter")
    print("to use default):")


def print_roster_summary(roster: list[str]) -> None:
    """
    Print the proposed agent roster.

    Proposed Agent Roster:
    ┌─────────────────────────────┐
    │ • auth_agent                │
    │ • api_agent                 │
    │ • quality                   │
    │ • evaluator                 │
    └─────────────────────────────┘

    Total: {n} agents
    """
    inner = 29  # chars between │ borders
    name_width = inner - 3  # subtract " • " prefix

    print()
    print("Proposed Agent Roster:")
    print(f"┌{'─' * inner}┐")
    for name in roster:
        content = f" • {name:<{name_width}}"
        print(f"│{content}│")
    print(f"└{'─' * inner}┘")
    print()
    print(f"Total: {len(roster)} agents")


def print_bonsai_complete(
    project_path: str,
    roster_count: int,
) -> None:
    """
    Print final success message.

    ╔══════════════════════════════════╗
    ║  Bonsai initialized successfully ║
    ╚══════════════════════════════════╝

    Project: {project_path}
    Agents:  {roster_count} ready
    Roots:   {project_path}/roots/

    Next: review roots/ and run
          bonsai run <task> to begin.
    """
    msg = "  Bonsai initialized successfully "
    inner = len(msg)
    print()
    print(f"╔{'═' * inner}╗")
    print(f"║{msg}║")
    print(f"╚{'═' * inner}╝")
    print()
    print(f"Project: {project_path}")
    print(f"Agents:  {roster_count} ready")
    print(f"Roots:   {project_path}/roots/")
    print()
    print("Next: review roots/ and run")
    print("      bonsai run <task> to begin.")
