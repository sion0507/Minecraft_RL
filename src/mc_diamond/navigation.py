"""Conservative level walking over directly observed clearance and full supports."""

import math
from collections import deque

from .schema import Candidate, CandidateSet, Observation


def observed_routes(observation: Observation) -> dict[tuple[int, int, int], list[list[float]]]:
    cells = {tuple(cell.position): cell for cell in observation.observed_map}
    sx, sy, sz = map(math.floor, observation.position)
    start = (sx, sy, sz)
    queue: deque[tuple[tuple[int, int, int], list[list[float]]]] = deque([(start, [])])
    routes: dict[tuple[int, int, int], list[list[float]]] = {start: []}
    while queue:
        (x, y, z), route = queue.popleft()
        if len(route) >= 16:
            continue
        for dx, dz in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            point = (x + dx, y, z + dz)
            if point in routes:
                continue
            floor = cells.get((point[0], y - 1, point[2]))
            feet = cells.get(point)
            head = cells.get((point[0], y + 1, point[2]))
            if not (floor and floor.support and not floor.hazard and feet and feet.passable
                    and not feet.hazard and head and head.passable and not head.hazard):
                continue
            path = [*route, [point[0] + 0.5, float(y), point[2] + 0.5]]
            routes[point] = path
            queue.append((point, path))
    return routes


def generate_movement_candidates(observation: Observation) -> CandidateSet:
    sx, _, sz = map(math.floor, observation.position)
    directions: dict[tuple[int, int], list[list[float]]] = {}
    for (x, _, z), path in observed_routes(observation).items():
        if path:
            directions[((x > sx) - (x < sx), (z > sz) - (z < sz))] = path
    candidates = [Candidate(
        candidate_id=f"{observation.obs_id}:move:{index}", action_kind="move_observed",
        params={"path": [[value for value in point] for point in route], "map_version": observation.map_version},
        max_ticks=min(400, observation.remaining_ticks), stop_rule_id="observed_path_or_hazard",
        source_obs_id=observation.obs_id, description=f"Walk over observed cells to {route[-1]}",
    ) for index, route in enumerate(directions.values()) if observation.remaining_ticks]
    return CandidateSet(candidates=candidates, mask=[True] * len(candidates))
