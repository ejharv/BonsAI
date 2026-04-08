# Codebase Map

> Updated after every significant code change. A module added without an entry here is not tracked.

---

## Current State

**Phase 2 complete. Root manager implemented and tested.**

Seven modules written. Core contracts defined and implemented. Root manager provides full read/write access to the roots/ file system.

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
| `root_manager/models.py` | Typed representations of all roots/ structures: FileStatus, Freshness, RootFile, RegionIndex, ProjectState, DecisionEntry, CodebaseEntry, DependencyEntry, RootManagerResult | Architect | `implemented` | 2026-04-07 |
| `root_manager/reader.py` | All read operations against roots/; parses .md content into typed structures; returns RootManagerResult | Builder | `implemented` | 2026-04-07 |
| `root_manager/writer.py` | All write operations against roots/; serializes typed structures to .md; marks files DIRTY after every write | Builder | `implemented` | 2026-04-07 |
| `root_manager/manager.py` | Single interface between agents and roots/; composes reader and writer; manages session-level file status cache | Builder | `implemented` | 2026-04-07 |
| `tests/test_root_manager.py` | 24 unit tests covering RootReader, RootWriter, and RootManager — all passing | Builder | `complete` | 2026-04-07 |
| `agents/reconnaissance/models.py` | Typed inputs and outputs for the reconnaissance agent: ConfidenceLevel, GapSeverity, ObservedDomain, DetectedPattern, DeveloperGap, ReconnaissanceInput, ReconnaissanceOutput | Architect | `implemented` | 2026-04-08 |
| `agents/reconnaissance/agent.py` | ReconnaissanceAgent — full ten-step pipeline: load_graphify_report, scan_project_structure, identify_domains, detect_patterns, analyze_git_history, identify_gaps, propose_roster, write_to_roots | Builder | `implemented` | 2026-04-08 |
| `tests/test_reconnaissance.py` | 31 unit tests covering ReconnaissanceAgent pipeline, domain identification, pattern detection, gap analysis, roster proposal, and write_to_roots — all passing | Builder | `complete` | 2026-04-08 |

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

_Last updated: 2026-04-08 (Phase 3)_
