"""
Typed inputs and outputs for all
executor backends. An executor
receives an AgentPrompt and returns
an ExecutorResult. The calling code
never knows which backend ran.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto


class ExecutorBackend(Enum):
    """
    CLAUDE_CODE: uses claude --print
        subprocess. Requires Claude Code
        CLI installed and authenticated.
        Works with Max plan.
    API: uses Anthropic Python SDK.
        Requires ANTHROPIC_API_KEY
        environment variable.
        Precise token tracking.
    """
    CLAUDE_CODE = auto()
    API = auto()


class ExecutorStatus(Enum):
    """
    SUCCESS: agent completed task
        and returned structured output
    PARTIAL: agent produced some output
        but did not fully complete task
    FAILED: agent failed to produce
        useful output
    TIMEOUT: execution exceeded
        time limit
    """
    SUCCESS = auto()
    PARTIAL = auto()
    FAILED = auto()
    TIMEOUT = auto()


@dataclass
class AgentContext:
    """
    agent_name: which agent is running
        e.g. "builder", "quality"
    agent_definition: full contents
        of roots/agents/{agent}.md
        as string
    relevant_roots: dict mapping
        root file path to contents
        only files this agent reads
    task: the specific task in plain
        english the agent must complete
    output_format: instructions for
        how agent should structure
        its response so Bonsai can
        parse it reliably
    roots_to_update: list of root
        file paths this agent should
        update as part of its response
    """
    agent_name: str
    agent_definition: str
    relevant_roots: dict[str, str]
    task: str
    output_format: str
    roots_to_update: list[str]


@dataclass
class AgentPrompt:
    """
    context: full agent context
    seed_depth: depth of this node
        in the agent tree
        0 = root, increments per branch
    budget_allocated: abstract budget
        units allocated to this execution
    parent_intent: intent of the
        parent node if depth > 0
        empty string at root
    success_criteria: what good output
        looks like for this specific task
    """
    context: AgentContext
    seed_depth: int
    budget_allocated: float
    parent_intent: str
    success_criteria: str


@dataclass
class BudgetUsage:
    """
    backend: which executor ran
    wall_time_seconds: elapsed time
    output_length_chars: length of
        raw output string
    tokens_used: exact count if
        api backend, None if
        claude_code backend
    budget_consumed: normalized budget
        units consumed this execution
        api: derived from token count
        claude_code: derived from
        wall_time and output_length
    """
    backend: ExecutorBackend
    wall_time_seconds: float
    output_length_chars: int
    tokens_used: Optional[int]
    budget_consumed: float


@dataclass
class ExecutorResult:
    """
    status: how execution went
    raw_output: full text returned
        by the agent
    budget_usage: what this cost
    roots_updates: dict mapping
        root file path to new content
        the agent wants to write
        Bonsai applies these after
        verifying they are safe
    error: error message if status
        is FAILED or TIMEOUT
    """
    status: ExecutorStatus
    raw_output: str
    budget_usage: BudgetUsage
    roots_updates: dict[str, str]
    error: Optional[str] = None
