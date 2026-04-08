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

**Phase 6 complete — multi-agent orchestration working**

`bonsai run-multi` live and smoke tested. Orchestrator manages multi-agent execution trees with agent-driven branching via `<branch_request>` tags. Node lifecycle fully enforced. Budget allocation and signal aggregation across children working. `check_signal_propagation` invariant implemented. One remaining stub: `check_intent_coherence` (requires embedding similarity — deferred to Phase 7+). 99 unit tests passing.

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

**Phase 7 — Observability and budget dashboard.**

Run history stored to roots/. Budget consumption trends per agent. Tree visualization from stored run results.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 6 complete)_
