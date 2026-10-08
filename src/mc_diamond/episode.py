"""Shared smoke execution flow. Research rewards and actors are subsequent work."""

import json
import time
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ValidationError

from .rpc import EpisodeError, PolicyEnvironment
from .schema import (
    Candidate, CandidateSet, EpisodeConfig, EpisodeSummary, ErrorInfo, Goal, Observation, SelectionResult,
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


def run_episode(config: EpisodeConfig, environment: PolicyEnvironment,
                reset: Callable[[], Observation], episode_id: str, attempt_id: str) -> EpisodeSummary:
    started = time.monotonic()
    active_ticks = decisions = 0
    reward_total = 0.0
    acquired_target = 0
    terminated = truncated = invalid = completed = False
    reason = "decision_limit"
    error: ErrorInfo | None = None
    clock_mode: Literal["mock", "paused", "realtime"] = "mock"
    try:
        initial = reset()
        emit("reset", initial)
        observation = environment.observe()
        if observation != initial:
            raise EpisodeError(ErrorInfo(code="protocol_error", message="Reset/observe state mismatch"))
        while decisions < config.max_decisions:
            if observation.episode_id != episode_id or observation.attempt_id != attempt_id:
                raise EpisodeError(ErrorInfo(code="protocol_error", message="Episode/attempt ID mismatch"))
            active_ticks = observation.active_ticks
            emit("observation", observation)
            emit("goal", config.goal)
            if observation.remaining_ticks == 0:
                truncated, reason = True, "active_tick_limit"
                break
            saved = generate_candidates(observation, config.goal)
            emit("candidates", saved)
            candidate = saved.candidates[0] if saved.candidates else Candidate(
                candidate_id=f"{observation.obs_id}:wait", action_kind="wait", params={},
                max_ticks=min(20, observation.remaining_ticks), stop_rule_id="time_or_hazard",
                source_obs_id=observation.obs_id, description="Wait when no candidate is available",
            )
            selection = SelectionResult(
                candidate_id=candidate.candidate_id, selector_mode="mock_fixed" if saved.candidates else "forced_wait",
                probabilities=None, latency_seconds=0.0, provider=None, model=None, usage=None,
            )
            emit("selection", selection)
            step = environment.step(candidate)
            decisions += 1
            if (step.observation.episode_id != episode_id or step.observation.attempt_id != attempt_id
                or step.observation.active_ticks != active_ticks + step.actual_ticks
                or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                or step.actual_ticks > candidate.max_ticks or step.observation.obs_id == observation.obs_id):
                raise EpisodeError(ErrorInfo(code="invalid_step", message="Inconsistent step IDs or tick accounting"))
            active_ticks = step.observation.active_ticks
            clock_mode = step.clock_mode
            emit("step", step)
            reward = float(sum(event.quantity for event in step.events if event.kind == "acquired"))
            reward_total += reward
            emit("reward", {"value": reward, "kind": "smoke_acquisition_count", "actor_valid": False})
            acquired_target += sum(event.quantity for event in step.events
                                   if event.kind == "acquired" and event.item == config.goal.target)
            completed = (not step.invalid and acquired_target >= config.goal.quantity
                         and step.observation.inventory.get(config.goal.target, 0) >= config.goal.quantity)
            terminated, truncated, invalid, reason = step.terminated, step.truncated, step.invalid, step.reason
            observation = step.observation
            if terminated or truncated or invalid:
                break
        else:
            truncated, reason = True, "decision_limit"
    except EpisodeError as failure:
        error, reason = failure.error, failure.error.code
        emit("error", error)
    except ValidationError:
        error = ErrorInfo(code="protocol_error", message="Backend result violates contract")
        reason = error.code
        emit("error", error)
    summary = EpisodeSummary(
        episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
        clock_mode=clock_mode, goal_completed=completed, terminated=terminated,
        truncated=truncated, invalid=invalid, reason=reason, error=error,
        active_ticks=active_ticks, wall_seconds=time.monotonic() - started,
        decisions=decisions, reward_total=reward_total,
    )
    emit("summary", summary)
    return summary
