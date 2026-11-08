"""Shared smoke execution flow. Research rewards and actors are subsequent work."""

import json
import math
import time
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from .rpc import EpisodeError, PolicyEnvironment
from .navigation import PICKS, SAFE_BAND, escape_candidates, generate_descent_candidates, generate_movement_candidates
from .macros import generate_wood_candidates
from .production import generate_production_candidates
from .schema import (
    Candidate, CandidateSet, EpisodeConfig, EpisodeSummary, ErrorInfo, Event, Goal, MacroEvidence, Observation, SelectionResult,
    StepResult,
)


def emit(kind: str, data: BaseModel | dict[str, object]) -> None:
    value = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    print(json.dumps({"type": kind, "data": value}, allow_nan=False), flush=True)


def generate_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    candidates = [Candidate(
        candidate_id=f"{observation.obs_id}:mine:{index}", action_kind="mine_visible_cluster",
        params=surface.model_dump(mode="json"), max_ticks=min(400, observation.remaining_ticks),
        stop_rule_id="goal_or_hazard", source_obs_id=observation.obs_id,
        description=f"Collect exposed {surface.block}",
    ) for index, surface in enumerate(observation.observed_map[:8]) if surface.block == goal.target]
    return CandidateSet(candidates=candidates, mask=[True] * len(candidates))


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


def descent_completed(step: StepResult) -> bool:
    """Iron pickaxe carried (inventory, not hand) through one uninterrupted 20-tick hold on observed ground at y=5-12."""
    return (SAFE_BAND[0] <= math.floor(step.observation.position[1]) <= SAFE_BAND[1]
            and step.stable_boundary and not step.invalid and not step.cancelled
            and step.observation.inventory.get("iron_pickaxe", 0) >= 1
            and any(event.kind == "safe_hold" and event.quantity >= 20 for event in step.events))


def first_candidate(saved: CandidateSet, _observation: Observation) -> Candidate:
    return saved.candidates[0]


def run_episode(config: EpisodeConfig, environment: PolicyEnvironment,
                reset: Callable[[], Observation], episode_id: str, attempt_id: str,
                *, movement: bool = False, macros: bool = False,
                select: Callable[[CandidateSet, Observation], Candidate] = first_candidate,
                selector_mode: Literal["mock_fixed", "human"] = "mock_fixed",
                verification: Callable[[], dict[str, Any]] | None = None) -> EpisodeSummary:
    """`verification` reads the administrator log only after the last decision, so no policy input can see it."""
    started = time.monotonic()
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
    terminated = truncated = invalid = completed = False
    reason = "decision_limit"
    error: ErrorInfo | None = None
    clock_mode: Literal["mock", "paused", "realtime", "unverified"] = "mock" if config.backend == "mock" else "unverified"
    try:
        initial = reset()
        provided_inventory = dict(initial.inventory)
        emit("reset", initial)
        observation = environment.observe()
        if observation != initial:
            raise EpisodeError(ErrorInfo(code="protocol_error", message="Reset/observe state mismatch"))
        while selection_requests < config.max_decisions:
            if observation.episode_id != episode_id or observation.attempt_id != attempt_id:
                raise EpisodeError(ErrorInfo(code="protocol_error", message="Episode/attempt ID mismatch"))
            active_ticks = observation.active_ticks
            emit("observation", observation)
            emit("goal", config.goal)
            if observation.remaining_ticks == 0:
                truncated, reason = True, "active_tick_limit"
                break
            if config.wall_limit_seconds is not None and time.monotonic() - started >= config.wall_limit_seconds:
                truncated, reason = True, "wall_time_limit"
                break
            escape = escape_candidates(observation) if macros else None
            saved = escape if escape is not None else (generate_movement_candidates(observation) if movement else
                     (generate_descent_candidates(observation) if config.goal.kind == "descend" else
                      generate_wood_candidates(observation, config.goal) if config.goal.target.endswith("_log") else
                      generate_production_candidates(observation, config.goal)) if macros else generate_candidates(observation, config.goal))
            emit("candidates", saved)
            candidate = select(saved, observation) if saved.candidates else Candidate(
                candidate_id=f"{observation.obs_id}:wait", action_kind="wait", params={},
                max_ticks=min(20, observation.remaining_ticks), stop_rule_id="no_candidates",
                source_obs_id=observation.obs_id, description="Wait when no candidate is available",
            )
            selection = SelectionResult(
                candidate_id=candidate.candidate_id, selector_mode=selector_mode if saved.candidates else "forced_wait",
                probabilities={candidate.candidate_id: 1.0} if macros and len(saved.candidates) <= 1 else None,
                latency_seconds=0.0, provider=None, model=None, usage=None,
            )
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
            reward = float(sum(event.quantity for event in step.events if event.kind == "acquired"))
            reward_total += reward
            emit("reward", {"value": reward, "kind": "smoke_acquisition_count", "actor_valid": False,
                            "trace_mask": 0 if step.cancelled else 1,
                            "actor_exclusion_reason": "cancelled" if step.cancelled else "no_candidates" if not saved.candidates
                            else "single_candidate" if len(saved.candidates) == 1 else "smoke_selector"})
            if config.goal.kind == "descend":
                completed = descent_completed(step)
            else:
                completion_kind = {"collect": "acquired", "mine_diamond": "acquired", "craft": "crafted",
                                   "smelt": "smelted"}[config.goal.kind]
                acquired_target += sum(event.quantity for event in step.events
                                       if event.kind == completion_kind and event.item == config.goal.target)
                completed = (not step.invalid and acquired_target > 0
                             and step.observation.inventory.get(config.goal.target, 0) >= config.goal.quantity)
            terminated, truncated, invalid, reason = step.terminated, step.truncated, step.invalid, step.reason
            unchanged = [step.observation.position, step.observation.map_version, step.observation.inventory, step.observation.tool_durability]
            stalled = stalled + 1 if step.actual_ticks <= 1 and not step.cancelled and unchanged == [
                observation.position, observation.map_version, observation.inventory, observation.tool_durability] else 0
            observation = step.observation
            if terminated or truncated or invalid:
                break
            if macros and completed:
                terminated, reason = True, "goal_completed"
                break
            if stalled >= STALL_LIMIT:
                # Nothing moved, cut or changed: the same choice would repeat until a budget ends (T07 G2 attempt 1).
                truncated, reason = True, "repeated_stall"
                break
        else:
            truncated, reason = True, "decision_limit"
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
    summary = EpisodeSummary(
        episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
        task="movement_smoke" if movement else "macros_smoke" if macros else "smoke",
        clock_mode=clock_mode, pause_verified=pause_verified, movement_steps=movement_steps,
        goal_completed=completed, terminated=terminated,
        truncated=truncated, invalid=invalid, reason=reason, error=error,
        active_ticks=active_ticks, wall_seconds=time.monotonic() - started,
        decisions=decisions, reward_total=reward_total,
        movement_completed=movement_completed, distance_moved=distance_moved,
        macro_steps=macro_steps, selection_requests=selection_requests, cancelled_selections=cancelled_selections,
        provided_inventory=provided_inventory, direct_crafted=direct_crafted,
        direct_smelted=direct_smelted, direct_acquired=direct_acquired, admin_verified=verified,
        diamond_success=config.goal.kind == "mine_diamond" and completed and verified.get("diamond", 0) >= 1,
    )
    emit("summary", summary)
    return summary
