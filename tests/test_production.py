"""T05 behavior through the agreed public smoke-macros boundary."""

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml
import pytest


def run_production(tmp_path: Path, fixture: dict[str, Any], *, target: str = "iron_pickaxe",
                   kind: str = "craft", quantity: int = 1) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    fixture_path = tmp_path / "production.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    config = {"backend": "mock", "fixture": str(fixture_path), "max_decisions": 8, "rpc_timeout_seconds": 180,
              "goal": {"goal_id": "production", "kind": kind, "target": target, "quantity": quantity}}
    config_path = tmp_path / "production.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(config_path)],
                            capture_output=True, text=True, timeout=15)
    return result, [json.loads(line) for line in result.stdout.splitlines()]


def production_fixture() -> dict[str, Any]:
    fixture: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text())
    initial = fixture["initial"]
    initial.update(inventory={"iron_ingot": 3, "stick": 2}, remaining_ticks=12000, position=[0.5, 64.0, 0.5],
                   observed_map=[{"block": "crafting_table", "position": [1.0, 64.0, 0.0], "support": True}])
    step = fixture["steps"][0]
    step.update(actual_ticks=5, terminated=False, reason="craft_completed", source_obs_id="obs-0",
                stop_evidence=["obs-1", "craft_completed"],
                events=[{"kind": "crafted", "item": "iron_pickaxe", "quantity": 1, "source": "mock", "event_id": "craft-1"}])
    step["observation"].update(active_ticks=5, remaining_ticks=initial["remaining_ticks"] - 5,
                               inventory={"iron_pickaxe": 1}, observed_map=initial["observed_map"])
    return fixture


def test_cli_crafts_iron_pickaxe_as_one_selected_recipe_with_direct_evidence(tmp_path: Path) -> None:
    result, output = run_production(tmp_path, production_fixture())
    assert result.returncode == 0, result.stderr
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    candidate = saved["candidates"][0]
    assert candidate["action_kind"] == "craft_batch"
    assert candidate["params"] == {"item": "iron_pickaxe", "quantity": 1, "table": [1.0, 64.0, 0.0]}
    assert candidate["max_ticks"] == 400
    assert saved["mask"] == [True]
    summary = output[-1]["data"]
    assert summary["goal_completed"] is True and summary["diamond_success"] is False
    assert summary["provided_inventory"] == {"iron_ingot": 3, "stick": 2}
    assert summary["direct_crafted"] == {"iron_pickaxe": 1}
    assert summary["active_ticks"] == 5 and summary["actor_transitions"] == 0


def test_shipping_bridge_production_contract() -> None:
    result = subprocess.run(["node", "fixtures/production_macros.cjs"], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}


@pytest.mark.parametrize("stock, cells, kind, params", [
    ({"crafting_table": 1, "iron_ingot": 3, "stick": 2}, [], "place_or_equip", {"item": "crafting_table"}),
    ({"oak_log": 2}, [], "craft_batch", {"item": "oak_planks", "quantity": 4, "table": None}),
    ({"stone_pickaxe": 1}, [{"block": "iron_ore", "position": [1.0, 64.0, 0.0], "support": True}],
     "place_or_equip", {"item": "stone_pickaxe"}),
])
def test_cli_resolves_one_observable_prerequisite_at_a_time(tmp_path: Path, stock: dict[str, int],
        cells: list[dict[str, Any]], kind: str, params: dict[str, Any]) -> None:
    fixture = production_fixture()
    fixture["initial"].update(inventory=stock, observed_map=cells + [
        {"block": "air", "position": [2.0, 64.0, 0.0], "passable": True},
        {"block": "stone", "position": [2.0, 63.0, 0.0], "support": True}])
    result, output = run_production(tmp_path, fixture,
                                   target="iron_ore" if "stone_pickaxe" in stock else "iron_pickaxe",
                                   kind="collect" if "stone_pickaxe" in stock else "craft")
    candidates = next(row["data"] for row in output if row["type"] == "candidates")["candidates"]
    assert candidates, result.stdout + result.stderr
    assert candidates[0]["action_kind"] == kind
    assert all(candidates[0]["params"][key] == value for key, value in params.items())
    assert all(candidate["action_kind"] not in {"tunnel", "stair_down"} for candidate in candidates)


def test_cli_keeps_gathering_materials_when_table_is_temporarily_occluded(tmp_path: Path) -> None:
    fixture = production_fixture()
    fixture["initial"].update(inventory={"wooden_pickaxe": 1}, tool="wooden_pickaxe", observed_map=[
        {"block": "crafting_table", "position": [3.0, 64.0, 0.0], "visible": False, "support": True},
        {"block": "stone", "position": [1.0, 64.0, 0.0], "support": True}])
    _, output = run_production(tmp_path, fixture, target="furnace")
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    assert saved["candidates"][0]["action_kind"] == "mine_visible_cluster"
    assert saved["candidates"][0]["params"]["block"] == "stone"


def test_cli_approaches_remembered_table_instead_of_crafting_another(tmp_path: Path) -> None:
    fixture = production_fixture()
    fixture["initial"]["observed_map"] = [
        {"block": "crafting_table", "position": [3.0, 64.0, 0.0], "visible": False, "support": True},
        *[{"block": block, "position": [float(x), float(y), 0.0], "passable": block == "air", "support": block == "stone"}
          for x in range(3) for y, block in [(63, "stone"), (64, "air"), (65, "air")]]]
    _, output = run_production(tmp_path, fixture)
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    assert saved["candidates"][0]["action_kind"] == "move_observed"
    assert "crafting_table" in saved["candidates"][0]["description"]


def test_cli_collect_goal_uses_total_stock_but_requires_new_direct_progress(tmp_path: Path) -> None:
    fixture = production_fixture()
    fixture["initial"].update(inventory={"stone_pickaxe": 1, "iron_ore": 2}, tool="stone_pickaxe",
        observed_map=[{"block": "iron_ore", "position": [1.0, 64.0, 0.0], "support": True}])
    step = fixture["steps"][0]
    step.update(reason="cluster_completed", stop_evidence=["obs-1", "cluster_completed"],
        events=[{"kind": "acquired", "item": "iron_ore", "quantity": 1, "source": "mock", "event_id": "ore-1"}])
    step["observation"]["inventory"] = {"stone_pickaxe": 1, "iron_ore": 3}
    result, output = run_production(tmp_path, fixture, target="iron_ore", kind="collect", quantity=3)
    assert result.returncode == 0, result.stdout + result.stderr
    summary = output[-1]["data"]
    assert summary["goal_completed"] and summary["direct_acquired"] == {"iron_ore": 1}
    assert summary["provided_inventory"]["iron_ore"] == 2


def test_cli_uses_supported_non_oak_logs_for_furnace_fuel(tmp_path: Path) -> None:
    fixture = production_fixture()
    fixture["initial"].update(inventory={"iron_ore": 3, "birch_log": 2},
        observed_map=[{"block": "furnace", "position": [1.0, 64.0, 0.0], "support": True}])
    _, output = run_production(tmp_path, fixture, target="iron_ingot", kind="smelt", quantity=3)
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    assert saved["candidates"], "Available birch logs should become furnace fuel"
    assert saved["candidates"][0]["params"] == {"item": "birch_planks", "quantity": 4, "table": None}


def test_cli_explores_unvisited_routes_when_farthest_endpoint_was_visited(tmp_path: Path) -> None:
    fixture = production_fixture()
    fixture["initial"].update(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe",
        visited=[[0.0, 64.0, 0.0], [4.0, 64.0, 0.0]], observed_map=[
            {"block": block, "position": [float(x), float(y), 0.0],
             "passable": block == "air", "support": block == "stone"}
            for x in range(5) for y, block in [(63, "stone"), (64, "air"), (65, "air")]])
    _, output = run_production(tmp_path, fixture, target="iron_ore", kind="collect", quantity=3)
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    moves = [c for c in saved["candidates"] if c["action_kind"] == "move_observed"]
    assert moves, "A visited endpoint must not hide other unexplored routes"
    assert all([float(int(v // 1)) for v in c["params"]["path"][-1]] not in fixture["initial"]["visited"] for c in moves)
