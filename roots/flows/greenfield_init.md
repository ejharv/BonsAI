# Flow: Greenfield Initialization

---

## Flow Name

**Greenfield Initialization**

---

## Intent

Derive a complete root system and agent roster from a project specification provided by a new developer. The developer describes what they are building; this flow produces a fully initialized Bonsai context map, a tailored agent roster, and a first agent ready to begin work — without the developer needing to understand the internal structure of the framework.

---

## Success Criteria

- Root system fully populated with project-specific content (not generic placeholders)
- Agent roster reviewed and explicitly approved by the developer
- Developer understands what each agent in the roster does and why it exists
- At least one agent is ready to begin its first task
- Developer has not been asked to answer the same question twice
- Total API cost for initialization is within acceptable bounds for a setup operation

---

## Input Schema

The developer provides a project specification containing:

| Field | Required | Description |
|-------|----------|-------------|
| `purpose` | required | What the project does and who it is for |
| `stack` | required | Languages, frameworks, infrastructure |
| `scale` | required | Expected load, team size, longevity |
| `constraints` | optional | Budget, timeline, compliance, platform |
| `priorities` | optional | Ordered list: e.g. speed, correctness, cost, maintainability |
| `involvement_preference` | required | How much the developer wants to be consulted: `high` (approve everything), `medium` (approve major decisions), `low` (approve only blocking decisions) |

---

## Steps

1. **Validate specification** — confirm all required fields are present and coherent. If gaps exist, ask targeted clarifying questions (one round maximum).

2. **Derive domains** — from the specification, the Architect identifies the distinct problem domains this project requires. Each domain becomes a candidate for an agent.

3. **Propose agent roster** — the Architect drafts an agent roster with one file per agent, each with a defined domain, skills, rules, and access boundaries. Presents to developer with rationale.

4. **Developer approval** — developer reviews roster. May approve, request changes, or remove agents. Changes are recorded in `project/decisions.md`.

5. **Initialize root system** — with the approved roster, populate all `roots/` files with project-specific content: vision, state, context schemas, quality schemas, flow adaptations.

6. **Begin** — the first agent in the approved roster is briefed on its first task. Work begins.

---

## Success Score

_Not evaluated. Will be set by Evaluator after first validation run._

---

_Last updated: 2026-04-07_
