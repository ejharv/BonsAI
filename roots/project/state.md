# Project State

> Snapshot of current work. Updated at the start and end of every session.

---

## Current Phase

**Phase 5 interfaces defined — executor layer contracted, awaiting Builder implementation**

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
- Reconnaissance agent implemented and tested
  - All `NotImplementedError` stubs replaced with working Python code
  - `load_graphify_report` — parses God Nodes, Communities, Connections sections from markdown
  - `scan_project_structure` — walks project tree with directory pruning via os.walk; collects folders, extensions, config files, entry points, manifest contents
  - `identify_domains` — multi-signal domain detection: top-level folders (with container folder unwrapping), graphify communities, requirements.txt packages, entry points, git frequency
  - `detect_patterns` — repeated filenames (excluding conventional), similar folder structures (Jaccard >70%), oversized files (>500 lines)
  - `analyze_git_history` — commit frequency per folder, co-change pairs, recent activity; all subprocess calls with 30s timeout
  - `identify_gaps` — four gap types with involvement_preference filtering (BLOCKING/IMPORTANT/OPTIONAL)
  - `propose_roster` — one agent per HIGH/MEDIUM domain, LOW merged or flagged unverified, always quality + evaluator
  - `write_to_roots` — codebase entries, dependency entries, pattern entries, project state, agent .md files
  - 31 unit tests in `tests/test_reconnaissance.py` — all passing
- CLI entry point implemented — bonsai init working
  - `bonsai/__main__.py` — argparse routing, `python -m bonsai` entry point
  - `bonsai/cli/display.py` — all terminal output: headers, steps, tables, gap questions, roster, completion
  - `bonsai/cli/init_command.py` — full init pipeline: validate, initialize roots/, run reconnaissance, present gaps, confirm roster, write .bonsai config
  - 18 unit tests in `tests/test_cli.py` — all passing
  - Smoke tested against BonsAI codebase itself — `bonsai init . --involvement low` completes successfully
- Executor interfaces defined — claude_code and api backends contracted
  - `core/executor/models.py` — ExecutorBackend, ExecutorStatus, AgentContext, AgentPrompt, BudgetUsage, ExecutorResult
  - `core/executor/base.py` — BaseExecutor ABC, shared _parse_roots_updates, build_prompt_text contract
  - `core/executor/claude_code.py` — ClaudeCodeExecutor contract (all NotImplementedError)
  - `core/executor/api.py` — APIExecutor contract (all NotImplementedError)
  - `bonsai/cli/run_command.py` — run_task, _load_bonsai_config, _select_executor, _route_task, _load_agent_context, _apply_roots_updates contracts
  - Two decisions recorded: executor backends, keyword routing

---

## In Progress

- Executor layer Builder implementation — all NotImplementedError stubs to be replaced

---

## Next

- Implement all NotImplementedError stubs in executor layer and run_command.py
- Write tests/test_executor.py and pass all tests
- Smoke test: bonsai run against BonsAI itself

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

**Session: 2026-04-08**

Reconnaissance agent implemented in full. All `NotImplementedError` stubs replaced with working Python code. `scan_project_structure` uses `os.walk` with in-place directory pruning to skip `.git`, `__pycache__`, `node_modules`, and similar. `identify_domains` unwraps container folders (`src/`, `app/`) to find domain subdirectories, then combines folder signals, graphify community signals, requirements.txt package hints, entry point signals, and git frequency signals — assigning HIGH (3+), MEDIUM (2), or LOW (1) confidence. `detect_patterns` checks for repeated filenames (≥3 occurrences, excluding conventional files), similar folder structures (Jaccard similarity >70%), and oversized files (>500 lines). `analyze_git_history` runs `git log` with subprocess, parses commit blocks into per-folder frequency counts and co-change pairs. `identify_gaps` produces four gaps (purpose, activity, duplication, constraints) filtered by involvement_preference. `propose_roster` produces one `{name}_agent` per HIGH/MEDIUM domain, merges LOW domains into parents or marks `_unverified_agent`, always appends quality and evaluator. `write_to_roots` writes codebase entries, dependency entries, pattern entries, project state, and agent `.md` files via RootManager and direct pathlib writes. 31 unit tests written and all passing. `AgentPipeline` pattern registered in `context/patterns.md`. Phase 3 complete.

---

**Session: 2026-04-08**

CLI entry point implemented in full. `bonsai/__main__.py` provides `python -m bonsai` routing with argparse subcommands. `bonsai/cli/display.py` centralises all terminal output with box-drawing table functions for domain summary and roster display. `bonsai/cli/init_command.py` wires the full init pipeline: path validation, roots/ initialization, RootManager startup, ReconnaissanceAgent run, developer gap presentation, roster confirmation, and .bonsai config write. 18 unit tests written and all passing. Smoke tested against BonsAI codebase itself — `bonsai init . --involvement low` completes successfully, writing .bonsai and vision.md. Phase 4 complete.

---

_Last updated: 2026-04-08_
