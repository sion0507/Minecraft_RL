"""Issue 49: numerical rewards and public movement/budget contracts; no actual pilot."""

import json
import gzip
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from mc_diamond.rewards import RewardLedger
from mc_diamond.schema import Goal, Surface
from test_learning import observation, step
from test_cli import fixture_config, movement_fixture, records


def test_discovery_pays_each_required_visible_kind_once_and_never_reset_kinds() -> None:
    goal = Goal(goal_id="stone", kind="collect", target="cobblestone", quantity=3)
    initial = observation(observed_map=[Surface(block="oak_log", position=[1., 64., 0.])])
    ledger = RewardLedger(initial, discovery_reward=.05)
    after = initial.model_copy(update={"observed_map": [
        Surface(block="stone", position=[2., 64., 0.]),
        Surface(block="stone", position=[3., 64., 0.]),
        Surface(block="birch_log", position=[4., 64., 0.], visible=False),
        Surface(block="oak_log", position=[1., 64., 0.]),
        Surface(block="diamond_ore", position=[5., 64., 0.])]})
    first = ledger.compute(initial, goal, step(initial, observation=after), goal_completed=False)
    assert first.components == {"time": -.02, "discovery": .05}
    assert first.total == pytest.approx(.03)
    assert first.discounted == pytest.approx(.02508988053672783)
    again = ledger.compute(after, goal.model_copy(update={"goal_id": "changed"}), step(after, observation=after),
                           goal_completed=False)
    assert again.components == {"time": -.02}
    visible = after.model_copy(update={"observed_map": [Surface(block="birch_log", position=[4., 64., 0.])]})
    assert ledger.compute(after, goal, step(after, observation=visible), goal_completed=False).components["discovery"] == .05
    assert RewardLedger(initial).compute(initial, goal, step(initial, observation=after),
                                          goal_completed=False).components == {"time": -.02}


@pytest.mark.parametrize(("objective", "inventory", "expected"), [
    ("local", {}, .1), ("local", {"wooden_pickaxe": 1}, .05), ("full", {}, 0.),
])
def test_discovery_source_blocks_tools_and_full_isolation(
        objective: str, inventory: dict[str, int], expected: float) -> None:
    initial = observation(objective_kind=objective, inventory=inventory, observed_map=[])
    after = initial.model_copy(update={"observed_map": [
        Surface(block="stone", position=[1., 64., 0.]),
        Surface(block="oak_log", position=[2., 64., 0.])]})
    ledger = RewardLedger(initial, discovery_reward=.05)
    goal = Goal(goal_id="stone", kind="collect", target="cobblestone", quantity=3)
    result = ledger.compute(initial, goal, step(initial, observation=after), goal_completed=False)
    assert result.components.get("discovery", 0.) == expected
    # A kind seen under an unrelated goal must not pay later when it becomes required.
    other = Goal(goal_id="iron", kind="collect", target="iron_ore", quantity=1)
    seen = after.model_copy(update={"observed_map": [Surface(block="iron_ore", position=[3., 64., 0.])]})
    ledger.compute(after, goal, step(after, observation=seen), goal_completed=False)
    assert "discovery" not in ledger.compute(seen, other, step(seen, observation=seen), goal_completed=False).components


def test_movement_cli_summarizes_currently_visible_endpoint_radius_without_changing_path(tmp_path: Path) -> None:
    fixture = movement_fixture()
    fixture["initial"]["observed_map"] += [
        {"block": "oak_log", "position": [18.5, 64., .5]},  # exactly 16 from endpoint; >16 from actor
        {"block": "diamond_ore", "position": [18.5, 64.1, .5]},  # outside in 3D
        {"block": "iron_ore", "position": [3., 64., 0.], "visible": False},
        {"block": "birch_log", "position": [2.5, 80., .5]},  # vertical boundary
    ]
    run = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(fixture_config(tmp_path, fixture))],
                         capture_output=True, text=True, timeout=15)
    assert run.returncode == 0, run.stderr
    saved = next(r["data"] for r in records(run) if r["type"] == "candidates")
    assert saved["mask"] == [True]
    candidate = saved["candidates"][0]
    assert candidate["candidate_id"] == "obs-0:move:0"
    assert candidate["params"] == {"path": [[1.5, 64., .5], [2.5, 64., .5]], "map_version": 1}
    assert candidate["description"] == ("Walk over observed cells to [2.5, 64.0, 0.5]; "
        "currently visible within 16 blocks of it: birch_log 1, oak_log 1, stone 3")


def test_selection_uses_initial_sample_time_tie_and_keeps_successes_first() -> None:
    pytest.importorskip("torch")
    from mc_diamond.wood_pilot import select_setting, time_tie_threshold
    rows = [{"phase": "initial", "success": i < 5, "attempts": [{"active_ticks": 800}]} for i in range(10)]
    threshold = time_tie_threshold(rows)
    assert threshold == pytest.approx(471.4045207910317)
    settings = [{"phase": "a", "choice_lr": 1e-4, "usable": True, "errors": []},
                {"phase": "b", "choice_lr": 3e-4, "usable": True, "errors": []}]
    rows += [{"phase": phase, "success": True, "attempts": [{"active_ticks": ticks}]}
             for phase, ticks in [("a", 1200), ("b", 800)] for _ in range(10)]
    assert select_setting(settings, rows, time_tie_ticks=threshold) == 1e-4
    assert select_setting(settings, rows, time_tie_ticks=400.) == 3e-4  # equality is outside the strict tie band
    rows[-1]["success"] = False
    assert select_setting(settings, rows, time_tie_ticks=0.) == 1e-4
    equal = [{"phase": "initial", "success": False, "attempts": []} for _ in range(10)]
    assert time_tie_threshold(equal) == 0.


def test_movement_cli_keeps_rarest_eight_kinds_in_name_order(tmp_path: Path) -> None:
    fixture = movement_fixture()
    fixture["initial"]["observed_map"] += [
        {"block": f"kind_{i}", "position": [4., float(66 + i), 0.]} for i in reversed(range(9))]
    run = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(fixture_config(tmp_path, fixture))],
                         capture_output=True, text=True, timeout=15)
    candidate = next(r["data"] for r in records(run) if r["type"] == "candidates")["candidates"][0]
    assert candidate["description"].endswith("kind_0 1, kind_1 1, kind_2 1, kind_3 1, kind_4 1, kind_5 1, kind_6 1, kind_7 1")


@pytest.mark.parametrize(("task", "ticks"), [("G1", 3600), ("G2", 12000), ("G3", 18000), ("G4", 18000), ("C4", 36000)])
def test_shipping_bridge_retains_default_budgets_and_allows_only_reductions(task: str, ticks: int) -> None:
    script = """
const assert = require('node:assert/strict')
const vm = require('node:vm')
const load = require('./fixtures/bridge_harness.cjs')
const [task, ticks] = JSON.parse(process.argv[1])
assert.equal(vm.runInContext('budget', load({bridgeArgs:['--task',task]})), ticks)
assert.equal(vm.runInContext('budget', load({bridgeArgs:['--task',task,'--budget-ticks','1800']})), 1800)
for (const value of ['0', '-1', '1.5', 'NaN', 'Infinity', String(ticks+1), '']) {
  assert.throws(() => load({bridgeArgs:['--task',task,'--budget-ticks',value]}), /Invalid backend configuration/)
}
assert.throws(() => load({bridgeArgs:['--task',task,'--budget-ticks']}), /Invalid backend configuration/)
"""
    run = subprocess.run(["node", "-e", script, json.dumps([task, ticks])], capture_output=True, text=True, timeout=15)
    assert run.returncode == 0, run.stderr


def test_trace_diagnostics_use_discounted_mc_and_exclude_incomplete_episodes(tmp_path: Path) -> None:
    from mc_diamond.pilot_diagnostics import critic_diagnostics, trace_diagnostics
    trace = tmp_path / "episode.jsonl.gz"
    rows: list[dict[str, Any]] = [{"type": "transition", "data": {"reward": .2, "discount": .5, "old_value": .4,
                "valid": True, "bootstrap": True}},
            {"type": "transition", "data": {"reward": .8, "discount": .5, "old_value": .8,
                "valid": True, "bootstrap": False}}]
    def write() -> None:
        with gzip.open(trace, "wt") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
    write()
    diagnostics = trace_diagnostics(trace, .05)
    assert diagnostics["mc_returns"] == pytest.approx([.6, .8])
    assert diagnostics["mc_values"] == [.4, .8]
    assert critic_diagnostics([diagnostics]) == {"transitions": 2, "explained_variance": pytest.approx(0.)}
    rows[-1]["data"]["bootstrap"] = True
    write()
    incomplete = trace_diagnostics(trace, .05)
    assert incomplete["mc_returns"] == []
    assert critic_diagnostics([incomplete]) == {"transitions": 0, "explained_variance": None}


def test_public_macro_evaluation_uses_the_same_opt_in_discovery_reward(tmp_path: Path) -> None:
    from test_cli import mock_fixture
    fixture = mock_fixture()
    fixture["initial"]["observed_map"] = []
    last = fixture["steps"][0]
    last["observation"].update(inventory={}, observed_map=[{"block": "stone", "position": [1., 64., 0.]}])
    last.update(events=[{"kind": "wait", "source": "mock"}], terminated=False)
    config = fixture_config(tmp_path, fixture)
    raw = yaml.safe_load(config.read_text())
    raw.update(max_decisions=1, discovery_reward=.05,
               goal={"goal_id": "stone", "kind": "collect", "target": "cobblestone", "quantity": 3})
    config.write_text(yaml.safe_dump(raw))
    run = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(config)], capture_output=True, text=True, timeout=15)
    reward = next(r["data"] for r in records(run) if r["type"] == "reward")
    assert reward["components"] == {"time": -.02, "discovery": .05, "failure": -.01}
    assert reward["value"] == pytest.approx(.02)
