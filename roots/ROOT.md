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

**Phase 5 complete — bonsai run working, system is self-building**

`bonsai run` fully implemented. Two executor backends (claude_code and api). 26 executor tests passing. Smoke tested: `bonsai run` routed to builder, executed via claude CLI, applied roots updates, consumed 7.59 budget units. Agent implemented `check_budget_conservation` in `core/invariants/invariants.py`.

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

**Phase 6 — Orchestrator.**

Multi-agent runs with real seed lifecycle. GERMINATING → GROWING → BRANCHING → CLOSING state machine. Budget allocation across multiple agents. Child seed spawning on complexity threshold. Signal aggregation from child results.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 5 complete)_
