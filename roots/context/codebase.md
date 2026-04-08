# Codebase Map

> Updated after every significant code change. A module added without an entry here is not tracked.

---

## Current State

**Phase 1 complete. Core structural contracts defined.**

Three modules written. No implementation logic exists yet. All modules contain contracts, dataclasses, and interfaces only.

---

## Structure

```
core/
├── __init__.py
├── seed/
│   ├── __init__.py
│   └── seed.py
├── invariants/
│   ├── __init__.py
│   └── invariants.py
└── lifecycle/
    ├── __init__.py
    └── lifecycle.py
```

---

## Module Registry

| Module Name | Purpose | Owner Agent | Status | Last Modified |
|-------------|---------|-------------|--------|---------------|
| `core/seed/seed.py` | Seed dataclass and all component structures (Identity, Contract, ResourceEnvelope, CapabilityNeed, GrowthConditions, Signal, Closure) | Architect | `defined` | 2026-04-07 |
| `core/invariants/invariants.py` | Three invariant contracts: intent coherence, budget conservation, signal propagation | Architect | `defined` | 2026-04-07 |
| `core/lifecycle/lifecycle.py` | Lifecycle stages enum and all valid state transitions | Architect | `defined` | 2026-04-07 |

Status values: `defined` (interface exists, no implementation) → `in progress` → `complete` → `deprecated`

---

## Freshness Protocol

This file must be updated whenever:
- A new module is created
- A module's status changes
- A module is deprecated or removed
- The owner agent changes

The Builder is responsible for keeping this file current. A codebase.md that lags behind `src/` is a bug.

---

_Last updated: 2026-04-07 (Phase 1)_
