"""T13: public reward/GAE numerical contracts and the shared CLI execution boundary."""

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from mc_diamond.schema import Event, Goal, Observation, StepResult


def observation(**updates: object) -> Observation:
    raw = json.loads(Path("fixtures/model_episode.json").read_text())["initial"]
    return Observation.model_validate({**raw, **updates})


def step(before: Observation, ticks: int = 20, **updates: object) -> StepResult:
    now = before.model_copy(update={"obs_id": f"obs-{before.active_ticks + ticks}",
                                  "active_ticks": before.active_ticks + ticks,
                                  "remaining_ticks": before.remaining_ticks - ticks})
    return StepResult.model_validate({"observation": now, "actual_ticks": ticks, "events": [],
        "terminated": False, "truncated": False, "invalid": False, "reason": "wait_completed",
        "clock_mode": "mock", "pause_verified": False, "stable_boundary": True, "wall_seconds": 0.0, **updates})


def event(kind: str, item: str | None = None, **updates: object) -> Event:
    return Event.model_validate({"kind": kind, "item": item, "quantity": 1, "source": "mock", **updates})


def test_local_rewards_use_actual_ticks_and_only_local_success() -> None:
    from mc_diamond.rewards import RewardLedger
    before = observation(remaining_ticks=100)
    goal = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    ledger = RewardLedger(before)
    result = ledger.compute(before, goal, step(before, events=[event("acquired", "oak_log")]), goal_completed=True)
    # gamma=2**(-1/100); nineteen -0.001 ticks, then terminal +1 -0.001.
    assert result.total == pytest.approx(.98)
    assert result.discounted == pytest.approx(.8578653157869611)
    assert result.discount == pytest.approx(.8705505632961241)
    assert result.terminal and result.components == {"time": -.02, "success": 1.0}
    died = RewardLedger(before).compute(before, goal, step(before, observation=before.model_copy(update={
        "health": 0.0, "obs_id": "dead", "active_ticks": 20, "remaining_ticks": 80}),
        events=[event("failed"), event("failed")], terminated=True), goal_completed=False)
    assert died.total == pytest.approx(-1.03)  # failure once per step, time, death
    assert died.terminal


def test_full_rewards_deduplicate_progress_and_meaningful_goals_without_blocking_completion() -> None:
    from mc_diamond.rewards import RewardLedger
    before = observation(objective_kind="full", remaining_ticks=36000, inventory={"crafting_table": 1})
    ledger = RewardLedger(before)
    goal = Goal(goal_id="first", kind="collect", target="oak_log", quantity=1)
    first = ledger.compute(before, goal, step(before, events=[event("acquired", "oak_log"),
        event("crafted", "crafting_table")]), goal_completed=True)
    assert first.components == {"time": -.001, "progress": 1.0, "goal": .5}
    repeated = goal.model_copy(update={"goal_id": "second", "quantity": 4, "direction": "west"})
    again = ledger.compute(before, repeated, step(before, events=[event("acquired", "oak_log")]), goal_completed=True)
    assert again.components == {"time": -.001}
    # Other wood species share the wood progress reward, but goal identity is kind+target.
    for index, (kind, target) in enumerate([("craft", "wooden_pickaxe"), ("craft", "stone_pickaxe"),
        ("craft", "furnace"), ("collect", "iron_ore"), ("smelt", "iron_ingot"), ("craft", "iron_pickaxe"),
        ("collect", "birch_log"), ("explore", "space")]):
        g = Goal.model_validate({"goal_id": str(index), "kind": kind, "target": target, "quantity": 1})
        ledger.compute(before, g, step(before, events=[event({"collect": "acquired", "craft": "crafted",
            "smelt": "smelted"}.get(kind, "moved"), target)]), goal_completed=True)
    assert ledger.progress_total == 17.0  # provided table excluded from 18
    assert len(ledger.completed_goals) == 8
    assert ledger.goal_total == 4.0
    ledger = RewardLedger(observation(objective_kind="full", remaining_ticks=36000))
    all_events = [event("acquired", "oak_log"), event("crafted", "crafting_table"),
        event("crafted", "wooden_pickaxe"), event("crafted", "stone_pickaxe"), event("crafted", "furnace"),
        event("acquired", "iron_ore"), event("smelted", "iron_ingot"), event("crafted", "iron_pickaxe")]
    ledger.compute(before, goal, step(before, events=all_events), goal_completed=False)
    assert ledger.progress_total == 18.0


def test_given_goals_and_unrelated_diamonds_do_not_earn_success() -> None:
    from mc_diamond.rewards import RewardLedger
    before = observation(objective_kind="full", remaining_ticks=36000, inventory={"diamond": 1})
    goal = Goal(goal_id="diamond", kind="mine_diamond", target="diamond", quantity=1)
    ledger = RewardLedger(before)
    result = ledger.compute(before, goal, step(before, events=[event("acquired", "diamond")]), goal_completed=True)
    assert result.components == {"time": -.001} and not result.terminal
    before = observation(objective_kind="full", remaining_ticks=36000, tool="iron_pickaxe",
                         inventory={"iron_pickaxe": 1})
    ledger = RewardLedger(before)
    mined = event("mined", "diamond_ore", position=[1., 10., 2.])
    ledger.compute(before, goal, step(before, events=[mined]), goal_completed=False)
    # Bridge acquisition coordinates are the spawned drop's position, not the mined block's integer coordinates.
    result = ledger.compute(before, goal, step(before, events=[event("acquired", "diamond", position=[1.4, 10.6, 2.3])]),
                            goal_completed=True)
    assert result.components == {"time": -.001, "diamond": 100.0, "goal": .5}
    assert result.terminal


def transition() -> Any:
    import torch
    from mc_diamond.learning import State, Transition
    from mc_diamond.schema import Candidate, CandidateSet
    before = observation()
    goal = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    candidates = [Candidate(candidate_id=f"saved-{i}", action_kind="wait", params={"ticks": i + 1},
        max_ticks=i + 1, stop_rule_id="elapsed", source_obs_id=before.obs_id, description="Wait") for i in range(3)]
    saved = CandidateSet(candidates=candidates, mask=[True, False, True], generated=3)
    state = State(before, goal, saved, torch.tensor([[1., 2., 3., 4.], [99., 99., 99., 99.], [4., 1., 0., 2.]]),
                  torch.tensor(saved.mask), torch.tensor([1., 0., .1, .2]))
    return Transition(state=state, candidate_id="saved-0", old_logprob=-.7, old_value=.2,
        reward=1., discount=.5, next_value=.4, bootstrap=True, trace=True, actor_valid=True,
        valid=True, next_obs_id="obs-next")


def test_gae_uses_macro_discount_bootstrap_and_only_contiguous_traces() -> None:
    pytest.importorskip("torch")
    from mc_diamond.learning import advantages
    first = transition()
    next_obs = first.state.observation.model_copy(update={"obs_id": "obs-next"})
    # Different full subgoals keep the trace: delta1=1+.5*.4-.2=1;
    # delta2=2-.4=1.6; A1=1+.5*.95*1.6=1.76, returns=1.96 and 2.
    first = replace(first, state=replace(first.state, observation=first.state.observation.model_copy(
        update={"objective_kind": "full"})))
    following_candidates = first.state.candidates.model_copy(update={"candidates": [c.model_copy(
        update={"source_obs_id": "obs-next"}) for c in first.state.candidates.candidates]})
    second = replace(first, state=replace(first.state, observation=next_obs.model_copy(update={"objective_kind": "full"}),
        candidates=following_candidates,
        goal=first.state.goal.model_copy(update={"goal_id": "new", "kind": "explore", "target": "space"})),
        old_value=.4, reward=2., bootstrap=False, trace=False)
    adv, returns = advantages([first, second])
    assert adv == pytest.approx([1.76, 1.6]) and returns == pytest.approx([1.96, 2.])
    assert advantages([first])[0] == pytest.approx([1.])  # rollout cut bootstraps
    for interrupted in [replace(second, valid=False, actor_valid=False), replace(second, trace_break=True, actor_valid=False),
                        replace(second, state=replace(second.state, observation=next_obs.model_copy(
                            update={"attempt_id": "new-attempt"})))]:
        assert advantages([first, interrupted])[0][0] == pytest.approx(1.)
    assert advantages([replace(first, bootstrap=False)])[0] == pytest.approx([.8])


def test_ppo_recomputes_saved_masked_logits_and_preserves_inactive_heads() -> None:
    torch = pytest.importorskip("torch")
    from mc_diamond.learning import PPO
    from mc_diamond.nanojev import parameter_hash
    from mc_diamond.schema import PPOConfig
    from test_model import tiny_adapter
    model = tiny_adapter()
    trainer = PPO(model, PPOConfig())
    row = transition()
    with torch.no_grad():
        logprob, _, value, _ = model.evaluate_actions(row.state.features, row.state.mask, row.state.context, "local", 0)
    row = replace(row, old_logprob=float(logprob), old_value=float(value))
    body, actor, full = parameter_hash(model.backbone), parameter_hash(model.choice), parameter_hash(model.critics["full"])
    other = replace(row, candidate_id="saved-2", reward=-1.)
    with torch.no_grad():
        lp, _, _, _ = model.evaluate_actions(row.state.features, row.state.mask, row.state.context, "local", 2)
    other = replace(other, old_logprob=float(lp))
    result = trainer.update([row, other])
    assert result["initial_ratios"] == pytest.approx([1., 1.])
    assert result["actor_transitions"] == 2 and not result["actor_skipped"]
    assert result["choice_changed"] and parameter_hash(model.choice) != actor
    assert parameter_hash(model.backbone) == body and parameter_hash(model.critics["full"]) == full
    # Existing Adam momentum must not change Choice during a critic-only rollout.
    actor = parameter_hash(model.choice)
    result = trainer.update([replace(row, actor_valid=False)])
    assert result["actor_skipped"] and result["actor_transitions"] == 0
    assert parameter_hash(model.choice) == actor
    assert result["critic_changed"]
    assert trainer.update([replace(row, valid=False, actor_valid=False)])["valid_transitions"] == 0


def test_ppo_clips_positive_and_negative_advantages_from_saved_old_probabilities() -> None:
    torch = pytest.importorskip("torch")
    from mc_diamond.learning import PPO
    from mc_diamond.schema import PPOConfig
    from test_model import tiny_adapter
    model = tiny_adapter()
    with torch.no_grad():
        for p in model.choice.parameters():
            p.zero_()
    row = transition()
    positive = replace(row, old_logprob=-1.3862943611198906, old_value=0., reward=1., bootstrap=False)
    negative = replace(row, old_logprob=0., old_value=0., reward=-1., bootstrap=False)
    report = PPO(model, PPOConfig(epochs=1)).update([positive, negative])
    assert report["initial_ratios"] == pytest.approx([2., .5])
    # Normalized advantages +1/-1: mean(-min(2,1.2), -min(-.5,-.8)) = -.2.
    assert report["policy_losses"] == pytest.approx([-.2])


def test_full_critic_warmup_preserves_choice_local_critic_and_backbone() -> None:
    pytest.importorskip("torch")
    from mc_diamond.learning import PPO
    from mc_diamond.nanojev import parameter_hash
    from mc_diamond.schema import PPOConfig
    from test_model import tiny_adapter
    model = tiny_adapter()
    row = transition()
    row = replace(row, state=replace(row.state, observation=row.state.observation.model_copy(update={"objective_kind": "full"})))
    before = [parameter_hash(module) for module in [model.choice, model.critics["local"], model.backbone]]
    full = parameter_hash(model.critics["full"])
    report = PPO(model, PPOConfig(critic_only=True)).update([row])
    assert report["actor_skipped"] and not report["policy_losses"]
    assert [parameter_hash(module) for module in [model.choice, model.critics["local"], model.backbone]] == before
    assert parameter_hash(model.critics["full"]) != full


def run_learning_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
                     fixture: dict[str, Any] | None = None, **config_updates: object) -> tuple[int, list[dict[str, Any]], Any]:
    pytest.importorskip("torch")
    import sys
    import yaml
    from mc_diamond.cli import main
    from mc_diamond.nanojev import NanoJevAdapter, parameter_hash
    from test_model import tiny_adapter
    model = tiny_adapter()

    class Tokenizer:
        eos_token_id = 1
        pad_token_id = 0

        def encode(self, value: str, add_special_tokens: bool) -> list[int]:
            return [ord(char) % 128 for char in value]

    model.tokenizer = Tokenizer()
    # Replace only the unavailable downloaded model boundary; RPC, policy, rewards and PPO are real.
    monkeypatch.setattr(NanoJevAdapter, "load", classmethod(lambda cls, root: model))
    config = yaml.safe_load(Path("configs/model_smoke.yaml").read_text())
    fixture_path = tmp_path / "learning.json"
    fixture_path.write_text(json.dumps(fixture or json.loads(Path("fixtures/model_episode.json").read_text())))
    config.update(config_updates, fixture=str(fixture_path))
    config_path = tmp_path / "ppo.yaml"
    config_path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr(sys, "argv", ["mc-diamond", "smoke-ppo", "--config", str(config_path)])
    status = main()
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    return status, output, model


def test_public_ppo_smoke_collects_updates_and_reports_real_head_changes(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    status, output, _ = run_learning_cli(tmp_path, monkeypatch, capsys)
    assert status == 0, [r for r in output if r["type"] in {"summary", "error", "learning_summary"}]
    kinds = [r["type"] for r in output]
    assert all(k in kinds for k in ["reset", "observation", "goal", "candidates", "selection", "step", "reward", "ppo_update"])
    reward = next(r["data"] for r in output if r["type"] == "reward")
    assert reward["kind"] == "local" and reward["value"] == pytest.approx(.98)
    row = next(r["data"] for r in output if r["type"] == "transition")
    candidates = next(r["data"] for r in output if r["type"] == "candidates")
    assert row["candidates"] == candidates and row["bootstrap"] is False
    assert row["actor_valid"] and row["old_logprob"] is not None
    summary = output[-1]["data"]
    assert output[-1]["type"] == "learning_summary"
    assert summary["valid_transitions"] == summary["actor_transitions"] == 1
    assert summary["updates"] == 1 and summary["backbone_unchanged"]
    assert summary["critic_changed"]


def test_full_repeated_completed_goals_keep_bootstrap_and_no_duplicate_reward(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    fixture = json.loads(Path("fixtures/model_episode.json").read_text())
    fixture["initial"]["objective_kind"] = "full"
    first = fixture["steps"][0]
    first["terminated"] = False
    first["observation"].update(objective_kind="full", observed_map=fixture["initial"]["observed_map"])
    second = json.loads(json.dumps(first))
    second.update(source_obs_id="obs-1", stop_evidence=["obs-2", first["reason"]])
    second["observation"].update(obs_id="obs-2", active_ticks=40, remaining_ticks=60, inventory={"oak_log": 2})
    fixture["steps"].append(second)
    status, output, _ = run_learning_cli(tmp_path, monkeypatch, capsys, fixture, planner={"backend": "scripted", "outputs": [
        '{"kind":"collect","target":"oak_log","quantity":1}',
        '{"kind":"collect","target":"oak_log","quantity":2}',
        '{"kind":"explore","target":"space","quantity":1}']})
    assert status == 0, [r for r in output if r["type"] in {"summary", "error", "learning_summary"}]
    transitions = [r["data"] for r in output if r["type"] == "transition"]
    assert len(transitions) == 2
    assert all(t["bootstrap"] and t["valid"] for t in transitions)
    assert [t["next_state"]["goal"]["goal_id"] for t in transitions] == ["model-wood:2", "model-wood:3"]
    rewards = [r["data"] for r in output if r["type"] == "reward"]
    assert rewards[0]["components"] == {"time": -.001, "progress": 1., "goal": .5}
    assert rewards[1]["components"] == {"time": -.001}
    episode = next(r["data"] for r in output if r["type"] == "summary")
    assert episode["reason"] == "decision_limit" and episode["truncated"] and episode["goal_completed"]


@pytest.mark.parametrize("mode", ["single", "empty", "cancelled", "invalid", "protocol"])
def test_actor_exclusions_preserve_costs_and_only_train_valid_critics(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str) -> None:
    fixture = json.loads(Path("fixtures/model_episode.json").read_text())
    initial, final = fixture["initial"], fixture["steps"][0]
    if mode in {"single", "empty"}:
        initial["observed_map"] = initial["observed_map"][:1] if mode == "single" else []
    if mode == "empty":
        final.update(terminated=False, reason="wait_completed", stop_evidence=["obs-1", "wait_completed"],
                     events=[{"kind": "wait", "source": "mock"}])
        final["observation"]["inventory"] = {}
    elif mode == "cancelled":
        final.update(cancelled=True, terminated=False, reason="selection_cancelled",
            stop_evidence=["obs-1", "selection_cancelled"], events=[{"kind": "wait", "source": "mock"},
            {"kind": "failed", "source": "mock"}])
        final["observation"]["inventory"] = {}
    elif mode == "invalid":
        final.update(invalid=True, terminated=False)
    elif mode == "protocol":
        final["observation"]["active_ticks"] = 99  # response violates the executed duration
    status, output, _ = run_learning_cli(tmp_path, monkeypatch, capsys, fixture, max_decisions=1)
    summary = output[-1]["data"]
    assert summary["actor_transitions"] == 0
    assert summary["valid_transitions"] == (0 if mode in {"invalid", "protocol"} else 1)
    assert status == (1 if mode in {"invalid", "protocol"} else 0)
    if mode not in {"invalid", "protocol"}:
        assert summary["updates"] == 1 and not summary["choice_changed"]
    if mode in {"empty", "cancelled"}:
        reward = next(r["data"] for r in output if r["type"] == "reward")
        assert reward["components"] == {"time": -.02, "failure": -.01}
        assert reward["value"] == pytest.approx(-.03)
        row = next(r["data"] for r in output if r["type"] == "transition")
        assert row["trace_break"] == (mode == "cancelled")
