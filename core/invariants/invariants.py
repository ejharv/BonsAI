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

    The sum of all budget allocated to children plus the node's own reserved
    budget must never exceed the total budget this node received.

    A node cannot spend what it does not have. A node cannot allocate 100% to
    children — it must always reserve enough for synthesis and closure.

    Prevents: budget overrun, nodes that cannot afford to synthesize their
    children's outputs, cascade budget failures.
    """
    allocated = seed.resource_envelope.budget_allocated
    reserved = seed.resource_envelope.budget_reserved
    total_child = sum(child_allocations)
    total = total_child + reserved
    if total > allocated:
        return (
            False,
            f"Budget overrun: child allocations ({total_child:.4f}) + reserved "
            f"({reserved:.4f}) = {total:.4f} exceeds allocated ({allocated:.4f})"
        )
    return (True, f"Budget conserved: {total:.4f} of {allocated:.4f} allocated")


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
    scores, misallocation of budget based on inflated performance signals.
    """
    if not child_signals:
        return (
            True,
            "No children: seed scores directly against its own contract.",
        )

    avg_score = sum(s.contribution_score for s in child_signals) / len(child_signals)
    seed_score = seed.signal.contribution_score
    delta = abs(seed_score - avg_score)

    if delta <= 0.2:
        return (
            True,
            f"Signal propagates: seed score {seed_score:.4f} within 0.2 of "
            f"child average {avg_score:.4f} (delta={delta:.4f})",
        )
    return (
        False,
        f"Signal violation: seed score {seed_score:.4f} differs from child "
        f"average {avg_score:.4f} by {delta:.4f} (threshold 0.2)",
    )
