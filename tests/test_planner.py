"""T09: public planner smoke and the shared provider boundary; games/providers are explicit fixtures."""

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml
import pytest


def test_smoke_planner_executes_regenerated_goal_and_reports_its_source(tmp_path: Path) -> None:
    config = yaml.safe_load(Path("configs/model_smoke.yaml").read_text())
    config.pop("model")
    config["fixture"] = str(Path("fixtures/model_episode.json").resolve())
    config["planner"] = {"backend": "scripted", "outputs": ["invalid", '{"kind":"collect","target":"oak_log","quantity":1}']}
    path = tmp_path / "planner.yaml"
    path.write_text(yaml.safe_dump(config))
    run = subprocess.run(["mc-diamond", "smoke-planner", "--config", str(path)], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    rows: list[dict[str, Any]] = [json.loads(line) for line in run.stdout.splitlines()]
    summary = next(row["data"] for row in rows if row["type"] == "summary")
    assert summary["goal_completed"] and summary["progress_by_source"] == {"regenerated": {"acquired:oak_log": 1}}
    assert (summary["planner_initial_errors"], summary["planner_regeneration_requests"], summary["rule_recoveries"]) == (1, 1, 0)
    assert summary["macro_steps"][0]["goal_source"] == "regenerated"


def test_documented_pilot_command_defaults_to_the_fixed_local_7b(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from mc_diamond.cli import main

    loaded: list[str] = []

    def load(config: Any, path: Path, emit: Any) -> Any:
        loaded.append(config.backend)
        return lambda *_: '{"kind":"collect","target":"oak_log","quantity":1}'

    monkeypatch.setattr("mc_diamond.planner.load_planner", load)
    monkeypatch.setattr("sys.argv", ["mc-diamond", "smoke-planner", "--config", "configs/pilot.yaml"])
    assert main() == 0
    assert loaded == ["local_7b"]
    rows = [json.loads(s) for s in capsys.readouterr().out.splitlines()]
    summary = next(row["data"] for row in rows if row["type"] == "summary")
    assert summary["planner_model"] == "Qwen/Qwen2.5-7B-Instruct" and summary["goal_completed"]


def test_astra_uses_common_prompt_regenerates_once_and_persists_attempt_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from io import BytesIO
    from mc_diamond.cli import main

    requests: list[dict[str, Any]] = []
    replies = iter(["not JSON", '{"kind":"collect","target":"oak_log","quantity":1}'])

    def send(_opener: Any, request: Any, **kwargs: Any) -> BytesIO:
        assert request.headers["Authorization"] == "Bearer test-secret-never-log"
        body = json.loads(request.data)
        requests.append(body)
        return BytesIO(json.dumps({"model": "fixture-astra", "choices": [{"message": {"content": next(replies)}}],
                                   "usage": {"prompt_tokens": 50, "completion_tokens": 20}}).encode())

    monkeypatch.setattr("urllib.request.OpenerDirector.open", send)
    monkeypatch.setenv("ASTRA_API_KEY", "test-secret-never-log")
    config = yaml.safe_load(Path("configs/model_smoke.yaml").read_text())
    config.pop("model")
    config["fixture"] = str(Path("fixtures/model_episode.json").resolve())
    config["planner"] = {"backend": "astra", "provider": "mock-provider", "model": "fixture-astra", "version": "fixture",
        "endpoint": "https://example.invalid/v1/chat/completions", "supported_settings": {"temperature": 0},
        "approved": True, "approval_reference": "mock-only-test", "max_calls": 2, "max_usd": 0.02,
        "request_usd_ceiling": 0.01, "budget_file": "budget.json", "rates_checked_on": "2026-11-09",
        "input_usd_per_million": 1.0, "output_usd_per_million": 2.0}
    path = tmp_path / "planner.yaml"
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr("sys.argv", ["mc-diamond", "smoke-planner", "--config", str(path)])
    assert main() == 0
    output = capsys.readouterr().out
    assert "test-secret-never-log" not in output
    summary = next(json.loads(s)["data"] for s in output.splitlines() if json.loads(s)["type"] == "summary")
    assert summary["planner_model"] == "fixture-astra" and summary["progress_by_source"]["regenerated"]["acquired:oak_log"] == 1
    assert len(requests) == 2 and requests[0]["messages"][0] == requests[1]["messages"][0]
    initial = json.loads(requests[0]["messages"][1]["content"])
    retry = json.loads(requests[1]["messages"][1]["content"])
    assert initial["feedback"] is None and "invalid_json" in retry["feedback"]
    assert initial["observation"]["inventory"] == {} and initial["task"]["target"] == "oak_log"
    assert "candidates" not in initial and "seed" not in initial and "knowledge" in initial
    assert main() == 1  # a new process/episode cannot reset the consumed budget
    assert len(requests) == 2


@pytest.mark.parametrize("reply", ['{"kind":"collect","target":{}}', '{"kind":[],"target":"oak_log"}',
                                  '{"kind":"explore","target":"space","direction":[]}'])
def test_malformed_goal_fields_reach_common_recovery_instead_of_crashing(reply: str) -> None:
    from mc_diamond.goals import Planning
    from mc_diamond.schema import Goal, Observation, PlannerConfig
    state = Observation.model_validate(json.loads(Path("fixtures/model_episode.json").read_text())["initial"])
    task = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    goal, decision = Planning(task, PlannerConfig(backend="scripted", outputs=[reply, reply])).decide(state, "episode_start")
    assert goal.source == "rule_recovery"
    assert isinstance(decision["requests"], list) and len(decision["requests"]) == 2


@pytest.mark.parametrize("broken", ['{"signature":"invalid","calls":-1,"reserved_usd":"-1"}', 'not JSON'])
def test_corrupt_astra_budget_is_never_reset_to_a_fresh_allowance(tmp_path: Path, broken: str) -> None:
    from mc_diamond.planner_budget import reserve
    from mc_diamond.rpc import EpisodeError
    from mc_diamond.schema import AstraPlannerConfig
    settings = AstraPlannerConfig(backend="astra", provider="mock", model="fixture", version="fixture",
        endpoint="https://example.invalid/v1/chat/completions", approved=True, approval_reference="test",
        max_calls=1, max_usd=0.01, request_usd_ceiling=0.01, budget_file="budget.json", rates_checked_on="2026-11-09",
        input_usd_per_million=1.0, output_usd_per_million=2.0)
    path = tmp_path / "budget.json"
    path.write_text(broken)
    with pytest.raises(EpisodeError):
        reserve(settings, path)
    assert path.read_text() == broken


def test_common_prompt_uses_only_validated_bounded_observation_and_rejects_injected_fields() -> None:
    from mc_diamond.planner import messages
    from mc_diamond.schema import Goal, Observation
    observation = Observation.model_validate(json.loads(Path("fixtures/model_episode.json").read_text())["initial"])
    task = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    first = messages(observation, task, None)
    changed = observation.model_copy(update={"episode_id": "different-admin-reset-id", "attempt_id": "other"})
    assert messages(changed, task, None) == first
    assert messages(observation.model_copy(update={"seed": 123}), task, None) == first
    with pytest.raises(ValueError):
        Observation.model_validate({**observation.model_dump(), "seed": 123})


@pytest.mark.parametrize("condition", ["unapproved", "missing_key", "network", "request_error", "bad_schema", "bad_model", "secret_reply"])
def test_astra_access_failures_keep_attempt_costs_and_do_not_become_goal_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, condition: str,
) -> None:
    from io import BytesIO
    from email.message import Message
    from urllib.error import HTTPError, URLError
    from mc_diamond.goals import Planning
    from mc_diamond.planner import AstraPlanner
    from mc_diamond.rpc import EpisodeError
    from mc_diamond.schema import AstraPlannerConfig, Goal, Observation

    settings = AstraPlannerConfig(backend="astra", provider="mock", model="fixture", version="fixture",
        endpoint="https://example.invalid/v1/chat/completions", approved=condition != "unapproved", approval_reference="test",
        max_calls=1, max_usd=0.01, request_usd_ceiling=0.01, budget_file="budget.json", rates_checked_on="2026-11-09",
        input_usd_per_million=1.0, output_usd_per_million=2.0)
    monkeypatch.setenv("ASTRA_API_KEY", "secret-sentinel")
    if condition == "missing_key":
        monkeypatch.delenv("ASTRA_API_KEY")
    reports: list[dict[str, Any]] = []
    attempts: list[object] = []

    def send(_opener: Any, request: Any, **kwargs: Any) -> BytesIO:
        attempts.append(request)
        if condition == "network":
            raise URLError("secret-sentinel")
        if condition == "request_error":
            raise HTTPError(request.full_url, 422, "secret-sentinel", Message(), None)
        body: Any = [] if condition == "bad_schema" else {"model": "wrong" if condition == "bad_model" else "fixture",
            "choices": [{"message": {"content": "secret-sentinel"}}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
        return BytesIO(json.dumps(body).encode())

    monkeypatch.setattr("urllib.request.OpenerDirector.open", send)
    path = tmp_path / "budget.json"
    ask = AstraPlanner(settings, path, lambda kind, report: reports.append(report))
    observation = Observation.model_validate(json.loads(Path("fixtures/model_episode.json").read_text())["initial"])
    task = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    plan = Planning(task, settings, ask)
    if condition == "secret_reply":
        # Secret text is redacted BEFORE it reaches goal decisions or provider logs.
        assert ask(observation, task, None) == "[REDACTED]"
    else:
        with pytest.raises(EpisodeError) as error:
            plan.decide(observation, "episode_start")
        assert "secret-sentinel" not in str(error.value)
        if condition == "request_error":
            assert error.value.error.code == "planner_error" and reports[-1]["http_status"] == 422
        assert plan.counts["rule_recoveries"] == 0 and plan.counts["planner_regeneration_requests"] == 0
    assert "secret-sentinel" not in json.dumps(reports)
    if condition in {"unapproved", "missing_key"}:
        assert not attempts and not path.exists()
    else:
        ledger = json.loads(path.read_text())
        assert ledger["calls"] == 1 and float(ledger["reserved_usd"]) == 0.01
        with pytest.raises(EpisodeError):
            ask(observation, task, None)
        assert len(attempts) == 1


def test_provider_cost_ceiling_violation_persistently_stops_the_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from io import BytesIO
    from mc_diamond.planner import AstraPlanner
    from mc_diamond.rpc import EpisodeError
    from mc_diamond.schema import AstraPlannerConfig, Goal, Observation
    settings = AstraPlannerConfig(backend="astra", provider="mock", model="fixture", version="fixture",
        endpoint="https://example.invalid/v1/chat/completions", approved=True, approval_reference="test",
        max_calls=2, max_usd=0.02, request_usd_ceiling=0.01, budget_file="budget.json", rates_checked_on="2026-11-09",
        input_usd_per_million=1.0, output_usd_per_million=2.0)
    monkeypatch.setenv("ASTRA_API_KEY", "test-key")
    requests: list[object] = []

    def send(_opener: Any, request: Any, **kwargs: Any) -> BytesIO:
        requests.append(request)
        return BytesIO(json.dumps({"model": "fixture", "choices": [{"message": {"content": "{}"}}],
            "usage": {"prompt_tokens": 30000, "completion_tokens": 0}}).encode())

    monkeypatch.setattr("urllib.request.OpenerDirector.open", send)
    path = tmp_path / "budget.json"
    observation = Observation.model_validate(json.loads(Path("fixtures/model_episode.json").read_text())["initial"])
    task = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    for _ in range(2):  # restarting the adapter must retain the billing violation
        with pytest.raises(EpisodeError):
            AstraPlanner(settings, path, lambda kind, report: None)(observation, task, None)
    assert len(requests) == 1
    ledger = json.loads(path.read_text())
    assert ledger["blocked"] and float(ledger["reported_cost_usd"]) == 0.03


def test_local_inference_error_preserves_jsonl_failure_and_common_episode_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    from types import SimpleNamespace
    torch = pytest.importorskip("torch")
    from mc_diamond.cli import main
    from mc_diamond.episode import emit
    from mc_diamond.planner import LocalPlanner
    from mc_diamond.schema import LocalPlannerConfig

    def generate(**kwargs: Any) -> None:
        raise RuntimeError("CUDA out of memory")

    ask = LocalPlanner.__new__(LocalPlanner)
    ask.config, ask.emit = LocalPlannerConfig(backend="local_7b"), emit
    ask.model = SimpleNamespace(device="cpu", generate=generate)
    ask.tokenizer = SimpleNamespace(eos_token_id=0, apply_chat_template=lambda *a, **kw: SimpleNamespace(
        to=lambda device: {"input_ids": torch.tensor([[1]])}))
    monkeypatch.setattr("mc_diamond.planner.load_planner", lambda *args: ask)
    config = yaml.safe_load(Path("configs/planner_smoke.yaml").read_text())
    config["fixture"] = str(Path("fixtures/model_episode.json").resolve())
    path = tmp_path / "planner.yaml"
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr("sys.argv", ["mc-diamond", "smoke-planner", "--config", str(path)])
    assert main() == 1
    rows = [json.loads(s) for s in capsys.readouterr().out.splitlines()]
    report = next(row["data"] for row in rows if row["type"] == "planner_call")
    summary = next(row["data"] for row in rows if row["type"] == "summary")
    assert report["error"] == "inference_failed" and report["latency_seconds"] >= 0
    assert summary["error"]["code"] == "planner_error" and summary["rule_recoveries"] == 0


def test_local_context_overflow_fails_loudly_with_its_token_count_and_summary_omissions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """#44: an over-long input is never truncated; the call record keeps its tokens and what the summary left out."""
    from types import SimpleNamespace
    torch = pytest.importorskip("torch")
    from mc_diamond.cli import main
    from mc_diamond.episode import emit
    from mc_diamond.planner import LocalPlanner
    from mc_diamond.schema import LocalPlannerConfig

    def generate(**kwargs: Any) -> None:
        raise AssertionError("an over-long input must never reach generation")

    ask = LocalPlanner.__new__(LocalPlanner)
    ask.config, ask.emit = LocalPlannerConfig(backend="local_7b"), emit
    ask.model = SimpleNamespace(device="cpu", generate=generate)
    ask.tokenizer = SimpleNamespace(eos_token_id=0, apply_chat_template=lambda *a, **kw: SimpleNamespace(
        to=lambda device: {"input_ids": torch.ones((1, 8000), dtype=torch.long)}))
    monkeypatch.setattr("mc_diamond.planner.load_planner", lambda *args: ask)
    config = yaml.safe_load(Path("configs/planner_smoke.yaml").read_text())
    fixture = json.loads(Path("fixtures/model_episode.json").read_text())
    fixture["initial"]["observed_map"] += [{"block": "stone", "position": [float(x), 63.0, float(z)], "support": True}
                                           for x in range(-10, 10) for z in range(-10, 10)]
    (tmp_path / "fixture.json").write_text(json.dumps(fixture))
    config["fixture"] = str(tmp_path / "fixture.json")
    path = tmp_path / "planner.yaml"
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr("sys.argv", ["mc-diamond", "smoke-planner", "--config", str(path)])
    assert main() == 1
    rows = [json.loads(s) for s in capsys.readouterr().out.splitlines()]
    report = next(row["data"] for row in rows if row["type"] == "planner_call")
    assert (report["error"], report["input_tokens"]) == ("context_exceeded", 8000)
    memory = report["memory"]
    assert memory["shown"] == 256 and memory["cells"] > 400 and memory["omitted"]["stone"] > 0
    assert sum(memory["omitted"].values()) == memory["cells"] - memory["shown"]
