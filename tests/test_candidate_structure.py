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
