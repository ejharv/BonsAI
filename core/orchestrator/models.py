"""
Typed structures for the orchestrator.
These represent the runtime state of
a multi-agent execution tree — nodes,
signals, branching requests, and
run results.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum, auto

from core.seed.seed import (
    Seed,
    Signal,
    Closure,
    Identity,
    Contract,
    ResourceEnvelope,
    CapabilityNeed,
    GrowthConditions,
)
from core.lifecycle.lifecycle import (
    LifecycleStage,
)
from core.executor.models import (
    ExecutorResult,
    AgentPrompt,
)


class NodeStatus(Enum):
    # PENDING: created but not yet started
    PENDING = auto()
    # RUNNING: executing via executor
    RUNNING = auto()
    # BRANCHING: spawning child nodes
    BRANCHING = auto()
    # WAITING_CHILDREN: parent waiting for all children to complete
    WAITING_CHILDREN = auto()
    # SYNTHESIZING: children done, parent combining their outputs
    SYNTHESIZING = auto()
    # COMPLETE: successfully finished
    COMPLETE = auto()
    # PRUNED: terminated early by orchestrator due to poor signal
    PRUNED = auto()
    # FAILED: error prevented completion
    FAILED = auto()


@dataclass
class BranchRequest:
    # subtask: plain english description of the subtask this child should handle
    subtask: str
    # agent_hint: suggested agent type e.g. "tester" or "builder", None means orchestrator decides
    agent_hint: Optional[str]
    # budget_fraction: fraction of parent remaining budget to allocate to this child
    # must be between 0.1 and 0.8; sum of all fractions in one request must not exceed 0.9
    budget_fraction: float
    # rationale: why this subtask needs its own agent rather than being handled by the parent
    rationale: str


@dataclass
class BranchingSignal:
    # requests: list of child spawn requests from the agent
    requests: list[BranchRequest]
    # parent_will_handle: what the parent agent will do after children complete
    parent_will_handle: str
    # synthesis_plan: how the parent plans to combine child outputs into a coherent whole
    synthesis_plan: str


@dataclass
class NodeResult:
    # node_id: matches Seed.identity.id
    node_id: str
    # status: final status of this node
    status: NodeStatus
    # output: raw output from executor or synthesized output for parent nodes
    output: str
    # signal: final signal emitted by this node
    signal: Signal
    # closure: populated if node was pruned or failed
    closure: Optional[Closure]
    # child_results: results from all child nodes, empty if leaf
    child_results: list[NodeResult]
    # budget_usage: BudgetUsage from executor result
    budget_usage: Any
    # depth: depth in the tree, 0 = root
    depth: int


@dataclass
class OrchestratorConfig:
    # min_branch_size: minimum budget units a subtask must warrant to be spawned as child
    min_branch_size: float
    # max_depth: maximum tree depth, prevents runaway branching
    max_depth: int
    # prune_threshold: contribution score below which a node is pruned mid-execution
    prune_threshold: float
    # warn_threshold: contribution score that triggers budget pressure signal to node
    warn_threshold: float
    # synthesis_budget_fraction: fraction of envelope reserved for parent synthesis after children
    synthesis_budget_fraction: float
    # timeout_per_node_seconds: hard timeout per node execution
    timeout_per_node_seconds: int

    @classmethod
    def default(cls) -> OrchestratorConfig:
        return cls(
            min_branch_size=1.0,
            max_depth=3,
            prune_threshold=0.2,
            warn_threshold=0.4,
            synthesis_budget_fraction=0.15,
            timeout_per_node_seconds=180,
        )


@dataclass
class RunResult:
    # run_id: unique identifier for run
    run_id: str
    # task: original task description
    task: str
    # root_result: full result tree from root node down
    root_result: NodeResult
    # total_budget_consumed: sum across all nodes in the tree
    total_budget_consumed: float
    # total_nodes: how many nodes ran
    total_nodes: int
    # pruned_nodes: how many were pruned
    pruned_nodes: int
    # max_depth_reached: deepest node that executed
    max_depth_reached: int
    # success: True if root node completed successfully
    success: bool
    # summary: plain english summary of what happened
    summary: str
