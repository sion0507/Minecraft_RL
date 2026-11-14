"""Rule-based action selector S (PLAN §6.5). `RULE_HASH` covers this file only; T19 locks it.

S compares candidates by one fixed lexicographic key (user decision 2026-11-09, #9):
  1. recent failure: the same action (kind + target/direction) failed among the last three failures -> later;
     when every candidate failed recently the key ties and is ignored
  2. observed hazard: any point the candidate reaches within 3 blocks of an observed hazard -> later
  3. goal relevance: direct work (mine target, craft, furnace, safe hold) 0 < preparation, approaching an observed
     target or (escape) walking away from the hazard 1 < search (tunnel, stairs, other walks) 2 < plain wait 3
  4. expected progress: larger workload first
  5. tie: saved candidate order (generation order)
It reads only the saved candidate set and mask, the goal, the observation and the outcomes of its own earlier steps.
Public preconditions are already applied by the generators and the mask: S never sees a candidate that fails them.
"""

import hashlib
import math
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from .goals import ESCAPE_DISTANCE
from .navigation import hazard_distance
from .schema import Candidate, CandidateSet, Goal, Observation, SelectionResult
from .selectors import result, signature

RULE_VERSION = "s-rules-v2-issue54"
RULE_HASH = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
BLOCK = {"cobblestone": "stone", "diamond": "diamond_ore"}  # goal target -> the block that drops it
FACILITY = {"craft": "crafting_table", "smelt": "furnace"}


def _number(candidate: Candidate, key: str) -> int:
    return int(cast(int, candidate.params.get(key, 0) or 0))


def reach(candidate: Candidate, observation: Observation) -> list[list[float]]:
    """Points the candidate ends at or cuts through, from its own parameters."""
    params = candidate.params
    x, y, z = map(math.floor, observation.position)
    path = cast(list[list[float]], params.get("path") or [])
    if path:
        return [path[-1]]
    if candidate.action_kind == "mine_visible_cluster":
        return [[v + 0.5 for v in block] for block in cast(list[list[float]], params["blocks"])]
    if "direction" in params:
        dx, dz = cast(list[int], params["direction"])
        if candidate.action_kind in {"stair_down", "stair_up"}:
            rise = 1 if candidate.action_kind == "stair_up" else -1
            return [[x + dx * k + 0.5, y + rise * k, z + dz * k + 0.5] for k in range(1, _number(candidate, "stairs") + 1)]
        return [[x + dx * k + 0.5, y, z + dz * k + 0.5] for k in range(1, _number(candidate, "cells") + 1)]
    if candidate.action_kind == "pillar_up":
        return [[x + 0.5, y + k, z + 0.5] for k in range(1, _number(candidate, "blocks") + 1)]
    return [list(observation.position)]


def workload(candidate: Candidate) -> float:
    kind = candidate.action_kind
    if kind in {"move_observed", "mine_visible_cluster"}:
        return float(len(cast(list[object], candidate.params["path" if kind == "move_observed" else "blocks"])))
    if kind == "tunnel":
        return float(_number(candidate, "cells") * _number(candidate, "height"))
    return float(_number(candidate, "blocks" if kind == "pillar_up" else "stairs" if kind in {"stair_down", "stair_up"} else "quantity"))


def relevance(candidate: Candidate, observation: Observation, goal: Goal) -> int:
    kind = candidate.action_kind
    if kind in {"craft_batch", "furnace_load", "furnace_collect"}:
        return 0
    if kind == "mine_visible_cluster":
        return 0 if candidate.params.get("block") == BLOCK.get(goal.target, goal.target) else 1
    if kind == "place_or_equip":
        return 1
    if kind == "wait":
        return 0 if candidate.stop_rule_id == "hold_or_hazard" else 3
    if kind == "stair_down":
        return 1 if goal.kind == "descend" else 2
    if kind == "move_observed":
        end = reach(candidate, observation)[0]
        if goal.kind == "escape":
            here = hazard_distance(observation.observed_map, observation.position)
            return 1 if hazard_distance(observation.observed_map, end) > here else 2
        block = FACILITY.get(goal.kind, BLOCK.get(goal.target, goal.target))
        targets = [[v + 0.5 for v in cell.position] for cell in observation.observed_map
                   if cell.visible and cell.block == block] + [drop.position for drop in observation.drops
                                                               if drop.item == goal.target]
        if targets and min(math.dist(end, t) for t in targets) < min(math.dist(observation.position, t) for t in targets):
            return 1
    return 2


def rule_select(observation: Observation, goal: Goal, saved: CandidateSet, failures: Sequence[str]) -> SelectionResult:
    """Selector S: deterministic, no model, no probabilities; `failures` are signatures of its own recent failures."""
    keys: dict[str, list[float]] = {}
    for candidate in saved.candidates:
        near = any(hazard_distance(observation.observed_map, point) < ESCAPE_DISTANCE for point in reach(candidate, observation))
        keys[candidate.candidate_id] = [float(signature(candidate) in failures), float(near),
                                        float(relevance(candidate, observation, goal)), -workload(candidate)]
    allowed = [c for c, ok in zip(saved.candidates, saved.mask) if ok]
    chosen = min(allowed, key=lambda c: keys[c.candidate_id])  # min keeps the first of equal keys: saved order
    return result(chosen, "rule_deterministic", rule_version=RULE_VERSION, rule_hash=RULE_HASH, rule_keys=keys)
