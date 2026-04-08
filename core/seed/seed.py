"""
The Seed is the fundamental recursive unit of Bonsai. Every node in the agent
tree — root, branch, or leaf — is an instantiation of this structure with
different context. The seed does not contain implementation logic. It defines
what every node must know about itself to participate in the system.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Identity:
    # id: stable unique identifier, never changes even as system adapts
    id: str
    # intent: outcome this node exists to produce, expressed in outcome language not process language
    intent: str
    # depth: distance from root, root is 0, increments each branch
    depth: int
    # parent_id: none at root, reference to parent otherwise
    parent_id: Optional[str]


@dataclass
class Contract:
    # success_criteria: what good output looks like, must be evaluable
    success_criteria: str
    # partial_success: what recoverable incomplete output looks like
    partial_success: str
    # failure_definition: what terminates this node without recovery
    failure_definition: str
    # input_schema: shape of what this node receives
    input_schema: dict
    # output_schema: shape of what this node must produce
    output_schema: dict


@dataclass
class ResourceEnvelope:
    # credits_allocated: total credits received from parent
    credits_allocated: float
    # credits_consumed: running counter of credits used during execution
    credits_consumed: float = 0.0
    # credits_reserved: minimum kept for synthesis and closure operations
    credits_reserved: float = 0.0
    # credits_available: allocated minus consumed minus reserved
    credits_available: float = 0.0
    # allocation_policy: rule for subdividing credits to children, stores the policy name not amounts
    allocation_policy: str = ""


@dataclass
class CapabilityNeed:
    # reasoning_depth: shallow, moderate, or deep
    reasoning_depth: str
    # output_type: structured, unstructured, code, or analysis
    output_type: str
    # latency_sensitivity: realtime or batch acceptable
    latency_sensitivity: str
    # accuracy_requirement: approximate, precise, or verified
    accuracy_requirement: str


@dataclass
class GrowthConditions:
    # branch_threshold: complexity signal score that triggers child spawning
    branch_threshold: float
    # warn_threshold: contribution ratio that triggers resource pressure
    warn_threshold: float
    # prune_threshold: contribution ratio that triggers node closure
    prune_threshold: float
    # min_budget_to_branch: credits available floor below which branching never occurs regardless of complexity signal
    min_budget_to_branch: float


@dataclass
class Signal:
    # contribution_score: how well this node is satisfying its contract
    contribution_score: float = 0.0
    # complexity_delta: positive means harder than expected, negative means easier
    complexity_delta: float = 0.0
    # confidence: how certain the node is about its output quality
    confidence: float = 0.0
    # credits_efficiency: contribution score divided by credits consumed
    credits_efficiency: float = 0.0


@dataclass
class Closure:
    # partial_output: what was produced before termination, may be empty
    partial_output: Any
    # termination_reason: why this node stopped, one of: completed, pruned, budget_exhausted, invariant_violated, parent_closed
    termination_reason: str
    # credits_returned: unused credits released back to parent
    credits_returned: float
    # pattern_record: what approach was tried, how far it got, what the failure mode was
    pattern_record: dict


@dataclass
class Seed:
    identity: Identity
    contract: Contract
    resource_envelope: ResourceEnvelope
    capability_need: CapabilityNeed
    growth_conditions: GrowthConditions
    signal: Signal = field(default_factory=Signal)
    closure: Optional[Closure] = None
    children: list[str] = field(default_factory=list)
