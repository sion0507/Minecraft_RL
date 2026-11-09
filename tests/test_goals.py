"""T08 (#9): goal validation, replanning, one regeneration, rule recovery and selector S.

Flows run through the public smoke-macros CLI on the mock backend. Goals whose macros are not yet linked to an actual
game check (explore, escape) are checked as event fixtures only; none of this is Minecraft evidence.
"""

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from mc_diamond.goals import GoalError, completed, recovery_goal, validate
from mc_diamond.schema import Candidate, CandidateSet, Goal, Observation, StepResult, allocate
from mc_diamond.selectors import RULE_HASH, rule_select, signature

BASE: dict[str, Any] = {**json.loads(Path("fixtures/mock_episode.json").read_text())["initial"], "remaining_ticks": 20000}
LOGS = [{"block": "air", "position": [float(x), 64.0, 0.0], "passable": True} for x in range(2, 6)] + [
    {"block": "oak_log", "position": [1.0, 64.0, 0.0], "support": True},
    {"block": "oak_log", "position": [0.0, 64.0, 1.0], "support": True}]
TASK = {"goal_id": "wood", "kind": "collect", "target": "oak_log", "quantity": 2}
ACQUIRED = [{"kind": "acquired", "item": "oak_log", "quantity": 1, "source": "mock"}]
FAILED = [{"kind": "failed", "source": "mock"}, {"kind": "stopped", "source": "mock"}]
WAIT = [{"kind": "wait", "source": "mock"}]


def observation(**update: Any) -> dict[str, Any]:
    return {**BASE, "observed_map": LOGS, **update}


def steps(*plan: tuple[int, list[dict[str, Any]], dict[str, int]], **update: Any) -> list[dict[str, Any]]:
    """(ticks, events, inventory) per step, chained by obs IDs and tick accounting."""
    found, total = [], 0
    for index, (ticks, events, inventory) in enumerate(plan, 1):
        total += ticks
        reason = "cluster_completed" if events == ACQUIRED else "wait_completed" if events == WAIT else "operation_failed"
        found.append({"observation": observation(obs_id=f"obs-{index}", active_ticks=total, remaining_ticks=20000 - total,
                                                 inventory=inventory, **update.get(f"obs{index}", {})),
                      "actual_ticks": ticks, "events": events, "terminated": False, "truncated": False, "invalid": False,
                      "reason": reason, "clock_mode": "mock", "pause_verified": False, "stable_boundary": True,
                      "wall_seconds": 0.0, "source_obs_id": f"obs-{index - 1}", "map_version": 0,
                      "stop_evidence": [f"obs-{index}", reason]})
    return found


def run(tmp_path: Path, plan: list[dict[str, Any]], outputs: list[str] | None = None, *, select: str = "fixed",
        initial: dict[str, Any] | None = None, task: dict[str, Any] = TASK, max_decisions: int = 32,
        verification: dict[str, Any] | None = None) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    fixture: dict[str, Any] = {"initial": initial or observation(), "steps": plan}
    if verification is not None:
        fixture["verification"] = verification
    (tmp_path / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    config: dict[str, Any] = {"backend": "mock", "fixture": str(tmp_path / "fixture.json"), "max_decisions": max_decisions,
                              "goal": task}
    if outputs is not None:
        config["planner"] = {"backend": "scripted", "outputs": outputs}
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    result = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(tmp_path / "config.yaml"), "--select", select],
                            capture_output=True, text=True, timeout=30)
    return result, [json.loads(line) for line in result.stdout.splitlines()]


def kind(output: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [row["data"] for row in output if row["type"] == name]


def chosen(output: list[dict[str, Any]], decision: int) -> dict[str, Any]:
    selected = kind(output, "selection")[decision]["candidate_id"]
    return next(c for c in kind(output, "candidates")[decision]["candidates"] if c["candidate_id"] == selected)


def collect(quantity: int = 1) -> str:
    return json.dumps({"kind": "collect", "target": "oak_log", "quantity": quantity})


# --- Planner goals through the public CLI -------------------------------------------------------------------------

def test_completed_goal_replans_and_links_actions_and_progress_to_the_adopted_goal(tmp_path: Path) -> None:
    result, output = run(tmp_path, steps((20, ACQUIRED, {"oak_log": 1}), (20, ACQUIRED, {"oak_log": 2})),
                         [collect(1), collect(2)])
    assert result.returncode == 0, result.stderr
    decisions = kind(output, "goal_decision")
    assert [(d["trigger"], d["source"], d["goal"]["goal_id"]) for d in decisions] == [
        ("episode_start", "planner", "wood:1"), ("goal_completed", "planner", "wood:2")]
    assert decisions[0]["planner_model"] == "mock-scripted" and decisions[0]["goal"]["preconditions"] == []
    summary = kind(output, "summary")[0]
    assert (summary["reason"], summary["goal_completed"]) == ("goal_completed", True)
    assert [(s["goal_id"], s["goal_source"]) for s in summary["macro_steps"]] == [("wood:1", "planner"), ("wood:2", "planner")]
    assert [r["goal_id"] for r in kind(output, "reward")] == ["wood:1", "wood:2"]
    assert summary["progress_by_source"] == {"planner": {"acquired:oak_log": 2}}
    assert [(o["goal_id"], o["completed"], o["end_reason"], o["direct"]) for o in summary["goal_outcomes"]] == [
        ("wood:1", True, "goal_completed", {"acquired:oak_log": 1}), ("wood:2", True, "goal_completed", {"acquired:oak_log": 1})]
    assert {key: summary[key] for key in ("planner_initial_requests", "planner_initial_errors", "planner_regeneration_requests",
                                          "planner_regeneration_errors", "rule_recoveries", "goal_decisions")} == {
        "planner_initial_requests": 2, "planner_initial_errors": 0, "planner_regeneration_requests": 0,
        "planner_regeneration_errors": 0, "rule_recoveries": 0, "goal_decisions": 2}


def test_invalid_reply_is_regenerated_once_with_its_own_denominator(tmp_path: Path) -> None:
    result, output = run(tmp_path, steps((20, ACQUIRED, {"oak_log": 1})), ["not json", collect()],
                         task={**TASK, "quantity": 1})
    assert result.returncode == 0, result.stderr
    decision = kind(output, "goal_decision")[0]
    assert [(r["kind"], r["error"]) for r in decision["requests"]] == [("initial", "invalid_json"), ("regeneration", None)]
    assert decision["source"] == "regenerated"
    summary = kind(output, "summary")[0]
    assert (summary["planner_initial_errors"], summary["planner_initial_requests"]) == (1, 1)
    assert (summary["planner_regeneration_errors"], summary["planner_regeneration_requests"]) == (0, 1)
    assert summary["progress_by_source"] == {"regenerated": {"acquired:oak_log": 1}}


def test_second_error_adopts_the_rule_recovery_goal_and_keeps_its_progress_apart(tmp_path: Path) -> None:
    opened = [{"block": "air", "position": [float(x), 70.0, 0.0], "passable": True} for x in range(16)]
    result, output = run(tmp_path, steps((20, WAIT, {}), (20, WAIT, {}), obs1={"observed_map": LOGS + opened}),
                         [json.dumps({"kind": "craft", "target": "iron_pickaxe"}), collect(99)], max_decisions=2)
    decisions = kind(output, "goal_decision")
    assert [(r["kind"], r["error"]) for r in decisions[0]["requests"]] == [("initial", "precondition"),
                                                                          ("regeneration", "invalid_format")]
    assert [(d["source"], d["goal"]["kind"], d["trigger"]) for d in decisions] == [
        ("rule_recovery", "explore", "episode_start"), ("rule_recovery", "explore", "goal_completed")]
    summary = kind(output, "summary")[0]
    assert (summary["rule_recoveries"], summary["goal_decisions"]) == (2, 2)
    assert (summary["planner_initial_errors"], summary["planner_initial_requests"]) == (2, 2)
    assert (summary["planner_regeneration_errors"], summary["planner_regeneration_requests"]) == (2, 2)
    assert summary["goal_outcomes"][0]["source"] == "rule_recovery" and summary["goal_outcomes"][0]["completed"] is True
    assert summary["goal_completed"] is False and summary["progress_by_source"] == {}
    assert result.returncode == 1  # the task (wood) is not done: recovery never solves it


@pytest.mark.parametrize("count, ticks, events, trigger", [
    (3, 2, FAILED, "consecutive_failures"),
    (20, 2, [{"kind": "stopped", "source": "mock"}], "macro_limit"),
    (9, 400, [{"kind": "stopped", "source": "mock"}], "goal_time_limit"),
])
def test_first_replan_trigger_switches_to_a_new_goal_decision(tmp_path: Path, count: int, ticks: int,
                                                              events: list[dict[str, Any]], trigger: str) -> None:
    plan = steps(*[(ticks, events, {}) for _ in range(count)], (20, ACQUIRED, {"oak_log": 1}))
    result, output = run(tmp_path, plan, [collect(), collect()], task={**TASK, "quantity": 1})
    assert result.returncode == 0, result.stderr
    decisions = kind(output, "goal_decision")
    assert [(d["trigger"], d["obs_id"], d["goal"]["goal_id"]) for d in decisions] == [
        ("episode_start", "obs-0", "wood:1"), (trigger, f"obs-{count}", "wood:2")]
    first = kind(output, "summary")[0]["goal_outcomes"][0]
    assert (first["end_reason"], first["macros"], first["completed"]) == (trigger, count, False)
    assert first["end_tick"] - first["start_tick"] == count * ticks


def test_fixed_task_goal_is_readopted_without_planner_requests(tmp_path: Path) -> None:
    plan = steps(*[(2, [{"kind": "stopped", "source": "mock"}], {}) for _ in range(20)], (20, ACQUIRED, {"oak_log": 1}))
    result, output = run(tmp_path, plan, task={**TASK, "quantity": 1})
    assert result.returncode == 0, result.stderr
    decisions = kind(output, "goal_decision")
    assert [(d["source"], d["requests"], d["goal"]["goal_id"]) for d in decisions] == [
        ("fixed", [], "wood:1"), ("fixed", [], "wood:2")]
    summary = kind(output, "summary")[0]
    assert (summary["planner_model"], summary["planner_initial_requests"], summary["goal_decisions"]) == (None, 0, 2)
    assert summary["progress_by_source"] == {"fixed": {"acquired:oak_log": 1}}


def test_reset_starts_goal_accounting_afresh_and_repeats_the_same_decisions(tmp_path: Path) -> None:
    runs = []
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
        _, output = run(tmp_path / name, steps((20, ACQUIRED, {"oak_log": 1}), (20, ACQUIRED, {"oak_log": 2})),
                        ["{", collect(1), collect(2)], select="rule")
        summary = kind(output, "summary")[0]
        runs.append((kind(output, "goal_decision"), [s["candidate_id"] for s in kind(output, "selection")],
                     summary["goal_outcomes"], summary["planner_initial_requests"]))
    assert runs[0] == runs[1]
    assert runs[0][3] == 2


# --- GoalRegistry contract ----------------------------------------------------------------------------------------

def obs(**update: Any) -> Observation:
    return Observation.model_validate({**BASE, **update})


@pytest.mark.parametrize("reply, inventory, cells, code", [
    ("nope", {}, [], "invalid_json"),
    ("[1]", {}, [], "invalid_json"),
    ('{"kind": "dig", "target": "oak_log"}', {}, [], "invalid_format"),
    ('{"kind": "collect", "target": "oak_log", "why": "x"}', {}, [], "invalid_format"),
    ('{"kind": "collect", "target": "oak_log", "quantity": 17}', {}, [], "invalid_format"),
    ('{"kind": "collect", "target": "oak_log", "quantity": true}', {}, [], "invalid_format"),
    ('{"kind": "craft", "target": "stick", "quantity": 9}', {}, [], "invalid_format"),
    ('{"kind": "descend", "target": "safe_mining_zone", "quantity": 2}', {}, [], "invalid_format"),
    ('{"kind": "collect", "target": "oak_log", "direction": "north"}', {}, [], "invalid_format"),
    ('{"kind": "collect", "target": "oak_log"}', {"oak_log": 1}, [], "already_satisfied"),
    ('{"kind": "collect", "target": "iron_ore"}', {"wooden_pickaxe": 1}, [], "precondition"),
    ('{"kind": "mine_diamond", "target": "diamond"}', {"stone_pickaxe": 1}, [], "precondition"),
    ('{"kind": "craft", "target": "wooden_pickaxe"}', {"oak_planks": 3, "stick": 2}, [], "precondition"),
    ('{"kind": "craft", "target": "stick", "quantity": 8}', {"oak_planks": 2}, [], "precondition"),
    ('{"kind": "smelt", "target": "iron_ingot"}', {"iron_ore": 1, "coal": 1}, [], "precondition"),
    ('{"kind": "smelt", "target": "iron_ingot"}', {"iron_ore": 1, "furnace": 1}, [], "precondition"),
    ('{"kind": "descend", "target": "safe_mining_zone"}', {"stone_pickaxe": 1}, [], "precondition"),
    ('{"kind": "escape", "target": "hazard"}', {}, [], "already_satisfied"),
])
def test_registry_rejects_format_provided_state_and_missing_immediate_preconditions(
        reply: str, inventory: dict[str, int], cells: list[dict[str, Any]], code: str) -> None:
    with pytest.raises(GoalError) as error:
        validate(reply, obs(inventory=inventory, observed_map=cells), "g:1", "planner")
    assert error.value.code == code


@pytest.mark.parametrize("reply, inventory, cells, preconditions", [
    ('{"kind": "collect", "target": "oak_log", "quantity": 4}', {"oak_log": 2}, [], []),
    ('{"kind": "collect", "target": "iron_ore", "quantity": 3}', {"stone_pickaxe": 1}, [], ["tool:stone_pickaxe"]),
    ('{"kind": "craft", "target": "wooden_pickaxe"}', {"oak_planks": 3, "stick": 2},
     [{"block": "crafting_table", "position": [3.0, 64.0, 0.0]}],
     ["ingredient:oak_planks*3", "ingredient:stick*2", "facility:crafting_table"]),
    ('{"kind": "smelt", "target": "iron_ingot", "quantity": 2}', {"iron_ore": 2, "oak_planks": 2, "furnace": 1}, [],
     ["ore:iron_ore", "fuel:oak_planks", "facility:furnace"]),
    ('{"kind": "explore", "target": "iron_ore", "direction": "east"}', {}, [], []),
    ('{"kind": "escape", "target": "hazard"}', {}, [{"block": "lava", "position": [2.0, 64.0, 0.0], "hazard": True}],
     ["hazard_within:3"]),
])
def test_registry_adopts_goals_with_the_checked_preconditions(reply: str, inventory: dict[str, int],
                                                              cells: list[dict[str, Any]], preconditions: list[str]) -> None:
    goal = validate(reply, obs(inventory=inventory, observed_map=cells), "g:1", "regenerated")
    assert (goal.preconditions, goal.source, goal.completion_rule_id, goal.active_budget_ticks) == (
        preconditions, "regenerated", goal.kind, 3600)


def test_recovery_escapes_an_observed_hazard_and_otherwise_explores() -> None:
    lava = [{"block": "lava", "position": [2.0, 64.0, 0.0], "hazard": True}]
    assert (recovery_goal(obs(observed_map=lava), "r").kind, recovery_goal(obs(), "r").kind) == ("escape", "explore")
    far = [{"block": "lava", "position": [3.0, 64.0, 0.0], "hazard": True}]  # 3.54 blocks away
    assert recovery_goal(obs(observed_map=far), "r").kind == "explore"


def outcome(observation: Observation, events: list[dict[str, Any]], **update: Any) -> StepResult:
    return StepResult.model_validate({"observation": observation.model_dump(), "actual_ticks": 20, "events": events,
        "terminated": False, "truncated": False, "invalid": False, "reason": "wait_completed", "clock_mode": "mock",
        "pause_verified": False, "stable_boundary": True, "wall_seconds": 0.0, **update})


HOLD = [{"kind": "wait", "source": "mock"}, {"kind": "safe_hold", "quantity": 20, "source": "mock"}]


@pytest.mark.parametrize("goal, after, events, direct, update, expected", [
    # direct event plus stock; stock alone (provided) is never completion
    ({"kind": "craft", "target": "stick", "quantity": 4}, {"inventory": {"stick": 4}}, [], 1, {}, True),
    ({"kind": "craft", "target": "stick", "quantity": 4}, {"inventory": {"stick": 4}}, [], 0, {}, False),
    ({"kind": "smelt", "target": "iron_ingot", "quantity": 1}, {"inventory": {"iron_ingot": 1}}, [], 1, {"invalid": True}, False),
    ({"kind": "mine_diamond", "target": "diamond", "quantity": 1}, {"inventory": {"diamond": 1}}, [], 1, {}, True),
    # explore: 16 newly observed open cells, or the target resource newly observed
    ({"kind": "explore", "target": "space", "quantity": 1},
     {"observed_map": [{"block": "air", "position": [float(x), 70.0, 0.0], "passable": True} for x in range(16)]}, [], 0, {}, True),
    ({"kind": "explore", "target": "space", "quantity": 1},
     {"observed_map": [{"block": "air", "position": [float(x), 70.0, 0.0], "passable": True} for x in range(15)]}, [], 0, {}, False),
    ({"kind": "explore", "target": "iron_ore", "quantity": 1},
     {"observed_map": [{"block": "iron_ore", "position": [4.0, 60.0, 0.0]}]}, [], 0, {}, True),
    # escape: 3+ blocks from every observed hazard and an uninterrupted 20-tick safe hold
    ({"kind": "escape", "target": "hazard", "quantity": 1},
     {"observed_map": [{"block": "lava", "position": [4.0, 64.0, 0.0], "hazard": True}]}, HOLD, 0, {}, True),
    ({"kind": "escape", "target": "hazard", "quantity": 1},
     {"observed_map": [{"block": "lava", "position": [2.0, 64.0, 0.0], "hazard": True}]}, HOLD, 0, {}, False),
    ({"kind": "escape", "target": "hazard", "quantity": 1},
     {"observed_map": [{"block": "lava", "position": [4.0, 64.0, 0.0], "hazard": True}]}, HOLD, 0, {"stable_boundary": False}, False),
    # descend: iron pickaxe, y=5-12, safe hold
    ({"kind": "descend", "target": "safe_mining_zone", "quantity": 1},
     {"position": [0.5, 11.0, 0.5], "inventory": {"iron_pickaxe": 1}}, HOLD, 0, {}, True),
    ({"kind": "descend", "target": "safe_mining_zone", "quantity": 1},
     {"position": [0.5, 13.0, 0.5], "inventory": {"iron_pickaxe": 1}}, HOLD, 0, {}, False),
])
def test_completion_rules_as_event_fixtures(goal: dict[str, Any], after: dict[str, Any], events: list[dict[str, Any]],
                                            direct: int, update: dict[str, Any], expected: bool) -> None:
    rule = Goal.model_validate({"goal_id": "g:1", **goal})
    assert completed(rule, obs(), outcome(obs(**after), events, **update), direct) is expected


# --- Selector S ----------------------------------------------------------------------------------------------------

def candidate(index: int, action: str, stop: str = "rule", **params: Any) -> Candidate:
    return Candidate(candidate_id=f"obs-0:c:{index}", action_kind=action, params=params,  # type: ignore[arg-type]
                     max_ticks=20 if action == "wait" else 400, stop_rule_id=stop, source_obs_id="obs-0", description=action)


def walk(index: int, *end: float, length: int = 1) -> Candidate:
    return candidate(index, "move_observed", path=[[0.5, 64.0, 0.5]] * (length - 1) + [list(end)], map_version=0)


def pick(saved: list[Candidate], goal: dict[str, Any] | None = None, failures: tuple[str, ...] = (), **update: Any) -> str:
    chosen = rule_select(obs(**update), Goal.model_validate({"goal_id": "g:1", **(goal or TASK)}), allocate(saved), failures)
    return chosen.candidate_id


def test_s_prefers_direct_goal_work_then_approach_then_search_then_plain_wait() -> None:
    mine = candidate(3, "mine_visible_cluster", block="oak_log", blocks=[[1.0, 64.0, 0.0]], map_version=0)
    approach, search = walk(1, 6.5, 64.0, 0.5), walk(2, -3.5, 64.0, 0.5, length=5)
    wait = candidate(0, "wait")
    cells = [{"block": "oak_log", "position": [8.0, 64.0, 0.0]}]
    assert pick([wait, search, approach, mine], observed_map=cells) == mine.candidate_id
    assert pick([wait, search, approach], observed_map=cells) == approach.candidate_id
    assert pick([wait, search], observed_map=cells) == search.candidate_id
    other = candidate(4, "mine_visible_cluster", block="stone", blocks=[[1.0, 64.0, 0.0]], map_version=0)
    assert pick([other, mine]) == mine.candidate_id


def test_s_avoids_observed_hazards_before_relevance_and_recent_failures_before_hazards() -> None:
    lava = [{"block": "lava", "position": [5.0, 64.0, 0.0], "hazard": True}]
    near = candidate(0, "mine_visible_cluster", block="oak_log", blocks=[[4.0, 64.0, 0.0]], map_version=0)
    away = walk(1, -3.5, 64.0, 0.5)
    assert pick([near, away], observed_map=lava) == away.candidate_id
    assert pick([near, away], failures=(signature(away),), observed_map=lava) == near.candidate_id
    # every candidate failed recently: the key ties and the other rules decide
    assert pick([near, away], failures=(signature(away), signature(near)), observed_map=lava) == away.candidate_id


def test_s_breaks_ties_by_saved_order_and_prefers_the_larger_workload() -> None:
    a, b = walk(0, 3.5, 64.0, 0.5), walk(1, -3.5, 64.0, 0.5)
    assert pick([a, b]) == a.candidate_id and pick([b, a]) == b.candidate_id
    short = candidate(0, "tunnel", direction=[1, 0], cells=2, height=2, map_version=0)
    long = candidate(1, "tunnel", direction=[0, 1], cells=8, height=2, map_version=0)
    assert pick([short, long]) == long.candidate_id


def test_s_holds_for_descend_and_escape_and_walks_away_from_the_hazard() -> None:
    hold = candidate(2, "wait", stop="hold_or_hazard")
    stair = candidate(1, "stair_down", direction=[1, 0], stairs=4, map_version=0)
    descend = {"goal_id": "g", "kind": "descend", "target": "safe_mining_zone", "quantity": 1}
    assert pick([walk(0, 3.5, 64.0, 0.5), stair], descend) == stair.candidate_id
    assert pick([walk(0, 3.5, 64.0, 0.5), stair, hold], descend) == hold.candidate_id
    escape = {"goal_id": "g", "kind": "escape", "target": "hazard", "quantity": 1}
    lava = [{"block": "lava", "position": [1.0, 64.0, 0.0], "hazard": True}]
    toward, away = walk(0, 0.5, 64.0, 1.5, length=2), walk(1, -3.5, 64.0, 0.5, length=2)
    assert pick([toward, away], escape, observed_map=lava) == away.candidate_id


def test_s_returns_one_offered_id_from_a_capped_set_with_its_rule_record() -> None:
    found = [walk(i, float(i) + 3.5, 64.0, 0.5) for i in range(21)]
    saved = allocate(found)
    assert (len(saved.candidates), saved.generated) == (16, 21)
    chosen = rule_select(obs(), Goal.model_validate(TASK), saved, ())
    assert chosen.candidate_id in [c.candidate_id for c in saved.candidates]
    assert (chosen.selector_mode, chosen.probabilities, chosen.provider, chosen.model, chosen.usage) == (
        "rule_deterministic", None, None, None, None)
    assert chosen.rule_version == "s-rules-v1"
    assert chosen.rule_hash == RULE_HASH == hashlib.sha256(Path("src/mc_diamond/selectors.py").read_bytes()).hexdigest()
    assert chosen.rule_keys is not None and set(chosen.rule_keys) == {c.candidate_id for c in saved.candidates}
    masked = saved.model_copy(update={"mask": [c.candidate_id != chosen.candidate_id for c in saved.candidates]})
    assert rule_select(obs(), Goal.model_validate(TASK), masked, ()).candidate_id != chosen.candidate_id


def test_s_cli_moves_off_a_recently_failed_action_and_is_blind_to_hidden_state(tmp_path: Path) -> None:
    plan = steps((20, FAILED, {}), (20, ACQUIRED, {"oak_log": 1}))
    runs = []
    for name, verification in [("plain", None), ("hidden", {"natural": True, "records": [{"block": "diamond_ore"}]})]:
        (tmp_path / name).mkdir()
        result, output = run(tmp_path / name, plan, select="rule", task={**TASK, "quantity": 1}, verification=verification)
        assert result.returncode == 0, result.stderr
        selections = kind(output, "selection")
        assert [s["selector_mode"] for s in selections] == ["rule_deterministic"] * 2
        assert [r["actor_exclusion_reason"] for r in kind(output, "reward")] == ["rule_selector"] * 2
        # the first log failed; the same action is offered again and S takes the other log
        assert [chosen(output, i)["params"]["blocks"] for i in (0, 1)] == [[[0.0, 64.0, 1.0]], [[1.0, 64.0, 0.0]]]
        runs.append([{k: v for k, v in s.items() if k != "latency_seconds"} for s in selections])
    assert runs[0] == runs[1]
    _, fixed = run(tmp_path, plan, task={**TASK, "quantity": 1})
    assert chosen(fixed, 1)["params"]["blocks"] == [[0.0, 64.0, 1.0]]  # the fixed selector repeats the failed log


@pytest.mark.parametrize("cells, mode, probabilities", [
    ([], "forced_wait", True),
    ([{"block": "oak_log", "position": [1.0, 64.0, 0.0], "support": True}], "rule_deterministic", True),
])
def test_s_cli_keeps_the_common_zero_and_single_candidate_contract(tmp_path: Path, cells: list[dict[str, Any]],
                                                                   mode: str, probabilities: bool) -> None:
    plan = steps((20, WAIT if not cells else ACQUIRED, {"oak_log": 1} if cells else {}))
    _, output = run(tmp_path, plan, select="rule", initial=observation(observed_map=cells), task={**TASK, "quantity": 1},
                    max_decisions=1)
    selection = kind(output, "selection")[0]
    assert selection["selector_mode"] == mode
    assert selection["probabilities"] == {selection["candidate_id"]: 1.0}
    assert kind(output, "reward")[0]["actor_exclusion_reason"] == ("single_candidate" if cells else "no_candidates")
