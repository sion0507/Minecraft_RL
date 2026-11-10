"""Shared smoke execution flow. Research rewards and actors are subsequent work."""

import json
import time
from collections import deque
from collections.abc import Callable
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ValidationError

from .rpc import EpisodeError, PolicyEnvironment
from .goals import COMPLETION_EVENT, ESCAPE_DISTANCE, ActiveGoal, Ask, Planning, completed, failed, tally
from .navigation import (
    ORE_TOP, PICKS, escape_candidates, fresh_movement_candidates, generate_descent_candidates, generate_movement_candidates,
    hazard_distance, hold_candidate, ore_search_choices, safe_ground,
)
from .macros import generate_wood_candidates
from .production import generate_production_candidates
from .selectors import Selector, first_candidate, signature
from .schema import (
    Candidate, CandidateSet, EpisodeConfig, EpisodeSummary, ErrorInfo, Event, Goal, GoalOutcome, MacroEvidence, Observation,
    SelectionResult, StepResult, allocate,
)


def emit(kind: str, data: BaseModel | dict[str, object]) -> None:
    value = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    print(json.dumps({"type": kind, "data": value}, allow_nan=False), flush=True)


def error_summary(config: EpisodeConfig, episode_id: str, attempt_id: str, error: ErrorInfo, wall_seconds: float) -> EpisodeSummary:
    """Summary of an episode whose backend failed before `run_episode` could produce one."""
    return EpisodeSummary(episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
                          clock_mode="mock" if config.backend == "mock" else "unverified", goal_completed=False,
                          terminated=False, truncated=False, invalid=False, reason=error.code, error=error,
                          active_ticks=0, wall_seconds=wall_seconds, decisions=0, reward_total=0.0)


def generate_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    candidates = [Candidate(
        candidate_id=f"{observation.obs_id}:mine:{index}", action_kind="mine_visible_cluster",
        params=surface.model_dump(mode="json"), max_ticks=min(400, observation.remaining_ticks),
        stop_rule_id="goal_or_hazard", source_obs_id=observation.obs_id,
        description=f"Collect exposed {surface.block}",
    ) for index, surface in enumerate(observation.observed_map) if surface.block == goal.target]
    return allocate(candidates)


def policy_candidates(observation: Observation, goal: Goal, *, movement: bool = False, macros: bool = False) -> CandidateSet:
    """The generator the episode uses for this goal; inside an observed hazard radius only escape walks."""
    escape = escape_candidates(observation) if macros else None
    if escape is not None:
        return escape
    if movement:
        return generate_movement_candidates(observation)
    if not macros:
        return generate_candidates(observation, goal)
    if goal.kind == "descend":
        return generate_descent_candidates(observation)
    if goal.kind == "escape":
        walks = generate_movement_candidates(observation).candidates
        hold = (hazard_distance(observation.observed_map, observation.position) >= ESCAPE_DISTANCE and safe_ground(observation)
                and observation.remaining_ticks)
        return allocate([hold_candidate(observation), *walks] if hold else walks)
    if goal.kind == "explore":
        return allocate(ore_search_choices(observation, goal.target, 0) if goal.target in ORE_TOP
                        else fresh_movement_candidates(observation))
    if goal.target.endswith("_log"):
        return generate_wood_candidates(observation, goal)
    return generate_production_candidates(observation, goal)


VERIFIED_ORES = {"diamond_ore": ("diamond", PICKS[:3]), "iron_ore": ("iron_ore", PICKS[:4])}  # block: (drop, tools)


def admin_verified(log: dict[str, Any], acquired: dict[str, Event]) -> dict[str, int]:
    """Count only acquisitions the administrator log ties to a natural ore broken with an allowed tool.

    Every unit of an acquired event needs its own record: server block before, air after, server-held tool,
    the ore's own drop entity and that same event. Given, chest, traded or foreign items have no such record.
    """
    linked: dict[str, int] = {}
    for record in log.get("records", []) if log.get("natural") is True else []:
        drop, tools = VERIFIED_ORES.get(record.get("block"), (None, ()))
        event = acquired.get(record.get("acquired_event_id"))
        if (drop and event and event.source == "minecraft" and event.item == drop and record.get("drop_item") == drop and record.get("natural") is True
                and record.get("server_block_before") is True and record.get("server_air_after") is True
                and record.get("server_tool") in tools and isinstance(record.get("drop_entity_id"), int)):
            linked[record["acquired_event_id"]] = linked.get(record["acquired_event_id"], 0) + 1
    verified: dict[str, int] = {}
    for event_id, units in linked.items():
        event = acquired[event_id]
        if event.item and units == event.quantity:
            verified[event.item] = verified.get(event.item, 0) + units
    return verified


STALL_LIMIT = 20  # consecutive <=1-tick steps with no position/map/inventory/durability change


class LearningObserver(Protocol):
    actor_transitions: int
    reward_kind: Literal["local", "full"]
    @property
    def needs_bootstrap(self) -> bool: ...

    def reset(self, observation: Observation) -> None: ...
    def begin(self, observation: Observation, goal: Goal, saved: CandidateSet) -> None: ...
    def record(self, selection: SelectionResult, step: StepResult, *, goal_completed: bool) -> dict[str, Any]: ...
    def finish(self) -> None: ...


def forced_wait_candidate(observation: Observation) -> Candidate:
    return Candidate(candidate_id=f"{observation.obs_id}:wait", action_kind="wait", params={},
        max_ticks=min(20, observation.remaining_ticks), stop_rule_id="no_candidates",
        source_obs_id=observation.obs_id, description="Wait when no candidate is available")


def run_episode(config: EpisodeConfig, environment: PolicyEnvironment,
                reset: Callable[[], Observation], episode_id: str, attempt_id: str,
                *, movement: bool = False, macros: bool = False, select: Selector = first_candidate,
                verification: Callable[[], dict[str, Any]] | None = None, planner: Ask | None = None,
                learning: LearningObserver | None = None) -> EpisodeSummary:
    """`verification` reads the administrator log only after the last decision, so no policy input can see it.

    `config.goal` is the task. Without a planner it is also the one fixed goal, re-adopted at every replan trigger.
    """
    started = time.monotonic()
    actor_before = learning.actor_transitions if learning is not None else 0
    active_ticks = decisions = 0
    selection_requests = cancelled_selections = 0
    seen_events: set[str] = set()
    reward_total = 0.0
    distance_moved = 0.0
    movement_completed = False
    movement_steps: list[MacroEvidence] = []
    macro_steps: list[MacroEvidence] = []
    pause_verified = False
    acquired_target = 0
    provided_inventory: dict[str, int] = {}
    direct_crafted: dict[str, int] = {}
    direct_smelted: dict[str, int] = {}
    direct_acquired: dict[str, int] = {}
    acquired_events: dict[str, Event] = {}
    verified: dict[str, int] = {}
    stalled = 0
    terminated = truncated = invalid = done = False
    planning = Planning(config.goal, config.planner, planner)
    active: ActiveGoal | None = None
    trigger = "episode_start"
    outcomes: list[GoalOutcome] = []
    progress_by_source: dict[str, dict[str, int]] = {}
    failures: deque[str] = deque(maxlen=3)  # signatures of the latest failed actions, for selector S
    reason = "decision_limit"
    error: ErrorInfo | None = None
    evaluation_rewards = None
    clock_mode: Literal["mock", "paused", "realtime", "unverified"] = "mock" if config.backend == "mock" else "unverified"
    try:
        initial = reset()
        provided_inventory = dict(initial.inventory)
        if learning is not None:
            learning.reset(initial)
            actor_before = learning.actor_transitions
        elif config.discovery_reward:
            from .rewards import RewardLedger
            evaluation_rewards = RewardLedger(initial, discovery_reward=config.discovery_reward)
        start = initial
        emit("reset", initial)
        observation = environment.observe()
        if observation != initial:
            raise EpisodeError(ErrorInfo(code="protocol_error", message="Reset/observe state mismatch"))
        while selection_requests < config.max_decisions:
            if observation.episode_id != episode_id or observation.attempt_id != attempt_id:
                raise EpisodeError(ErrorInfo(code="protocol_error", message="Episode/attempt ID mismatch"))
            active_ticks = observation.active_ticks
            emit("observation", observation)
            if observation.remaining_ticks == 0:
                truncated, reason = True, "active_tick_limit"
                break
            if config.wall_limit_seconds is not None and time.monotonic() - started >= config.wall_limit_seconds:
                truncated, reason = True, "wall_time_limit"
                break
            if active is None:
                retries = planning.counts["planner_regeneration_requests"]
                adopted, decision = planning.decide(observation, trigger)
                emit("goal_decision", decision)
                active = ActiveGoal(adopted, observation, planner_retries=planning.counts["planner_regeneration_requests"] - retries)
            goal = active.goal
            emit("goal", goal)
            saved = policy_candidates(observation, goal, movement=movement, macros=macros)
            emit("candidates", saved)
            if learning is not None:
                learning.begin(observation, goal, saved)
            if saved.candidates:
                asked = time.monotonic()
                selection = select(observation, goal, saved, tuple(failures))
                offered = {c.candidate_id: c for c, allowed in zip(saved.candidates, saved.mask) if allowed}
                if selection.candidate_id not in offered:
                    raise EpisodeError(ErrorInfo(code="invalid_selection", message="Selector returned no offered candidate"))
                candidate = offered[selection.candidate_id]
                selection = selection.model_copy(update={"latency_seconds": time.monotonic() - asked})
            else:
                candidate = forced_wait_candidate(observation)
                selection = SelectionResult(candidate_id=candidate.candidate_id, selector_mode="forced_wait", probabilities=None,
                                            latency_seconds=0.0, provider=None, model=None, usage=None)
            if macros and len(saved.candidates) <= 1:
                selection = selection.model_copy(update={"probabilities": {candidate.candidate_id: 1.0}})
            emit("selection", selection)
            selection_requests += 1
            step = environment.step(candidate)
            decisions += not step.cancelled
            cancelled_selections += step.cancelled
            if (step.observation.episode_id != episode_id or step.observation.attempt_id != attempt_id
                or step.observation.active_ticks != active_ticks + step.actual_ticks
                or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                or (not step.cancelled and step.actual_ticks > candidate.max_ticks)
                or step.observation.obs_id == observation.obs_id):
                raise EpisodeError(ErrorInfo(code="invalid_step", message="Inconsistent step IDs or tick accounting"))
            active_ticks = step.observation.active_ticks
            if not saved.candidates:
                if not any(event.kind == "wait" for event in step.events):
                    raise EpisodeError(ErrorInfo(code="invalid_step", message="Forced wait needs recorded wait evidence"))
                if not any(event.kind == "failed" for event in step.events):
                    step.events.append(Event(kind="failed", source="mock" if step.clock_mode == "mock" else "minecraft",
                                             event_id=f"{observation.obs_id}:no-candidates"))
            emit("step", step)
            if step.cancelled:
                if step.invalid or not any(event.kind == "wait" for event in step.events):
                    raise EpisodeError(ErrorInfo(code="invalid_step", message="Cancelled selection needs recorded wait"))
                emit("cancellation", {"candidates": saved.model_dump(mode="json"),
                     "selection": selection.model_dump(mode="json"), "reason": step.reason,
                     "actor_valid": False, "trace_mask": 0, "actual_ticks": step.actual_ticks,
                     "wall_seconds": step.wall_seconds})
            moving = candidate.action_kind == "move_observed" and not step.cancelled
            if macros or moving:
                if (step.actual_ticks < 1 or step.source_obs_id != observation.obs_id
                        or step.map_version != step.observation.map_version
                        or step.stop_evidence != [step.observation.obs_id, step.reason]
                        or not step.events
                        or any(event.source != ("mock" if step.clock_mode == "mock" else "minecraft") for event in step.events)):
                    raise EpisodeError(ErrorInfo(code="invalid_step", message="Inconsistent macro evidence"))
            if selection_requests == 1:
                clock_mode, pause_verified = step.clock_mode, step.pause_verified
            elif clock_mode != step.clock_mode:
                clock_mode, pause_verified = "unverified", False
            else:
                pause_verified &= step.pause_verified
            if moving:
                if (step.path != ([] if step.invalid or step.reason == "invalid_path" else candidate.params["path"])
                        or not any(event.kind == ("moved" if step.distance_moved > 0 else "stopped") for event in step.events)):
                    raise EpisodeError(ErrorInfo(code="invalid_step", message="Inconsistent movement evidence"))
            if macros or moving:
                evidence = MacroEvidence(
                    candidate_id=candidate.candidate_id, source_obs_id=observation.obs_id,
                    goal_id=goal.goal_id, goal_source=goal.source,
                    **step.model_dump(include={"map_version", "events", "reason", "actual_ticks", "wall_seconds",
                                               "path", "stop_evidence", "stable_boundary", "distance_moved", "cancelled"}),
                )
                if macros:
                    macro_steps.append(evidence)
                if moving:
                    movement_steps.append(evidence)
            distance_moved += step.distance_moved
            movement_completed |= (candidate.action_kind == "move_observed" and step.reason == "path_completed"
                                   and step.stable_boundary and 0 < step.distance_moved <= 16 and not step.invalid
                                   and step.clock_mode in {"mock", "paused"})
            for event in step.events:
                if event.event_id:
                    if event.event_id in seen_events:
                        raise EpisodeError(ErrorInfo(code="invalid_step", message="Repeated event identity"))
                    seen_events.add(event.event_id)
                    if event.kind == "acquired":
                        acquired_events[event.event_id] = event
                ledger = {"crafted": direct_crafted, "smelted": direct_smelted, "acquired": direct_acquired}.get(event.kind)
                if ledger is not None and event.item:
                    ledger[event.item] = ledger.get(event.item, 0) + event.quantity
            tally(progress_by_source.setdefault(goal.source, {}), step)
            smoke_reward = float(sum(event.quantity for event in step.events if event.kind == "acquired"))
            reward_record: dict[str, Any] = {"value": smoke_reward, "kind": "smoke_acquisition_count", "actor_valid": False,
                            "trace_mask": 0 if step.cancelled else 1, "goal_id": goal.goal_id, "goal_source": goal.source,
                            "actor_exclusion_reason": "cancelled" if step.cancelled else "no_candidates" if not saved.candidates
                            else "single_candidate" if len(saved.candidates) == 1
                            else "rule_selector" if selection.selector_mode == "rule_deterministic" else "smoke_selector"}
            if saved.candidates and not step.cancelled and failed(step):
                failures.append(signature(candidate))
            task_event = COMPLETION_EVENT.get(config.goal.kind)
            acquired_target += sum(event.quantity for event in step.events
                                   if event.kind == task_event and event.item == config.goal.target)
            done = completed(config.goal, start, step, acquired_target)
            trigger = active.record(step) or ""
            if learning is not None:
                reward_record = learning.record(selection, step, goal_completed=active.done)
            elif evaluation_rewards is not None:
                reward = evaluation_rewards.compute(observation, goal, step, goal_completed=active.done)
                reward_record.update(value=reward.total, kind=observation.objective_kind,
                    components=reward.components, discounted=reward.discounted, discount=reward.discount,
                    task_terminal=reward.terminal)
            reward_total += float(reward_record["value"])
            emit("reward", reward_record)
            if trigger:
                outcomes.append(active.outcome(step.observation.active_ticks, trigger))
                active = None
            terminated, truncated, invalid, reason = step.terminated, step.truncated, step.invalid, step.reason
            if learning is not None and reward_record["task_terminal"] and not invalid:
                terminated, truncated = True, False
                reason = ("death" if step.observation.health <= 0 else "active_tick_limit" if step.observation.remaining_ticks == 0
                          else "goal_completed" if observation.objective_kind == "local" else "diamond_success")
            unchanged = [step.observation.position, step.observation.map_version, step.observation.inventory, step.observation.tool_durability]
            stalled = stalled + 1 if step.actual_ticks <= 1 and not step.cancelled and unchanged == [
                observation.position, observation.map_version, observation.inventory, observation.tool_durability] else 0
            observation = step.observation
            if terminated or truncated or invalid:
                break
            if macros and done and learning is None:
                terminated, reason = True, "goal_completed"
                break
            if stalled >= STALL_LIMIT:
                # Nothing moved, cut or changed: the same choice would repeat until a budget ends (T07 G2 attempt 1).
                truncated, reason = True, "repeated_stall"
                break
        else:
            truncated, reason = True, "decision_limit"
        if learning is not None and learning.needs_bootstrap and observation.remaining_ticks > 0 and observation.health > 0:
            if active is None:
                adopted, decision = planning.decide(observation, trigger)
                emit("goal_decision", decision)
                active = ActiveGoal(adopted, observation)
            learning.begin(observation, active.goal, policy_candidates(observation, active.goal, movement=movement, macros=macros))
        if verification is not None:
            log = verification()
            emit("admin_verification", log)
            verified = admin_verified(log, acquired_events)
    except EpisodeError as failure:
        error, reason = failure.error, failure.error.code
        emit("error", error)
    except ValidationError:
        error = ErrorInfo(code="protocol_error", message="Backend result violates contract")
        reason = error.code
        emit("error", error)
    if error and clock_mode != "mock":
        clock_mode, pause_verified = "unverified", False
    if learning is not None:
        learning.finish()
    if active is not None:
        outcomes.append(active.outcome(active_ticks, reason))
    summary = EpisodeSummary(
        episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
        task="movement_smoke" if movement else "macros_smoke" if macros else "smoke",
        clock_mode=clock_mode, pause_verified=pause_verified, movement_steps=movement_steps,
        goal_completed=done, terminated=terminated,
        truncated=truncated, invalid=invalid, reason=reason, error=error,
        active_ticks=active_ticks, wall_seconds=time.monotonic() - started,
        decisions=decisions, reward_total=reward_total,
        reward_kind=learning.reward_kind if learning is not None else (
            initial.objective_kind if evaluation_rewards is not None else "smoke_acquisition_count"),
        actor_transitions=learning.actor_transitions - actor_before if learning is not None else 0,
        movement_completed=movement_completed, distance_moved=distance_moved,
        macro_steps=macro_steps, selection_requests=selection_requests, cancelled_selections=cancelled_selections,
        provided_inventory=provided_inventory, direct_crafted=direct_crafted,
        direct_smelted=direct_smelted, direct_acquired=direct_acquired, admin_verified=verified,
        diamond_success=config.goal.kind == "mine_diamond" and done and verified.get("diamond", 0) >= 1,
        planner_model=planning.model, planner_version=planning.version,
        progress_by_source={source: gained for source, gained in progress_by_source.items() if gained}, goal_outcomes=outcomes,
    )
    summary = EpisodeSummary.model_validate({**summary.model_dump(), **planning.counts})
    emit("summary", summary)
    return summary
