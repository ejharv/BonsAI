# Context Region — Index

This region is the living map of the project's runtime state. It tracks what has been built, what patterns exist, what has failed, and what depends on what. Every agent reads from this region. Builder and Tester are the primary writers. The Architect writes to dependencies when structural contracts change.

Context files decay. A stale context file is worse than no context file — it produces confident incorrect behavior. Every significant code change must trigger an update to the relevant file in this region.

---

## Table of Contents

| File | Purpose |
|------|---------|
| [codebase.md](codebase.md) | Module map — what has been built, who owns it, current status |
| [patterns.md](patterns.md) | Component registry — all reusable structures, checked before creating new ones |
| [failures.md](failures.md) | Failure history — what has been tried, why it failed, what was learned |
| [dependencies.md](dependencies.md) | Dependency graph — what connects to what for blast radius assessment |

---

## Status Table

| File | Status | Owner Agent | Last Updated | Freshness |
|------|--------|-------------|--------------|-----------|
| codebase.md | dirty | Builder | 2026-04-07 | fresh |
| patterns.md | clean | Builder | 2026-04-07 | fresh |
| failures.md | clean | Tester | 2026-04-07 | fresh |
| dependencies.md | clean | Architect / Builder | 2026-04-07 | fresh |

Freshness legend: `fresh` (updated this session) → `aging` (1–3 sessions old) → `stale` (needs review)

---

_Last updated: 2026-04-07_
