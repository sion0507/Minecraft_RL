"""Walking, safe drops and stair choices over directly observed cells only."""

import math
from collections import Counter, deque
from collections.abc import Iterable
from typing import cast

from pydantic import JsonValue

from .schema import Candidate, CandidateSet, Goal, Observation, Surface, allocate

PICKS = ["netherite_pickaxe", "diamond_pickaxe", "iron_pickaxe", "stone_pickaxe", "wooden_pickaxe", "golden_pickaxe"]
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
SAFE_BAND = (5, 12)  # PLAN 5.1 descend: y=5-12.
COMPASS = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north",
           (1, 1): "southeast", (1, -1): "northeast", (-1, 1): "southwest", (-1, -1): "northwest"}
BOUNCY = {"slime_block"}  # A landing bounces: a height change from or onto it overruns the 16-block cap (#37).


HAZARD_RADIUS = 1.5  # bridge `terrain.danger`: no macro starts or continues this close to an observed hazard.


def hazard_distance(cells: Iterable[Surface], position: Iterable[float]) -> float:
    """Distance to the nearest hazard cell, measured as bridge `terrain.hazardDistance` does; inf when none."""
    px, py, pz = position
    return min((math.hypot(c.position[0] + 0.5 - px, c.position[1] - py, c.position[2] + 0.5 - pz)
                for c in cells if c.hazard), default=math.inf)


def scaffold_material(observation: Observation, goal: Goal | None = None) -> tuple[str, int, int] | None:
    """Dirt first; retain stone for the current goal, a stone pick and a furnace still to be made."""
    stock = observation.inventory
    reserve = (0 if any(stock.get(p) for p in PICKS[:4]) else 3) + (0 if stock.get("furnace") else 8)
    if goal:
        reserve = max(reserve, goal.quantity if goal.target == "cobblestone" else
                      8 if goal.target == "furnace" else 3 if goal.target.startswith("stone_") else 0)
    for item, keep in (("dirt", 0), ("cobblestone", reserve)):
        if stock.get(item, 0) > keep:
            return item, keep, stock[item] - keep
    return None


def scaffold_count(observation: Observation, route: list[list[float]]) -> int:
    return sum(a[0] == b[0] and a[2] == b[2] and b[1] == a[1] + 1
               for a, b in zip([[math.floor(v) + (0 if i == 1 else 0.5) for i, v in enumerate(observation.position)], *route], route))


def walk_params(observation: Observation, route: list[list[float]], goal: Goal | None = None) -> dict[str, JsonValue]:
    params: dict[str, JsonValue] = {"path": cast(JsonValue, route), "map_version": observation.map_version}
    material = scaffold_material(observation, goal)
    if scaffold_count(observation, route) and material:
        params["scaffold"] = {"item": material[0], "reserve": material[1]}
    return params


def observed_routes(observation: Observation, goal: Goal | None = None) -> dict[tuple[int, int, int], list[list[float]]]:
    """Level walks, one-block climbs and drops up to three (bridge `terrain.canStep` uses the same rule).

    A point inside the hazard radius is used only farther from the hazard than the point before it (bridge `validPath`):
    walks never enter the radius, and a walk that starts inside it only moves away.
    """
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    hazards = [cell for cell in observation.observed_map if cell.hazard]

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
    material = scaffold_material(observation, goal)
    queue: deque[tuple[tuple[int, int, int], list[list[float]]]] = deque([(start, [])])
    routes: dict[tuple[int, int, int], list[list[float]]] = {start: []}
    while queue:
        (x, y, z), route = queue.popleft()
        if len(route) >= 16:
            continue
        last = hazard_distance(hazards, route[-1] if route else observation.position)
        for dx, dz in DIRECTIONS:
            # A two-block ledge: jump/place one block underfoot, then jump from it onto the observed ledge.
            ledge = (x + dx, y + 2, z + dz)
            if (ledge not in routes and material and scaffold_count(observation, route) < material[2] and len(route) <= 14
                    and footing((x, y, z)) and footing(ledge)
                    and all(clear((x, y + h, z)) for h in (0, 1, 2, 3))):
                pillar = [x + 0.5, float(y + 1), z + 0.5]
                top = [ledge[0] + 0.5, float(ledge[1]), ledge[2] + 0.5]
                if min(hazard_distance(hazards, p) for p in (pillar, top)) >= HAZARD_RADIUS:
                    routes[ledge] = [*route, pillar, top]
                    queue.append((ledge, routes[ledge]))
            for dy in (0, -1, 1, -2, -3):
                point = (x + dx, y + dy, z + dz)
                below = footing(point)
                if point in routes or below is None:
                    continue
                # A drop passes the front head cell at the start height; a jump lifts the head into the cell over the start.
                if dy and (below.block in BOUNCY or (here := footing((x, y, z))) is None or here.block in BOUNCY
                           or (dy < 0 and not all(clear((point[0], h, point[2])) for h in range(y + dy, y + 2)))
                           or (dy > 0 and not clear((x, y + 2, z)))):
                    continue
                centre = [point[0] + 0.5, float(point[1]), point[2] + 0.5]
                if (away := hazard_distance(hazards, centre)) < HAZARD_RADIUS and away <= last:
                    continue
                path = [*route, centre]
                routes[point] = path
                queue.append((point, path))
    return routes


def walk_summary(observation: Observation, route: list[list[float]]) -> str:
    """The walk in words a reader needs: length, compass direction and height change (same observed route, no new facts)."""
    dx, dy, dz = (route[-1][axis] - math.floor(observation.position[axis]) - (0.5 if axis != 1 else 0) for axis in range(3))
    heading = COMPASS.get(((dx > 0.5) - (dx < -0.5), (dz > 0.5) - (dz < -0.5)), "in place")
    height = "level" if abs(dy) < 1 else f"{abs(round(dy))} {'up' if dy > 0 else 'down'}"
    placed = scaffold_count(observation, route)
    return f"{len(route)} steps {heading}, {height}," + (f" use {placed} block(s)," if placed else "")


def movement_choices(observation: Observation, goal: Goal | None = None) -> list[Candidate]:
    sx, _, sz = map(math.floor, observation.position)
    visited = {tuple(point) for point in observation.visited}
    directions: dict[tuple[int, int, bool], list[list[float]]] = {}
    cells = {tuple(c.position): c for c in observation.observed_map}
    resources = [c for c in cells.values() if c.visible and (c.block == "stone" or c.block.endswith("_ore"))]

    def score(path: list[list[float]]) -> tuple[bool, float, int, int, int]:
        point = tuple(math.floor(v) for v in path[-1])
        nearby = sum(math.dist(c.position, path[-1]) <= 8 for c in resources)
        frontier = sum((point[0] + dx, point[1], point[2] + dz) not in cells for dx, dz in DIRECTIONS)
        return point not in visited, -point[1], nearby, frontier, len(path)
    routes = observed_routes(observation, goal)
    for point, path in routes.items():
        x, _, z = point
        direction = ((x > sx) - (x < sx), (z > sz) - (z < sz), bool(scaffold_count(observation, path)))
        # One walk per horizontal direction (at most 8). With steps a route can end above or below the start, in its own
        # column: that has no direction and would be a ninth choice (#37 run 2, natural G4).
        if direction[:2] != (0, 0):
            previous = directions.get(direction)
            if previous and score(previous) >= score(path):
                continue
            directions[direction] = path
    candidates = []
    for entrance in reversed(observation.cut_entrances):
        ex, ey, ez = map(math.floor, entrance)
        back = routes.get((ex, ey, ez)) or toward_path(observation, routes, entrance)
        if back:
            candidates.append(Candidate(candidate_id=f"{observation.obs_id}:entrance", action_kind="move_observed",
                params=walk_params(observation, back, goal), max_ticks=min(400, observation.remaining_ticks),
                stop_rule_id="observed_path_or_hazard", source_obs_id=observation.obs_id,
                description=f"Return toward the remembered cut entrance at {entrance}: {walk_summary(observation, back)}"))
            break
    paths = list(directions.values())
    climb = min((p for p in routes.values() if p and p[-1][1] > math.floor(observation.position[1])
                 and (math.floor(p[-1][0]), math.floor(p[-1][2])) != (sx, sz)), default=None, key=lambda p: (len(p), p))
    # Deep endpoints can otherwise replace every climb with flat ground before its first step (#54 information audit).
    if climb and climb not in paths:
        paths.insert(0, climb)
    for index, route in enumerate(paths):
        if not observation.remaining_ticks:
            break
        if any(c.params["path"] == route for c in candidates):
            continue
        counts = Counter(cell.block for cell in observation.observed_map
                         if cell.visible and cell.block not in {"air", "cave_air", "void_air"}
                         and math.dist(cell.position, route[-1]) <= 16)
        nearby = ", ".join(f"{block} {counts[block]}" for block in sorted(counts, key=lambda b: (counts[b], b))[:8])
        candidates.append(Candidate(
            candidate_id=f"{observation.obs_id}:move:{index}", action_kind="move_observed",
            params=walk_params(observation, route, goal),
            max_ticks=min(400, observation.remaining_ticks), stop_rule_id="observed_path_or_hazard",
            source_obs_id=observation.obs_id, description=f"Walk {walk_summary(observation, route)} over observed cells "
                f"to {route[-1]}; {'underground' if route[-1][1] < observation.position[1] else 'surface'} exploration, "
                f"deep/resource/frontier endpoint; currently visible within 16 blocks of it: {nearby or 'none'}"))
    return candidates


def generate_movement_candidates(observation: Observation, goal: Goal | None = None) -> CandidateSet:
    return allocate(movement_choices(observation, goal))


def ascent_choices(observation: Observation, goal: Goal) -> list[Candidate]:
    if not observation.remaining_ticks or not safe_ground(observation):
        return []
    material = scaffold_material(observation, goal)
    cells = {tuple(c.position): c for c in observation.observed_map}
    x, y, z = map(math.floor, observation.position)
    if not any(cells.get((x + dx, y + h, z + dz)) and cells[(x + dx, y + h, z + dz)].support
               for dx, dz in DIRECTIONS for h in (0, 1)) and not any(p[1] > y for p in observation.cut_entrances):
        return []
    height = 0
    if material:
        for h in range(1, min(4, material[2]) + 1):
            cell = cells.get((x, y + h + 1, z))
            if not cell or not cell.passable or cell.hazard:
                break
            height = h
    if not height or material is None:
        if not (observation.tool or "").endswith("_pickaxe") or not any(
                cells.get((x + dx, y + 1, z + dz)) and not cells[(x + dx, y + 1, z + dz)].passable for dx, dz in DIRECTIONS):
            return []
        stop = sorted({"diamond_ore", goal.target} & {"diamond_ore", "iron_ore", "coal_ore"})
        stairs = min(4, (observation.tool_durability or 0) // 4)
        if not stairs:
            return []
        directions = _facing_first(observation, (d for d in DIRECTIONS if _open(observation, stop,
            [(x, y + 2, z), *[(x + d[0], y + h, z + d[1]) for h in (1, 2, 3)]], (x + d[0], y, z + d[1]))))
        return [Candidate(candidate_id=f"{observation.obs_id}:up:{i}", action_kind="stair_up",
            params={"direction": list(d), "stairs": stairs, "stop_blocks": list(stop), "map_version": observation.map_version},
            max_ticks=min(400, observation.remaining_ticks), source_obs_id=observation.obs_id, stop_rule_id="ascent_or_hazard",
            description=f"Cut {stairs} stairs up toward {COMPASS[d]}, at most {4 * stairs} tool uses / 400 ticks")
            for i, d in enumerate(directions[:2])]
    return [Candidate(candidate_id=f"{observation.obs_id}:pillar", action_kind="pillar_up",
        params={"blocks": height, "item": material[0], "reserve": material[1], "map_version": observation.map_version},
        max_ticks=min(400, observation.remaining_ticks), source_obs_id=observation.obs_id, stop_rule_id="ascent_or_hazard",
        description=f"Pillar up {height} blocks, using {height} {material[0]} (retain {material[1]}), at most 400 ticks")]


def fresh_movement_candidates(observation: Observation, goal: Goal | None = None) -> list[Candidate]:
    walks = movement_choices(observation, goal)
    fresh = [candidate for candidate in walks
             if candidate.candidate_id.endswith(":entrance") or
             [float(math.floor(v)) for v in candidate.params["path"][-1]] not in observation.visited]  # type: ignore
    # Every walk ends on visited ground (the foot of cut stairs, a pit): walking back out beats no choice at all.
    return fresh or walks


def toward_path(observation: Observation, routes: dict[tuple[int, int, int], list[list[float]]],
                centre: list[float]) -> list[list[float]] | None:
    """The observed walk that ends nearest to a point no route reaches, if it gets at least a block closer."""
    path = min((route for route in routes.values() if route), default=None,
               key=lambda route: (round(math.dist(route[-1], centre), 3), len(route), route))
    return path if path is not None and math.dist(path[-1], centre) <= math.dist(observation.position, centre) - 1 else None


def safe_ground(observation: Observation) -> bool:
    """Same observed conditions the bridge re-checks on every hold tick."""
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    x, y, z = map(math.floor, observation.position)
    floor, feet, head = (cells.get((x, y + offset, z)) for offset in (-1, 0, 1))
    return bool(observation.on_ground and not observation.in_liquid and not observation.on_fire
                and floor and floor.support and not floor.hazard and feet and feet.passable and head and head.passable
                and hazard_distance(cells.values(), observation.position) >= HAZARD_RADIUS)


def escape_candidates(observation: Observation) -> CandidateSet | None:
    """Inside the hazard radius every other macro stops at once: then only walks away, visited ground included."""
    if hazard_distance(observation.observed_map, observation.position) >= HAZARD_RADIUS:
        return None
    return generate_movement_candidates(observation)


STONE_STAIRS: int | None = None  # set by mc_diamond.exp --stone-stairs; None keeps every open direction (6 slots)
ORE_TOP = {"iron_ore": 63, "diamond_ore": 15}  # Highest generation layer in 1.16.5: range(64) and range(16).


def _ready(observation: Observation, walking: list[Candidate]) -> list[Candidate] | None:
    """Walking, or equipping a carried pickaxe as its own choice, until a cut is possible; None once it is."""
    if observation.in_liquid or observation.on_fire or not observation.remaining_ticks:
        return walking
    if not (observation.tool or "").endswith("_pickaxe"):
        pick = next((name for name in PICKS if observation.inventory.get(name)), None)
        return walking if pick is None else [Candidate(
            candidate_id=f"{observation.obs_id}:stair:equip", action_kind="place_or_equip", params={"item": pick},
            max_ticks=min(400, observation.remaining_ticks), stop_rule_id="stair_ore_or_hazard",
            source_obs_id=observation.obs_id, description=f"Equip {pick} for the stairs")]
    return None


def supports_way_back(observation: Observation, point: Iterable[float]) -> bool:
    """The block is the floor of a cell the agent has stood in: cutting it breaks the steps it came down by.

    Keep the existing return route even when an ascent alternative exists; its materials or tool may run out.
    The earlier experiment lost 3/10 untrained stone-pickaxe episodes after cutting their own way back.
    """
    x, y, z = point
    return [float(x), float(y) + 1, float(z)] in observation.visited


def _open(observation: Observation, stop_blocks: list[str], column: list[tuple[int, int, int]],
          floor: tuple[int, int, int]) -> bool:
    """Only an observed cell can veto a cut: a nearby hazard, an open floor, or a stop ore/bedrock in it.

    Whatever is still unseen is judged by the macro at the moment it is exposed, so this never depends on hidden terrain.
    """
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    hazards = [cell.position for cell in cells.values() if cell.hazard]
    if any(max(abs(a - b) for a, b in zip(point, hazard)) <= 1 for hazard in hazards for point in (*column, floor)):
        return False
    if any(supports_way_back(observation, point) for point in column):
        return False
    if any((above := cells.get((p[0], p[1] + 1, p[2]))) and above.block in {"sand", "red_sand", "gravel"}
           for p in column):
        return False
    if floor in cells and not cells[floor].support:
        return False
    return not any(point in cells and (cells[point].block in stop_blocks or cells[point].block == "bedrock")
                   for point in column)


def _facing_first(observation: Observation, directions: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    facing = (-math.sin(observation.yaw), -math.cos(observation.yaw))
    previous = (observation.last_cut or {}).get("direction")
    return sorted(directions, key=lambda d: (list(d) != previous,
                  -round(d[0] * facing[0] + d[1] * facing[1], 6),
                  -round(facing[0] * d[1] - facing[1] * d[0], 6), DIRECTIONS.index(d)))


def _stairs(observation: Observation, stop_blocks: list[str], stairs: int) -> tuple[list[Candidate], list[Candidate]]:
    """Every open direction at the full workload, then the single-stair workload."""
    if stairs < 1:
        return [], []
    x, y, z = map(math.floor, observation.position)
    directions = _facing_first(observation, (d for d in DIRECTIONS if _open(
        observation, stop_blocks, [(x + d[0], y + h, z + d[1]) for h in (1, 0, -1)], (x + d[0], y - 2, z + d[1]))))

    def stair(index: int, direction: tuple[int, int], count: int) -> Candidate:
        speed = {"wooden": 2, "stone": 4, "iron": 6, "diamond": 8, "netherite": 9, "golden": 12}.get(
            (observation.tool or "").split("_")[0], 1)
        estimate = min(400, observation.remaining_ticks, count * (3 * (math.ceil(45 / speed) + 1) + 20))
        return Candidate(
            candidate_id=f"{observation.obs_id}:stair:{index}", action_kind="stair_down",
            params={"direction": list(direction), "stairs": count, "stop_blocks": list(stop_blocks),
                    "map_version": observation.map_version},
            max_ticks=min(400, observation.remaining_ticks), stop_rule_id="stair_ore_or_hazard",
            source_obs_id=observation.obs_id, description=("Continue: " if observation.last_cut and
                observation.last_cut.get("kind") == "stair_down" and observation.last_cut.get("direction") == list(direction) else "") +
                f"Cut {count} stairs down toward {COMPASS[direction]} {list(direction)}: "
                f"dig from y={y} to y={y - count}, collecting what the cut blocks drop; "
                f"estimated {estimate} ticks assuming stone, capped at {min(400, observation.remaining_ticks)}; "
                "hazard, ore or tool failure stops earlier")

    directions = directions[:2]  # C1: representative directions, retain the short workload as a distinct cost.
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
        for direction in directions[:2 if height == 2 else 1]:
            found.append(Candidate(
                candidate_id=f"{observation.obs_id}:tunnel:{len(found)}", action_kind="tunnel",
                params={"direction": list(direction), "cells": cells, "height": height, "stop_blocks": list(stop_blocks),
                        "map_version": observation.map_version},
                max_ticks=min(400, observation.remaining_ticks), stop_rule_id="tunnel_ore_or_hazard",
                source_obs_id=observation.obs_id,
                description=("Continue: " if observation.last_cut and observation.last_cut.get("kind") == "tunnel"
                    and observation.last_cut.get("direction") == list(direction) else "") +
                            f"Tunnel {cells} cells 1x{height} toward {COMPASS[direction]} {list(direction)} at y={y}, "
                            f"collecting what the cut blocks drop"))
    return found


def descent_choices(observation: Observation) -> list[Candidate]:
    """Every open direction, then observed walking, then the smaller workload; `allocate` applies the cap."""
    y = math.floor(observation.position[1])
    walking = fresh_movement_candidates(observation)
    early = walking if y - SAFE_BAND[0] < 1 else _ready(observation, walking)
    if early is not None:
        return early
    broad, narrow = _stairs(observation, ["diamond_ore"], min(4, y - SAFE_BAND[0]))
    return [*broad, *walking, *narrow]


def ore_search_choices(observation: Observation, target: str, reserve: int, goal: Goal | None = None) -> list[Candidate]:
    """Stairs while above the ore's generation layers, then level tunnels; walking new ground stays a choice.

    No cut may spend the durability still needed to mine the remaining target ores (`reserve`).
    """
    y = math.floor(observation.position[1])
    walking = fresh_movement_candidates(observation, goal)
    early = _ready(observation, walking)
    if early is not None:
        return early
    stop_blocks = sorted({"diamond_ore", target})
    durability = (observation.tool_durability or 0) - reserve
    broad, narrow = _stairs(observation, stop_blocks, min(4, y - SAFE_BAND[0], durability // 3))
    tunnels = _tunnels(observation, stop_blocks, durability)
    if y > ORE_TOP[target]:
        return [*broad, *tunnels, *walking, *narrow]
    return [*walking[:4], *tunnels, *broad, *walking[4:], *narrow]  # Cutting stays a choice in open ground.


def stone_search_choices(observation: Observation, reserve: int, goal: Goal | None = None) -> list[Candidate]:
    """No exposed stone within reach: stairs down through the ground are a choice next to walking new ground.

    Same macro and observed-cell vetoes as the ore search; the cut never spends the durability the goal still needs.
    """
    walking = fresh_movement_candidates(observation, goal)
    early = _ready(observation, walking)
    if early is not None:
        return early
    y = math.floor(observation.position[1])
    durability = (observation.tool_durability or 0) - reserve
    broad, narrow = _stairs(observation, ["diamond_ore"], min(4, y - SAFE_BAND[0], durability // 3))
    if STONE_STAIRS is not None:  # experiment arm: directions are near-duplicates, so fewer of them and no 1-stair copies
        broad, narrow = broad[:STONE_STAIRS], []
    return [*broad, *walking, *narrow]


def target_cut(observation: Observation, goal: Goal, target: tuple[float, ...], reserve: int) -> Candidate | None:
    """One short cut toward a visible unreachable target; its direction need not be a generic search representative."""
    x, y, z = map(math.floor, observation.position)
    dx, dz = target[0] - x, target[2] - z
    direction = (1 if dx > 0 else -1, 0) if abs(dx) >= abs(dz) else (0, 1 if dz > 0 else -1)
    rise = -1 if target[1] < y else 1 if target[1] > y + 2 else 0
    stop = sorted({"diamond_ore", goal.target} & {"diamond_ore", "iron_ore"})
    height = 3 if rise else 2
    count = min(4 if rise else 8, max(1, int(abs(dx) + abs(dz)) - 1),
                ((observation.tool_durability or 0) - reserve) // (4 if rise > 0 else height))
    if rise < 0:
        count = min(count, y - SAFE_BAND[0])
    column = [(x + direction[0], y + h + rise, z + direction[1]) for h in range(height)]
    if count < 1 or not _open(observation, stop, column, (x + direction[0], y + rise - 1, z + direction[1])):
        return None
    params: dict[str, JsonValue] = {"direction": list(direction), "stop_blocks": list(stop), "map_version": observation.map_version,
        "target_position": list(target), "walking_path_available": False}
    params.update({"stairs": count} if rise else {"cells": count, "height": height})
    return Candidate.model_validate({"candidate_id": f"{observation.obs_id}:target-cut",
        "action_kind": "stair_up" if rise > 0 else "stair_down" if rise < 0 else "tunnel", "params": params,
        "max_ticks": min(400, observation.remaining_ticks), "source_obs_id": observation.obs_id,
        "stop_rule_id": "target_or_hazard", "description": f"Dig toward visible {goal.target} at {list(target)}; "
            f"no walking path, at most {count} cells, {count * (4 if rise > 0 else height)} tool uses / 400 ticks"})


def hold_candidate(observation: Observation) -> Candidate:
    """A 20-tick wait the bridge reports as `safe_hold` when the observed ground stays stable (descend, escape)."""
    return Candidate(candidate_id=f"{observation.obs_id}:hold", action_kind="wait", params={},
                     max_ticks=min(20, observation.remaining_ticks), stop_rule_id="hold_or_hazard",
                     source_obs_id=observation.obs_id, description="Hold observed safe ground for 20 ticks")


def generate_descent_candidates(observation: Observation) -> CandidateSet:
    choices = descent_choices(observation)
    if (observation.remaining_ticks and SAFE_BAND[0] <= math.floor(observation.position[1]) <= SAFE_BAND[1]
            and observation.inventory.get("iron_pickaxe") and safe_ground(observation)):
        choices = [hold_candidate(observation), *choices]
    return allocate(choices)
