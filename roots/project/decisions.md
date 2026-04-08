# Decision Log

> Append-only. Never edit existing entries. Add new rows at the bottom.

---

## Format

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| — | — | — | — |

---

## Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-04-07 | Use `.md` files as root system substrate | Human readable — any developer can inspect state without tooling. Git native — every change is diffable and reversible. Agent readable — structured tables with consistent schemas are deterministically parseable. Versionable — context history is commit history. Spatially efficient — no retrieval infrastructure required. | **Database** (requires running infrastructure, not git native, opaque to humans); **JSON files** (machine-readable but hostile to human editing and review); **Vector store** (high retrieval overhead, hallucination risk, requires embeddings pipeline, opaque) |
| 2026-04-07 | Python as Bonsai's implementation language | AI ecosystem is Python first. Anthropic SDK, agent tooling, async task execution, and open source contributor familiarity all favor Python. Bonsai's target projects can be in any language — Bonsai itself only manages agents and reads/writes files. The implementation language and the target project language are independent concerns. | **TypeScript** — ruled out because the core integration layer is AI tooling which is Python first. Not because of target project limitations. |
| 2026-04-07 | NotImplementedError for invariant logic in Phase 1 | Invariants are contracts first, implementations second. Defining what they must do before defining how they do it prevents implementation from distorting the contract. | **Stub returns** — rejected because they could be accidentally called without raising. **Mock implementations** — rejected for the same reason. |
| 2026-04-07 | Use budget not credits as internal resource unit terminology | Credits implies API billing which Bonsai does not manage. Budget better represents the abstract concept of allocated agent effort. Bonsai's resource accounting is billing agnostic. | **Tokens** — ambiguous (also used for LLM context length). **Units** — too generic. **Compute** — implies infrastructure cost. All more ambiguous than budget. |
| 2026-04-07 | RootManager as single interface — no direct file access by agents | Centralizing file access enables dirty flag management, session caching, and consistent parsing without duplicating logic across agents. One place to fix if the roots/ structure changes. | **Agents read files directly** — rejected because dirty flag propagation becomes impossible to coordinate. |
| 2026-04-07 | Bonsai runs alongside projects, not inside them. Roots live inside the target project. | Bonsai is installed once as a tool and pointed at any project. The `roots/` directory lives inside the target project and is committed to that project's git repo. This keeps roots and code version controlled together, makes context available to all developers who clone the project, and preserves the history of what Bonsai understood at the moment each piece of code was written. A `.bonsai` config file in the project root stores the project spec and involvement preference. | **Roots in separate repo** — rejected because context gets lost on clone. **Bonsai as project template** — rejected because it pollutes the project structure and couples the project to Bonsai. |
| 2026-04-07 | CLI interface for Bonsai — `bonsai init` and `bonsai run` | Developers interact with Bonsai through a CLI. Two primary commands: `bonsai init` for brownfield onboarding or greenfield initialization, `bonsai run` for executing tasks. This keeps the interface simple and scriptable without requiring developers to understand the internal architecture. | **Python API only** — rejected because it requires developers to write orchestration code themselves. **Web interface** — out of scope for core. |

---

_Last updated: 2026-04-07_
