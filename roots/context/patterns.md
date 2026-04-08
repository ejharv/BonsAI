# Pattern Registry

> The Builder checks this file before creating any new component. If a pattern already exists that satisfies the need, it is used — not duplicated.

---

## Purpose

Track all reusable components and structures created in this project. This is the primary tool for preventing duplication. Before creating any new component, the Builder confirms that an equivalent does not already exist here.

The Quality agent reads this file during every analysis pass to identify when the same component has been created more than once without being registered as a pattern.

---

## Component Registry

| Component Name | Purpose | Interface Shape | Locations | Instance Count | Pruning Candidate |
|----------------|---------|-----------------|-----------|---------------|-------------------|
| MarkdownTableParser | Parse .md table rows into typed dataclass instances | takes raw string content and section marker, returns list of dataclass instances | root_manager/reader.py | 1 | no |

Pruning Candidate: `no` → `watch` (2+ instances, not yet consolidatable) → `yes` (consolidation clearly beneficial)

---

## Registration Protocol

When the Builder creates a new reusable component:
1. Add an entry to this table
2. Set Instance Count to 1
3. Set Pruning Candidate to `no`

When the Builder reuses an existing pattern:
1. Increment Instance Count
2. Reassess Pruning Candidate flag

When Instance Count reaches 3+, Quality will assess for consolidation.

---

_Last updated: 2026-04-07 (Phase 2)_
