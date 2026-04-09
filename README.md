# BonsAI

**An adaptive agent orchestration
framework inspired by tree growth.**

Structure emerges from your project.
Agents justify their existence.
Everything that doesn't earn its
place gets pruned.

---

## The Idea

Most agent frameworks make you design
the structure upfront. You define
a graph, a pipeline, a hierarchy.
Then you wire agents into it.

BonsAI works the other way.

You describe what you're building.
BonsAI reads your codebase, derives
domain boundaries, assigns agents,
and grows a structure that fits your
project — not a generic template.

Like a bonsai tree, the shape that
emerges reflects the environment
it grew in.

---

## How It Works

BonsAI has two systems:

**The Root System** — a set of `.md`
files that live inside your project.
They track what exists, what's been
tried, what failed, and where the
project is going. Every agent reads
from and writes to the roots. This
is how agents stay in sync without
sharing a context window.

**The Tree** — the agents themselves.
Each agent owns a domain. No overlap.
They run concurrently where possible,
branch when tasks are complex, and
prune themselves when they're not
earning their budget.

---

## Quickstart

**Install:**

```bash
pip install bonsaif
```

**Initialize on an existing project:**

```bash
cd your-project
bonsai init .
```

BonsAI will scan your codebase,
identify domain boundaries, ask you
one question (what is this project
for?), and propose an agent roster.

**Run a task:**

```bash
bonsai run "implement user authentication
in src/auth/" --budget 20.0
```

**Check status:**

```bash
bonsai status
```

**Generate reports:**

```bash
bonsai report runs
bonsai report health
bonsai report tree --run-id <id>
```

---

## Commands

| Command | Description |
|---------|-------------|
| `bonsai init <path>` | Initialize BonsAI on a project |
| `bonsai run <task>` | Run a task with a single agent |
| `bonsai run-multi <task>` | Run with multi-agent orchestration |
| `bonsai status` | Live project dashboard |
| `bonsai report <type>` | Generate run/budget/health/tree reports |

---

## Executor Backends

BonsAI supports two backends:

**Claude Code (default)**
Uses your Claude Max plan.
No API key needed.
```bash
bonsai run "your task" --executor claude_code
```

**Anthropic API**
Precise token tracking.
Requires `ANTHROPIC_API_KEY`.
```bash
pip install bonsaif[api]
bonsai run "your task" --executor api
```

---

## What Gets Created

Running `bonsai init` adds two things
to your project:

```
your-project/
├── roots/           # BonsAI's context map
│   ├── ROOT.md      # Master index
│   ├── project/     # Vision, state, decisions
│   ├── agents/      # Agent definitions
│   ├── context/     # Codebase map, patterns
│   ├── quality/     # Repetitions, debt, pruning log
│   └── flows/       # Flow contracts
└── .bonsai          # Config (executor, roster)
```

Your source code is untouched.
The `roots/` directory is committed
to your repo — it's documentation
that stays in sync with your code.

---

## The Pruning Agent

BonsAI ships with a quality agent
that continuously monitors for:

- Repeated components across the codebase
- Oversized files that should be decomposed
- Dead code with no recent activity
- Structural debt

It never acts unilaterally. It
proposes. You decide.

```bash
bonsai run "find duplicate components
and propose consolidations" \
--agent quality
```

---

## Multi-Agent Runs

For complex tasks BonsAI can spawn
child agents that work in parallel:

```bash
bonsai run-multi \
  "implement and test the payment flow" \
  --budget 40.0 \
  --max-depth 2
```

The root agent decides whether to
branch based on task complexity and
available budget. Child agents get
focused context — only what they
need for their subtask.

---

## Observability

Every run is recorded. BonsAI tracks:
- Which agents ran and for how long
- Budget consumed per run
- Success rates over time
- Which tasks produced pruning proposals

```bash
bonsai status          # live dashboard
bonsai report health   # health overview
bonsai report budget   # spend by agent
```

---

## Philosophy

**Agents should earn their existence.**
Every agent tracks its contribution
relative to its cost. Low-value agents
get fewer resources. Consistently
low-value agents get pruned.

**Structure should emerge, not be imposed.**
BonsAI derives agent boundaries from
your actual codebase — not from a
template you fill in.

**The roots are the memory.**
Agents don't share a context window.
They share a file system. The `roots/`
directory is the project's long-term
memory — readable by humans and
agents alike.

---

## Requirements

- Python 3.10+
- Claude Code CLI (for `claude_code`
  executor) — install from
  [claude.ai/code](https://claude.ai/code)
- Claude Max, Pro, or Team plan
  (or set `ANTHROPIC_API_KEY` for
  api executor mode)

---

## Status

BonsAI is in active development.
Current version: 0.1.0 (Alpha)

What works:
- `bonsai init` on greenfield and
  brownfield projects
- `bonsai run` with claude_code
  and api executors
- Multi-agent runs with branching
- Full observability and reporting
- 128 unit tests passing

What's coming:
- `check_intent_coherence` invariant
  (requires embedding similarity)
- Web dashboard
- More agent types
- Plugin system for custom executors

---

## Contributing

BonsAI is open source under
Apache 2.0.

Before contributing read
`ARCHITECTURE.md` — it explains
the design principles behind every
decision. PRs that conflict with
the architecture will be declined
not because they're wrong but because
they need to be reasoned through first.

```bash
git clone https://github.com/ejharv/BonsAI
cd BonsAI
python3 -m unittest discover tests/ -v
```

---

## License

Apache 2.0 — see LICENSE file.

---

*Structure emerges. Agents earn
their place. Everything else
gets pruned.*
