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

**Phase 7 complete — polishing for real project test**

RunStore persists every run to `roots/runs/` as JSON with a fast-summary index.md. `bonsai status` renders a live terminal dashboard. `bonsai report` generates runs, budget, health, and tree reports. RunStore wired into both `bonsai run` and `bonsai run-multi`. Progress spinner on `claude --print` execution. Default timeout raised to 300s. `--timeout` flag on `run` and `run-multi`. CLAUDE.md created. 128 unit tests passing.

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

**Test on FitCypher site repo — first real project run.**

Then Phase 8 — Package and publish: pyproject.toml, README, PyPI.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 7 complete — polishing)_
