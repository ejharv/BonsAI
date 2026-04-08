# Bonsai — Root System Index

> Adaptive agent orchestration framework where structure emerges from the problem.

---

## Region Map

| Region | Purpose | Owner Agent |
|--------|---------|-------------|
| [project/](project/index.md) | Vision, state, and architectural decisions | Architect |
| [agents/](agents/index.md) | Agent definitions, domains, and rules | Architect |
| [context/](context/index.md) | Living codebase map, patterns, failures, dependencies | Builder / Tester |
| [quality/](quality/index.md) | Duplication tracking, debt log, pruning proposals | Quality |
| [flows/](flows/index.md) | Orchestration flow definitions and success criteria | Architect / Evaluator |

---

## Current Phase

**Phase 4 complete — bonsai init CLI working**

`bonsai/__main__.py`, `bonsai/cli/display.py`, and `bonsai/cli/init_command.py` implemented. `python -m bonsai init <path>` validates the project, initializes roots/, runs ReconnaissanceAgent, presents developer gaps interactively, confirms agent roster, and writes .bonsai config. 18 CLI tests passing. Smoke tested against BonsAI itself.

---

## Health Table

| Region | Status | Notes |
|--------|--------|-------|
| project/ | in progress | Vision, state, and decisions written; state reflects Phase 3 complete |
| agents/ | in progress | All five agent definitions written; reconnaissance agent fully implemented |
| context/ | in progress | Codebase map updated (Phase 3); dependency map current; patterns registry has two entries |
| quality/ | initialized | Schema defined, no entries yet |
| flows/ | initialized | Greenfield and brownfield flows written |

Status legend: `initialized` → `in progress` → `complete` → `degraded`

---

## Next Priority

**bonsai run command — Phase 5.**

Task execution against an initialized project. Routes a task description to the appropriate agent(s) based on domain, executes with budget tracking and session management.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 4)_
