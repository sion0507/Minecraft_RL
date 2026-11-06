"""T06 behavior through the public smoke-macros boundary and the shipping bridge."""

import json
import math
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml


def cell(block: str, x: int, y: int, z: int, **flags: bool) -> dict[str, Any]:
    return {"block": block, "position": [float(x), float(y), float(z)], **flags}


def ground(y: int = 64) -> list[dict[str, Any]]:
    """Observed standing cell at the origin; the surrounding rock is still unseen."""
    return [cell("stone", 0, y - 1, 0, support=True), cell("air", 0, y, 0, passable=True),
            cell("air", 0, y + 1, 0, passable=True)]


def run(tmp_path: Path, initial: dict[str, Any], steps: list[dict[str, Any]],
        goal: dict[str, Any] | None = None) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    fixture: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text())
    fixture["initial"].update(initial)
    template = fixture["steps"][0]
    fixture["steps"] = [{**template, **step, "observation": {**fixture["initial"], "obs_id": f"obs-{index + 1}", **step["observation"]}}
                        for index, step in enumerate(steps)]
    path = tmp_path / "descent.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    config = {"backend": "mock", "fixture": str(path), "max_decisions": len(steps) or 1, "rpc_timeout_seconds": 5,
              "goal": goal or {"goal_id": "g3", "kind": "descend", "target": "safe_mining_zone", "quantity": 1}}
    config_path = tmp_path / "descent.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(config_path)],
                            capture_output=True, text=True, timeout=15)
    return result, [json.loads(line) for line in result.stdout.splitlines()]


def first_candidates(output: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = next(row["data"] for row in output if row["type"] == "candidates")["candidates"]
    return candidates


def surface(**update: Any) -> dict[str, Any]:
    state = {"inventory": {"iron_pickaxe": 1}, "tool": "iron_pickaxe", "position": [0.5, 64.0, 0.5], "yaw": math.pi,
             "on_ground": True, "remaining_ticks": 18000, "observed_map": ground()}
    return {**state, **update}


def stop_step(**update: Any) -> dict[str, Any]:
    step = {"actual_ticks": 40, "source_obs_id": "obs-0", "reason": "stairs_completed", "terminated": False,
            "stop_evidence": ["obs-1", "stairs_completed"], "stable_boundary": True,
            "events": [{"kind": "descended", "quantity": 1, "source": "mock", "event_id": "stair-1"}],
            "observation": {"active_ticks": 40, "remaining_ticks": 17960}}
    return {**step, **update}


def directions(candidates: list[dict[str, Any]]) -> list[list[int]]:
    return [c["params"]["direction"] for c in candidates if c["action_kind"] == "stair_down" and c["params"]["stairs"] == 4]


def test_cli_offers_each_direction_facing_first_with_two_workloads_and_saves_the_stop_rule(tmp_path: Path) -> None:
    _, output = run(tmp_path, surface(), [stop_step()])
    candidates = first_candidates(output)
    assert directions(candidates)[0] == [0, 1], "yaw pi faces south, so continuing is the first choice"
    assert sorted(map(tuple, directions(candidates))) == [(-1, 0), (0, -1), (0, 1), (1, 0)]
    assert len(candidates) == 8
    assert {c["params"]["stairs"] for c in candidates} == {1, 4}
    assert all(c["params"]["stop_blocks"] == ["diamond_ore"] and c["max_ticks"] == 400 for c in candidates)
    assert all(c["params"]["map_version"] == 0 for c in candidates)


@pytest.mark.parametrize("veto", [
    cell("lava", 1, 65, 0, hazard=True), cell("water", 1, 62, 0, hazard=True), cell("lava", 2, 64, 1, hazard=True),
    cell("air", 1, 62, 0, passable=True), cell("bedrock", 1, 63, 0, support=True), cell("diamond_ore", 1, 64, 0, support=True),
], ids=["lava-in-corridor", "water-floor", "lava-beside", "open-floor", "bedrock", "stop-ore"])
def test_cli_only_an_observed_cell_can_veto_a_direction(tmp_path: Path, veto: dict[str, Any]) -> None:
    _, output = run(tmp_path, surface(observed_map=[*ground(), veto]), [stop_step()])
    candidates = first_candidates(output)
    assert [1, 0] not in directions(candidates)
    assert [-1, 0] in directions(candidates), "the opposite side stays open"


def test_cli_never_digs_below_the_lowest_safe_band(tmp_path: Path) -> None:
    _, output = run(tmp_path, surface(position=[0.5, 7.0, 0.5], observed_map=ground(7)), [stop_step()])
    assert {c["params"]["stairs"] for c in first_candidates(output) if c["action_kind"] == "stair_down"} == {1, 2}
    _, output = run(tmp_path, surface(position=[0.5, 5.0, 0.5], observed_map=ground(5)), [stop_step()])
    assert [c for c in first_candidates(output) if c["action_kind"] == "stair_down"] == []


def test_cli_equips_a_carried_pickaxe_as_its_own_choice(tmp_path: Path) -> None:
    _, output = run(tmp_path, surface(tool=None), [stop_step()])
    candidates = first_candidates(output)
    assert [(c["action_kind"], c["params"]) for c in candidates] == [("place_or_equip", {"item": "iron_pickaxe"})]


def test_cli_walks_observed_cells_when_every_direction_is_vetoed(tmp_path: Path) -> None:
    room = [cell("stone", x, 63, z, support=True) for x in range(-2, 3) for z in range(-2, 3)]
    room += [cell("air", x, y, z, passable=True) for x in range(-2, 3) for y in (64, 65) for z in range(-2, 3)]
    pit = [cell("air", x, 62, z, passable=True) for x, z in [(1, 0), (0, 1), (-1, 0), (0, -1)]]
    _, output = run(tmp_path, surface(observed_map=room + pit), [stop_step()])
    candidates = first_candidates(output)
    assert candidates and {c["action_kind"] for c in candidates} == {"move_observed"}


HOLD = stop_step(actual_ticks=20, reason="wait_completed", stop_evidence=["obs-1", "wait_completed"],
                 events=[{"kind": "wait", "source": "mock", "event_id": "wait-1"},
                         {"kind": "safe_hold", "quantity": 20, "source": "mock", "event_id": "hold-1"}],
                 observation={"active_ticks": 20, "remaining_ticks": 17980})


def zone(**update: Any) -> dict[str, Any]:
    return surface(position=[0.5, 12.0, 0.5], observed_map=ground(12), **update)


def test_cli_completes_descend_from_a_real_hold_in_the_safe_band(tmp_path: Path) -> None:
    result, output = run(tmp_path, zone(), [HOLD])
    assert result.returncode == 0, result.stderr
    candidates = first_candidates(output)
    assert candidates[0]["action_kind"] == "wait" and candidates[0]["max_ticks"] == 20
    assert any(c["action_kind"] == "stair_down" for c in candidates), "continuing stays a choice"
    summary = output[-1]["data"]
    assert summary["goal_completed"] is True and summary["reason"] == "goal_completed"
    assert summary["active_ticks"] == 20 and summary["diamond_success"] is False


@pytest.mark.parametrize("step", [
    {**HOLD, "events": [{"kind": "wait", "source": "mock", "event_id": "wait-1"}]},
    {**HOLD, "events": [{"kind": "safe_hold", "quantity": 19, "source": "mock", "event_id": "hold-1"}]},
    {**HOLD, "stable_boundary": False},
    {**HOLD, "observation": {**HOLD["observation"], "position": [0.5, 13.0, 0.5]}},
    {**HOLD, "observation": {**HOLD["observation"], "position": [0.5, 4.0, 0.5]}},
    {**HOLD, "observation": {**HOLD["observation"], "inventory": {"stone_pickaxe": 1}}},
], ids=["no-hold", "short-hold", "unstable", "above-band", "below-band", "no-iron-pickaxe"])
def test_cli_rejects_descend_completion_without_every_condition(tmp_path: Path, step: dict[str, Any]) -> None:
    result, output = run(tmp_path, zone(), [step])
    assert result.returncode == 1
    assert output[-1]["data"]["goal_completed"] is False


def test_cli_does_not_offer_a_hold_beside_an_observed_hazard(tmp_path: Path) -> None:
    lava = cell("lava", 1, 12, 0, hazard=True)
    _, output = run(tmp_path, surface(position=[0.5, 12.0, 0.5], observed_map=[*ground(12), lava]), [stop_step()])
    assert all(c["action_kind"] != "wait" for c in first_candidates(output))


IRON = {"goal_id": "g2", "kind": "collect", "target": "iron_ore", "quantity": 3}


def test_cli_g2_descends_with_the_provided_pickaxe_when_no_iron_is_observed(tmp_path: Path) -> None:
    state = surface(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", remaining_ticks=12000)
    _, output = run(tmp_path, state, [stop_step()], goal=IRON)
    candidates = first_candidates(output)
    assert candidates[0]["action_kind"] == "stair_down"
    assert candidates[0]["params"]["stop_blocks"] == ["diamond_ore", "iron_ore"]


def test_cli_g2_prefers_exposed_iron_and_keeps_descending_past_iron_out_of_reach(tmp_path: Path) -> None:
    pickaxe = {"inventory": {"stone_pickaxe": 1}, "tool": "stone_pickaxe", "remaining_ticks": 12000}
    reachable = surface(**pickaxe, observed_map=[*ground(), cell("iron_ore", 1, 64, 0, support=True)])
    _, output = run(tmp_path, reachable, [stop_step()], goal=IRON)
    assert {c["action_kind"] for c in first_candidates(output)} == {"mine_visible_cluster"}
    below = surface(**pickaxe, observed_map=[*ground(), cell("iron_ore", 1, 60, 0, support=True)])
    _, output = run(tmp_path, below, [stop_step()], goal=IRON)
    assert first_candidates(output)[0]["action_kind"] == "stair_down"


def test_shipping_bridge_stair_contract() -> None:
    result = subprocess.run(["node", "fixtures/stair_macros.cjs"], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}
