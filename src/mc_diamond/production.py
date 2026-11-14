"""Individual production candidates; every prerequisite remains a separate choice."""

import json
import math
from importlib.resources import files
from typing import Any, Literal

from pydantic import JsonValue

from .macros import generate_resource_candidates
from .navigation import PICKS, generate_movement_candidates, observed_routes, toward_path
from .schema import Candidate, CandidateSet, Goal, Observation, allocate

RECIPES: list[dict[str, Any]] = json.loads(files("mc_diamond").joinpath("recipes.json").read_text())
FUELS = {"coal": 1600, "charcoal": 1600, **{r["item"]: 300 for r in RECIPES if r["item"].endswith("_planks")}}


def generate_production_candidates(observation: Observation, goal: Goal) -> CandidateSet:
    stock = observation.inventory
    if not observation.remaining_ticks or stock.get(goal.target, 0) >= goal.quantity:
        return allocate([])
    eye = [observation.position[0], observation.position[1] + 1.62, observation.position[2]]
    cells = {tuple(c.position): c for c in observation.observed_map}

    def choice(kind: Literal["craft_batch", "furnace_load", "furnace_collect", "place_or_equip", "wait", "move_observed"],
               params: dict[str, JsonValue], description: str) -> CandidateSet:
        candidate = Candidate(candidate_id=f"{observation.obs_id}:production:0", action_kind=kind,
            params=params, max_ticks=min(200 if kind == "wait" else 400, observation.remaining_ticks),
            stop_rule_id="production_or_hazard", source_obs_id=observation.obs_id, description=description)
        return allocate([candidate])

    def facilities(item: str) -> list[list[float]]:
        return sorted([c.position for c in cells.values() if c.block == item],
                      key=lambda p: (math.dist([v + 0.5 for v in p], eye), p))

    def nearby(item: str) -> list[float] | None:
        return next((p for p in facilities(item) if cells[tuple(p)].visible
                     and math.dist([v + 0.5 for v in p], eye) <= 4.5), None)

    def facility(item: str) -> CandidateSet:
        if stock.get(item, 0):
            sites = [c.position for c in cells.values() if c.visible and c.block == "air" and c.passable
                     and c.position[1] == math.floor(observation.position[1])
                     and not (abs(c.position[0] + 0.5 - observation.position[0]) < 0.8
                              and abs(c.position[2] + 0.5 - observation.position[2]) < 0.8)
                     and (floor := cells.get((c.position[0], c.position[1] - 1, c.position[2]))) is not None
                     and floor.visible and floor.support and not floor.hazard
                     and math.dist([v + 0.5 for v in c.position], eye) <= 4.5]
            if sites:
                point = min(sites, key=lambda p: (math.dist(p, observation.position), p))
                return choice("place_or_equip", {"item": item, "position": [v for v in point],
                    "map_version": observation.map_version}, f"Place {item} on observed support")
            # Carried but no free cell to put it on (the foot of a cut staircase): walking on is the way to one,
            # never forced waits to the end of the budget (exp/candidate-structure, arm T training episode 49).
            return generate_movement_candidates(observation)
        if facilities(item):
            routes = [path for point, path in observed_routes(observation).items() if path and
                      any(math.dist([v + 0.5 for v in p], [point[0] + 0.5, point[1] + 1.62, point[2] + 0.5]) <= 2
                          for p in facilities(item))]
            if routes:
                route = min(routes, key=lambda p: (len(p), p))
                return choice("move_observed", {"path": [[v for v in p] for p in route],
                    "map_version": observation.map_version}, f"Approach observed {item}")
            # Remembered but beyond every observed route (left behind after digging down or walking far): walking back
            # toward it and making another one are both ways on, never a dead end of forced waits (exp/candidate-structure).
            all_routes = observed_routes(observation)
            again = resolve(item, 1).candidates
            for point in facilities(item):
                centre = [v + 0.5 for v in point]
                path = toward_path(observation, all_routes, centre)
                if path is not None:
                    back = Candidate(candidate_id=f"{observation.obs_id}:production:toward", action_kind="move_observed",
                        params={"path": [[v for v in p] for p in path], "map_version": observation.map_version},
                        max_ticks=min(400, observation.remaining_ticks), stop_rule_id="production_or_hazard",
                        source_obs_id=observation.obs_id,
                        description=f"Walk toward remembered {item} at {point}: {math.dist(observation.position, centre):.0f} "
                                    f"blocks away now, {math.dist(path[-1], centre):.0f} after these {len(path)} steps")
                    return allocate([back, *again])
            return allocate(again or generate_movement_candidates(observation).candidates)
        return resolve(item, 1)

    def resolve(item: str, quantity: int) -> CandidateSet:
        missing = quantity - stock.get(item, 0)
        if missing <= 0:
            return allocate([])
        recipes = [r for r in RECIPES if r["item"] == item]
        if recipes:
            recipe = min(recipes, key=lambda r: sum(max(0, n - stock.get(name, 0) -
                (stock.get(name.replace("_planks", "_log"), 0) * 4 if name.endswith("_planks") else 0))
                for name, n in r["ingredients"].items()))
            quantity = min(8, math.ceil(missing / recipe["count"]) * recipe["count"])
            repeats = quantity // recipe["count"]
            for name, count in recipe["ingredients"].items():
                if stock.get(name, 0) < count * repeats:
                    return resolve(name, count * repeats)
            table = nearby("crafting_table") if recipe["table"] else None
            if recipe["table"] and table is None:
                return facility("crafting_table")
            return choice("craft_batch", {"item": item, "quantity": quantity,
                "table": [v for v in table] if table else None}, f"Craft {quantity} {item}")
        if item == "iron_ingot":
            point = nearby("furnace")
            if point is None:
                return facility("furnace")
            known = next((f for f in observation.furnaces if f.position == point), None)
            if known and known.output_count:
                return choice("furnace_collect", {"position": [v for v in point], "quantity": min(8, missing, known.output_count),
                    "map_version": observation.map_version}, "Collect selected furnace output")
            if known and known.input_count:
                if observation.active_ticks - known.last_observed_tick >= 200:
                    return choice("furnace_collect", {"position": [v for v in point], "quantity": min(8, missing),
                        "map_version": observation.map_version}, "Inspect and collect selected furnace output")
                return choice("wait", {}, "Wait for previously observed furnace input")
            amount = min(8, missing)
            if stock.get("iron_ore", 0) < amount:
                return resolve("iron_ore", amount)
            fuel = next((name for name, ticks in FUELS.items() if stock.get(name, 0) >= math.ceil(amount * 200 / ticks)), None)
            if fuel is None:
                plank = max((name for name in FUELS if name.endswith("_planks")),
                            key=lambda name: stock.get(name, 0) + 4 * stock.get(name.replace("_planks", "_log"), 0)
                            + 4 * sum(c.visible and c.block == name.replace("_planks", "_log") for c in cells.values()))
                return resolve(plank, math.ceil(amount * 200 / 300))
            return choice("furnace_load", {"position": [v for v in point], "item": "iron_ore", "quantity": amount,
                "fuel": fuel, "fuel_quantity": math.ceil(amount * 200 / FUELS[fuel]),
                "map_version": observation.map_version}, "Load only selected furnace input and fuel")
        if item in {"cobblestone", "iron_ore"}:
            tools = PICKS if item == "cobblestone" else PICKS[:4]
            if not any(stock.get(tool, 0) for tool in tools):
                return resolve("wooden_pickaxe" if item == "cobblestone" else "stone_pickaxe", 1)
        return generate_resource_candidates(observation, Goal(goal_id=goal.goal_id, kind="collect", target=item, quantity=quantity))

    return resolve(goal.target, goal.quantity)
