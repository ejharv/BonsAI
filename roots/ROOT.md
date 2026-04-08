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

**Phase 0 — Root system initialization**

The structural skeleton is being established. No code has been written. The root system exists to give every future agent a shared, traversable context map before a single line of implementation is produced.

---

## Health Table

| Region | Status | Notes |
|--------|--------|-------|
| project/ | initialized | Vision, state, and decisions written |
| agents/ | initialized | All five agent definitions written |
| context/ | initialized | Schema defined, no entries yet |
| quality/ | initialized | Schema defined, no entries yet |
| flows/ | initialized | Greenfield and brownfield flows written |

Status legend: `initialized` → `in progress` → `complete` → `degraded`

---

## Next Priority

**Seed definition in code.**

With the root system in place, the Architect agent should derive the first structural interfaces: the `Seed` type (project specification schema), the `Flow` runner contract, and the `Agent` base interface. These become the trunk from which all branches grow. No implementation yet — contracts and interfaces only.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-07_
