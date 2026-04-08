# Project State

> Snapshot of current work. Updated at the start and end of every session.

---

## Current Phase

**Phase 3 interface complete — reconnaissance agent interface defined**

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
- Root manager implemented and tested
  - `RootReader` — parses `.md` files into typed structures (ProjectState, DecisionEntry, CodebaseEntry, DependencyEntry)
  - `RootWriter` — serializes typed structures back to `.md`, marks files DIRTY, handles table upserts
  - `RootManager` — composes reader and writer, manages session cache, implements `begin_session` / `end_session`
  - 24 unit tests in `tests/test_root_manager.py` — all passing
- Reconnaissance agent interface defined
  - `agents/reconnaissance/models.py` — all typed inputs and outputs contracted
  - `agents/reconnaissance/agent.py` — full ten-step pipeline contracted, all methods raise NotImplementedError
  - Graphify integration decided: graphify runs once at onboarding, roots/ owns continuous updates
  - Three decisions recorded in project/decisions.md

---

## In Progress

_Nothing._

---

## Next

- **Reconnaissance agent implementation — Phase 3** — implement all NotImplementedError stubs in agent.py
  - Implement `scan_project_structure`, `load_graphify_report`, `identify_domains`
  - Implement `detect_patterns`, `analyze_git_history`, `identify_gaps`, `propose_roster`
  - Implement `write_to_roots` and the top-level `run` pipeline
  - Write tests covering the full pipeline

---

## Blockers

_None._

---

## Last Session Summary

**Session: 2026-04-07**

Root manager interface defined. `root_manager/models.py` establishes all typed structures (FileStatus, Freshness, RootFile, RegionIndex, ProjectState, DecisionEntry, CodebaseEntry, DependencyEntry, RootManagerResult). `root_manager/reader.py` defines nine read contracts. `root_manager/writer.py` defines eight write contracts including dirty flag management and pattern tracking. `root_manager/manager.py` defines the single agent-facing interface with session lifecycle and needs_reread. Decision recorded: RootManager as single interface, no direct file access by agents. Codebase map, dependency map, state, and ROOT.md updated. Root manager interface pushed to main.

---

**Session: 2026-04-07**

Root manager implemented in full. All `NotImplementedError` stubs replaced with working Python code. `RootReader` parses `.md` files into typed structures using a generic `_parse_table` helper and dedicated parsers for `ProjectState` and `DecisionEntry`. `RootWriter` serializes typed structures back to `.md` using a phase-based `_split_at_table` helper that cleanly separates pre/table/post content, enabling safe upsert and append operations. `RootManager` composes both, manages session-level file status cache from region index files, and implements `begin_session`/`end_session`/`needs_reread`. 24 unit tests written and all passing. `MarkdownTableParser` pattern registered in `context/patterns.md`. Codebase map updated to reflect implemented status. Phase 2 complete.

---

**Session: 2026-04-07**

Reconnaissance agent interface defined. Three decisions recorded: graphify integration strategy, graphify lifecycle boundary, and reconnaissance read-only constraint. `agents/reconnaissance/models.py` defines `ConfidenceLevel`, `GapSeverity`, `ObservedDomain`, `DetectedPattern`, `DeveloperGap`, `ReconnaissanceInput`, and `ReconnaissanceOutput` — all as dataclasses with full field documentation. `agents/reconnaissance/agent.py` defines `ReconnaissanceAgent` with a ten-step `run` pipeline and seven dedicated methods — all raising `NotImplementedError`. Codebase map, dependency map, state, and ROOT.md updated. Phase 3 interface complete.

---

_Last updated: 2026-04-07_
