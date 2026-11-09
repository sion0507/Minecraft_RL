"""Wood candidates derived only from the saved public observation."""

import math
from typing import Literal

from pydantic import JsonValue

from .navigation import ORE_TOP, PICKS, fresh_movement_candidates, observed_routes, ore_search_choices
from .schema import Candidate, CandidateSet, Goal, Observation, allocate


def generate_wood_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    return generate_resource_candidates(observation, goal)


def generate_resource_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    candidates: list[Candidate] = []
    remaining = goal.quantity - observation.inventory.get(goal.target, 0)
    block = {"cobblestone": "stone", "diamond": "diamond_ore"}.get(goal.target, goal.target)
    if not observation.remaining_ticks or remaining <= 0 or not (block.endswith("_log") or block in {"stone", *ORE_TOP}):
        return allocate([])

    def search() -> CandidateSet:
        return allocate(ore_search_choices(observation, block, remaining) if block in ORE_TOP
                        else fresh_movement_candidates(observation))

    def add(kind: Literal["place_or_equip", "mine_visible_cluster", "move_observed", "wait"],
            params: dict[str, JsonValue], description: str) -> None:
        candidates.append(Candidate(
            candidate_id=f"{observation.obs_id}:wood:{len(candidates)}", action_kind=kind,
            params=params, max_ticks=min(20 if kind == "wait" else 400, observation.remaining_ticks),
            stop_rule_id="wood_or_hazard", source_obs_id=observation.obs_id, description=description,
        ))

    routes = observed_routes(observation)
    for drop in observation.drops:
        if drop.item != goal.target:
            continue
        routes_near_drop = [(point, path) for point, path in routes.items()
                            if math.dist(path[-1] if path else observation.position, drop.position) <= 1.0]
        if routes_near_drop:
            _, path = min(routes_near_drop, key=lambda pair: (len(pair[1]), pair[0]))
            if path:
                add("move_observed", {"path": [[v for v in p] for p in path], "map_version": observation.map_version},
                    f"Collect observed {drop.item} drop")
            else:
                add("wait", {}, f"Wait for observed {drop.item} pickup")
            return allocate(candidates)
    logs = sorted({tuple(cell.position) for cell in observation.observed_map if cell.block == block and cell.visible},
                  key=lambda p: (math.dist(p, observation.position), p))
    if not logs:
        return search()
    seen_paths: set[str] = set()
    used: set[tuple[float, ...]] = set()
    eye = [observation.position[0], observation.position[1] + 1.62, observation.position[2]]
    for target in logs:
        if target in used:
            continue
        def close(p: tuple[float, ...]) -> bool:
            return (math.hypot(p[0] + 0.5 - observation.position[0],
                               p[2] + 0.5 - observation.position[2]) <= 1.8
                    and math.dist([v + 0.5 for v in p], eye) <= 4.5
                    and p[1] >= math.floor(observation.position[1]))
        if close(target):
            tools = (["netherite_axe", "diamond_axe", "iron_axe", "stone_axe", "wooden_axe", "golden_axe"] if block.endswith("_log")
                     else PICKS[:3] if block == "diamond_ore" else PICKS[:4] if block == "iron_ore" else PICKS)
            axes = [name for name in tools
                    if observation.inventory.get(name, 0)]
            if not block.endswith("_log") and not axes:
                continue
            if axes and observation.tool != axes[0]:
                add("place_or_equip", {"item": axes[0]}, f"Equip {axes[0]}")
                break
            cluster = [target]
            for point in cluster:
                for other in logs:
                    if (other not in cluster and close(other) and math.dist(point, other) == 1
                            and len(cluster) < min(8, remaining)):
                        cluster.append(other)
            used.update(cluster)
            for count in sorted({1, len(cluster)}):
                add("mine_visible_cluster", {"block": block, "blocks": [list(p) for p in cluster[:count]],
                                             "map_version": observation.map_version},
                    f"Mine {count} exposed {goal.target} at {list(target)} and collect its drops")
        else:
            approaches = [path for (x, y, z), path in routes.items() if path and
                          math.hypot(x - target[0], z - target[2]) <= 1.01 and y <= target[1] <= y + 3]
            if approaches:
                path = min(approaches, key=lambda route: (len(route), route))
                signature = str(path)
                if signature not in seen_paths:
                    seen_paths.add(signature)
                    add("move_observed", {"path": [[v for v in p] for p in path], "map_version": observation.map_version},
                        f"Approach exposed {goal.target} at {list(target)}")
    if not candidates:
        # Seen but unreachable: ores need cutting; a log seen beyond every 16-step route (radius 32, #44) needs walking.
        return search()
    return allocate(candidates)
