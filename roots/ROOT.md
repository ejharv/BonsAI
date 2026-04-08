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

**Phase 1 complete — all core interfaces defined**

The seed, invariants, lifecycle, and root manager interface are all defined as typed contracts. No implementation logic exists yet. All methods raise `NotImplementedError` — ready for Phase 2.

---

## Health Table

| Region | Status | Notes |
|--------|--------|-------|
| project/ | in progress | Vision, state, and decisions written; state reflects Phase 1 complete |
| agents/ | initialized | All five agent definitions written |
| context/ | in progress | Codebase map and dependency map populated with Phase 1 + root manager modules |
| quality/ | initialized | Schema defined, no entries yet |
| flows/ | initialized | Greenfield and brownfield flows written |

Status legend: `initialized` → `in progress` → `complete` → `degraded`

---

## Next Priority

**Root manager implementation — Phase 2.**

Make the `NotImplementedError` stubs in `root_manager/` into working code. Reader parses `.md` into typed structures. Writer serializes typed structures to `.md` and marks files DIRTY. Manager composes both and handles session lifecycle.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-07_
