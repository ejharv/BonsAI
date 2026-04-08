# Technical Debt Log

> Known shortcuts and structural problems. Every item here represents a known deviation from the intended design that has been accepted temporarily.

---

## Purpose

Track deliberate shortcuts, deferred work, and structural problems that have been acknowledged but not yet resolved. Technical debt is not inherently bad — sometimes it is the right trade-off. What is unacceptable is unacknowledged debt. Every item here is named, located, severity-rated, and has a suggested resolution path.

---

## Debt Registry

| Item | Location | Severity | Suggested Resolution | Date Logged |
|------|----------|----------|---------------------|-------------|
| — | — | — | — | — |

Severity values:
- `critical` — this will cause failures if not addressed soon
- `high` — this is actively slowing development or creating confusion
- `medium` — this should be addressed in the next cleanup phase
- `low` — this is a known imperfection, acceptable indefinitely

---

## Entry Protocol

When logging a new debt item:
- Be specific about location (file path, function name)
- Explain why the shortcut was taken (time pressure, uncertainty, experimentation)
- Provide a concrete resolution path, not just "fix it"
- Severity should reflect actual impact, not aesthetic preference

---

_Last updated: 2026-04-07_
