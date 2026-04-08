# Bonsai — Vision

---

## What Bonsai Is

Bonsai is an adaptive agent orchestration framework where structure emerges from the problem rather than being imposed on it. Instead of prescribing a fixed topology of agents, Bonsai derives its agent roster, domains, and coordination flows from a project specification. Each project grown with Bonsai gets the exact structure it needs — no more, no less.

The framework is designed for developers building agent-powered products who need reliable, inspectable, and cost-aware orchestration without betting on a black-box platform.

---

## Core Thesis

**API credits are a first-class signal.**

Every agent in Bonsai must justify its existence through contribution per cost. This is not a constraint added at optimization time — it is a design principle present from the beginning. Agents that do not produce measurable output relative to their cost are pruning candidates. The Evaluator agent exists specifically to enforce this signal.

This principle has downstream consequences:
- Agents are defined narrowly, not broadly
- Flows minimize redundant calls
- Context is spatially efficient (hence .md files, not embeddings)
- Quality is checked before, not after, expensive generation

---

## The Tree Metaphor

Bonsai is structured like a tree, deliberately.

| Layer | Metaphor | What It Contains |
|-------|----------|-----------------|
| Trunk | Foundational flows | Core orchestration logic — greenfield init, brownfield onboarding, the evaluation loop |
| Branches | Features | Domain-specific agent clusters, custom flow extensions, integration adapters |
| Leaves | Atomic operations | Single-responsibility functions, tool calls, schema validators |

Growth is intentional. A branch is only added when it serves a defined flow. A leaf is pruned when it duplicates another. The shape of the tree at any point is a direct reflection of the problems it has been asked to solve.

---

## The Root System Metaphor

The `roots/` directory is the distributed context layer of Bonsai.

Rather than storing project context in a database, a vector store, or ephemeral memory, Bonsai uses structured `.md` files as its persistent, human-readable, agent-readable, and version-controlled substrate.

Properties:
- **Human readable** — any developer can open any file and understand the state of the system
- **Git native** — every change is diffable, attributable, and reversible
- **Agent readable** — structured tables and consistent schemas make parsing deterministic
- **Spatially efficient** — no embeddings, no retrieval overhead, no hallucinated context
- **Logically traversable** — ROOT.md is the map; every region index is a directory

The root system is not documentation. It is the living nervous system of the project. Agents write to it. Agents read from it. It decays if not maintained and regenerates when maintained well.

---

## Primary Users

Developers building agent-powered products who:
- Want inspectable orchestration, not black-box pipelines
- Are cost-sensitive and need contribution-per-call accountability
- Are working on greenfield agent systems or onboarding agents onto existing codebases
- Prefer structured context over memory injection
- Value a small, stable core they can extend without fighting the framework

---

## Open Source Philosophy

Bonsai will have a small, stable core and rich extension points.

The core will cover:
- The root system schema and lifecycle
- The five foundational agents (Architect, Builder, Tester, Quality, Evaluator)
- The two foundational flows (Greenfield Init, Brownfield Onboarding)
- The evaluation loop and cost signal protocol

Extensions will cover:
- Domain-specific agent profiles
- Custom flow definitions
- Alternative model backends
- Integration adapters (CI/CD, issue trackers, deployment targets)

The core will change slowly and deliberately. Extensions will evolve with the ecosystem.

---

_Last updated: 2026-04-07_
