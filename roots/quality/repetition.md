# Repetition Registry

> Active list of detected duplication. The Quality agent maintains this. The developer approves action. The Builder executes consolidation.

---

## Purpose

Track all currently active instances of detected code duplication. This is the working list — items here are ready for the Quality agent to act on, pending developer approval. Resolved items are moved to [pruning_log.md](pruning_log.md).

---

## Active Duplication

| Pattern Name | Locations | Instance Count | Suggested Action | Status |
|--------------|-----------|---------------|-----------------|--------|
| — | — | — | — | — |

Status values: `detected` → `proposal written` → `approved` → `resolved` (moved to pruning_log)

---

## Entry Protocol

When the Quality agent detects duplication:
1. Add entry here with status `detected`
2. Write a consolidation proposal in [pruning_log.md](pruning_log.md)
3. Update status to `proposal written`
4. Await developer approval before any action

---

_Last updated: 2026-04-07_
