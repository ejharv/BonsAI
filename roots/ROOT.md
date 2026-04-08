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

**Phase 3 complete — reconnaissance agent implemented**

`agents/reconnaissance/agent.py` fully implemented. All ten pipeline steps working: project structure scanning with directory pruning, multi-signal domain identification (folders, graphify, config packages, entry points, git history), pattern detection (repeated filenames, similar folder structures, oversized files), git history analysis, gap identification with involvement preference filtering, roster proposal, and full root system writes. 31 tests passing.

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

**CLI entry point — Phase 4.**

`bonsai init` command that wires the reconnaissance agent to a real project. Accepts a project path, initializes `roots/`, runs `ReconnaissanceAgent`, and presents developer gaps interactively.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08_
