"""T12 (#13): planned evaluation slots through the public `evaluate` CLI on the mock backend.

Mock slots never stand for Minecraft or model results; the summary keeps `mock: true`.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from mc_diamond.evaluation import EvaluationConfig, schedule

FIXTURE: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text())


def config(tmp_path: Path, *, fixture: dict[str, Any] | None = None, **update: Any) -> Path:
    (tmp_path / "fixture.json").write_text(json.dumps(fixture or FIXTURE), encoding="utf-8")
    episode = {"backend": "mock", "fixture": str(tmp_path / "fixture.json"), "max_decisions": 4,
               "goal": {"goal_id": "mock-task", "kind": "collect", "target": "oak_log", "quantity": 1}}
    (tmp_path / "episode.yaml").write_text(yaml.safe_dump(episode), encoding="utf-8")
    data = {"episodes": {"C4": "episode.yaml", "G4": "episode.yaml"}, "evaluation_seeds": [11, 12, 13, 14, 15],
            "g4_seeds": [21, 22, 23], "fixed_seed": 7, "budget_usd": 5.0, **update}
    (tmp_path / "evaluation.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return tmp_path / "evaluation.yaml"


def evaluate(path: Path, groups: str, task: str) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    result = subprocess.run(["mc-diamond", "evaluate", "--config", str(path), "--groups", groups, "--task", task],
                            capture_output=True, text=True, timeout=120)
    return result, [json.loads(line) for line in result.stdout.splitlines()]


def kind(output: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [row["data"] for row in output if row["type"] == name]


def slots(output: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["slot"]["slot_id"]: row for row in kind(output, "slot_result")}


def failing(*attempts: str) -> dict[str, Any]:
    return {**FIXTURE, "server_error_attempts": list(attempts)}


def base() -> EvaluationConfig:
    return EvaluationConfig.model_validate({"episodes": {"C4": "c4.yaml", "G4": "g4.yaml"},
                                            "evaluation_seeds": [11, 12, 13, 14, 15], "g4_seeds": [21, 22, 23]})


@pytest.mark.parametrize("scale, core, g4", [("core", 22, 6), ("reduced", 14, 6)])
def test_schedule_fixes_core_g4_and_the_separate_s_denominators(scale: str, core: int, g4: int) -> None:
    plan = schedule(base().model_copy(update={"scale": scale}))
    by_table = {table: [s for s in plan if s.table == table] for table in ("core_c4", "g4", "s")}
    assert [len(by_table[t]) for t in ("core_c4", "g4", "s")] == [core, g4, 1]
    assert len(plan) == core + g4 + 1 == (29 if scale == "core" else 21)
    assert len({s.slot_id for s in plan}) == len(plan)
    runs = 5 if scale == "core" else 3
    seeds = {(s.group, s.mode): [x.seed for x in plan if (x.group, x.mode, x.table) == (s.group, s.mode, "core_c4")]
             for s in by_table["core_c4"]}
    assert seeds[("A", "sampling")] == seeds[("B", "sampling")] == [11, 12, 13, 14, 15][:runs]  # A/B share the list
    assert len(seeds[("A", "argmax")]) == len(seeds[("B", "argmax")]) == 1
    assert seeds[("J", "sampling")] == seeds[("F", "sampling")] == seeds[("A", "sampling")]  # verified Jev distribution (T11)
    assert sorted((s.group, s.seed) for s in by_table["g4"]) == [("A", 21), ("A", 22), ("A", 23), ("B", 21), ("B", 22), ("B", 23)]
    assert [(s.group, s.task, s.mode) for s in by_table["s"]] == [("S", "C4", "rule_deterministic")]
    # evaluation blocks interleave the groups (§9.3): block i runs A, B, J, F with the i-th seed
    mode = {"A": "sampling", "B": "sampling", "J": "sampling", "F": "sampling"}
    assert [s.group for s in by_table["core_c4"] if s.mode == mode[s.group]][:8] == list("ABJFABJF")
    assert [s.group for s in by_table["g4"]][:2] == ["A", "B"]


def test_server_error_then_successful_retry_is_one_successful_slot(tmp_path: Path) -> None:
    result, output = evaluate(config(tmp_path, fixture=failing("core_c4-A-sampling-1:1")), "A", "C4")
    assert result.returncode == 0, result.stderr
    first = slots(output)["core_c4-A-sampling-1"]
    assert (first["outcome"], first["success"], first["retry"]) == ("success", True, "used")
    assert [(a["attempt_id"], a["error_code"], a["success"]) for a in first["attempts"]] == [
        ("core_c4-A-sampling-1:1", "backend_error", False), ("core_c4-A-sampling-1:2", None, True)]
    assert first["first_error"] == "backend_error"
    assert {a["seed"] for a in first["attempts"]} == {11} and len({a["snapshot"] for a in first["attempts"]}) == 1
    table = kind(output, "evaluation_summary")[0]["tables"]["core_c4"]
    assert (table["planned"], table["successes"], table["errors"], table["attempts"], table["retries_used"]) == (6, 6, 0, 7, 1)
    assert table["active_ticks"] == sum(a["active_ticks"] for s in slots(output).values() for a in s["attempts"])
    assert len(kind(output, "reset")) == 7  # every attempt starts from its own reset
    assert kind(output, "evaluation_summary")[0]["mock"] is True


def test_two_server_errors_leave_an_error_slot_in_the_denominator(tmp_path: Path) -> None:
    _, output = evaluate(config(tmp_path, fixture=failing("core_c4-A-argmax-1:1", "core_c4-A-argmax-1:2")), "A", "C4")
    slot = slots(output)["core_c4-A-argmax-1"]
    assert (slot["outcome"], slot["success"], slot["retry"], len(slot["attempts"])) == ("error", False, "used", 2)
    table = kind(output, "evaluation_summary")[0]["tables"]["core_c4"]
    assert (table["planned"], table["successes"], table["errors"]) == (6, 5, 1)


@pytest.mark.parametrize("change, reason", [
    ({"health": 0.0}, "death"),            # dying is a behaviour result, never a server error
    ({"active_ticks": 99}, "invalid_step"),  # a contract error is not a server error either
])
def test_behaviour_failures_and_contract_errors_are_never_retried(tmp_path: Path, change: dict[str, Any], reason: str) -> None:
    fixture = json.loads(json.dumps(FIXTURE))
    step = fixture["steps"][0]
    step["observation"].update(change, inventory={})
    step.update(events=[{"kind": "stopped", "source": "mock"}], reason=reason, stop_evidence=["obs-1", reason])
    _, output = evaluate(config(tmp_path, fixture=fixture), "B", "G4")
    results = slots(output)
    assert len(results) == 3 and all(len(r["attempts"]) == 1 and r["retry"] == "none" and not r["success"]
                                     for r in results.values())
    expected = "error" if reason == "invalid_step" else "failure"
    assert {r["outcome"] for r in results.values()} == {expected}


def test_cost_stop_keeps_unrun_slots_and_an_unrun_retry_in_the_denominator(tmp_path: Path) -> None:
    path = config(tmp_path, fixture=failing("core_c4-J-sampling-3:1"), budget_usd=2.5, mock_cost_per_decision_usd=1.0)
    _, output = evaluate(path, "J", "C4")
    results = slots(output)
    assert [results[f"core_c4-J-sampling-{i}"]["outcome"] for i in range(1, 6)] == [
        "success", "success", "error", "not_run", "not_run"]
    assert results["core_c4-J-sampling-3"]["retry"] == "not_run_budget"
    assert results["core_c4-J-sampling-4"]["not_run_reason"] == "budget_stopped"
    summary = kind(output, "evaluation_summary")[0]
    table = summary["tables"]["core_c4"]
    assert (table["planned"], table["successes"], table["errors"], table["not_run"], table["retries_not_run"]) == (5, 2, 1, 2, 1)
    assert summary["spent_usd"] == table["cost_usd"] == 3.0
    assert all(s["usage"] == {"cost_usd": 1.0} for s in kind(output, "selection"))


def test_unavailable_reference_groups_stay_planned_as_not_run(tmp_path: Path) -> None:
    _, output = evaluate(config(tmp_path, astra_available=False), "J,F", "C4")
    results = slots(output)
    assert {r["not_run_reason"] for k, r in results.items() if "-F-" in k} == {"astra_unavailable"}
    assert {r["outcome"] for k, r in results.items() if "-J-" in k} == {"success"}
    assert kind(output, "evaluation_summary")[0]["tables"]["core_c4"]["planned"] == 10


def test_jev_unavailable_still_runs_local_a_b_and_keeps_j_f_planned(tmp_path: Path) -> None:
    result, output = evaluate(config(tmp_path, jev_available=False), "A,B,J,F", "C4")
    assert result.returncode == 0, result.stderr
    results = slots(output)
    assert {r["outcome"] for k, r in results.items() if "-A-" in k or "-B-" in k} == {"success"}
    assert {r["not_run_reason"] for k, r in results.items() if "-J-" in k or "-F-" in k} == {"jev_unavailable"}
    assert kind(output, "evaluation_summary")[0]["tables"]["core_c4"]["planned"] == 22


def test_s_slot_uses_the_rule_selector_and_reports_its_own_table(tmp_path: Path) -> None:
    result, output = evaluate(config(tmp_path), "S", "C4")
    assert result.returncode == 0, result.stderr
    assert {s["selector_mode"] for s in kind(output, "selection")} == {"rule_deterministic"}
    summary = kind(output, "evaluation_summary")[0]
    assert set(summary["tables"]) == {"s"} and summary["tables"]["s"]["planned"] == 1
    assert summary["s_diagnostic"] == {"success": "1/1", "highest_stage": 1, "active_ticks": 20,
        "wall_seconds": summary["s_diagnostic"]["wall_seconds"], "selections": 1, "planner_calls": 0,
        "failure_reason": None, "api_cost_usd": 0.0, "cost_usd": None, "outcome": "success"}  # 7B/GPU cost unmeasured


def test_s_server_errors_keep_its_single_planned_slot_and_every_attempt(tmp_path: Path) -> None:
    _, output = evaluate(config(tmp_path, fixture=failing("s-S-rule_deterministic-1:1", "s-S-rule_deterministic-1:2")), "S", "C4")
    slot = slots(output)["s-S-rule_deterministic-1"]
    assert (slot["outcome"], slot["retry"], [a["error_code"] for a in slot["attempts"]]) == (
        "error", "used", ["backend_error", "backend_error"])
    summary = kind(output, "evaluation_summary")[0]
    assert summary["tables"]["s"]["planned"] == 1 and summary["s_diagnostic"]["success"] == "0/1"
    assert summary["s_diagnostic"]["wall_seconds"] == sum(a["wall_seconds"] for a in slot["attempts"]) > 0


def test_budget_counts_spend_recorded_before_this_run(tmp_path: Path) -> None:
    _, output = evaluate(config(tmp_path, budget_usd=5.0, jev_spent_usd=4.5, mock_cost_per_decision_usd=1.0), "J", "C4")
    assert [r["outcome"] for r in slots(output).values()] == ["success"] + ["not_run"] * 4
    assert kind(output, "evaluation_summary")[0]["spent_usd"] == 5.5


def test_budget_continues_from_the_jev_ledger(tmp_path: Path) -> None:
    (tmp_path / "ledger.jsonl").write_text('{"cost_usd": 4.0}\n{"cost_usd": null}\n')  # 4.0 confirmed + 1 unconfirmed request
    _, output = evaluate(config(tmp_path, budget_usd=5.0, jev_ledger=str(tmp_path / "ledger.jsonl"),
                                mock_cost_per_decision_usd=1.0), "J", "C4")
    assert [r["outcome"] for r in slots(output).values()] == ["success"] + ["not_run"] * 4
    assert kind(output, "evaluation_summary")[0]["spent_usd"] == pytest.approx(5.001)


@pytest.mark.parametrize("groups, task", [("X", "C4"), ("A", "C5")])
def test_unknown_groups_or_tasks_are_rejected(tmp_path: Path, groups: str, task: str) -> None:
    result, _ = evaluate(config(tmp_path), groups, task)
    assert result.returncode == 2


def test_unconnected_selectors_refuse_the_actual_backend(tmp_path: Path) -> None:
    path = config(tmp_path)
    episode = yaml.safe_load((tmp_path / "episode.yaml").read_text())
    episode.pop("fixture")
    episode.update(backend="rpc", command=["node", "bridge/minecraft.js", "--task", "C4"])
    (tmp_path / "episode.yaml").write_text(yaml.safe_dump(episode), encoding="utf-8")
    result, output = evaluate(path, "A", "C4")
    assert result.returncode == 2
    assert kind(output, "error")[0]["code"] == "invalid_config"


def test_shipped_mock_schedule_runs_every_planned_slot_in_separate_tables() -> None:
    result, output = evaluate(Path("configs/evaluation_mock.yaml"), "A,B,J,F,S", "C4,G4")
    assert result.returncode == 0, result.stderr
    summary = kind(output, "evaluation_summary")[0]
    assert {table: row["planned"] for table, row in summary["tables"].items()} == {"core_c4": 22, "g4": 6, "s": 1}
    assert summary["mock"] is True and len(kind(output, "slot_result")) == 29
