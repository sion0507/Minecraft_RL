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
    assert saved.candidates[0].params["path"][-1][0] == 3.5  # type: ignore[index]  # the observed walk that ends nearest to it
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


def test_a_step_that_may_not_be_mined_is_not_walked_up_to_either() -> None:
    # T evaluation seed 15011: the only stone in view was two of its own steps, offered as approach after approach to the end.
    step = [{"block": "stone", "position": [2.0, 64.0, 0.0], "support": True}]
    saved = generate_resource_candidates(scene("dirt", step, visited=[[2.0, 65.0, 0.0]]), STONE)
    assert not any("[2.0, 64.0, 0.0]" in c.description for c in saved.candidates)
    assert any(c.action_kind == "stair_down" for c in saved.candidates)


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


def test_an_approach_that_ends_where_the_agent_already_stood_comes_with_the_cuts() -> None:
    # T iron evaluation slots 4 and 8: the ore was out of reach from the approach's end, and that walk was the only candidate.
    iron = Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=3)
    ore = [{"block": "iron_ore", "position": [2.0, 64.0, 0.0], "support": True}]
    tools = {"inventory": {"stone_pickaxe": 1}, "tool": "stone_pickaxe"}
    first = generate_resource_candidates(scene("dirt", ore, **tools), iron)
    assert {c.action_kind for c in first.candidates} == {"move_observed"}
    again = generate_resource_candidates(scene("dirt", ore, visited=[[1.0, 64.0, 0.0]], **tools), iron)
    assert any(c.description.startswith("Approach exposed iron_ore") for c in again.candidates)
    assert {"stair_down", "tunnel"} & {c.action_kind for c in again.candidates}


def test_two_block_ledge_has_a_scaffold_walk_and_pit_has_bounded_ascent() -> None:
    from mc_diamond.episode import policy_candidates
    ledge = [{"block": "stone", "position": [1.0, float(y), 0.0], "support": True} for y in (64, 65)]
    ledge += [{"block": "air", "position": [float(x), float(y), 0.0], "passable": True}
              for x in (0, 1) for y in range(66, 71)]
    observation = scene("dirt", ledge, inventory={"wooden_pickaxe": 1, "dirt": 4})
    saved = policy_candidates(observation, STONE, movement=True)
    walks = [c for c in saved.candidates if c.params.get("scaffold")]
    assert any(c.params["path"][-1] == [1.5, 66.0, 0.5] for c in walks)  # type: ignore[index]
    for c in walks:
        assert c.params["scaffold"] == {"item": "dirt", "reserve": 0}
        assert "block" in c.description
    ascent = policy_candidates(observation, STONE, macros=True)
    pillars = [c for c in ascent.candidates if c.action_kind == "pillar_up"]
    assert pillars and all(1 <= c.params["blocks"] <= 4 for c in pillars)  # type: ignore[operator]
    from mc_diamond.rule_selector import rule_select
    assert rule_select(observation, STONE, ascent, []).candidate_id in [c.candidate_id for c in ascent.candidates]


def test_visible_unreachable_ore_offers_one_targeted_cut_but_walkable_ore_never_does() -> None:
    iron = Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=3)
    ore = [{"block": "iron_ore", "position": [4.0, 64.0, 0.0], "support": True}]
    wall = [{"block": "stone", "position": [1.0, float(y), float(z)], "support": True}
            for y in range(64, 69) for z in range(-3, 4)]
    o = scene("dirt", [*ore, *wall], inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131)
    choices = generate_resource_candidates(o, iron).candidates
    cuts = [c for c in choices if "target_position" in c.params]
    assert len(cuts) == 1 and cuts[0].params["direction"] == [1, 0]
    assert cuts[0].params["walking_path_available"] is False
    assert any(c.action_kind == "move_observed" for c in choices)
    clear = scene("dirt", ore, inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131)
    assert not any("target_position" in c.params for c in generate_resource_candidates(clear, iron).candidates)


def test_descent_offers_explicit_crafting_table_recovery_and_remembered_return() -> None:
    from mc_diamond.episode import policy_candidates
    table = [{"block": "crafting_table", "position": [1.0, 64.0, 0.0], "support": True}]
    observation = scene("dirt", table, cut_entrances=[[-2.0, 64.0, 0.0]], visited=[[-2.0, 64.0, 0.0]])
    saved = policy_candidates(observation, STONE, macros=True)
    assert any(c.action_kind == "mine_visible_cluster" and c.params.get("block") == "crafting_table" for c in saved.candidates)
    assert any(c.description.startswith("Return toward") for c in saved.candidates)


def test_ascent_keeps_crafting_stock_and_shares_saved_ids_with_models_and_s() -> None:
    from mc_diamond.episode import policy_candidates
    from mc_diamond.model_input import choice_input
    from mc_diamond.rule_selector import rule_select
    wall = [{"block": "stone", "position": [1.0, float(y), 0.0], "support": True} for y in (64, 65)]
    air = [{"block": "air", "position": [0.0, float(y), 0.0], "passable": True} for y in range(66, 71)]
    o = scene("dirt", wall + air, inventory={"wooden_pickaxe": 1, "cobblestone": 3})
    saved = policy_candidates(o, STONE, macros=True)
    assert not any(c.action_kind == "pillar_up" or "scaffold" in c.params for c in saved.candidates)
    assert any(c.action_kind == "stair_up" for c in saved.candidates)
    shared = choice_input(o, STONE, saved)
    assert shared.candidate_ids == [c.candidate_id for c in saved.candidates]
    assert rule_select(o, STONE, saved, []).candidate_id in shared.candidate_ids
    assert saved.generated == len(saved.candidates) + sum(saved.truncated.values())


def test_continuation_is_explicit_without_increasing_the_cut_limit() -> None:
    o = scene("dirt", [], remaining_ticks=3600, last_cut={"kind": "stair_down", "direction": [1, 0], "position": [0, 64, 0]})
    saved = generate_resource_candidates(o, STONE)
    first = saved.candidates[0]
    assert first.description.startswith("Continue:") and first.params["direction"] == [1, 0]
    assert first.params["stairs"] == 4 and first.max_ticks == 400


def test_target_cut_never_spends_durability_reserved_for_the_ore() -> None:
    ore = [{"block": "iron_ore", "position": [4.0, 64.0, 0.0], "support": True}]
    wall = [{"block": "stone", "position": [1.0, float(y), float(z)], "support": True}
            for y in range(64, 69) for z in range(-3, 4)]
    o = scene("dirt", ore + wall, inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=1)
    saved = generate_resource_candidates(o, Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=3))
    assert not any("target_position" in c.params for c in saved.candidates)


def test_targeted_cut_replaces_the_same_generic_execution_choice() -> None:
    wall = [{"block": "stone", "position": [1.0, float(y), float(z)], "support": True}
            for y in range(64, 69) for z in range(-3, 4)]
    ore = [{"block": "iron_ore", "position": [5.0, 60.0, 0.0], "support": True}]
    o = scene("dirt", wall + ore, inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131)
    saved = generate_resource_candidates(o, Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=3))
    signatures = [json.dumps([c.action_kind, {k: v for k, v in c.params.items()
        if k not in {"target_position", "walking_path_available"}}, c.max_ticks], sort_keys=True) for c in saved.candidates]
    assert len(signatures) == len(set(signatures))


def test_targeted_descent_preserves_the_lowest_safe_band() -> None:
    wall = [{"block": "stone", "position": [1.0, float(y), float(z)], "support": True}
            for y in range(64, 69) for z in range(-3, 4)]
    ore = [{"block": "diamond_ore", "position": [5.0, 60.0, 0.0], "support": True}]
    o = scene("dirt", wall + ore, inventory={"iron_pickaxe": 1}, tool="iron_pickaxe", tool_durability=250)
    o = o.model_copy(update={"position": [0.5, 6.0, 0.5], "observed_map": [
        c.model_copy(update={"position": [c.position[0], c.position[1] - 58, c.position[2]]}) for c in o.observed_map]})
    saved = generate_resource_candidates(o, Goal(goal_id="diamond", kind="mine_diamond", target="diamond", quantity=1))
    cuts = [c for c in saved.candidates if "target_position" in c.params]
    assert cuts and all(c.params["stairs"] == 1 for c in cuts), "from y6 no cut may descend below y5"


def test_walkable_high_or_diagonal_ore_is_approached_without_cutting() -> None:
    for target in ([4.0, 68.0, 0.0], [4.0, 64.0, 4.0]):
        ore = [{"block": "iron_ore", "position": target, "support": True}]
        o = scene("dirt", ore, inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131)
        saved = generate_resource_candidates(o, Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=3))
        assert saved.candidates and all(c.action_kind == "move_observed" for c in saved.candidates), target
