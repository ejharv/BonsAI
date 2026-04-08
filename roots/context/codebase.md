# Codebase Map

> Updated after every significant code change. A module added without an entry here is not tracked.

---

## Current State

**Phase 6 in progress. Orchestrator interfaces defined and implemented.**

Twenty-five modules tracked. Core contracts, root manager, reconnaissance agent, CLI, executor layer, and orchestrator all present. `bonsai run-multi` wired — multi-agent execution tree with agent-driven branching.

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
├── lifecycle/
│   ├── __init__.py
│   └── lifecycle.py
├── executor/
│   ├── __init__.py
│   ├── models.py
│   ├── base.py
│   ├── claude_code.py
│   └── api.py
└── orchestrator/
    ├── __init__.py
    ├── models.py
    ├── node.py
    └── orchestrator.py
```

---

## Module Registry

| Module Name | Purpose | Owner Agent | Status | Last Modified |
|-------------|---------|-------------|--------|---------------|
| `core/seed/seed.py` | Seed dataclass and all component structures (Identity, Contract, ResourceEnvelope, CapabilityNeed, GrowthConditions, Signal, Closure) | Architect | `defined` | 2026-04-07 |
| `core/invariants/invariants.py` | Three invariant contracts: intent coherence, budget conservation, signal propagation — check_budget_conservation implemented by smoke test agent | Architect/Builder | `partial` | 2026-04-08 |
| `core/lifecycle/lifecycle.py` | Lifecycle stages enum and all valid state transitions | Architect | `defined` | 2026-04-07 |
| `core/executor/models.py` | Typed inputs and outputs for all executor backends: ExecutorBackend, ExecutorStatus, AgentContext, AgentPrompt, BudgetUsage, ExecutorResult | Architect | `implemented` | 2026-04-08 |
| `core/executor/base.py` | Abstract BaseExecutor ABC; shared _parse_roots_updates; build_prompt_text fully implemented | Builder | `implemented` | 2026-04-08 |
| `core/executor/claude_code.py` | ClaudeCodeExecutor — claude --print subprocess; is_available, execute, _parse_roots_updates, _calculate_budget implemented | Builder | `implemented` | 2026-04-08 |
| `core/executor/api.py` | APIExecutor — Anthropic SDK; is_available, execute with exact token tracking, _calculate_budget implemented | Builder | `implemented` | 2026-04-08 |
| `root_manager/models.py` | Typed representations of all roots/ structures: FileStatus, Freshness, RootFile, RegionIndex, ProjectState, DecisionEntry, CodebaseEntry, DependencyEntry, RootManagerResult | Architect | `implemented` | 2026-04-07 |
| `root_manager/reader.py` | All read operations against roots/; parses .md content into typed structures; returns RootManagerResult | Builder | `implemented` | 2026-04-07 |
| `root_manager/writer.py` | All write operations against roots/; serializes typed structures to .md; marks files DIRTY after every write | Builder | `implemented` | 2026-04-07 |
| `root_manager/manager.py` | Single interface between agents and roots/; composes reader and writer; manages session-level file status cache | Builder | `implemented` | 2026-04-07 |
| `agents/reconnaissance/models.py` | Typed inputs and outputs for the reconnaissance agent: ConfidenceLevel, GapSeverity, ObservedDomain, DetectedPattern, DeveloperGap, ReconnaissanceInput, ReconnaissanceOutput | Architect | `implemented` | 2026-04-08 |
| `agents/reconnaissance/agent.py` | ReconnaissanceAgent — full ten-step pipeline: load_graphify_report, scan_project_structure, identify_domains, detect_patterns, analyze_git_history, identify_gaps, propose_roster, write_to_roots | Builder | `implemented` | 2026-04-08 |
| `bonsai/__main__.py` | CLI entry point; routes `python -m bonsai <command>` to subcommand handlers; argparse-based with `init` and `run` subcommands | Builder | `implemented` | 2026-04-08 |
| `bonsai/cli/display.py` | All terminal output for the CLI; print_header, print_step, print_success, print_warning, print_error, print_domain_summary, print_gap_question, print_roster_summary, print_bonsai_complete | Builder | `implemented` | 2026-04-08 |
| `bonsai/cli/init_command.py` | Implementation of `bonsai init`; wires ReconnaissanceAgent, gap presentation, roots/ initialization, roster confirmation, and .bonsai config write | Builder | `implemented` | 2026-04-08 |
| `bonsai/cli/run_command.py` | Implementation of `bonsai run`; routes task to agent, builds AgentPrompt, executes via executor, applies roots updates, reports results | Builder | `implemented` | 2026-04-08 |
| `tests/test_root_manager.py` | 24 unit tests covering RootReader, RootWriter, and RootManager — all passing | Builder | `complete` | 2026-04-07 |
| `tests/test_reconnaissance.py` | 31 unit tests covering ReconnaissanceAgent pipeline, domain identification, pattern detection, gap analysis, roster proposal, and write_to_roots — all passing | Builder | `complete` | 2026-04-08 |
| `tests/test_cli.py` | 18 unit tests covering _initialize_roots, display functions, _write_bonsai_config, and run_init integration — all passing | Builder | `complete` | 2026-04-08 |
| `tests/test_executor.py` | 26 unit tests covering ClaudeCodeExecutor, APIExecutor, _load_bonsai_config, and _route_task — all passing | Builder | `complete` | 2026-04-08 |
| `core/orchestrator/models.py` | Typed structures for orchestrator runtime: NodeStatus, BranchRequest, BranchingSignal, NodeResult, OrchestratorConfig, RunResult | Architect | `implemented` | 2026-04-08 |
| `core/orchestrator/node.py` | Node — live Seed in execution; wraps Seed with stage, status, children, executor; all methods implemented | Builder | `implemented` | 2026-04-08 |
| `core/orchestrator/orchestrator.py` | Orchestrator — manages multi-agent execution trees; agent-driven branching; budget allocation; signal aggregation; all methods implemented | Builder | `implemented` | 2026-04-08 |
| `bonsai/cli/multi_command.py` | Implementation of `bonsai run-multi`; wires Orchestrator to CLI; print_run_result with tree output | Builder | `implemented` | 2026-04-08 |

Status values: `defined` (interface exists, no implementation) → `in progress` → `implemented` → `complete` → `deprecated`

---

## Freshness Protocol

This file must be updated whenever:
- A new module is created
- A module's status changes
- A module is deprecated or removed
- The owner agent changes

The Builder is responsible for keeping this file current. A codebase.md that lags behind `src/` is a bug.

---

_Last updated: 2026-04-08 (Phase 6 orchestrator implemented)_
