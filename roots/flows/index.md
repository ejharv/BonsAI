# Flows Region — Index

This region defines the orchestration flows that Bonsai can execute. Each flow file specifies its intent, success criteria, input schema, and step sequence. Flows are the trunk of the tree — foundational paths that every feature and integration builds on top of.

The Architect defines flows. The Evaluator scores them. Flows are versioned by their success criteria; a flow is only considered stable when its success score has been validated by the Evaluator.

---

## Table of Contents

| File | Flow Name | Intent |
|------|-----------|--------|
| [greenfield_init.md](greenfield_init.md) | Greenfield Initialization | Derive complete root system and agent roster from a new project spec |
| [brownfield_onboarding.md](brownfield_onboarding.md) | Brownfield Onboarding | Derive root system and agent roster from an existing codebase |

---

## Status Table

| File | Status | Owner Agent | Last Updated | Freshness | Success Score |
|------|--------|-------------|--------------|-----------|---------------|
| greenfield_init.md | clean | Architect | 2026-04-07 | fresh | not evaluated |
| brownfield_onboarding.md | clean | Architect | 2026-04-07 | fresh | not evaluated |

Freshness legend: `fresh` (updated this session) → `aging` (1–3 sessions old) → `stale` (needs review)
Success Score: set by Evaluator after validation runs

---

_Last updated: 2026-04-07_
