# Project State

> Snapshot of current work. Updated at the start and end of every session.

---

## Current Phase

**Phase 6 in progress — orchestrator implemented, multi-agent runs available**

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
- bonsai run working — executor layer complete, smoke test passed
  - `core/executor/models.py` — ExecutorBackend, ExecutorStatus, AgentContext, AgentPrompt, BudgetUsage, ExecutorResult
  - `core/executor/base.py` — BaseExecutor ABC, shared _parse_roots_updates, build_prompt_text implemented
  - `core/executor/claude_code.py` — ClaudeCodeExecutor fully implemented
  - `core/executor/api.py` — APIExecutor fully implemented
  - `bonsai/cli/run_command.py` — full run pipeline implemented
  - 26 unit tests in `tests/test_executor.py` — all passing
  - Smoke tested: `bonsai run` routed to builder, executed via claude_code, applied roots updates, 7.59 budget units, 70.8s
  - `check_budget_conservation` implemented in `core/invariants/invariants.py` by smoke test agent
- Orchestrator layer implemented
  - `core/orchestrator/models.py` — NodeStatus, BranchRequest, BranchingSignal, NodeResult, OrchestratorConfig, RunResult
  - `core/orchestrator/node.py` — Node (live Seed in execution): transition_to, record_budget_consumed, update_signal, to_result, make_seed all implemented
  - `core/orchestrator/orchestrator.py` — Orchestrator: __init__, run, _execute_node, _build_prompt, _parse_branching_signal, _spawn_children, _aggregate_signal, _prune_node, _build_run_result, _load_agent_context_for_node, _validate_transition all implemented
  - `bonsai/cli/multi_command.py` — run_multi, print_run_result, _print_node_tree implemented
  - `bonsai/__main__.py` — run-multi subcommand added
  - Two decisions recorded: agent-driven branching, orchestrator lifecycle ownership

---

## In Progress

_Orchestrator smoke test pending._

---

## Next

- **Phase 6 smoke test** — run `bonsai run-multi` against BonsAI itself and verify tree output
- **Phase 6 complete** — implement `check_intent_coherence` and `check_signal_propagation` invariants (currently raise NotImplementedError; orchestrator guards around them gracefully)

---

## Blockers

_None._

---

## Last Session Summary

**Session: 2026-04-08**

Phase 5 complete. Executor layer implemented in full. `core/executor/base.py` — BaseExecutor ABC with shared `_parse_roots_updates` and `build_prompt_text`. `core/executor/claude_code.py` — ClaudeCodeExecutor: runs claude --print subprocess, tracks wall time and output length for budget proxy. `core/executor/api.py` — APIExecutor: calls Anthropic SDK, tracks exact tokens, 3x output weight in budget formula. `bonsai/cli/run_command.py` — full run pipeline: config loading, auto-select executor, keyword routing, agent context assembly, prompt construction, execution, roots update application, result reporting. 26 unit tests in `tests/test_executor.py` — all passing. Smoke tested: `bonsai run "implement check_budget_conservation..." --executor claude_code --budget 15.0` completed in 70.8s consuming 7.5934 budget units, routed to builder agent, applied roots updates to state.md and codebase.md. Agent provided `check_budget_conservation` implementation which was applied to `core/invariants/invariants.py`.

---

_Last updated: 2026-04-08 (Phase 6 orchestrator implemented)_
