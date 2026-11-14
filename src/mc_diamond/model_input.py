"""One public state/question/candidate-set meaning for local NanoJev and the later Jev adapter."""

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schema import CandidateSet, Goal, Observation

INPUT_HASH = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()  # pins these summary rules for the lock (#44)
SUMMARY_CELLS = 256
OPEN = {"air", "cave_air", "void_air"}

INSTRUCTIONS = ("Choose one offered macro action to make progress toward the current goal within the remaining active ticks. "
                "Use only the observed state and supplied candidates. Consider the action parameters, duration and stop rule. "
                "Return a choice among the supplied keys.")


def text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def memory_summary(observation: Observation) -> list[dict[str, Any]]:
    """Remembered non-air cells grouped by kind, at most SUMMARY_CELLS in all; never a cell that was not observed.

    Kinds are filled smallest first with an even share of what is left, nearest cells first, so a few ores, hazards or
    facilities are never pushed out by abundant floor (#44). `now` cells are in the current view, `past` ones remembered.
    """
    kinds: dict[tuple[str, bool, bool, bool], list[Any]] = {}
    for cell in observation.observed_map:
        if cell.block not in OPEN:
            kinds.setdefault((cell.block, cell.passable, cell.support, cell.hazard), []).append(cell)
    left, summary = SUMMARY_CELLS, []
    for index, kind in enumerate(sorted(kinds, key=lambda k: (len(kinds[k]), k))):
        cells = sorted(kinds[kind], key=lambda c: (sum((a - b) ** 2 for a, b in zip(c.position, observation.position)), c.position))
        shown = cells[:min(len(cells), -(-left // (len(kinds) - index)))]  # ceil: rare kinds never get 0 while room is left
        left -= len(shown)
        summary.append({"block": kind[0], "passable": kind[1], "support": kind[2], "hazard": kind[3], "total": len(cells),
                        "now": [[int(v) for v in c.position] for c in shown if c.visible],
                        "past": [[int(v) for v in c.position] for c in shown if not c.visible]})
    return sorted(summary, key=lambda k: (k["block"], k["passable"], k["support"], k["hazard"]))


def memory_counts(state: dict[str, Any]) -> dict[str, Any]:
    """Remembered non-air cells before/after the summary and what each block kind left out, for every model call log."""
    omitted: dict[str, int] = {}
    for kind in state["memory"]:
        left = kind["total"] - len(kind["now"]) - len(kind["past"])
        if left:
            omitted[kind["block"]] = omitted.get(kind["block"], 0) + left
    return {"cells": sum(kind["total"] for kind in state["memory"]), "shown": sum(len(k["now"]) + len(k["past"]) for k in state["memory"]),
            "omitted": omitted}


def public_state(observation: Observation) -> dict[str, Any]:
    """The one bounded state every planner (Qwen/Astra) and action model (NanoJev/Jev/S inputs) receives."""
    # Revalidate copies: model_copy and later mutation must not bypass the policy boundary.
    observation = Observation.model_validate(observation.model_dump())
    state = observation.model_dump(exclude={"episode_id", "attempt_id", "obs_id", "observed_map", "visited", "history"})
    state.update(memory=memory_summary(observation), visited_count=len(observation.visited),
                 recent_visited=observation.visited[-32:], recent_results=observation.history[-8:],
                 cut_entrances=observation.cut_entrances[-8:])
    return state


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
    state = public_state(observation)
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
