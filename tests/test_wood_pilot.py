"""T14 public CLI: real execution/PPO with a tiny model at the downloaded-weight boundary."""

import json
import shutil
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
    initial = {**template["initial"], "remaining_ticks": 1800}
    steps = []
    for i in range(1, 33):
        final = i == 32
        step = {**template["steps"][0], "terminated": final, "reason": "mock_goal_completed" if final else "macro_completed",
                "source_obs_id": f"obs-{i - 1}", "events": [{"kind": "acquired", "item": "cobblestone", "quantity": 1,
                    "event_id": f"stone-{i}", "source": "mock"}] if i in (8, 16, 32) else [{"kind": "stopped", "source": "mock"}]}
        # After the first decision the scripted game already holds the pickaxe and stands next to two exposed stones.
        step["observation"] = {**initial, "obs_id": f"obs-{i}", "active_ticks": i * 20, "remaining_ticks": 1800 - i * 20,
                               "inventory": {"wooden_pickaxe": 1, "cobblestone": sum(i >= n for n in (8, 16, 32))},
                               "tool": "wooden_pickaxe",
                               "observed_map": [{**cell, "block": "stone"} for cell in initial["observed_map"]]}
        step["stop_evidence"] = [f"obs-{i}", step["reason"]]
        steps.append(step)
    fixture = tmp_path / "wood.json"
    fixture.write_text(json.dumps({"initial": initial, "steps": steps, **fixture_updates}))
    config = tmp_path / "wood.yaml"
    config.write_text(yaml.safe_dump({"backend": "mock", "fixture": str(fixture), "max_decisions": 3600, "discovery_reward": .05,
        "goal": {"goal_id": "pilot-wood", "kind": "collect", "target": "cobblestone", "quantity": 3}}))
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
    assert summary["time_tie_ticks"] > 0  # one failed initial slot is charged the full 1,800 ticks
    settings = summary["settings"]
    assert [s["choice_lr"] for s in settings] == [1e-4, 3e-4]
    assert settings[0]["initial_hashes"] == settings[1]["initial_hashes"]
    for setting in settings:
        assert setting["collected_decisions"] == 1024
        assert len(setting["updates"]) == 8
        assert all(u["valid_transitions"] == 128 for u in setting["updates"])
        assert setting["actor_transitions"] == 896 and setting["backbone_unchanged"]  # first rollout is critic-only
        assert setting["updates"][0]["actor_skipped"] and not setting["updates"][1]["actor_skipped"]
        assert setting["choice_changed"] and setting["critic_changed"] and setting["usable"]
        assert [p["update"] for p in setting["start_state_probes"]] == list(range(9))
        assert all(0 <= p["normalized_entropy"] <= 1.000001 for p in setting["start_state_probes"])
        assert setting["start_state_probes"][0]["probabilities"] == setting["start_state_probes"][1]["probabilities"]
        assert setting["episode_halves"]["first"]["episodes"] == setting["episode_halves"]["last"]["episodes"] == 16
        diagnostics = setting["episodes"][0]["diagnostics"]
        assert diagnostics["first_pickaxe_tick"] == diagnostics["first_stone_visible_tick"] == 20
        assert diagnostics["first_cobblestone_tick"] == 160
        assert diagnostics["discovery_awards"] == 1
        assert len(diagnostics["mc_returns"]) == 32
        assert setting["mc_critic"]["transitions"] == 1024
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
        assert attempt["direct_cobblestone"] == 3 and attempt["planner_calls"] == 0
        assert attempt["diagnostics"]["discovery_awards"] == 1
        assert len(attempt["diagnostics"]["mc_returns"]) == 32
    import gzip
    traces = list((tmp_path / "pilot" / "baseline").glob("*.jsonl.gz"))
    with gzip.open(traces[0], "rt") as handle:
        goal = next(json.loads(line)["data"] for line in handle if json.loads(line)["type"] == "goal")
    assert goal["target"] == "cobblestone" and goal["quantity"] == 3 and goal["source"] == "fixed"
    episode_actor_total = 0
    for trace in (tmp_path / "pilot" / "baseline").glob("lr-0.0001-train-*.jsonl.gz"):
        with gzip.open(trace, "rt") as handle:
            for line in handle:
                row = json.loads(line)
                if row["type"] == "summary":
                    episode_actor_total += row["data"]["actor_transitions"]
    assert episode_actor_total == 896  # per-episode summaries must not repeat the learner's cumulative count
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
    assert main() == 1  # a usable LR1e-4 setting cannot be supplemented
    assert not (tmp_path / "pilot" / "correction").exists()
    capsys.readouterr()


def test_wrong_reset_budget_defers_settings_but_keeps_all_slots_and_restores(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    bad = json.loads(Path("fixtures/model_episode.json").read_text())["initial"]  # 100 ticks instead of 1,800
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
    assert first["episodes"][0]["direct_cobblestone"] == 1
    assert first["episodes"][0]["reward_total"] == pytest.approx(.05 - .1 * 160 / 1800)
    assert len(summary["evaluations"]) == 30


def test_final_verification_failure_excludes_training_attempt_from_mc_ev(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from mc_diamond.rpc import EpisodeError, RpcSession
    from mc_diamond.schema import ErrorInfo
    def failed_verification(*args: Any, **kwargs: Any) -> Any:
        raise EpisodeError(ErrorInfo(code="invalid_step", message="final verification failed after terminal transition"))
    monkeypatch.setattr(RpcSession, "verification_log", failed_verification)
    status, summary, _ = pilot_cli(tmp_path, monkeypatch, capsys)
    assert status == 1 and summary["restored_initial"]
    for setting in summary["settings"]:
        assert not setting["episodes"][0]["valid"]
        assert setting["mc_critic"] == {"transitions": 0, "explained_variance": None}


def test_failed_lr1e4_supplement_reuses_initial_evaluation_and_preserves_original_run(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    status, original, model = pilot_cli(tmp_path, monkeypatch, capsys,
                                      server_error_attempts=["lr-0.0001-train-3:1"])
    assert status == 0 and not original["settings"][0]["usable"] and original["settings"][1]["usable"]
    from mc_diamond.cli import main
    directory = tmp_path / "pilot"
    baseline = (directory / "baseline/summary.json").read_bytes()
    args = list(sys.argv)
    monkeypatch.setattr(sys, "argv", [*args, "--correction-reason", "approved", "--correction-lr", "0.0003"])
    assert main() == 1 and not (directory / "correction").exists()
    monkeypatch.setattr(sys, "argv", [*args, "--correction-reason", "approved startup recovery supplement",
                                      "--correction-lr", "0.0001"])
    manifest = directory / "baseline/manifest.json"
    manifest_bytes = manifest.read_bytes()
    changed = json.loads(manifest_bytes)
    changed["input_hash"] = "mismatched policy input"
    manifest.write_text(json.dumps(changed))
    assert main() == 1 and not (directory / "correction").exists()
    manifest.write_bytes(manifest_bytes)
    assert main() == 0
    corrected = json.loads((directory / "correction/summary.json").read_text())
    assert corrected["planned_slots"] == len(corrected["evaluations"]) == 10
    assert corrected["restored_initial"]
    assert len(corrected["settings"]) == 1
    record = corrected["settings"][0]
    assert record["choice_lr"] == 1e-4 and record["usable"] and record["collected_decisions"] == 1024
    assert len(record["updates"]) == 8 and record["updates"][0]["actor_skipped"]
    assert record["initial_hashes"] == original["settings"][1]["initial_hashes"]
    assert corrected["time_tie_ticks"] == original["time_tie_ticks"]
    assert corrected["comparison"]["prior_failed_setting_errors"] == ["backend_error"]
    assert corrected["selected_choice_lr"] == 3e-4  # equal score/time: retain the original LR1e-4 backend error
    assert all(row["phase"] == "lr-0.0001" and row["success"] for row in corrected["evaluations"])
    assert not list((directory / "correction").glob("initial-eval*"))
    assert (directory / "baseline/summary.json").read_bytes() == baseline
    saved = (directory / "correction/summary.json").read_bytes()
    assert main() == 1
    assert (directory / "correction/summary.json").read_bytes() == saved
    # A failed supplement stays a failure even though the completed original LR3e-4 is still selectable.
    other = tmp_path / "failed-supplement"
    shutil.copytree(directory / "baseline", other / "baseline")
    def model_failure(encoded: Any) -> Any:
        raise RuntimeError("supplement numerical failure")
    model.encode_candidates = model_failure
    monkeypatch.setattr(sys, "argv", [*args[:-1], str(other), "--correction-reason", "approved startup supplement"])
    assert main() == 1
    failed = json.loads((other / "correction/summary.json").read_text())
    assert failed["selected_choice_lr"] == 3e-4 and not failed["settings"][0]["usable"]
    assert failed["restored_initial"] and len(failed["evaluations"]) == 10
    assert all(not r["attempts"] for r in failed["evaluations"])
    capsys.readouterr()


@pytest.mark.parametrize(("successes", "ticks", "errors", "usable", "expected"), [
    ([1, 2], [10, 100], [0, 0], [True, True], 3e-4),
    ([1, 1], [100, 20], [0, 1], [True, True], 3e-4),
    ([0, 0], [1, 100], [2, 0], [True, True], 3e-4),
    ([0, 0], [1, 100], [0, 0], [True, True], 1e-4),
    ([3, 1], [10, 100], [0, 0], [False, True], 3e-4),
    ([0, 0], [10, 100], [1, 1], [False, False], None),
])
def test_selection_charges_failures_the_full_budget_and_excludes_unusable_settings(
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
        "discovery_reward": .05,
        "goal": {"goal_id": "wood", "kind": "collect", "target": "cobblestone", "quantity": 3}}))
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
