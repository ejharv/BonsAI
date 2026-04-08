# Dependency Map

> Before any pruning proposal, the Quality agent reads this file to assess blast radius. A component cannot be removed without understanding what depends on it.

---

## Purpose

Map what connects to what across the entire project. This enables the Quality agent to assess blast radius before proposing any removal or restructuring, and helps the Architect reason about the structural impact of interface changes.

The Architect writes to this file when establishing structural contracts. The Builder updates it when adding or removing dependencies during implementation.

---

## Dependency Registry

| Component | Depends On | Depended On By | Criticality |
|-----------|-----------|----------------|-------------|
| `core/seed/seed.py` | nothing external | `core/invariants/invariants.py`, everything that executes a seed | `critical` |
| `core/invariants/invariants.py` | `core/seed/seed.py` | everything that executes a seed | `critical` |
| `core/lifecycle/lifecycle.py` | nothing external | everything that transitions a seed | `critical` |
| `root_manager/models.py` | nothing external | `root_manager/reader.py`, `root_manager/writer.py`, `root_manager/manager.py`, all agents | `critical` |
| `root_manager/reader.py` | `root_manager/models.py` | `root_manager/manager.py`, all agents | `critical` |
| `root_manager/writer.py` | `root_manager/models.py` | `root_manager/manager.py`, all agents | `critical` |
| `root_manager/manager.py` | `root_manager/reader.py`, `root_manager/writer.py`, `root_manager/models.py` | all agents | `critical` |
| `agents/reconnaissance/models.py` | nothing external | `agents/reconnaissance/agent.py` | `critical` |
| `agents/reconnaissance/agent.py` | `root_manager/manager.py`, `agents/reconnaissance/models.py` | `bonsai/cli/init_command.py` | `high` |
| `bonsai/cli/display.py` | nothing external | `bonsai/cli/init_command.py` | `medium` |
| `bonsai/cli/init_command.py` | `agents/reconnaissance/agent.py`, `agents/reconnaissance/models.py`, `root_manager/manager.py`, `bonsai/cli/display.py` | `bonsai/__main__.py` | `high` |
| `bonsai/__main__.py` | `bonsai/cli/init_command.py`, `bonsai/cli/run_command.py` | nothing (entry point) | `medium` |
| `core/executor/models.py` | nothing external | `core/executor/base.py`, `core/executor/claude_code.py`, `core/executor/api.py`, `bonsai/cli/run_command.py` | `critical` |
| `core/executor/base.py` | `core/executor/models.py` | `core/executor/claude_code.py`, `core/executor/api.py`, `bonsai/cli/run_command.py` | `critical` |
| `core/executor/claude_code.py` | `core/executor/base.py`, `core/executor/models.py` | `bonsai/cli/run_command.py` | `high` |
| `core/executor/api.py` | `core/executor/base.py`, `core/executor/models.py` | `bonsai/cli/run_command.py` | `high` |
| `bonsai/cli/run_command.py` | `core/executor/base.py`, `core/executor/models.py`, `root_manager/manager.py` | `bonsai/__main__.py`, `core/orchestrator/orchestrator.py` | `high` |
| `core/orchestrator/models.py` | `core/seed/seed.py`, `core/lifecycle/lifecycle.py`, `core/executor/models.py` | `core/orchestrator/node.py`, `core/orchestrator/orchestrator.py`, `bonsai/cli/multi_command.py` | `critical` |
| `core/orchestrator/node.py` | `core/seed/seed.py`, `core/lifecycle/lifecycle.py`, `core/executor/base.py`, `core/orchestrator/models.py` | `core/orchestrator/orchestrator.py` | `critical` |
| `core/orchestrator/orchestrator.py` | `core/orchestrator/node.py`, `core/orchestrator/models.py`, `core/seed/seed.py`, `core/lifecycle/lifecycle.py`, `core/invariants/invariants.py`, `core/executor/base.py`, `root_manager/manager.py`, `bonsai/cli/run_command.py` | `bonsai/cli/multi_command.py` | `critical` |
| `bonsai/cli/multi_command.py` | `core/orchestrator/orchestrator.py`, `core/orchestrator/models.py`, `bonsai/cli/run_command.py`, `bonsai/cli/display.py`, `root_manager/manager.py` | `bonsai/__main__.py` | `high` |

Criticality values:
- `critical` — removing this component breaks core flows
- `high` — removing this component breaks multiple features
- `medium` — removing this component breaks one feature
- `low` — removing this component has no downstream failures (safe to prune)

---

## Assessment Protocol

Before proposing any pruning action, the Quality agent must:
1. Look up the component in this table
2. Identify all entries in "Depended On By"
3. Assess whether those dependents can be updated or if the removal is safe
4. Include this blast radius assessment in the pruning proposal

A pruning proposal without a blast radius assessment will not be approved.

---

_Last updated: 2026-04-08 (Phase 6 orchestrator)_
