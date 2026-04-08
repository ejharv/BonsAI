"""
The three invariants that every Seed must satisfy at all times. These are the
laws of the system. They cannot be overridden by any agent, any flow,
or any configuration.
"""

from core.seed.seed import Seed, Signal
from typing import Optional


def check_intent_coherence(
    seed: Seed,
    parent_seed: Optional[Seed] = None
) -> tuple[bool, str]:
    """
    Invariant 1 — Intent Coherence.

    A child seed's intent must be a decomposition of its parent's intent.
    It cannot introduce goals orthogonal to the parent. If it does, the
    branching decision that created it was wrong.

    At root level (parent_seed is None) this check always passes — the root
    defines its own intent from the project specification.

    Prevents: agents pursuing goals that don't serve the parent node, silent
    scope creep, structural incoherence.
    """
    raise NotImplementedError(
        "Intent coherence check requires semantic comparison of intent "
        "strings. Implementation will use embedding similarity against a "
        "threshold. Defined in Phase 2."
    )


def check_budget_conservation(
    seed: Seed,
    child_allocations: list[float]
) -> tuple[bool, str]:
    """
    Invariant 2 — Budget Conservation.

    The sum of all credits allocated to children plus the node's own reserved
    credits must never exceed the total credits this node received.

    A node cannot spend what it does not have. A node cannot allocate 100% to
    children — it must always reserve enough for synthesis and closure.

    Prevents: credit overrun, nodes that cannot afford to synthesize their
    children's outputs, cascade budget failures.
    """
    raise NotImplementedError(
        "Budget conservation is arithmetically checkable. "
        "Implementation in Phase 2."
    )


def check_signal_propagation(
    seed: Seed,
    child_signals: list[Signal]
) -> tuple[bool, str]:
    """
    Invariant 3 — Signal Propagation.

    A node's contribution score must reflect the weighted performance of all
    its children. A node cannot claim success if its children failed. A node
    with no children scores itself directly against its contract.

    Prevents: parent nodes masking child failures, false positive contribution
    scores, misallocation of credits based on inflated performance signals.
    """
    raise NotImplementedError(
        "Signal propagation requires weighted aggregation strategy. "
        "Weighting policy defined in Phase 2."
    )
