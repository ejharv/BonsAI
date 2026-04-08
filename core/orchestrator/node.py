"""
A Node is a live Seed in execution.
It wraps a Seed with runtime state —
its current lifecycle stage, its
executor, its children, and its result.
The orchestrator creates and manages
nodes. Nodes do not manage themselves.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from core.seed.seed import Seed, Signal
from core.lifecycle.lifecycle import (
    LifecycleStage,
)
from core.executor.base import BaseExecutor
from core.orchestrator.models import (
    NodeStatus,
    NodeResult,
    BranchingSignal,
)

if TYPE_CHECKING:
    from core.orchestrator.orchestrator import Orchestrator


@dataclass
class Node:
    """
    A live Seed in execution.
    Created by the Orchestrator.
    Never creates itself or its children.

    The relationship between Node and Seed:
    Seed defines what a node must know.
    Node is what a seed becomes at runtime.
    Every Node has exactly one Seed.
    """

    seed: Seed
    executor: BaseExecutor
    stage: LifecycleStage = field(
        default=LifecycleStage.GERMINATING
    )
    status: NodeStatus = field(
        default=NodeStatus.PENDING
    )
    children: list[Node] = field(
        default_factory=list
    )
    result: Optional[NodeResult] = None
    branching_signal: Optional[BranchingSignal] = None
    raw_output: str = ""

    @property
    def node_id(self) -> str:
        """
        The node's identity comes from
        its seed. They share the same id.
        """
        return self.seed.identity.id

    @property
    def depth(self) -> int:
        """
        Depth from the seed identity.
        """
        return self.seed.identity.depth

    @property
    def budget_remaining(self) -> float:
        """
        Credits available in envelope.
        """
        env = self.seed.resource_envelope
        return (
            env.budget_allocated
            - env.budget_consumed
            - env.budget_reserved
        )

    @property
    def contribution_score(self) -> float:
        """
        Current contribution score
        from signal.
        """
        return self.seed.signal.contribution_score

    def transition_to(
        self,
        stage: LifecycleStage,
    ) -> None:
        """
        Transition this node to a new
        lifecycle stage.
        Does not validate the transition
        — the orchestrator is responsible
        for ensuring transitions are valid
        per VALID_TRANSITIONS.
        Updates self.stage.
        """
        self.stage = stage

    def record_budget_consumed(
        self,
        amount: float,
    ) -> None:
        """
        Update budget_consumed in the
        seed's resource envelope.
        Recalculate budget_available.
        """
        env = self.seed.resource_envelope
        env.budget_consumed += amount
        env.budget_available = (
            env.budget_allocated
            - env.budget_consumed
            - env.budget_reserved
        )

    def update_signal(
        self,
        contribution_score: float,
        confidence: float,
        complexity_delta: float = 0.0,
    ) -> None:
        """
        Update this node's signal fields.
        Recalculate value_efficiency:
            contribution_score /
            max(budget_consumed, 0.001)
        """
        sig = self.seed.signal
        sig.contribution_score = contribution_score
        sig.confidence = confidence
        sig.complexity_delta = complexity_delta
        budget_consumed = self.seed.resource_envelope.budget_consumed
        sig.value_efficiency = (
            contribution_score / max(budget_consumed, 0.001)
        )

    def to_result(
        self,
        status: NodeStatus,
        child_results: list[NodeResult],
    ) -> NodeResult:
        """
        Convert this node to a NodeResult
        for reporting.
        Populates all NodeResult fields
        from current node state.
        """
        from core.executor.models import BudgetUsage, ExecutorBackend
        return NodeResult(
            node_id=self.node_id,
            status=status,
            output=self.raw_output,
            signal=self.seed.signal,
            closure=self.seed.closure,
            child_results=child_results,
            budget_usage=BudgetUsage(
                backend=self.executor.backend,
                wall_time_seconds=0.0,
                output_length_chars=len(self.raw_output),
                tokens_used=None,
                budget_consumed=self.seed.resource_envelope.budget_consumed,
            ),
            depth=self.depth,
        )

    @staticmethod
    def make_seed(
        intent: str,
        depth: int,
        parent_id: Optional[str],
        budget_allocated: float,
        budget_reserved: float,
        agent_name: str,
        config: object,
    ) -> Seed:
        """
        Factory method — creates a Seed
        for a new node.
        Generates a new UUID for identity.
        Sets sensible defaults for
        GrowthConditions from config.
        agent_name goes into
        CapabilityNeed.output_type
        as a routing hint.
        """
        from core.seed.seed import (
            Identity,
            Contract,
            ResourceEnvelope,
            CapabilityNeed,
            GrowthConditions,
            Signal,
            Seed,
        )
        import uuid

        node_id = str(uuid.uuid4())

        return Seed(
            identity=Identity(
                id=node_id,
                intent=intent,
                depth=depth,
                parent_id=parent_id,
            ),
            contract=Contract(
                success_criteria=f"Complete: {intent}",
                partial_success="Partial progress made",
                failure_definition="No useful output produced",
                input_schema={},
                output_schema={},
            ),
            resource_envelope=ResourceEnvelope(
                budget_allocated=budget_allocated,
                budget_consumed=0.0,
                budget_reserved=budget_reserved,
                budget_available=(
                    budget_allocated - budget_reserved
                ),
                allocation_policy="fraction_based",
            ),
            capability_need=CapabilityNeed(
                reasoning_depth="moderate",
                output_type=agent_name,
                latency_sensitivity="batch",
                accuracy_requirement="precise",
            ),
            growth_conditions=GrowthConditions(
                branch_threshold=0.7,
                warn_threshold=getattr(config, "warn_threshold", 0.4),
                prune_threshold=getattr(config, "prune_threshold", 0.2),
                min_budget_to_branch=getattr(config, "min_branch_size", 1.0),
            ),
            signal=Signal(),
        )
