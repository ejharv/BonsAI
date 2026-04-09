# Project State

> Snapshot of current work. Updated at the start and end of every session.

---

## Current Phase

**Phase 8 in progress — packaging complete, awaiting PyPI upload**

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
  - 31 unit tests in `tests/test_reconnaissance.py` — all passing
- CLI entry point implemented — bonsai init working
  - `bonsai/__main__.py` — argparse routing, `python -m bonsai` entry point
  - `bonsai/cli/display.py` — all terminal output: headers, steps, tables, gap questions, roster, completion
  - `bonsai/cli/init_command.py` — full init pipeline: validate, initialize roots/, run reconnaissance, present gaps, confirm roster, write .bonsai config
  - 18 unit tests in `tests/test_cli.py` — all passing
  - Smoke tested against BonsAI codebase itself — `bonsai init . --involvement low` completes successfully
- bonsai run working — executor layer complete, smoke test passed
  - `core/executor/models.py` — ExecutorBackend, ExecutorStatus, AgentContext, AgentPrompt, BudgetUsage, ExecutorResult
  - `core/executor/base.py` — BaseExecutor ABC, shared _parse_roots_updates, build_prompt_text implemented
  - `core/executor/claude_code.py` — ClaudeCodeExecutor fully implemented
  - `core/executor/api.py` — APIExecutor fully implemented
  - `bonsai/cli/run_command.py` — full run pipeline implemented
  - 26 unit tests in `tests/test_executor.py` — all passing
  - Smoke tested: `bonsai run` routed to builder, executed via claude_code, applied roots updates, 7.59 budget units, 70.8s
  - `check_budget_conservation` implemented in `core/invariants/invariants.py` by smoke test agent
- Orchestrator implemented and smoke tested — multi-agent runs working
  - `core/orchestrator/models.py` — NodeStatus, BranchRequest, BranchingSignal, NodeResult, OrchestratorConfig, RunResult
  - `core/orchestrator/node.py` — Node (live Seed in execution): all methods implemented
  - `core/orchestrator/orchestrator.py` — Orchestrator: all 11 methods implemented; agent-driven branching; budget allocation; signal aggregation; lifecycle enforcement
  - `bonsai/cli/multi_command.py` — run_multi, print_run_result, _print_node_tree implemented
  - `bonsai/__main__.py` — run-multi subcommand added
  - Two decisions recorded: agent-driven branching, orchestrator lifecycle ownership
  - Smoke tested: `bonsai run-multi` completed in 116.3s, 1 node, 12.26 budget units, Success: True
  - `check_signal_propagation` implemented in `core/invariants/invariants.py`
- Observability layer implemented — bonsai status and bonsai report working
  - `bonsai/observability/store.py` — RunStore fully implemented; JSON persistence, prefix-match load, index prepend
  - `bonsai/observability/report.py` — ReportGenerator fully implemented; run_summary, budget, tree, health reports
  - `bonsai/observability/dashboard.py` — Dashboard fully implemented; all render sections working
  - `bonsai/cli/status_command.py` — run_status implemented
  - `bonsai/cli/report_command.py` — run_report implemented
  - `bonsai/__main__.py` — status and report subcommands wired
  - RunStore wired into orchestrator.py (saves after every run-multi)
  - RunStore wired into run_command.py (saves after every bonsai run)
  - 29 unit tests in tests/test_observability.py — all passing (128 total)
  - Smoke tested: bonsai status, bonsai report runs/health/tree all working
  - Two decisions recorded: run history as JSON, status/report as CLI commands
- Timeout UX fixed, progress spinner added, CLAUDE.md created
  - Progress spinner in ClaudeCodeExecutor — thread + itertools.cycle braille frames
  - Default timeout raised from 180s to 300s across all execution paths
  - --timeout flag added to bonsai run and bonsai run-multi
  - Better timeout error message with exact retry command
  - CLAUDE.md created in project root with environment, structure, git, commands, and style rules
  - 128 unit tests still passing
- Reconnaissance agent bugs fixed — 5 bugs from FitCypher real project test
  - Bug 1: .vscode and roots/ appearing as domains — expanded _EXCLUDED_DIRS, filter top_level_folders
  - Bug 2: public/ not detected as domain — content-based _is_container_folder replaces name-based _CONTAINER_FOLDERS check
  - Bug 3: deprecated code getting MEDIUM confidence — analyze_git_history moved before identify_domains; confidence adjustment step added
  - Bug 4: multi-line paste breaks gap input — _flush_stdin() added to init_command.py, called after each input() and before roster confirmation
  - Bug 5: index.md false positive repetition — _CONVENTIONAL_FILENAMES expanded; roots/ excluded via _EXCLUDED_DIRS
  - 128 unit tests still passing
- FitCypher real project test complete — bonsai init and bonsai run both validated on real external project
- Roster-aware routing, roots format instructions, validator fix applied
- pyproject.toml created, README written, package built (bonsaif-0.1.0 — twine check PASSED)

---

## In Progress

- PyPI publish (waiting for account confirmation)

---

## Next

- Upload to PyPI (`python3 -m twine upload dist/*`)

---

## Blockers

_None._

---

## Last Session Summary

**Session: 2026-04-08**

Phase 5 complete. Executor layer implemented in full. `core/executor/base.py` — BaseExecutor ABC with shared `_parse_roots_updates` and `build_prompt_text`. `core/executor/claude_code.py` — ClaudeCodeExecutor: runs claude --print subprocess, tracks wall time and output length for budget proxy. `core/executor/api.py` — APIExecutor: calls Anthropic SDK, tracks exact tokens, 3x output weight in budget formula. `bonsai/cli/run_command.py` — full run pipeline: config loading, auto-select executor, keyword routing, agent context assembly, prompt construction, execution, roots update application, result reporting. 26 unit tests in `tests/test_executor.py` — all passing. Smoke tested: `bonsai run "implement check_budget_conservation..." --executor claude_code --budget 15.0` completed in 70.8s consuming 7.5934 budget units, routed to builder agent, applied roots updates to state.md and codebase.md. Agent provided `check_budget_conservation` implementation which was applied to `core/invariants/invariants.py`.

---

**Session: 2026-04-08 (orchestrator)**

Phase 6 complete. Orchestrator implemented in full. `core/orchestrator/models.py`, `core/orchestrator/node.py`, `core/orchestrator/orchestrator.py` — all interfaces defined and all stubs implemented. `bonsai/cli/multi_command.py` — run-multi CLI wired. `bonsai/__main__.py` — run-multi subcommand added. `check_signal_propagation` invariant implemented. Smoke tested: `bonsai run-multi` completed in 116.3s, 1 node, 12.2627 budget units consumed, Success: True. No branching in this run (task handled by single node). 99 unit tests passing.

---

**Session: 2026-04-08 (Phase 8)**

Phase 8 in progress. pyproject.toml created — name bonsaif, version 0.1.0, zero required dependencies, anthropic SDK optional via `bonsaif[api]`. README.md written — full public-facing documentation covering quickstart, commands, executor backends, philosophy, and status. Package built: `python3 -m build` succeeded, both sdist and wheel created. `twine check` PASSED on both artifacts. Zero-dependency decision recorded in decisions.md. Awaiting PyPI account confirmation before upload.

---

_Last updated: 2026-04-08 (Phase 8 in progress — packaging complete, awaiting PyPI upload)_
