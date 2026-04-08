# Quality Region — Index

This region tracks the health of the codebase over time. It is the Quality agent's working space and the developer's visibility into structural debt, detected duplication, and the history of pruning decisions. Nothing in this region modifies source code — it observes, records, and proposes.

Developer approval is required before any pruning action is executed. This region is the audit trail for every such decision.

---

## Table of Contents

| File | Purpose |
|------|---------|
| [patterns.md](patterns.md) | Quality-specific pattern findings from analysis passes |
| [repetition.md](repetition.md) | Active list of detected duplication awaiting action |
| [debt.md](debt.md) | Known shortcuts and structural problems with severity ratings |
| [pruning_log.md](pruning_log.md) | Complete record of all pruning proposals and their outcomes |

---

## Status Table

| File | Status | Owner Agent | Last Updated | Freshness |
|------|--------|-------------|--------------|-----------|
| patterns.md | clean | Quality | 2026-04-07 | fresh |
| repetition.md | clean | Quality | 2026-04-07 | fresh |
| debt.md | clean | Quality | 2026-04-07 | fresh |
| pruning_log.md | clean | Quality / Evaluator | 2026-04-07 | fresh |

Freshness legend: `fresh` (updated this session) → `aging` (1–3 sessions old) → `stale` (needs review)

---

_Last updated: 2026-04-07_
