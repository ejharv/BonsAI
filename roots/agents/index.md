# Agents Region — Index

This region defines every agent in the Bonsai framework. Each file is a contract: it specifies the agent's domain, capabilities, rules of operation, and the exact files it is permitted to read from and write to. No agent operates outside these boundaries without an explicit architectural decision recorded in [project/decisions.md](../project/decisions.md).

---

## Table of Contents

| File | Agent | Domain Summary |
|------|-------|---------------|
| [architect.md](architect.md) | Architect | System design, seed definition, root structure, agent boundaries |
| [builder.md](builder.md) | Builder | Implementation of defined interfaces, production code |
| [tester.md](tester.md) | Tester | Test coverage, behavior verification, regression detection |
| [quality.md](quality.md) | Quality | Pattern detection, duplication identification, pruning proposals |
| [evaluator.md](evaluator.md) | Evaluator | Synthetic testing, persona simulation, success criteria assessment |

---

## Status Table

| File | Status | Owner Agent | Last Updated | Freshness |
|------|--------|-------------|--------------|-----------|
| architect.md | clean | Architect | 2026-04-07 | fresh |
| builder.md | clean | Architect | 2026-04-07 | fresh |
| tester.md | clean | Architect | 2026-04-07 | fresh |
| quality.md | clean | Architect | 2026-04-07 | fresh |
| evaluator.md | clean | Architect | 2026-04-07 | fresh |

Freshness legend: `fresh` (updated this session) → `aging` (1–3 sessions old) → `stale` (needs review)

---

_Last updated: 2026-04-07_
