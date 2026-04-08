# Project State

> Snapshot of current work. Updated at the start and end of every session.

---

## Current Phase

**Phase 1 complete — all core interfaces defined**

---

## Completed

- Root system initialization — `roots/` directory structure and all foundational `.md` files
- Seed definition in code — `core/seed/seed.py`, `core/invariants/invariants.py`, `core/lifecycle/lifecycle.py`
  - All structures as dataclasses, no implementation logic
  - Three invariants defined as `NotImplementedError` contracts
  - Full lifecycle state machine with all valid transitions
- Root manager interface — `root_manager/models.py`, `root_manager/reader.py`, `root_manager/writer.py`, `root_manager/manager.py`
  - All types, reader contracts, writer contracts, and session management interface defined
  - All methods raise `NotImplementedError` — contracts only, no implementation logic
- Deployment model decided — tool not template, roots inside project

---

## In Progress

_Nothing._

---

## Next

- **Root manager implementation — Phase 2** — make the `NotImplementedError` stubs into working code
  - `RootReader`: parse `.md` files into typed structures
  - `RootWriter`: serialize typed structures back to `.md`, mark files DIRTY
  - `RootManager`: compose reader and writer, manage session cache, implement `begin_session` / `end_session`

---

## Blockers

_None._

---

## Last Session Summary

**Session: 2026-04-07**

Root manager interface defined. `root_manager/models.py` establishes all typed structures (FileStatus, Freshness, RootFile, RegionIndex, ProjectState, DecisionEntry, CodebaseEntry, DependencyEntry, RootManagerResult). `root_manager/reader.py` defines nine read contracts. `root_manager/writer.py` defines eight write contracts including dirty flag management and pattern tracking. `root_manager/manager.py` defines the single agent-facing interface with session lifecycle and needs_reread. Decision recorded: RootManager as single interface, no direct file access by agents. Codebase map, dependency map, state, and ROOT.md updated. Root manager interface pushed to main.

---

_Last updated: 2026-04-07_
