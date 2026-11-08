"""Conservative walking (level or one-block steps) and stair choices over directly observed cells only."""

import math
from collections import deque
from collections.abc import Iterable

from .schema import Candidate, CandidateSet, Observation, Surface

PICKS = ["netherite_pickaxe", "diamond_pickaxe", "iron_pickaxe", "stone_pickaxe", "wooden_pickaxe", "golden_pickaxe"]
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
SAFE_BAND = (5, 12)  # PLAN 5.1 descend: y=5-12.
BOUNCY = {"slime_block"}  # A landing bounces: a height change from or onto it overruns the 16-block cap (#37).


def observed_routes(observation: Observation) -> dict[tuple[int, int, int], list[list[float]]]:
    """Level walks and one-block steps (bridge `terrain.canStep` is the same rule) over observed cells only."""
    cells = {tuple(cell.position): cell for cell in observation.observed_map}

    def clear(point: tuple[int, int, int]) -> bool:
        cell = cells.get(point)
        return bool(cell and cell.passable and not cell.hazard)

    def footing(point: tuple[int, int, int]) -> Surface | None:
        """The floor of a standable cell (bridge `terrain.safe`): supporting, safe, with clear feet and head."""
        cell = cells.get((point[0], point[1] - 1, point[2]))
        standable = cell and cell.support and not cell.hazard and clear(point) and clear((point[0], point[1] + 1, point[2]))
        return cell if standable else None

    sx, sy, sz = map(math.floor, observation.position)
    start = (sx, sy, sz)
    queue: deque[tuple[tuple[int, int, int], list[list[float]]]] = deque([(start, [])])
    routes: dict[tuple[int, int, int], list[list[float]]] = {start: []}
    while queue:
        (x, y, z), route = queue.popleft()
        if len(route) >= 16:
            continue
        for dx, dz in DIRECTIONS:
            for dy in (0, -1, 1):
                point = (x + dx, y + dy, z + dz)
                below = footing(point)
                if point in routes or below is None:
                    continue
                # A drop passes the front head cell at the start height; a jump lifts the head into the cell over the start.
                if dy and (below.block in BOUNCY or (here := footing((x, y, z))) is None or here.block in BOUNCY
                           or not clear((point[0], y + 1, point[2]) if dy < 0 else (x, y + 2, z))):
                    continue
                path = [*route, [point[0] + 0.5, float(point[1]), point[2] + 0.5]]
                routes[point] = path
                queue.append((point, path))
    return routes


def generate_movement_candidates(observation: Observation) -> CandidateSet:
    sx, _, sz = map(math.floor, observation.position)
    visited = {tuple(point) for point in observation.visited}
    directions: dict[tuple[int, int], list[list[float]]] = {}
    for point, path in observed_routes(observation).items():
        if path:
            x, _, z = point
            direction = ((x > sx) - (x < sx), (z > sz) - (z < sz))
            previous = directions.get(direction)
            if previous and point in visited and tuple(math.floor(v) for v in previous[-1]) not in visited:
                continue
            directions[direction] = path
    candidates = [Candidate(
        candidate_id=f"{observation.obs_id}:move:{index}", action_kind="move_observed",
        params={"path": [[value for value in point] for point in route], "map_version": observation.map_version},
        max_ticks=min(400, observation.remaining_ticks), stop_rule_id="observed_path_or_hazard",
        source_obs_id=observation.obs_id, description=f"Walk over observed cells to {route[-1]}",
    ) for index, route in enumerate(directions.values()) if observation.remaining_ticks]
    return CandidateSet(candidates=candidates, mask=[True] * len(candidates))


def fresh_movement_candidates(observation: Observation) -> list[Candidate]:
    return [candidate for candidate in generate_movement_candidates(observation).candidates
            if [float(math.floor(v)) for v in candidate.params["path"][-1]] not in observation.visited]  # type: ignore


def safe_ground(observation: Observation) -> bool:
    """Same observed conditions the bridge re-checks on every hold tick."""
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    px, py, pz = observation.position
    x, y, z = math.floor(px), math.floor(py), math.floor(pz)
    floor, feet, head = (cells.get((x, y + offset, z)) for offset in (-1, 0, 1))
    return bool(observation.on_ground and not observation.in_liquid and not observation.on_fire
                and floor and floor.support and not floor.hazard and feet and feet.passable and head and head.passable
                and not any(c.hazard and math.hypot(c.position[0] + 0.5 - px, c.position[1] - py, c.position[2] + 0.5 - pz) < 1.5
                            for c in cells.values()))


ORE_TOP = {"iron_ore": 63, "diamond_ore": 15}  # Highest generation layer in 1.16.5: range(64) and range(16).


def _ready(observation: Observation, walking: list[Candidate]) -> list[Candidate] | None:
    """Walking, or equipping a carried pickaxe as its own choice, until a cut is possible; None once it is."""
    if observation.in_liquid or observation.on_fire or not observation.remaining_ticks:
        return walking[:8]
    if not (observation.tool or "").endswith("_pickaxe"):
        pick = next((name for name in PICKS if observation.inventory.get(name)), None)
        return walking[:8] if pick is None else [Candidate(
            candidate_id=f"{observation.obs_id}:stair:equip", action_kind="place_or_equip", params={"item": pick},
            max_ticks=min(400, observation.remaining_ticks), stop_rule_id="stair_ore_or_hazard",
            source_obs_id=observation.obs_id, description=f"Equip {pick} for the stairs")]
    return None


def _open(observation: Observation, stop_blocks: list[str], column: list[tuple[int, int, int]],
          floor: tuple[int, int, int]) -> bool:
    """Only an observed cell can veto a cut: a nearby hazard, an open floor, or a stop ore/bedrock in it.

    Whatever is still unseen is judged by the macro at the moment it is exposed, so this never depends on hidden terrain.
    """
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    hazards = [cell.position for cell in cells.values() if cell.hazard]
    if any(max(abs(a - b) for a, b in zip(point, hazard)) <= 1 for hazard in hazards for point in (*column, floor)):
        return False
    if floor in cells and not cells[floor].support:
        return False
    return not any(point in cells and (cells[point].block in stop_blocks or cells[point].block == "bedrock")
                   for point in column)


def _facing_first(observation: Observation, directions: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    facing = (-math.sin(observation.yaw), -math.cos(observation.yaw))
    return sorted(directions, key=lambda d: (-round(d[0] * facing[0] + d[1] * facing[1], 6), DIRECTIONS.index(d)))


def _stairs(observation: Observation, stop_blocks: list[str], stairs: int) -> tuple[list[Candidate], list[Candidate]]:
    """Every open direction at the full workload, then the single-stair workload."""
    if stairs < 1:
        return [], []
    x, y, z = map(math.floor, observation.position)
    directions = _facing_first(observation, (d for d in DIRECTIONS if _open(
        observation, stop_blocks, [(x + d[0], y + h, z + d[1]) for h in (1, 0, -1)], (x + d[0], y - 2, z + d[1]))))

    def stair(index: int, direction: tuple[int, int], count: int) -> Candidate:
        return Candidate(
            candidate_id=f"{observation.obs_id}:stair:{index}", action_kind="stair_down",
            params={"direction": list(direction), "stairs": count, "stop_blocks": list(stop_blocks),
                    "map_version": observation.map_version},
            max_ticks=min(400, observation.remaining_ticks), stop_rule_id="stair_ore_or_hazard",
            source_obs_id=observation.obs_id, description=f"Cut {count} stairs down toward {list(direction)}")

    broad = [stair(index, direction, stairs) for index, direction in enumerate(directions)]
    narrow = [stair(len(broad) + index, direction, 1) for index, direction in enumerate(directions)] if stairs > 1 else []
    return broad, narrow


def _tunnels(observation: Observation, stop_blocks: list[str], durability: int) -> list[Candidate]:
    """Level 1x2 tunnels in every open, unvisited direction, then the taller 1x3 section facing first."""
    x, y, z = map(math.floor, observation.position)
    visited = {tuple(point) for point in observation.visited}
    found: list[Candidate] = []
    for height in (2, 3):
        cells = min(8, durability // height)
        if cells < 1:
            continue
        directions = _facing_first(observation, (d for d in DIRECTIONS if (x + d[0], y, z + d[1]) not in visited and _open(
            observation, stop_blocks, [(x + d[0], y + h, z + d[1]) for h in range(height)], (x + d[0], y - 1, z + d[1]))))
        for direction in directions[:4 if height == 2 else 1]:
            found.append(Candidate(
                candidate_id=f"{observation.obs_id}:tunnel:{len(found)}", action_kind="tunnel",
                params={"direction": list(direction), "cells": cells, "height": height, "stop_blocks": list(stop_blocks),
                        "map_version": observation.map_version},
                max_ticks=min(400, observation.remaining_ticks), stop_rule_id="tunnel_ore_or_hazard",
                source_obs_id=observation.obs_id, description=f"Tunnel {cells} cells 1x{height} toward {list(direction)}"))
    return found


def descent_choices(observation: Observation) -> list[Candidate]:
    """Every open direction, then observed walking, then the smaller workload, within the 8-choice cap."""
    y = math.floor(observation.position[1])
    walking = fresh_movement_candidates(observation)
    early = walking[:8] if y - SAFE_BAND[0] < 1 else _ready(observation, walking)
    if early is not None:
        return early
    broad, narrow = _stairs(observation, ["diamond_ore"], min(4, y - SAFE_BAND[0]))
    return [*broad, *walking, *narrow][:8]


def ore_search_choices(observation: Observation, target: str, reserve: int) -> list[Candidate]:
    """Stairs while above the ore's generation layers, then level tunnels; walking new ground stays a choice.

    No cut may spend the durability still needed to mine the remaining target ores (`reserve`).
    """
    y = math.floor(observation.position[1])
    walking = fresh_movement_candidates(observation)
    early = _ready(observation, walking)
    if early is not None:
        return early
    stop_blocks = sorted({"diamond_ore", target})
    durability = (observation.tool_durability or 0) - reserve
    broad, narrow = _stairs(observation, stop_blocks, min(4, y - SAFE_BAND[0], durability // 3))
    tunnels = _tunnels(observation, stop_blocks, durability)
    if y > ORE_TOP[target]:
        return [*broad, *tunnels, *walking, *narrow][:8]
    return [*walking[:4], *tunnels, *broad, *walking[4:], *narrow][:8]  # Cutting stays a choice in open ground.


def generate_descent_candidates(observation: Observation) -> CandidateSet:
    choices = descent_choices(observation)
    if (observation.remaining_ticks and SAFE_BAND[0] <= math.floor(observation.position[1]) <= SAFE_BAND[1]
            and observation.inventory.get("iron_pickaxe") and safe_ground(observation)):
        hold = Candidate(candidate_id=f"{observation.obs_id}:hold", action_kind="wait", params={},
                         max_ticks=min(20, observation.remaining_ticks), stop_rule_id="hold_or_hazard",
                         source_obs_id=observation.obs_id, description="Hold observed safe ground for 20 ticks")
        choices = [hold, *choices][:8]
    return CandidateSet(candidates=choices, mask=[True] * len(choices))
