"""
The lifecycle defines every valid state a Seed can be in and every valid
transition between states. A Seed that violates a lifecycle transition has a
bug. The lifecycle is the grammar of Bonsai execution.
"""

from enum import Enum, auto
from dataclasses import dataclass


class LifecycleStage(Enum):
    GERMINATING = auto()   # assessing input, forming growth intention, not yet consuming significant budget
    GROWING = auto()       # actively executing against intent as single agent
    BRANCHING = auto()     # spawning child seeds, subdividing resource envelope
    CONTRACTING = auto()   # reducing resource usage under pressure from parent, simplifying approach
    CLOSING = auto()       # emitting closure signal, returning budget, writing pattern record
    CLOSED = auto()        # terminal state, node is done, cannot transition further


@dataclass
class LifecycleTransition:
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    # trigger: what causes this transition
    trigger: str
    # reason: why this transition is valid
    reason: str


VALID_TRANSITIONS: list[LifecycleTransition] = [
    LifecycleTransition(
        from_stage=LifecycleStage.GERMINATING,
        to_stage=LifecycleStage.GROWING,
        trigger="assessment_complete",
        reason="Node has assessed input and formed growth intention",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GERMINATING,
        to_stage=LifecycleStage.CLOSING,
        trigger="germination_failed",
        reason="Input cannot be assessed or violates contract input schema",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GROWING,
        to_stage=LifecycleStage.BRANCHING,
        trigger="complexity_threshold_exceeded",
        reason="Task complexity exceeds single agent capacity and budget headroom exists",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GROWING,
        to_stage=LifecycleStage.CONTRACTING,
        trigger="warn_threshold_reached",
        reason="Contribution ratio has fallen below warn threshold",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GROWING,
        to_stage=LifecycleStage.CLOSING,
        trigger="task_complete",
        reason="Node has satisfied its success criteria",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GROWING,
        to_stage=LifecycleStage.CLOSING,
        trigger="prune_threshold_reached",
        reason="Contribution ratio is consistently below prune threshold",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.GROWING,
        to_stage=LifecycleStage.CLOSING,
        trigger="budget_exhausted",
        reason="budget_available has reached zero before task completion",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.BRANCHING,
        to_stage=LifecycleStage.GROWING,
        trigger="children_complete",
        reason="All child seeds have closed, node synthesizes their outputs",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.BRANCHING,
        to_stage=LifecycleStage.CLOSING,
        trigger="all_children_pruned",
        reason="All spawned children were pruned before producing output",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.CONTRACTING,
        to_stage=LifecycleStage.GROWING,
        trigger="efficiency_restored",
        reason="Contribution ratio recovered above warn threshold",
    ),
    LifecycleTransition(
        from_stage=LifecycleStage.CONTRACTING,
        to_stage=LifecycleStage.CLOSING,
        trigger="contraction_insufficient",
        reason="Contracting did not restore contribution ratio above prune threshold",
    ),
]
