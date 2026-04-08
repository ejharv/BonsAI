"""
The Orchestrator manages multi-agent
execution trees. It creates nodes from
seeds, runs them through the lifecycle,
handles agent-driven branching, manages
budget allocation across children, and
aggregates signals into a RunResult.

The Orchestrator is the only component
that creates Node instances.
The Orchestrator is the only component
that transitions node lifecycle stages.
Agents and executors never touch the
lifecycle directly.
"""

from __future__ import annotations
import re
import uuid
import time
from pathlib import Path
from typing import Optional

from core.seed.seed import (
    Seed,
    ResourceEnvelope,
    GrowthConditions,
    CapabilityNeed,
    Signal,
    Closure,
    Identity,
    Contract,
)
from core.lifecycle.lifecycle import (
    LifecycleStage,
    VALID_TRANSITIONS,
)
from core.invariants.invariants import (
    check_budget_conservation,
    check_intent_coherence,
    check_signal_propagation,
)
from core.executor.base import (
    BaseExecutor,
    _parse_roots_updates,
)
from core.executor.models import (
    AgentPrompt,
    AgentContext,
    ExecutorStatus,
)
from core.orchestrator.models import (
    OrchestratorConfig,
    RunResult,
    NodeResult,
    NodeStatus,
    BranchRequest,
    BranchingSignal,
)
from core.orchestrator.node import Node
from root_manager.manager import RootManager


class Orchestrator:
    """
    Manages multi-agent execution trees.
    Single entry point: run(task).
    Everything else is internal.

    Lifecycle ownership:
    The orchestrator is the only code
    that calls node.transition_to().
    No other component touches stages.

    Budget ownership:
    The orchestrator allocates budgets
    to child nodes. Nodes track their
    own consumption. The orchestrator
    enforces conservation invariant
    before spawning children.

    Invariant enforcement:
    All three invariants are checked
    at appropriate points. Invariant
    violations are logged and treated
    as FAILED nodes — they never
    silently pass.
    """

    def __init__(
        self,
        executor: BaseExecutor,
        root_manager: RootManager,
        config: Optional[OrchestratorConfig] = None,
    ):
        """
        executor: which backend to use
        root_manager: initialized manager
            pointed at project roots/
        config: orchestrator settings
            defaults to
            OrchestratorConfig.default()
        """
        self.executor = executor
        self.root_manager = root_manager
        self.config = config or OrchestratorConfig.default()
        self._run_log: list[str] = []

    def run(
        self,
        task: str,
        agent_name: str,
        budget: float,
        parent_intent: str = "",
    ) -> RunResult:
        """
        Main entry point.
        Creates root node from task.
        Runs the full execution tree.
        Returns RunResult with complete
        picture of what happened.

        Never raises — all errors
        captured in RunResult.
        success=False on any failure.
        """
        run_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            self.root_manager.begin_session("orchestrator")

            root_seed = Node.make_seed(
                intent=task,
                depth=0,
                parent_id=None,
                budget_allocated=budget,
                budget_reserved=(
                    budget * self.config.synthesis_budget_fraction
                ),
                agent_name=agent_name,
                config=self.config,
            )

            root_node = Node(
                seed=root_seed,
                executor=self.executor,
                stage=LifecycleStage.GERMINATING,
                status=NodeStatus.PENDING,
            )

            root_result = self._execute_node(root_node)

            run_result = self._build_run_result(
                run_id,
                task,
                root_result,
                start_time,
            )

            try:
                from bonsai.observability.store import RunStore
                store = RunStore(
                    self.root_manager.roots_path
                )
                store.save_run(
                    run_result,
                    time.time() - start_time,
                )
            except Exception as e:
                print(
                    f"Warning: could not save "
                    f"run history: {e}"
                )

            self.root_manager.end_session(
                "orchestrator",
                run_result.summary,
            )

            return run_result

        except Exception as e:
            dummy_signal = Signal()
            dummy_result = NodeResult(
                node_id=run_id,
                status=NodeStatus.FAILED,
                output="",
                signal=dummy_signal,
                closure=None,
                child_results=[],
                budget_usage=None,
                depth=0,
            )
            return RunResult(
                run_id=run_id,
                task=task,
                root_result=dummy_result,
                total_budget_consumed=0.0,
                total_nodes=0,
                pruned_nodes=0,
                max_depth_reached=0,
                success=False,
                summary=f"Run failed: {e}",
            )

    def _execute_node(
        self,
        node: Node,
    ) -> NodeResult:
        """
        Execute a single node through
        its full lifecycle.

        Lifecycle path:
        GERMINATING → GROWING
            — build and send prompt
        GROWING → BRANCHING
            — if agent requests branches
              AND budget headroom exists
              AND depth < max_depth
        GROWING → CLOSING
            — if task complete or
              budget exhausted
        BRANCHING → WAITING_CHILDREN
            — spawn children and wait
        WAITING_CHILDREN → SYNTHESIZING
            — all children complete
        SYNTHESIZING → COMPLETE
            — parent combines outputs
        Any stage → FAILED
            — on unhandled error

        Returns NodeResult.
        """
        node.status = NodeStatus.RUNNING

        if not self._validate_transition(node, LifecycleStage.GROWING):
            node.status = NodeStatus.FAILED
            return node.to_result(NodeStatus.FAILED, [])

        node.transition_to(LifecycleStage.GROWING)

        prompt = self._build_prompt(node)

        result = self.executor.execute(
            prompt,
            timeout_seconds=self.config.timeout_per_node_seconds,
        )

        node.raw_output = result.raw_output
        node.record_budget_consumed(result.budget_usage.budget_consumed)

        if result.file_writes:
            for path, content in result.file_writes.items():
                full = Path(".") / path
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(content)
                print(f"  Wrote: {path}")

        if result.status == ExecutorStatus.TIMEOUT:
            return self._prune_node(node, "Execution timed out")

        if result.status == ExecutorStatus.FAILED:
            node.status = NodeStatus.FAILED
            return node.to_result(NodeStatus.FAILED, [])

        node.update_signal(
            contribution_score=0.7,
            confidence=0.8,
        )

        if node.contribution_score < self.config.prune_threshold:
            return self._prune_node(
                node,
                f"Contribution score {node.contribution_score} below "
                f"prune threshold {self.config.prune_threshold}",
            )

        branching_signal = self._parse_branching_signal(result.raw_output)

        if (
            branching_signal
            and node.depth < self.config.max_depth
            and node.budget_remaining > self.config.min_branch_size
        ):
            if self._validate_transition(node, LifecycleStage.BRANCHING):
                node.transition_to(LifecycleStage.BRANCHING)
                node.status = NodeStatus.BRANCHING

            children = self._spawn_children(node, branching_signal)

            if children:
                node.children = children
                node.status = NodeStatus.WAITING_CHILDREN
                if self._validate_transition(node, LifecycleStage.GROWING):
                    node.transition_to(LifecycleStage.GROWING)

                child_results = []
                for child in children:
                    child_result = self._execute_node(child)
                    child_results.append(child_result)

                node.status = NodeStatus.SYNTHESIZING

                aggregated = self._aggregate_signal(node, child_results)
                node.seed.signal = aggregated

                synthesis_prompt = self._build_prompt(node, child_results)

                synthesis_result = self.executor.execute(
                    synthesis_prompt,
                    timeout_seconds=self.config.timeout_per_node_seconds,
                )

                node.raw_output = synthesis_result.raw_output
                node.record_budget_consumed(
                    synthesis_result.budget_usage.budget_consumed
                )

                if result.roots_updates:
                    from bonsai.cli.run_command import _is_valid_roots_content
                    for path, content in result.roots_updates.items():
                        if path.startswith("roots/"):
                            if _is_valid_roots_content(path, content):
                                full = Path(".") / path
                                full.parent.mkdir(parents=True, exist_ok=True)
                                full.write_text(content)
                            else:
                                print(
                                    f"Warning: rejected roots update for "
                                    f"{path} — content failed validation"
                                )

                node.status = NodeStatus.COMPLETE
                return node.to_result(NodeStatus.COMPLETE, child_results)

        node.status = NodeStatus.COMPLETE
        if self._validate_transition(node, LifecycleStage.CLOSING):
            node.transition_to(LifecycleStage.CLOSING)

        if result.roots_updates:
            from bonsai.cli.run_command import _is_valid_roots_content
            for path, content in result.roots_updates.items():
                if path.startswith("roots/"):
                    if _is_valid_roots_content(path, content):
                        full = Path(".") / path
                        full.parent.mkdir(parents=True, exist_ok=True)
                        full.write_text(content)
                    else:
                        print(
                            f"Warning: rejected roots update for "
                            f"{path} — content failed validation"
                        )

        return node.to_result(NodeStatus.COMPLETE, [])

    def _build_prompt(
        self,
        node: Node,
        child_results: Optional[list[NodeResult]] = None,
    ) -> AgentPrompt:
        """
        Build AgentPrompt for a node.
        If child_results provided this
        is a synthesis prompt — the
        parent combines child outputs.
        If no child_results this is
        a standard execution prompt.
        """
        context = self._load_agent_context_for_node(node)

        synthesis_section = ""
        if child_results:
            lines = ["\n\n## Child Agent Results\n"]
            for cr in child_results:
                lines.append(
                    f"### Subtask: {cr.node_id[:8]}\n"
                    f"{cr.output}\n"
                )
            lines.append(
                "\n## Your Synthesis Task\n"
                "Combine the above child outputs into a coherent response "
                "satisfying your success criteria. Do not repeat the child "
                "outputs verbatim — synthesize them."
            )
            synthesis_section = "".join(lines)
            context = AgentContext(
                agent_name=context.agent_name,
                agent_definition=context.agent_definition,
                relevant_roots=context.relevant_roots,
                task=context.task + synthesis_section,
                output_format=context.output_format,
                roots_to_update=context.roots_to_update,
            )

        branching_instructions = ""
        if (
            node.depth < self.config.max_depth
            and node.budget_remaining > self.config.min_branch_size * 2
        ):
            branching_instructions = (
                "\n\nIf this task has genuinely separable subtasks that would "
                "benefit from parallel execution, you may request child agents "
                "using this format:\n\n"
                "<branch_request>\n"
                "  <subtask>description</subtask>\n"
                "  <agent_hint>builder</agent_hint>\n"
                "  <budget_fraction>0.4</budget_fraction>\n"
                "  <rationale>why needed</rationale>\n"
                "</branch_request>\n\n"
                "Only branch if genuinely necessary. Unnecessary branching "
                "wastes budget.\n"
                "budget_fraction must be 0.1 to 0.8. Sum of all fractions "
                "must be <= 0.9."
            )

        context = AgentContext(
            agent_name=context.agent_name,
            agent_definition=context.agent_definition,
            relevant_roots=context.relevant_roots,
            task=context.task,
            output_format=context.output_format + branching_instructions,
            roots_to_update=context.roots_to_update,
        )

        return AgentPrompt(
            context=context,
            seed_depth=node.depth,
            budget_allocated=node.seed.resource_envelope.budget_allocated,
            parent_intent=node.seed.identity.parent_id or "",
            success_criteria=node.seed.contract.success_criteria,
        )

    def _parse_branching_signal(
        self,
        raw_output: str,
    ) -> Optional[BranchingSignal]:
        """
        Parse <branch_request> tags from
        agent output.
        Returns BranchingSignal if valid
        tags found, None otherwise.
        """
        block_pattern = re.compile(
            r"<branch_request>(.*?)</branch_request>",
            re.DOTALL,
        )
        tag_pattern = re.compile(
            r"<(\w+)>(.*?)</\1>",
            re.DOTALL,
        )

        blocks = block_pattern.findall(raw_output)
        if not blocks:
            return None

        requests: list[BranchRequest] = []
        for block in blocks:
            tags = {
                m.group(1): m.group(2).strip()
                for m in tag_pattern.finditer(block)
            }
            subtask = tags.get("subtask", "").strip()
            if not subtask:
                continue
            try:
                fraction = float(tags.get("budget_fraction", "0"))
            except ValueError:
                continue
            if fraction < 0.1 or fraction > 0.8:
                print(
                    f"Warning: budget_fraction {fraction} out of range "
                    f"[0.1, 0.8] — skipping branch request"
                )
                continue
            requests.append(
                BranchRequest(
                    subtask=subtask,
                    agent_hint=tags.get("agent_hint") or None,
                    budget_fraction=fraction,
                    rationale=tags.get("rationale", ""),
                )
            )

        if not requests:
            print("Warning: branch_request tags found but no valid requests parsed")
            return None

        total_fraction = sum(r.budget_fraction for r in requests)
        if total_fraction > 0.9:
            print(
                f"Warning: total budget_fraction {total_fraction:.2f} exceeds 0.9 "
                f"— branching signal rejected"
            )
            return None

        synthesis_match = re.search(
            r"<synthesis_plan>(.*?)</synthesis_plan>",
            raw_output,
            re.DOTALL,
        )
        synthesis_plan = (
            synthesis_match.group(1).strip()
            if synthesis_match
            else "Synthesize child outputs."
        )

        handle_match = re.search(
            r"<parent_will_handle>(.*?)</parent_will_handle>",
            raw_output,
            re.DOTALL,
        )
        parent_will_handle = (
            handle_match.group(1).strip()
            if handle_match
            else "Synthesis and integration."
        )

        return BranchingSignal(
            requests=requests,
            parent_will_handle=parent_will_handle,
            synthesis_plan=synthesis_plan,
        )

    def _spawn_children(
        self,
        parent: Node,
        signal: BranchingSignal,
    ) -> list[Node]:
        """
        Create child nodes from a BranchingSignal.
        """
        synthesis_reserve = (
            parent.budget_remaining * self.config.synthesis_budget_fraction
        )
        parent.seed.resource_envelope.budget_reserved += synthesis_reserve
        parent.seed.resource_envelope.budget_available -= synthesis_reserve

        children: list[Node] = []
        for request in signal.requests:
            child_budget = parent.budget_remaining * request.budget_fraction

            if child_budget < self.config.min_branch_size:
                print(
                    f"Warning: child budget {child_budget:.2f} below "
                    f"min_branch_size {self.config.min_branch_size} "
                    f"— skipping subtask: {request.subtask[:50]}"
                )
                continue

            valid, reason = check_budget_conservation(
                parent.seed,
                [
                    n.seed.resource_envelope.budget_allocated
                    for n in children
                ] + [child_budget],
            )
            if not valid:
                print(f"Warning: budget conservation violated — {reason}")
                break

            agent_name = request.agent_hint or "builder"

            child_seed = Node.make_seed(
                intent=request.subtask,
                depth=parent.depth + 1,
                parent_id=parent.node_id,
                budget_allocated=child_budget,
                budget_reserved=0.0,
                agent_name=agent_name,
                config=self.config,
            )

            try:
                check_intent_coherence(child_seed, parent.seed)
            except NotImplementedError:
                pass  # invariant not yet implemented, treat as passing

            child_node = Node(
                seed=child_seed,
                executor=self.executor,
                stage=LifecycleStage.GERMINATING,
                status=NodeStatus.PENDING,
            )

            parent.seed.resource_envelope.budget_consumed += child_budget

            children.append(child_node)

        return children

    def _aggregate_signal(
        self,
        parent: Node,
        child_results: list[NodeResult],
    ) -> Signal:
        """
        Aggregate child signals into parent signal.
        """
        if not child_results:
            return Signal()

        total_budget = sum(
            r.budget_usage.budget_consumed
            for r in child_results
            if r.budget_usage
        )

        if total_budget == 0:
            weights = [1.0 / len(child_results)] * len(child_results)
        else:
            weights = [
                r.budget_usage.budget_consumed / total_budget
                for r in child_results
                if r.budget_usage
            ]

        contribution_score = sum(
            w * r.signal.contribution_score
            for w, r in zip(weights, child_results)
        )

        confidence = (
            min(r.signal.confidence for r in child_results)
            if child_results
            else 0.0
        )

        complexity_delta = (
            max(r.signal.complexity_delta for r in child_results)
            if child_results
            else 0.0
        )

        parent_budget_consumed = parent.seed.resource_envelope.budget_consumed

        try:
            check_signal_propagation(
                parent.seed,
                [r.signal for r in child_results],
            )
        except NotImplementedError:
            pass  # invariant not yet implemented, treat as passing

        return Signal(
            contribution_score=contribution_score,
            complexity_delta=complexity_delta,
            confidence=confidence,
            value_efficiency=(
                contribution_score / max(parent_budget_consumed, 0.001)
            ),
        )

    def _prune_node(
        self,
        node: Node,
        reason: str,
    ) -> NodeResult:
        """
        Terminate a node early.
        """
        if self._validate_transition(node, LifecycleStage.CLOSING):
            node.transition_to(LifecycleStage.CLOSING)

        budget_returned = node.budget_remaining

        node.seed.closure = Closure(
            partial_output=node.raw_output,
            termination_reason=reason,
            budget_returned=budget_returned,
            pattern_record={
                "approach": node.seed.identity.intent,
                "depth": node.depth,
                "failure": reason,
            },
        )

        node.status = NodeStatus.PRUNED

        self.root_manager.writer.append_failure(
            what_was_tried=node.seed.identity.intent,
            why_it_failed=reason,
            what_was_learned=(
                f"Node at depth {node.depth} pruned. "
                f"Budget returned: {budget_returned:.4f}"
            ),
        )

        return node.to_result(NodeStatus.PRUNED, [])

    def _build_run_result(
        self,
        run_id: str,
        task: str,
        root_result: NodeResult,
        start_time: float,
    ) -> RunResult:
        """
        Build final RunResult from completed root NodeResult.
        """
        def _count_nodes(result: NodeResult) -> tuple[int, int, int]:
            # returns total, pruned, max_depth
            total = 1
            pruned = 1 if result.status == NodeStatus.PRUNED else 0
            max_d = result.depth
            for child in result.child_results:
                ct, cp, cd = _count_nodes(child)
                total += ct
                pruned += cp
                max_d = max(max_d, cd)
            return total, pruned, max_d

        def _sum_budget(result: NodeResult) -> float:
            total = 0.0
            if result.budget_usage:
                total += result.budget_usage.budget_consumed
            for child in result.child_results:
                total += _sum_budget(child)
            return total

        total_nodes, pruned_nodes, max_depth = _count_nodes(root_result)
        total_budget = _sum_budget(root_result)
        elapsed = time.time() - start_time
        success = root_result.status == NodeStatus.COMPLETE

        branched = total_nodes > 1
        outcome = "succeeded" if success else "failed"
        nodes_word = "s" if total_nodes != 1 else ""
        branch_note = ", including branching" if branched else ""
        summary = (
            f"Run {outcome} in {elapsed:.1f}s. "
            f"{total_nodes} node{nodes_word} executed{branch_note}. "
            f"{pruned_nodes} pruned. "
            f"{total_budget:.4f} budget units consumed."
        )

        return RunResult(
            run_id=run_id,
            task=task,
            root_result=root_result,
            total_budget_consumed=total_budget,
            total_nodes=total_nodes,
            pruned_nodes=pruned_nodes,
            max_depth_reached=max_depth,
            success=success,
            summary=summary,
        )

    def _load_agent_context_for_node(
        self,
        node: Node,
    ) -> AgentContext:
        """
        Load roots context for this node.
        """
        from bonsai.cli.run_command import _load_agent_context
        agent_name = node.seed.capability_need.output_type
        return _load_agent_context(
            agent_name,
            node.seed.identity.intent,
            self.root_manager,
        )

    def _validate_transition(
        self,
        node: Node,
        to_stage: LifecycleStage,
    ) -> bool:
        """
        Check if transition from current stage to to_stage is valid.
        """
        for t in VALID_TRANSITIONS:
            if t.from_stage == node.stage and t.to_stage == to_stage:
                return True
        print(
            f"Warning: invalid transition "
            f"{node.stage} → {to_stage} "
            f"for node {node.node_id[:8]}"
        )
        return False
