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
    # Each hazard stays outside the 1.5-block bridge radius of the bot, where escape walks would replace every cut.
    cell("lava", 2, 65, 0, hazard=True), cell("water", 1, 62, 0, hazard=True), cell("lava", 2, 64, 1, hazard=True),
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
    state = surface(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131, remaining_ticks=12000)
    _, output = run(tmp_path, state, [stop_step()], goal=IRON)
    candidates = first_candidates(output)
    assert candidates[0]["action_kind"] == "stair_down"
    assert candidates[0]["params"]["stop_blocks"] == ["diamond_ore", "iron_ore"]


def test_cli_g2_prefers_exposed_iron_and_keeps_descending_past_iron_out_of_reach(tmp_path: Path) -> None:
    pickaxe = {"inventory": {"stone_pickaxe": 1}, "tool": "stone_pickaxe", "tool_durability": 131, "remaining_ticks": 12000}
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


# T07: level tunnels and the diamond/iron ore search through the same public smoke-macros boundary.
DIAMOND = {"goal_id": "g4", "kind": "mine_diamond", "target": "diamond", "quantity": 1}


def chamber(**update: Any) -> dict[str, Any]:
    """G4-like: standing at y=11 with an iron pickaxe; only the standing cell is observed."""
    return surface(**{"position": [0.5, 11.0, 0.5], "observed_map": ground(11), "tool_durability": 250, **update})


def tunnels(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [c for c in candidates if c["action_kind"] == "tunnel"]


def test_cli_g4_offers_level_tunnels_in_each_direction_with_a_taller_section(tmp_path: Path) -> None:
    _, output = run(tmp_path, chamber(), [stop_step()], goal=DIAMOND)
    found = tunnels(first_candidates(output))
    assert [c["params"]["direction"] for c in found][0] == [0, 1], "yaw pi faces south, so continuing is the first choice"
    assert sorted(tuple(c["params"]["direction"]) for c in found if c["params"]["height"] == 2) == [(-1, 0), (0, -1), (0, 1), (1, 0)]
    assert [c["params"]["height"] for c in found] == [2, 2, 2, 2, 3]
    assert all(c["params"]["cells"] == 8 and c["params"]["stop_blocks"] == ["diamond_ore"] and c["max_ticks"] == 400
               and c["stop_rule_id"] == "tunnel_ore_or_hazard" for c in found)


def test_cli_g4_walks_new_ground_before_cutting_below_the_diamond_layers(tmp_path: Path) -> None:
    room = [cell("stone", x, 10, z, support=True) for x in (-1, 0, 1) for z in (-1, 0, 1)]
    room += [cell("air", x, y, z, passable=True) for x in (-1, 0, 1) for y in (11, 12) for z in (-1, 0, 1)]
    _, output = run(tmp_path, chamber(observed_map=room), [stop_step()], goal=DIAMOND)
    kinds = [c["action_kind"] for c in first_candidates(output)]
    assert kinds[0] == "move_observed" and "tunnel" in kinds


def test_cli_g2_tunnels_first_inside_the_iron_layers_and_keeps_durability_for_the_ore(tmp_path: Path) -> None:
    state = surface(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=10, remaining_ticks=12000,
                    position=[0.5, 61.0, 0.5], observed_map=ground(61))
    _, output = run(tmp_path, state, [stop_step()], goal=IRON)
    candidates = first_candidates(output)
    assert candidates[0]["action_kind"] == "tunnel"
    assert candidates[0]["params"]["stop_blocks"] == ["diamond_ore", "iron_ore"]
    assert {c["params"]["cells"] for c in tunnels(candidates)} == {3, 2}, "(10 - 3 ores) // 2 and // 3 cells"
    assert {c["params"]["stairs"] for c in candidates if c["action_kind"] == "stair_down"} == {2, 1}, "(10 - 3) // 3 stairs and one"
    _, output = run(tmp_path, {**state, "tool_durability": 4}, [stop_step()], goal=IRON)
    assert [c for c in first_candidates(output) if c["action_kind"] in {"tunnel", "stair_down"}] == []


def test_cli_g2_still_descends_first_above_the_iron_layers(tmp_path: Path) -> None:
    state = surface(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131, remaining_ticks=12000)
    _, output = run(tmp_path, state, [stop_step()], goal=IRON)
    kinds = [c["action_kind"] for c in first_candidates(output)]
    assert kinds[:4] == ["stair_down"] * 4 and "tunnel" in kinds


# T07C (#38): one shared cap of 16 with slots per kind (walk 6, tunnel 5, stair 4, any other kind 1).
def open_ground(y: int = 64) -> list[dict[str, Any]]:
    """Observed floor and headroom two cells around the start: a walk in each of the eight directions."""
    span = range(-2, 3)
    return ([cell("stone", x, y - 1, z, support=True) for x in span for z in span]
            + [cell("air", x, h, z, passable=True) for x in span for h in (y, y + 1) for z in span])


def saved_set(output: list[dict[str, Any]]) -> dict[str, Any]:
    return next(row["data"] for row in output if row["type"] == "candidates")


def test_cli_cuts_ore_search_to_sixteen_by_kind_slots_and_records_the_cut(tmp_path: Path) -> None:
    state = surface(inventory={"stone_pickaxe": 1}, tool="stone_pickaxe", tool_durability=131, remaining_ticks=12000,
                    observed_map=open_ground())
    step = stop_step(observation={"active_ticks": 40, "remaining_ticks": 11960})
    _, output = run(tmp_path, state, [step], goal=IRON)
    saved = saved_set(output)
    # Generated above the iron layers: 4 full stairs, 5 tunnels, 8 walks, 4 single stairs (21). Slots keep 15; the free
    # 16th goes to the first cut candidate in generation order, the seventh walk. Kept candidates stay in that order.
    assert [c["action_kind"] for c in saved["candidates"]] == ["stair_down"] * 4 + ["tunnel"] * 5 + ["move_observed"] * 7
    assert {c["params"]["stairs"] for c in saved["candidates"] if c["action_kind"] == "stair_down"} == {4}
    assert saved["mask"] == [True] * 16
    assert saved["generated"] == 21 and saved["truncated"] == {"move_observed": 1, "stair_down": 4}
    selection = next(row["data"] for row in output if row["type"] == "selection")
    executed = output[-1]["data"]["macro_steps"][0]
    assert selection["candidate_id"] == executed["candidate_id"] == saved["candidates"][0]["candidate_id"]
    assert executed["source_obs_id"] == saved["candidates"][0]["source_obs_id"]
    _, again = run(tmp_path, state, [step], goal=IRON)
    assert saved_set(again) == saved, "the same observation always saves the same IDs, contents and order"


def test_cli_keeps_every_candidate_up_to_the_cap(tmp_path: Path) -> None:
    _, output = run(tmp_path, chamber(), [stop_step()], goal=DIAMOND)
    saved = saved_set(output)
    assert len(saved["candidates"]) == saved["generated"] == 13, "4 full and 4 single stairs, 5 tunnels"
    assert saved["truncated"] == {}


@pytest.mark.parametrize("veto", [
    cell("lava", 1, 12, 1, hazard=True), cell("air", 1, 10, 0, passable=True), cell("diamond_ore", 1, 12, 0, support=True, visible=False),
    cell("bedrock", 1, 11, 0, support=True),
], ids=["lava-beside", "open-floor", "stop-ore", "bedrock"])
def test_cli_only_an_observed_cell_can_veto_a_tunnel(tmp_path: Path, veto: dict[str, Any]) -> None:
    _, output = run(tmp_path, chamber(observed_map=[*ground(11), veto]), [stop_step()], goal=DIAMOND)
    directions = [c["params"]["direction"] for c in tunnels(first_candidates(output))]
    assert [1, 0] not in directions and [-1, 0] in directions


def test_cli_never_offers_a_tunnel_back_over_visited_ground(tmp_path: Path) -> None:
    _, output = run(tmp_path, chamber(visited=[[0.0, 11.0, 0.0], [1.0, 11.0, 0.0]]), [stop_step()], goal=DIAMOND)
    assert [1, 0] not in [c["params"]["direction"] for c in tunnels(first_candidates(output))]


def test_cli_mines_exposed_diamond_only_with_an_iron_tier_pickaxe(tmp_path: Path) -> None:
    ore = cell("diamond_ore", 1, 11, 0, support=True)
    _, output = run(tmp_path, chamber(observed_map=[*ground(11), ore]), [stop_step()], goal=DIAMOND)
    assert [(c["action_kind"], c["params"]["blocks"]) for c in first_candidates(output)] == [("mine_visible_cluster", [[1.0, 11.0, 0.0]])]
    stone = chamber(observed_map=[*ground(11), ore], inventory={"stone_pickaxe": 1}, tool="stone_pickaxe")
    _, output = run(tmp_path, stone, [stop_step()], goal=DIAMOND)
    assert all(c["action_kind"] != "mine_visible_cluster" for c in first_candidates(output))


DIAMOND_STEP = stop_step(actual_ticks=30, reason="cluster_completed", stop_evidence=["obs-1", "cluster_completed"],
                         events=[{"kind": "mined", "item": "diamond_ore", "quantity": 1, "source": "mock", "event_id": "m-1"},
                                 {"kind": "acquired", "item": "diamond", "quantity": 1, "source": "mock", "event_id": "a-1"}],
                         observation={"active_ticks": 30, "remaining_ticks": 17970,
                                      "inventory": {"iron_pickaxe": 1, "diamond": 1}})


def test_cli_mock_diamond_completes_the_goal_but_never_counts_as_diamond_success(tmp_path: Path) -> None:
    result, output = run(tmp_path, chamber(), [DIAMOND_STEP], goal=DIAMOND)
    assert result.returncode == 0, result.stderr
    kinds = [row["type"] for row in output]
    assert kinds.index("admin_verification") > max(i for i, k in enumerate(kinds) if k == "step"), "read after the last decision"
    summary = output[-1]["data"]
    assert summary["goal_completed"] is True and summary["diamond_success"] is False and summary["admin_verified"] == {}


def test_cli_stops_at_the_wall_clock_limit(tmp_path: Path) -> None:
    fixture = tmp_path / "wall.yaml"
    run(tmp_path, chamber(), [stop_step()], goal=DIAMOND)
    config = yaml.safe_load((tmp_path / "descent.yaml").read_text())
    fixture.write_text(yaml.safe_dump(dict(config, wall_limit_seconds=1e-9)))
    result = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(fixture)], capture_output=True, text=True, timeout=15)
    summary = json.loads(result.stdout.splitlines()[-1])["data"]
    assert summary["reason"] == "wall_time_limit" and summary["truncated"] and summary["decisions"] == 0


def test_admin_verification_counts_only_natural_linked_breaks() -> None:
    from mc_diamond.episode import admin_verified
    from mc_diamond.schema import Event

    def acquired(quantity: int) -> dict[str, Event]:
        return {"a-1": Event(kind="acquired", item="diamond", quantity=quantity, source="minecraft", event_id="a-1")}
    good: dict[str, Any] = {"block": "diamond_ore", "natural": True, "server_block_before": True, "server_air_after": True,
            "server_tool": "iron_pickaxe", "drop_item": "diamond", "drop_entity_id": 7, "acquired_event_id": "a-1"}
    log = {"natural": True, "records": [good]}
    assert admin_verified(log, acquired(1)) == {"diamond": 1}
    variants: list[dict[str, Any]] = [{"natural": False}, {"server_block_before": False}, {"server_air_after": False}, {"server_tool": "stone_pickaxe"},
                   {"drop_item": "coal"}, {"acquired_event_id": "other"}, {"drop_entity_id": None}]
    for broken in variants:
        assert admin_verified({"natural": True, "records": [{**good, **broken}]}, acquired(1)) == {}, broken
    assert admin_verified({"natural": False, "records": [good]}, acquired(1)) == {}, "constructed fixture"
    assert admin_verified(log, acquired(2)) == {}, "a merged pickup needs one record per unit"
    assert admin_verified({"natural": True, "records": [good, {**good, "drop_entity_id": 8}]}, acquired(2)) == {"diamond": 2}
    mock = {"a-1": Event(kind="acquired", item="diamond", quantity=1, source="mock", event_id="a-1")}
    assert admin_verified(log, mock) == {}


def test_shipping_bridge_diamond_and_merge_contract() -> None:
    result = subprocess.run(["node", "fixtures/diamond_macros.cjs"], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}


def test_cli_ends_a_run_of_identical_one_tick_stops(tmp_path: Path) -> None:
    """G2 attempt 1 repeated the same 1-tick `observed_hazard` 2,107 times until the wall limit; 20 in a row end the episode."""
    stuck = [stop_step(actual_ticks=1, source_obs_id=f"obs-{n}", reason="observed_hazard", stop_evidence=[f"obs-{n + 1}", "observed_hazard"],
                       events=[{"kind": "stopped", "source": "mock", "event_id": f"stop-{n}"}],
                       observation={"active_ticks": n + 1, "remaining_ticks": 17999 - n}) for n in range(25)]
    result, output = run(tmp_path, chamber(), stuck, goal=DIAMOND)
    summary = output[-1]["data"]
    assert summary["reason"] == "repeated_stall" and summary["truncated"] and summary["decisions"] == 20, summary
    moving = [stop_step(actual_ticks=1, source_obs_id=f"obs-{n}", reason="observed_hazard", stop_evidence=[f"obs-{n + 1}", "observed_hazard"],
                        events=[{"kind": "stopped", "source": "mock", "event_id": f"stop-{n}"}],
                        observation={"active_ticks": n + 1, "remaining_ticks": 17999 - n, "map_version": n + 2}) for n in range(25)]
    _, output = run(tmp_path, chamber(), moving, goal=DIAMOND)
    assert output[-1]["data"]["reason"] != "repeated_stall", "a changing map is progress"
