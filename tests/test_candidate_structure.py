"""exp/candidate-structure: what a collect decision offers (stairs for stone, walks toward far targets, no approach flood)."""

import json
from pathlib import Path
from typing import Any

from mc_diamond.macros import APPROACHES_WHEN_MINEABLE, generate_resource_candidates
from mc_diamond.schema import Goal, Observation

STONE = Goal(goal_id="stone", kind="collect", target="cobblestone", quantity=3)


def scene(floor: str, extra: list[dict[str, Any]], **update: Any) -> Observation:
    base = json.loads(Path("fixtures/mock_episode.json").read_text())["initial"]
    ground = [{"block": floor, "position": [float(x), 63.0, float(z)], "support": True} for x in range(-3, 4) for z in range(-3, 4)]
    air = [{"block": "air", "position": [float(x), float(y), float(z)], "passable": True}
           for x in range(-3, 4) for y in (64, 65) for z in range(-3, 4)]
    return Observation.model_validate({**base, "position": [0.5, 64.0, 0.5], "observed_map": ground + air + extra, "visited": [],
                                       "inventory": {"wooden_pickaxe": 1}, "tool": "wooden_pickaxe", "tool_durability": 59, **update})


def test_no_stone_in_view_offers_stairs_down_next_to_walks() -> None:
    kinds = [c.action_kind for c in generate_resource_candidates(scene("dirt", []), STONE).candidates]
    assert "stair_down" in kinds and "move_observed" in kinds


def test_unequipped_pickaxe_is_equipped_before_any_cut() -> None:
    saved = generate_resource_candidates(scene("dirt", [], tool=None, tool_durability=None), STONE)
    assert [c.action_kind for c in saved.candidates] == ["place_or_equip"]


def test_stone_seen_beyond_every_route_offers_a_walk_toward_it_first() -> None:
    far = [{"block": "stone", "position": [28.0, 64.0, 0.0], "support": True}]
    saved = generate_resource_candidates(scene("dirt", far), STONE)
    assert saved.candidates[0].description.startswith("Walk toward exposed cobblestone at [28.0, 64.0, 0.0]: 28 blocks away now")
    assert saved.candidates[0].params["path"][-1][0] == 3.5  # the observed walk that ends nearest to it
    assert any(c.action_kind == "stair_down" for c in saved.candidates)


def test_standing_on_stone_keeps_mining_from_being_buried_under_approaches() -> None:
    wall = [{"block": "stone", "position": [1.0, 64.0, 0.0], "support": True}]
    saved = generate_resource_candidates(scene("stone", wall), STONE)
    kinds = [c.action_kind for c in saved.candidates]
    assert kinds.count("mine_visible_cluster") >= 1
    assert kinds.count("move_observed") <= APPROACHES_WHEN_MINEABLE


def test_foot_of_a_shaft_with_only_visited_ground_still_offers_the_walk_back() -> None:
    visited = [[float(x), 64.0, float(z)] for x in range(-3, 4) for z in range(-3, 4)]
    saved = generate_resource_candidates(scene("dirt", [], visited=visited, tool_durability=3), STONE)
    assert saved.candidates and all(c.action_kind == "move_observed" for c in saved.candidates)


def test_remembered_crafting_table_beyond_every_route_offers_walking_back_toward_it() -> None:
    from mc_diamond.production import generate_production_candidates
    table = [{"block": "crafting_table", "position": [28.0, 64.0, 0.0], "support": True, "visible": False}]
    observation = scene("dirt", table, inventory={"cobblestone": 3, "stick": 2, "wooden_pickaxe": 1})
    saved = generate_production_candidates(observation, Goal(goal_id="pick", kind="craft", target="stone_pickaxe", quantity=1))
    assert saved.candidates[0].description.startswith("Walk toward remembered crafting_table at [28.0, 64.0, 0.0]: 28 blocks away now")


def test_the_step_the_agent_came_down_by_is_neither_mined_nor_cut_under() -> None:
    step = [{"block": "stone", "position": [1.0, 64.0, 0.0], "support": True}]
    came_from = scene("stone", step, visited=[[1.0, 65.0, 0.0], [0.0, 64.0, 0.0]])
    assert not any(c.action_kind == "mine_visible_cluster" for c in generate_resource_candidates(came_from, STONE).candidates)
    under = scene("dirt", [], visited=[[1.0, 64.0, 0.0], [0.0, 64.0, 0.0]])  # east column's y=63 floors a visited cell
    stairs = [c for c in generate_resource_candidates(under, STONE).candidates if c.action_kind == "stair_down"]
    assert stairs and [1, 0] not in [c.params["direction"] for c in stairs]


def test_pilot_tick_cost_prices_every_active_tick_and_default_keeps_the_plan_rate() -> None:
    from mc_diamond.rewards import RewardLedger
    from mc_diamond.schema import StepResult
    start = scene("dirt", [], objective_kind="local", active_ticks=0, remaining_ticks=1800)
    after = start.model_copy(update={"obs_id": "obs-next", "active_ticks": 120, "remaining_ticks": 1680})
    step = StepResult.model_validate({"observation": after, "actual_ticks": 120, "events": [], "terminated": False,
        "truncated": False, "invalid": False, "reason": "wait_completed", "clock_mode": "mock", "pause_verified": False,
        "stable_boundary": True, "wall_seconds": 0.0})
    craft = Goal(goal_id="pick", kind="craft", target="stone_pickaxe", quantity=1)
    priced = RewardLedger(start, pilot_signal=True, tick_cost=1 / 1200).compute(start, craft, step, goal_completed=False)
    plain = RewardLedger(start, pilot_signal=True).compute(start, craft, step, goal_completed=False)
    assert abs(priced.components["time"] + 0.1) < 1e-9 and abs(plain.components["time"] + 0.1 * 120 / 1800) < 1e-9


def test_carried_crafting_table_with_no_cell_to_put_it_on_offers_walks_instead_of_nothing() -> None:
    from mc_diamond.production import generate_production_candidates
    span = [(float(x), float(z)) for x in range(-3, 4) for z in range(-3, 4)]
    pit = ([{"block": "dirt", "position": [x, 63.0, z], "support": True} for x, z in span]
           + [{"block": "stone", "position": [x, 64.0, z], "support": True} for x, z in span if (x, z) != (0, 0)]
           + [{"block": "air", "position": [0.0, 64.0, 0.0], "passable": True}]
           + [{"block": "air", "position": [x, y, z], "passable": True} for x, z in span for y in (65.0, 66.0, 67.0)])
    observation = scene("dirt", [], observed_map=pit, inventory={"cobblestone": 3, "stick": 2, "wooden_pickaxe": 1, "crafting_table": 1})
    saved = generate_production_candidates(observation, Goal(goal_id="pick", kind="craft", target="stone_pickaxe", quantity=1))
    assert saved.candidates and all(c.action_kind == "move_observed" for c in saved.candidates)


def test_stone_stair_cap_keeps_the_first_directions_at_full_depth_only(monkeypatch: Any) -> None:
    from mc_diamond import navigation
    full = [c for c in generate_resource_candidates(scene("dirt", []), STONE).candidates if c.action_kind == "stair_down"]
    monkeypatch.setattr(navigation, "STONE_STAIRS", 2)
    capped = [c for c in generate_resource_candidates(scene("dirt", []), STONE).candidates if c.action_kind == "stair_down"]
    assert len(full) > 2 and [c.params["stairs"] for c in capped] == [4, 4]
