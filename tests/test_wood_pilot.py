"""T14 public CLI: real execution/PPO with a tiny model at the downloaded-weight boundary."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml


def pilot_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
              fail_on_call: int | None = None, **fixture_updates: object) -> tuple[int, dict[str, Any], Any]:
    torch = pytest.importorskip("torch")
    from mc_diamond.cli import main
    from mc_diamond.nanojev import NanoJevAdapter, parameter_hash
    from test_model import tiny_adapter
    torch.set_num_threads(1)
    model = tiny_adapter()

    class Tokenizer:
        eos_token_id = 1
        pad_token_id = 0

        def encode(self, value: str, add_special_tokens: bool) -> list[int]:
            return [ord(c) % 128 for c in value]

    model.tokenizer = Tokenizer()
    if fail_on_call is not None:
        encode = model.encode_candidates
        calls = 0
        def failing_encode(encoded: Any) -> Any:
            nonlocal calls
            calls += 1
            if calls >= fail_on_call:
                raise RuntimeError("Numerical model failure after partial game progress")
            return encode(encoded)
        model.encode_candidates = failing_encode
    initial_hash = parameter_hash(model)
    monkeypatch.setattr(NanoJevAdapter, "load", classmethod(lambda cls, root: model))
    template = json.loads(Path("fixtures/model_episode.json").read_text())
    initial = {**template["initial"], "remaining_ticks": 3600}
    steps = []
    for i in range(1, 33):
        final = i == 32
        step = {**template["steps"][0], "terminated": final, "reason": "mock_goal_completed" if final else "macro_completed",
                "source_obs_id": f"obs-{i - 1}", "events": [{"kind": "acquired", "item": "oak_log", "quantity": 1,
                    "event_id": f"log-{i}", "source": "mock"}] if i % 8 == 0 else [{"kind": "stopped", "source": "mock"}]}
        step["observation"] = {**initial, "obs_id": f"obs-{i}", "active_ticks": i * 20,
                               "remaining_ticks": 3600 - i * 20, "inventory": {"oak_log": i // 8}}
        step["stop_evidence"] = [f"obs-{i}", step["reason"]]
        steps.append(step)
    fixture = tmp_path / "wood.json"
    fixture.write_text(json.dumps({"initial": initial, "steps": steps, **fixture_updates}))
    config = tmp_path / "wood.yaml"
    config.write_text(yaml.safe_dump({"backend": "mock", "fixture": str(fixture), "max_decisions": 3600,
        "goal": {"goal_id": "pilot-wood", "kind": "collect", "target": "oak_log", "quantity": 4}}))
    monkeypatch.setattr(sys, "argv", ["mc-diamond", "pilot-wood", "--config", str(config), "--output", str(tmp_path / "pilot")])
    status = main()
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert output[-1]["type"] == "pilot_summary", output[-2:]
    summary = output[-1]["data"]
    assert parameter_hash(model) == initial_hash
    return status, summary, model


def test_pilot_cli_runs_two_complete_settings_and_restores_initial_actor(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    status, summary, _ = pilot_cli(tmp_path, monkeypatch, capsys, server_error_attempts=[
        "initial-eval-1:1", "initial-eval-2:1", "initial-eval-2:2"])
    assert status == 0, summary
    assert summary["mock"] and summary["restored_initial"]
    assert summary["planned_slots"] == 30 and len(summary["evaluations"]) == 30
    assert summary["selected_choice_lr"] == 1e-4
    assert summary["main_training_decisions"] == 0
    settings = summary["settings"]
    assert [s["choice_lr"] for s in settings] == [1e-4, 3e-4]
    assert settings[0]["initial_hashes"] == settings[1]["initial_hashes"]
    for setting in settings:
        assert setting["collected_decisions"] == 1024
        assert len(setting["updates"]) == 8
        assert all(u["valid_transitions"] == 128 for u in setting["updates"])
        assert setting["actor_transitions"] == 1024 and setting["backbone_unchanged"]
        assert setting["choice_changed"] and setting["critic_changed"] and setting["usable"]
    groups = [[r for r in summary["evaluations"] if r["phase"] == phase] for phase in ["initial", "lr-0.0001", "lr-0.0003"]]
    assert [[r["seed"] for r in group] for group in groups] == [list(range(15000, 15010))] * 3
    for row in summary["evaluations"]:
        if row["slot_id"] == "initial-eval-2":
            assert not row["success"] and len(row["attempts"]) == 2
            continue
        assert row["success"] and len(row["attempts"]) == (2 if row["slot_id"] == "initial-eval-1" else 1)
        attempt = row["attempts"][0]
        if row["slot_id"] == "initial-eval-1":
            assert row["attempts"][0]["seed"] == row["attempts"][1]["seed"]
            assert row["attempts"][0]["snapshot"] == row["attempts"][1]["snapshot"]
            attempt = row["attempts"][-1]
        assert attempt["direct_logs"] == 4 and attempt["planner_calls"] == 0
    import gzip
    traces = list((tmp_path / "pilot" / "baseline").glob("*.jsonl.gz"))
    with gzip.open(traces[0], "rt") as handle:
        goal = next(json.loads(line)["data"] for line in handle if json.loads(line)["type"] == "goal")
    assert goal["quantity"] == 4 and goal["source"] == "fixed"
    from mc_diamond.cli import main
    baseline = (tmp_path / "pilot" / "baseline" / "summary.json").read_bytes()
    assert main() == 1  # existing campaign cannot be overwritten or silently extended
    assert (tmp_path / "pilot" / "baseline" / "summary.json").read_bytes() == baseline
    original_args = list(sys.argv)
    monkeypatch.setattr(sys, "argv", [*original_args, "--correction-reason", "invalid LR", "--correction-lr", "0"])
    assert main() == 1
    assert not (tmp_path / "pilot" / "correction").exists()
    monkeypatch.setattr(sys, "argv", original_args)
    monkeypatch.setattr(sys, "argv", [*sys.argv, "--correction-reason", "verified execution correction"])
    assert main() == 0
    corrected = json.loads((tmp_path / "pilot" / "correction" / "summary.json").read_text())
    assert corrected["planned_slots"] == 20 and len(corrected["evaluations"]) == 20
    assert len(corrected["settings"]) == 1 and corrected["selected_choice_lr"] == 1e-4
    assert corrected["restored_initial"]
    saved = (tmp_path / "pilot" / "correction" / "summary.json").read_bytes()
    assert main() == 1  # a second corrective pilot is never launched
    assert (tmp_path / "pilot" / "correction" / "summary.json").read_bytes() == saved
    capsys.readouterr()


def test_wrong_reset_budget_defers_settings_but_keeps_all_slots_and_restores(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    bad = json.loads(Path("fixtures/model_episode.json").read_text())["initial"]  # 100 ticks instead of 3,600
    status, summary, _ = pilot_cli(tmp_path, monkeypatch, capsys, initial=bad)
    assert status == 1 and summary["selected_choice_lr"] is None and summary["restored_initial"]
    assert len(summary["evaluations"]) == 30
    assert all(not r["success"] for r in summary["evaluations"])
    assert all(not s["usable"] and s["collected_decisions"] == 0 for s in summary["settings"])
    assert sum(r["not_run_reason"] == "setting_unusable" for r in summary["evaluations"]) == 20


def test_model_failure_preserves_partial_decisions_time_and_direct_progress(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    status, summary, _ = pilot_cli(tmp_path, monkeypatch, capsys, fail_on_call=329)
    assert status == 1 and summary["selected_choice_lr"] is None and summary["restored_initial"]
    first = summary["settings"][0]
    assert not first["usable"] and first["collected_decisions"] == 8
    assert first["episodes"][0]["active_ticks"] == 160
    assert first["episodes"][0]["direct_logs"] == 1
    assert first["episodes"][0]["reward_total"] < 0
    assert len(summary["evaluations"]) == 30


@pytest.mark.parametrize(("successes", "ticks", "errors", "usable", "expected"), [
    ([1, 2], [10, 100], [0, 0], [True, True], 3e-4),
    ([1, 1], [100, 20], [0, 1], [True, True], 3e-4),
    ([0, 0], [1, 100], [2, 0], [True, True], 3e-4),
    ([0, 0], [1, 100], [0, 0], [True, True], 1e-4),
    ([3, 1], [10, 100], [0, 0], [False, True], 3e-4),
    ([0, 0], [10, 100], [1, 1], [False, False], None),
])
def test_selection_uses_only_successful_times_and_excludes_unusable_settings(
        successes: list[int], ticks: list[int], errors: list[int], usable: list[bool], expected: float | None) -> None:
    pytest.importorskip("torch")
    from mc_diamond.wood_pilot import select_setting
    settings: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    for index, lr in enumerate([1e-4, 3e-4]):
        settings.append({"phase": str(index), "choice_lr": lr, "usable": usable[index], "errors": ["error"] * errors[index]})
        evaluations.extend({"phase": str(index), "success": n < successes[index],
                            "attempts": [{"active_ticks": ticks[index] if n < successes[index] else 1}]} for n in range(10))
    assert select_setting(settings, evaluations) == expected


def test_corrective_pilot_requires_baseline_and_a_written_reason(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from mc_diamond.cli import main
    config = tmp_path / "wood.yaml"
    config.write_text(yaml.safe_dump({"backend": "mock", "fixture": str(Path("fixtures/model_episode.json").resolve()),
        "goal": {"goal_id": "wood", "kind": "collect", "target": "oak_log", "quantity": 4}}))
    monkeypatch.setattr(sys, "argv", ["mc-diamond", "pilot-wood", "--config", str(config), "--output", str(tmp_path / "pilot"),
                                      "--correction-reason", "fixed a confirmed execution error"])
    assert main() == 1
    last = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert "baseline" in last["data"]["error"].lower()
    assert not (tmp_path / "pilot" / "correction").exists()


def test_missing_model_dependency_reports_installation_guidance(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    import builtins
    from mc_diamond.cli import main
    original = builtins.__import__
    def without_model(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "wood_pilot":
            raise ImportError("No module named torch")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", without_model)
    monkeypatch.setattr(sys, "argv", ["mc-diamond", "pilot-wood", "--config", "configs/wood_pilot_mock.yaml",
                                      "--output", str(tmp_path / "pilot")])
    assert main() == 2
    last = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert last["type"] == "pilot_summary" and "mc-diamond[model]" in last["data"]["error"]
    assert not (tmp_path / "pilot").exists()
