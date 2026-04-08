# Bonsai — Claude Code Instructions

## Environment
- Always use `python3` not `python`
- Always use `pip3` not `pip`
- All tests run with:
  `python3 -m unittest discover tests/ -v`

## Project Structure
- Root system lives in `roots/`
- Read `roots/project/state.md`
  at the start of every session
- Source code organized as:
  `core/` — seed, invariants,
  lifecycle, executor, orchestrator
  `root_manager/` — file interface
  `agents/` — agent implementations
  `bonsai/` — CLI entry points
  `tests/` — all test files

## Git
- Default branch is `main`
- Always push to `origin main`
- Commit message format:
  "Phase N: description"

## Commands
- Run all tests:
  `python3 -m unittest discover tests/ -v`
- Run Bonsai:
  `python3 -m bonsai <command>`
- Check status:
  `python3 -m bonsai status`

## Style Rules
- stdlib only unless explicitly told
  otherwise
- pathlib over os.path always
- Type annotations on all functions
- No external dependencies without
  explicit approval
