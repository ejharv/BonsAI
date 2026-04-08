# Pruning Log

> Complete audit trail of all pruning proposals and their outcomes. Written by the Quality agent and Evaluator. Approved or rejected by the developer. Executed by the Builder.

---

## Purpose

Record every pruning proposal made in this project, whether approved or rejected, and the outcome of each action taken. This log exists so that pruning decisions can be reviewed, reversed, and learned from. A pruning action taken without a log entry is an unauthorized action.

---

## Pruning History

| Date | What | Why | Proposed Action | Developer Decision | Outcome |
|------|------|-----|-----------------|--------------------|---------|
| — | — | — | — | — | — |

Developer Decision values: `approved` / `rejected` / `deferred`
Outcome values: `completed` / `reverted` / `superseded` / `pending`

---

## Proposal Protocol

When the Quality agent or Evaluator writes a pruning proposal:
1. Add entry with developer decision = `pending`
2. Surface the proposal to the developer
3. Record developer decision when given
4. If approved: Builder executes, Outcome updated to `completed`
5. If rejected: record reason in Outcome column

No pruning action may be taken without a `approved` entry in this log.

---

_Last updated: 2026-04-07_
