"""One public state/question/candidate-set meaning for local NanoJev and the later Jev adapter."""

import json
import math
from dataclasses import dataclass
from typing import Any

from .schema import CandidateSet, Goal, Observation

INSTRUCTIONS = ("Choose one offered macro action to make progress toward the current goal within the remaining active ticks. "
                "Use only the observed state and supplied candidates. Consider the action parameters, duration and stop rule. "
                "Return a choice among the supplied keys.")


def text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class ChoiceInput:
    payload: dict[str, Any]
    candidate_ids: list[str]
    mask: list[bool]
    context: list[float]
    objective: str


def choice_input(observation: Observation, goal: Goal, saved: CandidateSet) -> ChoiceInput:
    # Revalidate copies: model_copy and later mutation must not bypass the policy boundary.
    observation = Observation.model_validate(observation.model_dump())
    goal = Goal.model_validate(goal.model_dump())
    saved = CandidateSet.model_validate(saved.model_dump())
    if not any(saved.mask):
        raise ValueError("Choice requires at least one unmasked candidate")
    if any(c.source_obs_id != observation.obs_id for c in saved.candidates):
        raise ValueError("Candidate source observation mismatch")
    state = observation.model_dump(exclude={"episode_id", "attempt_id", "obs_id", "observed_map", "visited", "history"})
    # Shared bounded memory summary, selected by distance alone; never query unobserved cells.
    surfaces = sorted((s for s in observation.observed_map if s.block not in {"air", "cave_air", "void_air"}),
                      key=lambda s: (sum((a - b) ** 2 for a, b in zip(s.position, observation.position)), s.position, s.block))
    state["observed_surfaces"] = [[*s.position, s.block, s.passable, s.support, s.hazard] for s in surfaces[:64]]
    state["observed_surface_count"] = len(surfaces)
    state["visited_count"], state["recent_visited"] = len(observation.visited), observation.visited[-32:]
    state["recent_results"] = observation.history[-8:]
    state["goal"] = goal.model_dump(exclude={"goal_id"})
    criteria = {f"a{i}": text(c.model_dump(exclude={"candidate_id", "source_obs_id"}))
                for i, c in enumerate(saved.candidates)}
    return ChoiceInput(
        payload={"states": [{"id": "decision", "state": text(state), "questions": {
            "action": {"type": "choice", "instructions": INSTRUCTIONS, "criteria": criteria}}}]},
        candidate_ids=[c.candidate_id for c in saved.candidates], mask=list(saved.mask),
        context=[float(observation.objective_kind == "local"), float(observation.objective_kind == "full"),
                 math.log1p(observation.remaining_ticks) / math.log1p(36000),
                 math.log1p(goal.active_budget_ticks) / math.log1p(36000)], objective=observation.objective_kind,
    )
