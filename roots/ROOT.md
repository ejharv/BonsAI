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

**Phase 1 — Core seed defined**

The structural contracts are established. `core/seed/seed.py` defines the Seed and all component dataclasses. Invariants and lifecycle are defined as contracts. No implementation logic exists yet.

---

## Health Table

| Region | Status | Notes |
|--------|--------|-------|
| project/ | in progress | Vision, state, and decisions written; state reflects Phase 1 complete |
| agents/ | initialized | All five agent definitions written |
| context/ | in progress | Codebase map and dependency map populated with Phase 1 modules |
| quality/ | initialized | Schema defined, no entries yet |
| flows/ | initialized | Greenfield and brownfield flows written |

Status legend: `initialized` → `in progress` → `complete` → `degraded`

---

## Next Priority

**Root manager.**

The interface between agents and the `.md` file system. Agents should never touch root files directly — all reads and writes go through the root manager. This is the first piece of runtime infrastructure.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-07_
