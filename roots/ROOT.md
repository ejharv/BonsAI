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

**Phase 8 — packaging complete, awaiting PyPI upload**

pyproject.toml created (bonsaif 0.1.0, zero required dependencies, anthropic SDK optional). README.md written. Package built: `bonsaif-0.1.0.tar.gz` and `bonsaif-0.1.0-py3-none-any.whl` — twine check PASSED. Awaiting PyPI account confirmation before upload.

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

**Upload to PyPI** — run `python3 -m twine upload dist/*` once PyPI account is confirmed.

See [project/state.md](project/state.md) for current blockers and session context.

---

_Last updated: 2026-04-08 (Phase 8 — packaging complete, awaiting PyPI upload)_
