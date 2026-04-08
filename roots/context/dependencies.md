# Dependency Map

> Before any pruning proposal, the Quality agent reads this file to assess blast radius. A component cannot be removed without understanding what depends on it.

---

## Purpose

Map what connects to what across the entire project. This enables the Quality agent to assess blast radius before proposing any removal or restructuring, and helps the Architect reason about the structural impact of interface changes.

The Architect writes to this file when establishing structural contracts. The Builder updates it when adding or removing dependencies during implementation.

---

## Dependency Registry

| Component | Depends On | Depended On By | Criticality |
|-----------|-----------|----------------|-------------|
| — | — | — | — |

Criticality values:
- `critical` — removing this component breaks core flows
- `high` — removing this component breaks multiple features
- `medium` — removing this component breaks one feature
- `low` — removing this component has no downstream failures (safe to prune)

---

## Assessment Protocol

Before proposing any pruning action, the Quality agent must:
1. Look up the component in this table
2. Identify all entries in "Depended On By"
3. Assess whether those dependents can be updated or if the removal is safe
4. Include this blast radius assessment in the pruning proposal

A pruning proposal without a blast radius assessment will not be approved.

---

_Last updated: 2026-04-07_
