# Flow: Brownfield Onboarding

---

## Flow Name

**Brownfield Onboarding**

---

## Intent

Derive a root system and agent roster from an existing codebase with minimal developer input. The developer points Bonsai at a codebase; this flow produces a populated context map, an agent roster calibrated to what already exists, and a quality baseline — without requiring the developer to explain what they have already built.

---

## Success Criteria

- Codebase mapped accurately in `context/codebase.md` and `context/patterns.md`
- Structural gaps and risks identified in `quality/debt.md`
- Developer questions during the flow are minimal (under 5), specific, and non-redundant
- Agent roster proposed reflects the actual structure of the codebase, not a generic template
- Developer has approved the roster understanding what each agent will do to their codebase
- Quality baseline established: debt logged, patterns registered, dependencies mapped
- First agent ready to begin work on developer's stated priority

---

## Input Schema

| Field | Required | Description |
|-------|----------|-------------|
| `codebase_path` | required | Path to the root of the existing codebase |
| `trust_git_history` | required | `true` to use git log for context derivation; `false` to rely only on current state |
| `involvement_preference` | required | How much the developer wants to be consulted: `high`, `medium`, or `low` |
| `stated_priority` | optional | What the developer most wants help with first (e.g. "add tests", "refactor auth", "build new feature X") |

---

## Phases

### Phase 1: Reconnaissance

The Architect and Quality agents survey the codebase:
- Directory structure and module boundaries
- Language, framework, and dependency stack
- Test coverage presence and patterns
- Git history (if `trust_git_history: true`) for intent and evolution
- Existing documentation and inline comments

Output: draft `context/codebase.md`, draft `context/patterns.md`, draft `context/dependencies.md`

### Phase 2: Draft Generation

From the reconnaissance output, draft all root system files:
- `project/vision.md` — inferred from codebase purpose
- `project/state.md` — current phase set to "Brownfield Onboarding"
- `quality/debt.md` — initial findings from reconnaissance
- `agents/` — proposed roster based on codebase structure

### Phase 3: Gap-Filling Dialogue

Surface specific, targeted questions to the developer for information that cannot be derived from code inspection. Questions must be:
- Specific (not "tell me about your architecture")
- Non-redundant (never ask what is already in the code)
- Bounded (maximum 5 questions per onboarding session)

Examples of valid gap-filling questions:
- "This service appears to handle auth — is there an external identity provider, or is it fully self-contained?"
- "I see three similar data transformation modules. Are these intentionally separate or candidates for consolidation?"

### Phase 4: Roster Proposal

Present the proposed agent roster with rationale. Each agent entry includes:
- Why this domain needs its own agent given this specific codebase
- What the agent's first action will be
- What it will not touch

### Phase 5: Confirmation

Developer approves or modifies the roster. All modifications recorded in `project/decisions.md`. First agent begins work on `stated_priority` (or the highest-value identified gap if none was stated).

---

## Success Score

_Not evaluated. Will be set by Evaluator after first validation run._

---

_Last updated: 2026-04-07_
