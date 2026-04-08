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

---

_Last updated: 2026-04-07_
