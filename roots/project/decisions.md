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

---

_Last updated: 2026-04-07_
