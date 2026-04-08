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

**Phase 7 — Observability interfaces defined**

RunStore, ReportGenerator, and Dashboard contracted. `bonsai status` and `bonsai report` subcommands wired in `__main__.py`. Two decisions recorded. All methods raise NotImplementedError — implementation is next. Phase 6 complete: `bonsai run-multi` live and smoke tested, 99 unit tests passing.

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

**Phase 7 — Implement observability stubs.**

All interfaces contracted. Builder implements RunStore, ReportGenerator, Dashboard, status_command, report_command. Wire RunStore into orchestrator and run_command. Write tests. Smoke test bonsai status and bonsai report live.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 7 interfaces defined)_
