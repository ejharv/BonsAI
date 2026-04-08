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

**Phase 3 — Reconnaissance agent interface defined**

Brownfield onboarding agent interface fully contracted. `agents/reconnaissance/models.py` defines all typed inputs and outputs: `ConfidenceLevel`, `GapSeverity`, `ObservedDomain`, `DetectedPattern`, `DeveloperGap`, `ReconnaissanceInput`, `ReconnaissanceOutput`. `agents/reconnaissance/agent.py` defines the full pipeline — ten-step `run` contract plus seven dedicated methods, all raising `NotImplementedError`. Graphify integration decided and recorded.

---

## Health Table

| Region | Status | Notes |
|--------|--------|-------|
| project/ | in progress | Vision, state, and decisions written; state reflects Phase 2 complete |
| agents/ | initialized | All five agent definitions written |
| context/ | in progress | Codebase map updated (Phase 2); dependency map current; patterns registry has first entry |
| quality/ | initialized | Schema defined, no entries yet |
| flows/ | initialized | Greenfield and brownfield flows written |

Status legend: `initialized` → `in progress` → `complete` → `degraded`

---

## Next Priority

**Reconnaissance agent — Phase 3.**

First real agent that reads an existing codebase and populates the root system. Uses `RootManager` to write `context/codebase.md` and `context/dependencies.md` from static analysis of a target project.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-07_
