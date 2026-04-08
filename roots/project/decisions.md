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
| 2026-04-07 | Use graphify for brownfield codebase comprehension during onboarding | graphify is a Claude Code skill that produces a structured knowledge graph from an existing codebase cheaply and locally using tree-sitter AST for code files. The reconnaissance agent reads graphify's GRAPH_REPORT.md as its starting orientation rather than discovering structure from scratch. Clean division of responsibility: graphify answers what exists, reconnaissance agent answers what it means for how Bonsai should build. This reduces reconnaissance agent budget consumption significantly. | **Reconnaissance agent reads codebase directly** — rejected because graphify does this better, cheaper, and without sending code to external APIs. |
| 2026-04-07 | Graphify runs once at brownfield onboarding, roots/ owns continuous updates thereafter | graphify is a comprehension tool not a continuous update system. After onboarding, Bonsai's root system tracks all changes as agents work. Graphify may re-run periodically as an independent audit — comparing fresh extraction against roots/ state to detect drift from manual changes made outside Bonsai. It never replaces roots/ as the live source of truth. | **Continuous graphify re-extraction** — rejected as expensive and redundant given roots/ already tracks changes continuously. |
| 2026-04-07 | Reconnaissance agent is read-only with respect to source code | The reconnaissance agent must never modify project files. It only reads and writes to roots/. This makes onboarding safe to run on any project without risk of unintended changes. Trust must be earned before write access is granted. | **Agent proposes fixes during reconnaissance** — rejected because onboarding is an observation phase not a build phase. |

---

### Decision: "Two executor backends — claude_code and api"
**Date:** 2026-04-08
**Rationale:** Bonsai supports two execution modes. claude_code mode uses Claude Code CLI via subprocess with --print flag — works with Max plan subscription, no API key needed. api mode calls Anthropic API directly via Python SDK — requires API key, gives precise token tracking, better for production deployments. The executor interface is identical in both modes. The .bonsai config specifies which executor a project uses. Budget tracking: api mode uses exact token counts. claude_code mode uses wall clock time and output length as proxy metrics.
**Alternatives considered:** claude_code only — rejected because production deployments may not have Max plan. api only — rejected because user already pays for Max plan and should not need separate API credits for local development.

### Decision: "Keyword routing for initial task-to-agent mapping"
**Date:** 2026-04-08
**Rationale:** Simple keyword matching routes tasks to agents for the first implementation. Sufficient for Phase 5. Will be replaced with semantic routing using embeddings in a future phase when the system has enough usage data to validate routing accuracy.
**Alternatives considered:** Embedding similarity routing — deferred, adds complexity before we have evidence simple routing fails.

### Decision: "Agent-driven branching — agents request child spawning via structured output tags"
**Date:** 2026-04-08
**Rationale:** The executing agent has more context about task complexity than any pre-analysis heuristic. Agents signal branching need via `<branch_request>` tags in their output. The orchestrator reads these signals and spawns child seeds with sub-envelopes carved from the parent's remaining budget. Over-branching is prevented by the budget envelope — children cannot spawn if headroom is below `min_branch_size` threshold. Branching is more efficient not less — child agents carry narrow focused context rather than full task context. Parent role shrinks to decomposition and synthesis.
**Alternatives considered:** Orchestrator pre-analysis branching — rejected because it loses the agent's nuanced understanding of task complexity.

### Decision: "Orchestrator owns all lifecycle transitions — no other component touches stages"
**Date:** 2026-04-08
**Rationale:** Centralizing lifecycle management in the orchestrator prevents race conditions and invalid transitions in concurrent execution. Clear ownership makes debugging straightforward — if a node is in the wrong stage the orchestrator is always where to look.
**Alternatives considered:** Nodes manage their own transitions — rejected because it distributes lifecycle logic across the codebase making invariant enforcement harder.

### Decision: "Run history stored as .json files in roots/runs/"
**Date:** 2026-04-08
**Rationale:** Run history needs to be persistent, queryable, and human readable. JSON files in roots/runs/ give us all three. One file per run named {run_id}.json. An index file roots/runs/index.md summarizes all runs in a scannable table. This keeps observability data alongside the project state it describes and makes it git-trackable. A developer can inspect any run by reading its JSON file directly.
**Alternatives considered:** SQLite — rejected because it is not human readable or git-diffable. In-memory only — rejected because history is lost between sessions.

### Decision: "bonsai status and bonsai report as observability CLI commands"
**Date:** 2026-04-08
**Rationale:** Developers need two modes of observability. status is a quick live dashboard — run it anytime to see project health. report generates detailed artifacts suitable for sharing or archiving. Both read from the same RunStore and ReportGenerator — the CLI commands are thin wrappers.
**Alternatives considered:** Web dashboard — rejected as too heavy for a CLI tool. Single combined command — rejected because status and report have different use patterns.

---

_Last updated: 2026-04-08_
