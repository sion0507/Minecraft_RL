"""Resource candidates derived only from the saved public observation."""

import math
from typing import Literal

from pydantic import JsonValue

from .navigation import (
    ORE_TOP, PICKS, fresh_movement_candidates, observed_routes, ore_search_choices, stone_search_choices, supports_way_back,
    target_cut, toward_path, walk_params,
)
from .schema import Candidate, CandidateSet, Goal, Observation, allocate

APPROACHES = 3  # nearest distinct targets offered as walks; more are the same choice again (exp/candidate-structure)
APPROACHES_WHEN_MINEABLE = 2
TOWARD = 2  # walks toward a visible target that no observed 16-step route reaches yet
Draft = tuple[Literal["place_or_equip", "mine_visible_cluster", "move_observed", "wait"], dict[str, JsonValue], str]


def generate_wood_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    return generate_resource_candidates(observation, goal)


def generate_resource_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    remaining = goal.quantity - observation.inventory.get(goal.target, 0)
    block = {"cobblestone": "stone", "diamond": "diamond_ore"}.get(goal.target, goal.target)
    if not observation.remaining_ticks or remaining <= 0 or not (block.endswith("_log") or block in {"stone", *ORE_TOP}):
        return allocate([])

    def build(drafts: list[Draft]) -> list[Candidate]:
        return [Candidate(
            candidate_id=f"{observation.obs_id}:wood:{index}", action_kind=kind,
            params=params, max_ticks=min(20 if kind == "wait" else 400, observation.remaining_ticks),
            stop_rule_id="wood_or_hazard", source_obs_id=observation.obs_id, description=description,
        ) for index, (kind, params, description) in enumerate(drafts)]

    def walk(path: list[list[float]], description: str) -> Draft:
        return "move_observed", walk_params(observation, path, goal), description

    def search(toward: list[Draft]) -> CandidateSet:
        found = (ore_search_choices(observation, block, remaining, goal) if block in ORE_TOP
                 else stone_search_choices(observation, remaining, goal) if block == "stone"
                 else fresh_movement_candidates(observation, goal))
        directed: list[Candidate] = []
        if block in {"stone", *ORE_TOP} and (observation.tool or "").endswith("_pickaxe"):
            for target in targets:
                if math.dist(target, observation.position) > 8 or close(target):
                    continue
                walking = any(close(target, path[-1] if path else observation.position) for path in routes.values())
                if walking:
                    continue
                cut = target_cut(observation, goal, target, remaining)
                if cut is not None:
                    directed = [cut]
                    execution = {k: v for k, v in cut.params.items() if k not in {"target_position", "walking_path_available"}}
                    found = [c for c in found if c.action_kind != cut.action_kind or c.params != execution or c.max_ticks != cut.max_ticks]
                    break
        return allocate([*build(toward), *directed, *found])

    routes = observed_routes(observation, goal)
    for drop in observation.drops:
        if drop.item != goal.target:
            continue
        routes_near_drop = [(point, path) for point, path in routes.items()
                            if math.dist(path[-1] if path else observation.position, drop.position) <= 1.0]
        if routes_near_drop:
            _, path = min(routes_near_drop, key=lambda pair: (len(pair[1]), pair[0]))
            return allocate(build([walk(path, f"Collect observed {drop.item} drop")] if path
                                  else [("wait", {}, f"Wait for observed {drop.item} pickup")]))
    # Preserve the existing return steps even with ascent choices: neither mine them nor repeatedly approach them,
    # or two such steps are offered as approach after approach to the end of the budget (T evaluation seed 15011).
    sources = [cell for cell in observation.observed_map
               if cell.block == block and not supports_way_back(observation, cell.position)]
    targets = sorted({tuple(cell.position) for cell in sources if cell.visible},
                     key=lambda p: (math.dist(p, observation.position), p))

    def toward_walks(cells: list[tuple[float, ...]], seen: str) -> list[Draft]:
        found: list[Draft] = []
        ends: set[str] = set()
        for target in cells:
            centre = [v + 0.5 for v in target]
            now = math.dist(observation.position, centre)
            path = toward_path(observation, routes, centre)
            if path is None or str(path[-1]) in ends:
                continue
            ends.add(str(path[-1]))
            found.append(walk(path, f"Walk toward {seen} {goal.target} at {list(target)}: {now:.0f} blocks away now, "
                                    f"{math.dist(path[-1], centre):.0f} after these {len(path)} steps"))
            if len(found) == TOWARD:
                break
        return found

    if not targets:
        # Nothing in view: a cell remembered from an earlier observation is still a place to walk back to.
        remembered = sorted({tuple(cell.position) for cell in sources},
                            key=lambda p: (math.dist(p, observation.position), p))
        return search(toward_walks(remembered, "remembered (seen earlier, may have changed)"))
    mines: list[Draft] = []
    approaches: list[tuple[int, Draft]] = []
    equip: Draft | None = None
    seen_paths: set[str] = set()
    used: set[tuple[float, ...]] = set()
    repeated = False  # an approach ends in a cell the agent already stood in
    def close(p: tuple[float, ...], position: list[float] | None = None) -> bool:
        position = observation.position if position is None else position
        eye = [position[0], position[1] + 1.62, position[2]]
        return (math.hypot(p[0] + 0.5 - position[0], p[2] + 0.5 - position[2]) <= 1.8
                and math.dist([v + 0.5 for v in p], eye) <= 4.5 and p[1] >= math.floor(position[1]))

    for target in targets:
        if target in used:
            continue
        if close(target):
            tools = (["netherite_axe", "diamond_axe", "iron_axe", "stone_axe", "wooden_axe", "golden_axe"] if block.endswith("_log")
                     else PICKS[:3] if block == "diamond_ore" else PICKS[:4] if block == "iron_ore" else PICKS)
            carried = [name for name in tools if observation.inventory.get(name, 0)]
            if not block.endswith("_log") and not carried:
                continue
            if carried and observation.tool != carried[0]:
                equip = ("place_or_equip", {"item": carried[0]}, f"Equip {carried[0]}")
                break
            cluster = [target]
            for point in cluster:
                for other in targets:
                    if (other not in cluster and close(other) and math.dist(point, other) == 1
                            and len(cluster) < min(8, remaining)):
                        cluster.append(other)
            used.update(cluster)
            for count in sorted({1, len(cluster)}):
                mines.append(("mine_visible_cluster", {"block": block, "blocks": [list(p) for p in cluster[:count]],
                                                       "map_version": observation.map_version},
                              f"Mine {count} exposed {goal.target} at {list(target)} within reach now and collect its drops"))
        else:
            found = [path for path in routes.values() if path and close(target, path[-1])]
            if found:
                path = min(found, key=lambda route: (len(route), route))
                if str(path) not in seen_paths:
                    seen_paths.add(str(path))
                    repeated |= [float(math.floor(path[-1][0])), path[-1][1], float(math.floor(path[-1][2]))] in observation.visited
                    approaches.append((len(path), walk(path, f"Approach exposed {goal.target} at {list(target)}: "
                                                             f"{len(path)} steps to stand next to it")))
    if equip is not None:
        return allocate(build([*(draft for _, draft in approaches[:APPROACHES_WHEN_MINEABLE]), equip]))
    # Every further reachable target is the same decision again: keep the nearest few (exp/candidate-structure).
    nearest = [draft for _, draft in sorted(approaches, key=lambda pair: pair[0])]
    kept = [*mines, *nearest[:APPROACHES_WHEN_MINEABLE if mines else APPROACHES]]
    if kept:
        # Having stood at an approach's end without the target coming into reach (it is above, below or out of sight
        # from there), that walk alone is the same move for ever: the cuts are offered next to it (T iron slots 4, 8).
        return search(kept) if repeated and not mines else allocate(build(kept))
    # Seen but beyond every observed 16-step route: the walk that ends nearest to it, next to the search choices
    # (ores and stone can be cut toward; a log needs walking).
    return search(toward_walks(targets, "exposed"))
