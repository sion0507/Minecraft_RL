"""T11 (#12): Jev request mapping, re-ask/fallback, transport retries, ledger cap and secret removal against a mock API.

No test here calls the paid service; actual access is `mc-diamond smoke-jev --config configs/jev_smoke.yaml`.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from mc_diamond.model_input import INSTRUCTIONS
from mc_diamond.jev import ENDPOINT, KEY_ENDPOINT, JevSelector, Ledger, smoke_jev
from mc_diamond.rpc import EpisodeError
from mc_diamond.schema import Candidate, CandidateSet, EpisodeConfig, Goal, JevConfig, Observation

KEY = "sk-or-v1-secret"


def inputs() -> tuple[Observation, Goal, CandidateSet]:
    observation = Observation.model_validate(json.loads(Path("fixtures/mock_episode.json").read_text())["initial"])
    goal = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    candidates = [Candidate(candidate_id=f"saved-{i}", action_kind="wait", params={"ticks": ticks}, max_ticks=ticks,
                            stop_rule_id="elapsed", source_obs_id=observation.obs_id, description=f"Wait {ticks} ticks")
                  for i, ticks in enumerate([20, 100, 200])]
    return observation, goal, CandidateSet(candidates=candidates, mask=[True, False, True], generated=3)


def answer(choice: str, probabilities: dict[str, float] | None = None, cost: float = 0.00002) -> tuple[int, dict[str, Any]]:
    action: dict[str, Any] = {"type": "choice", "choice": choice, "confidence": 0.7}
    if probabilities is not None:
        action["probabilities"] = probabilities
    return 200, {"id": "gen-1", "model": "typesafe/jev-1.13-x", "provider": "TypeSafe", "answers": {"action": action},
                 "usage": {"input_tokens": 400, "output_tokens": 0, "cost": cost}}


class FakeApi:
    def __init__(self, *responses: tuple[int, dict[str, Any]]) -> None:
        self.responses, self.bodies = list(responses), []  # type: ignore[var-annotated]

    def __call__(self, url: str, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
        if url == KEY_ENDPOINT:
            return 200, {"data": {"usage": 0.5, "limit": None, "limit_remaining": None, "is_free_tier": False}}
        assert url == ENDPOINT
        self.bodies.append(body)
        return self.responses.pop(0)


def selector(tmp_path: Path, api: FakeApi, **settings: Any) -> tuple[JevSelector, Ledger, list[float]]:
    config = JevConfig(ledger=str(tmp_path / "ledger.jsonl"), **settings)
    ledger, sleeps = Ledger(config), []  # type: ignore[var-annotated]
    return JevSelector(config, api, ledger, key=KEY, sleep=sleeps.append), ledger, sleeps


def test_request_omits_masked_keys_and_maps_the_choice_to_the_saved_id(tmp_path: Path) -> None:
    api = FakeApi(answer("a2", {"a0": 0.25, "a2": 0.75}))
    select, ledger, _ = selector(tmp_path, api)
    chosen = select(*inputs(), ())
    body = api.bodies[0]
    assert body["model"] == "typesafe/jev-1.13" and isinstance(body["state"], str)
    assert list(body["questions"]["action"]["criteria"]) == ["a0", "a2"]  # a1 is masked; keys keep the saved index
    assert body["questions"]["action"]["instructions"] == INSTRUCTIONS  # the common text NanoJev gets; no J-only hints
    assert chosen.candidate_id == "saved-2" and chosen.selector_mode == "native_choice" and not chosen.actor_eligible
    assert chosen.probabilities == {"saved-0": 0.25, "saved-1": 0.0, "saved-2": 0.75}
    assert ledger.totals()["confirmed_usd"] == pytest.approx(0.00002) and ledger.totals()["unconfirmed_requests"] == 0


def test_invalid_answer_is_reasked_once_with_the_same_body_then_falls_back(tmp_path: Path) -> None:
    api = FakeApi(answer("a1"), answer("a0"))  # masked key, then a valid one
    select, _, _ = selector(tmp_path, api)
    chosen = select(*inputs(), ())
    assert chosen.candidate_id == "saved-0" and chosen.retries == 1 and api.bodies[0] == api.bodies[1]
    api = FakeApi((200, {"answers": {"action": {"type": "refusal"}}}), answer("zz"))
    select, ledger, _ = selector(tmp_path / "b", api)
    chosen = select(*inputs(), ())
    assert chosen.selector_mode == "fallback" and chosen.fallback and chosen.candidate_id == "saved-0"
    assert chosen.error is not None and chosen.error.code == "model_response_invalid" and len(api.bodies) == 2
    assert ledger.totals()["requests"] == 2  # both failed answers stay in the cost ledger


def test_transport_retries_are_bounded_logged_and_never_leak_the_key(tmp_path: Path) -> None:
    api = FakeApi((429, {"error": {"message": "rate"}}), (0, {"error": {"message": "timeout"}}), answer("a0"))
    select, ledger, sleeps = selector(tmp_path, api)
    assert select(*inputs(), ()).retries == 2 and sleeps == [1.0, 2.0]
    assert ledger.totals()["unconfirmed_requests"] == 2  # failed requests are charged max_call_usd toward the cap
    api = FakeApi(*[(503, {"error": {"message": "down"}})] * 3)
    select, _, sleeps = selector(tmp_path / "b", api)
    with pytest.raises(EpisodeError) as failure:
        select(*inputs(), ())
    assert failure.value.error.code == "jev_error" and len(api.bodies) == 3 and sleeps == [1.0, 2.0]
    api = FakeApi((401, {"error": {"message": f"bad key {KEY}"}}))
    select, ledger, _ = selector(tmp_path / "c", api)
    with pytest.raises(EpisodeError) as failure:
        select(*inputs(), ())
    assert failure.value.error.code == "jev_unavailable" and KEY not in failure.value.error.message
    assert KEY not in ledger.path.read_text() and "<redacted>" in ledger.path.read_text()


def test_cap_stops_before_sending_and_counts_the_planned_reserve(tmp_path: Path) -> None:
    api = FakeApi(answer("a0"))
    select, ledger, _ = selector(tmp_path, api, cap_usd=1.0, reserve_usd=0.5)
    ledger.record({"cost_usd": 0.4995})
    with pytest.raises(EpisodeError) as failure:
        select(*inputs(), ())
    assert failure.value.error.code == "budget_exceeded" and api.bodies == []


def test_sampling_uses_only_a_complete_distribution(tmp_path: Path) -> None:
    api = FakeApi(answer("a0", {"a0": 0.0, "a2": 1.0}))
    select, _, _ = selector(tmp_path, api, mode="sampling")
    chosen = select(*inputs(), ())
    assert chosen.selector_mode == "sampling" and chosen.candidate_id == "saved-2" and chosen.logprob == 0.0
    for broken in ({"a0": 0.5}, {"a0": 0.5, "a2": 0.2}, {"a0": -0.5, "a2": 1.5}, None):  # partial, sum, negative, confidence only
        api = FakeApi(answer("a0", broken))
        select, _, _ = selector(tmp_path, api, mode="sampling")
        chosen = select(*inputs(), ())
        assert chosen.selector_mode == "native_choice" and chosen.candidate_id == "saved-0" and chosen.probabilities is None


def test_single_offered_candidate_sends_no_paid_request(tmp_path: Path) -> None:
    observation, goal, saved = inputs()
    saved = saved.model_copy(update={"mask": [False, False, True]})
    api = FakeApi()
    select, ledger, _ = selector(tmp_path, api)
    assert select(observation, goal, saved, ()).candidate_id == "saved-2" and ledger.totals()["requests"] == 0


def config(tmp_path: Path) -> tuple[EpisodeConfig, Path]:
    data = yaml.safe_load(Path("configs/jev_smoke.yaml").read_text())
    data["fixture"] = str(Path("fixtures/model_episode.json").resolve())
    data["jev"]["ledger"] = str(tmp_path / "ledger.jsonl")
    path = tmp_path / "jev.yaml"
    path.write_text(yaml.safe_dump(data))
    return EpisodeConfig.model_validate(data), path


def test_smoke_jev_runs_the_public_flow_with_a_mock_api(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    episode, path = config(tmp_path)
    assert smoke_jev(episode, path, FakeApi(*[answer("a0", {"a0": 0.6, "a1": 0.4})] * 4)) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    summary = next(r["data"] for r in rows if r["type"] == "jev_summary")
    assert summary["status"] == "verified" and summary["full_distributions"] >= 1 and summary["environment_backend"] == "mock"
    assert any(r["type"] == "selection" and r["data"]["provider"] == "TypeSafe" for r in rows)
    assert smoke_jev(episode, path, FakeApi((403, {"error": {"message": "no access"}}))) == 1
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    summary = next(r["data"] for r in rows if r["type"] == "jev_summary")
    assert summary["status"] == "unavailable" and "Q3_J_vs_F" in summary["unverified"]


def test_smoke_jev_cli_without_a_key_stops_before_any_request(tmp_path: Path) -> None:
    _, path = config(tmp_path)
    run = subprocess.run(["mc-diamond", "smoke-jev", "--config", str(path)], capture_output=True, text=True, timeout=60,
                         env={**os.environ, "HOME": str(tmp_path), "JEV_API_KEY": ""})
    summary = json.loads(run.stdout.splitlines()[-1])["data"]
    assert run.returncode == 2 and summary["status"] == "missing_key" and not (tmp_path / "ledger.jsonl").exists()
