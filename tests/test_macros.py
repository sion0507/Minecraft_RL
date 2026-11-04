"""T04 checks at the existing public CLI and shipping bridge boundaries."""

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml
import pytest


def run_macros(tmp_path: Path, fixture: dict[str, Any]) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    fixture_path = tmp_path / "macros.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    config = {"backend": "mock", "fixture": str(fixture_path), "max_decisions": 8,
              "goal": {"goal_id": "wood", "kind": "collect", "target": "oak_log", "quantity": 1}}
    config_path = tmp_path / "macros.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(config_path)],
                            capture_output=True, text=True, timeout=15)
    return result, [json.loads(line) for line in result.stdout.splitlines()]


def wood_fixture() -> dict[str, Any]:
    fixture: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text())
    fixture["initial"]["observed_map"] = [
        {"block": "air", "position": [float(x), 64.0, 0.0], "passable": True}
        for x in range(10)
    ] + [{"block": "oak_log", "position": [1.0, 64.0, 0.0], "support": True}]
    fixture["steps"][0].update(source_obs_id="obs-0", map_version=0,
                               stop_evidence=["obs-1", "cluster_completed"], reason="cluster_completed")
    return fixture


def test_macro_cli_finds_log_after_first_eight_cells_and_forces_single_probability(tmp_path: Path) -> None:
    result, output = run_macros(tmp_path, wood_fixture())
    assert result.returncode == 0, result.stderr
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    assert len(saved["candidates"]) == 1
    candidate = saved["candidates"][0]
    assert candidate["action_kind"] == "mine_visible_cluster"
    assert candidate["params"]["blocks"] == [[1.0, 64.0, 0.0]]
    assert saved["mask"] == [True]
    selection = next(row["data"] for row in output if row["type"] == "selection")
    assert selection["probabilities"] == {candidate["candidate_id"]: 1.0}
    summary = output[-1]["data"]
    assert summary["task"] == "macros_smoke"
    assert summary["goal_completed"] is True
    assert summary["actor_transitions"] == 0
    assert summary["macro_steps"][0]["candidate_id"] == candidate["candidate_id"]
    assert summary["reward_total"] == 1.0


def test_macro_cli_zero_candidates_records_real_wait_and_failure(tmp_path: Path) -> None:
    fixture = wood_fixture()
    fixture["initial"]["observed_map"] = []
    step = fixture["steps"][0]
    step.update(terminated=False, truncated=True, reason="active_tick_limit",
                stop_evidence=["obs-1", "active_tick_limit"],
                events=[{"kind": "wait", "source": "mock"}, {"kind": "failed", "source": "mock"}])
    step["observation"]["inventory"] = {}
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 1
    assert next(row["data"] for row in output if row["type"] == "candidates")["candidates"] == []
    assert next(row["data"] for row in output if row["type"] == "selection")["selector_mode"] == "forced_wait"
    summary = output[-1]["data"]
    assert summary["active_ticks"] == 20
    assert summary["reward_total"] == 0
    assert summary["macro_steps"][0]["events"][1]["kind"] == "failed"


def test_shipping_bridge_mines_only_exposed_blocks_and_bounds_waits() -> None:
    result = subprocess.run(["node", "fixtures/wood_macros.cjs"], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("cancel_ticks", [20, 450])
def test_macro_cli_cancelled_selection_reselects_without_reusing_events_or_actor_trace(tmp_path: Path, cancel_ticks: int) -> None:
    fixture = wood_fixture()
    first = fixture["steps"][0]
    fixture["initial"]["remaining_ticks"] = 1000
    first["actual_ticks"] = cancel_ticks
    first["observation"].update(active_ticks=cancel_ticks, remaining_ticks=1000-cancel_ticks)
    first.update(cancelled=True, terminated=False, reason="candidate_invalidated",
                 stop_evidence=["obs-1", "candidate_invalidated"],
                 events=[{"kind": "wait", "source": "mock", "event_id": "wait-1"}])
    first["observation"].update(inventory={}, observed_map=fixture["initial"]["observed_map"])
    last = json.loads(json.dumps(first))
    last.update(cancelled=False, terminated=True, reason="cluster_completed", source_obs_id="obs-1",
                actual_ticks=20,
                stop_evidence=["obs-2", "cluster_completed"],
                events=[{"kind": "acquired", "source": "mock", "event_id": "drop-1", "item": "oak_log", "quantity": 1}])
    last["observation"].update(obs_id="obs-2", active_ticks=cancel_ticks+20, remaining_ticks=980-cancel_ticks, inventory={"oak_log": 1})
    fixture["steps"].append(last)
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 0, result.stderr
    cancel = next(row["data"] for row in output if row["type"] == "cancellation")
    selections = [row["data"] for row in output if row["type"] == "selection"]
    assert cancel["selection"] == selections[0]
    assert cancel["actor_valid"] is False and cancel["trace_mask"] == 0
    assert cancel["candidates"]["candidates"][0]["candidate_id"] == selections[0]["candidate_id"]
    assert selections[0]["candidate_id"] != selections[1]["candidate_id"]
    summary = output[-1]["data"]
    assert summary["decisions"] == 1
    assert summary["selection_requests"] == 2
    assert summary["cancelled_selections"] == 1
    assert summary["active_ticks"] == cancel_ticks+20 and summary["reward_total"] == 1
    assert summary["macro_steps"][0]["cancelled"] is True


def test_macro_cli_waits_for_its_observed_drop_before_exploring(tmp_path: Path) -> None:
    fixture = wood_fixture()
    fixture["initial"].update(observed_map=[], drops=[{"entity_id": 7, "item": "oak_log", "quantity": 1,
                                                     "position": [0.5, 64.0, 0.5]}])
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 0, result.stderr
    candidate = next(row["data"] for row in output if row["type"] == "candidates")["candidates"][0]
    assert candidate["action_kind"] == "wait"
    assert candidate["max_ticks"] == 20


def test_macro_cli_rejects_duplicate_event_instead_of_rewarding_it_twice(tmp_path: Path) -> None:
    fixture = wood_fixture()
    first = fixture["steps"][0]
    first.update(terminated=False, events=[{"kind": "wait", "source": "mock", "event_id": "same-event"}])
    first["observation"].update(inventory={}, observed_map=fixture["initial"]["observed_map"])
    last = json.loads(json.dumps(first))
    last.update(source_obs_id="obs-1", stop_evidence=["obs-2", "cluster_completed"],
                events=[{"kind": "acquired", "source": "mock", "event_id": "same-event", "item": "oak_log", "quantity": 1}])
    last["observation"].update(obs_id="obs-2", active_ticks=40, remaining_ticks=60, inventory={"oak_log": 1})
    fixture["steps"].append(last)
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 1
    assert output[-1]["data"]["error"]["code"] == "invalid_step"
    assert output[-1]["data"]["reward_total"] == 0


def test_macro_cli_deduplicates_visible_targets_before_eight_candidate_cap(tmp_path: Path) -> None:
    fixture = wood_fixture()
    cells = [{"block": "oak_log", "position": [float(x), float(y), float(z)], "visible": True}
             for x in [-1, 0, 1] for y in [64, 65] for z in [-1, 0, 1]]
    fixture["initial"]["observed_map"] = cells * 2 + [
        {"block": "oak_log", "position": [0.0, 66.0, 0.0], "visible": False}]
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 0, result.stderr
    saved = next(row["data"] for row in output if row["type"] == "candidates")
    assert len(saved["candidates"]) == 8 and saved["mask"] == [True] * 8
    targets = [candidate["params"]["blocks"] for candidate in saved["candidates"]]
    assert len({json.dumps(target) for target in targets}) == 8
    assert [[0.0, 66.0, 0.0]] not in targets


def test_macro_cli_uses_actual_position_for_drop_pickup_distance(tmp_path: Path) -> None:
    fixture = wood_fixture()
    cells = [{"block": block, "position": [float(x), float(y), 0.0],
              "support": block == "stone", "passable": block == "air"}
             for x in range(3) for y, block in [(63, "stone"), (64, "air"), (65, "air")]]
    fixture["initial"].update(position=[1.79, 64.0, 0.5], observed_map=cells,
                              drops=[{"entity_id": 7, "item": "oak_log", "quantity": 1, "position": [0.2, 64.0, 0.5]}])
    step = fixture["steps"][0]
    step.update(path=[[0.5, 64.0, 0.5]], reason="path_completed", stop_evidence=["obs-1", "path_completed"],
                distance_moved=1.29, events=[{"kind": "moved", "source": "mock"}, *step["events"]])
    step["observation"].update(position=[0.5, 64.0, 0.5])
    result, output = run_macros(tmp_path, fixture)
    assert result.returncode == 0, result.stderr
    candidate = next(row["data"] for row in output if row["type"] == "candidates")["candidates"][0]
    assert candidate["action_kind"] == "move_observed"
    assert candidate["params"]["path"] == [[0.5, 64.0, 0.5]]
