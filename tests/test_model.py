"""T10: public input boundary and tiny numerical training checks; no downloaded weights needed."""

import json
from pathlib import Path
from typing import Any

import pytest

from mc_diamond.schema import Candidate, CandidateSet, Goal, Observation


def inputs() -> tuple[Observation, Goal, CandidateSet]:
    observation = Observation.model_validate(json.loads(Path("fixtures/mock_episode.json").read_text())["initial"])
    goal = Goal(goal_id="wood", kind="collect", target="oak_log", quantity=1)
    candidates = [Candidate(candidate_id=f"saved-{i}", action_kind="wait", params={"ticks": ticks},
                            max_ticks=ticks, stop_rule_id="elapsed", source_obs_id=observation.obs_id,
                            description=f"Wait {ticks} active ticks") for i, ticks in enumerate([20, 100, 200])]
    return observation, goal, CandidateSet(candidates=candidates, mask=[True, False, True], generated=3)


def test_choice_input_preserves_saved_ids_order_mask_and_public_budget() -> None:
    from mc_diamond.model_input import choice_input
    observation, goal, saved = inputs()
    encoded = choice_input(observation, goal, saved)
    row = encoded.payload["states"][0]
    assert encoded.candidate_ids == ["saved-0", "saved-1", "saved-2"]
    assert encoded.mask == [True, False, True]
    assert list(row["questions"]["action"]["criteria"]) == ["a0", "a1", "a2"]
    assert json.loads(row["questions"]["action"]["criteria"]["a2"])["params"] == {"ticks": 200}
    state = json.loads(row["state"])
    assert state["objective_kind"] == "local" and state["remaining_ticks"] == 100
    assert state["goal"]["target"] == "oak_log"
    assert "episode_id" not in state and "seed" not in state and "admin_verified" not in state
    saved.candidates.reverse()
    saved.mask[0] = False
    assert encoded.candidate_ids == ["saved-0", "saved-1", "saved-2"] and encoded.mask == [True, False, True]


def test_choice_input_rejects_stale_empty_and_all_masked_candidates() -> None:
    from mc_diamond.model_input import choice_input
    observation, goal, saved = inputs()
    for bad in [CandidateSet(candidates=[], mask=[], generated=0), saved.model_copy(update={"mask": [False] * 3})]:
        with pytest.raises(ValueError):
            choice_input(observation, goal, bad)
    saved.candidates[1].source_obs_id = "old-observation"
    with pytest.raises(ValueError, match="observation"):
        choice_input(observation, goal, saved)


def tiny_adapter() -> Any:
    import torch
    from torch import nn
    from types import SimpleNamespace
    from mc_diamond.nanojev import NanoJevAdapter

    class Body(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.config = SimpleNamespace(hidden_size=4)
            self.embedding = nn.Embedding(128, 4)
            self.dropout = nn.Dropout(0.8)

        def forward(self, input_ids: Any, attention_mask: Any, use_cache: bool) -> Any:
            assert not torch.is_grad_enabled() and not use_cache
            return SimpleNamespace(last_hidden_state=self.dropout(self.embedding(input_ids)))

    torch.manual_seed(11)
    return NanoJevAdapter(Body())


def test_masked_set_and_critic_ignore_disallowed_features_and_freeze_backbone() -> None:
    torch = pytest.importorskip("torch")
    from mc_diamond.nanojev import parameter_hash
    model = tiny_adapter()
    model.train()
    before = parameter_hash(model.backbone)
    features = model.encode_tokens([[1, 2, 3], [4, 5], [6, 7, 8, 9]], pad_token=0)
    assert not features.requires_grad
    assert torch.equal(features[0], model.backbone.embedding.weight[3])
    assert torch.equal(features[1], model.backbone.embedding.weight[5])
    assert model.backbone.dropout.p == 0 and not model.backbone.training
    mask = torch.tensor([True, False, True])
    context = torch.tensor([1., 0., 0.1, 0.2])
    logits, values = model.score_features(features, mask, context)
    changed = features.clone()
    changed[1] = 1e5
    other_logits, other_values = model.score_features(changed, mask, context)
    assert torch.equal(logits, other_logits) and torch.isneginf(logits[1])
    assert all(torch.equal(values[k], other_values[k]) for k in ["local", "full"])
    expected = model.critics["local"](torch.cat([features[[0, 2]].mean(0), context])).squeeze(-1)
    assert torch.allclose(values["local"], expected)
    loss = -logits.log_softmax(0)[0] + values["local"].square() + values["full"].square()
    loss.backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.choice.parameters())
    assert all(p.grad is None and not p.requires_grad for p in model.backbone.parameters())
    assert parameter_hash(model.backbone) == before


def test_trainable_heads_update_restore_and_single_candidate_excludes_actor(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    from mc_diamond.nanojev import parameter_hash
    model = tiny_adapter()
    features = model.encode_tokens([[1, 2], [3, 4]], 0)
    context = torch.tensor([0., 1., 0.4, 0.5])
    model.save_heads(tmp_path / "heads.safetensors")
    initial = parameter_hash(model.choice)
    backbone = parameter_hash(model.backbone)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4, weight_decay=0)
    logprob, entropy, value, eligible = model.evaluate_actions(features, torch.tensor([True, True]), context, "local", 0)
    assert eligible and torch.isfinite(logprob + entropy + value)
    loss = -logprob + (value - 1).square()
    loss.backward()
    optimizer.step()
    assert parameter_hash(model.choice) != initial and parameter_hash(model.backbone) == backbone
    model.load_heads(tmp_path / "heads.safetensors")
    assert parameter_hash(model.choice) == initial
    model.zero_grad(set_to_none=True)
    logprob, entropy, value, eligible = model.evaluate_actions(features, torch.tensor([False, True]), context, "full", 1)
    assert not eligible and logprob.item() == 0 and entropy.item() == 0
    (value - 1).square().backward()
    assert all(p.grad is None for p in model.choice.parameters())
    assert any(p.grad is not None for p in model.critics["full"].parameters())
    assert all(p.grad is None for p in model.critics["local"].parameters())
    with pytest.raises(ValueError):
        model.evaluate_actions(features, torch.tensor([False, True]), context, "full", 0)


def test_seeded_sampling_argmax_and_single_probability_keep_saved_mapping() -> None:
    torch = pytest.importorskip("torch")
    from mc_diamond.nanojev import NanoJevSelector
    observation, goal, saved = inputs()
    model = tiny_adapter()

    class Tokenizer:
        eos_token_id = 1
        pad_token_id = 0

        def encode(self, value: str, add_special_tokens: bool) -> list[int]:
            assert not add_special_tokens
            return [ord(char) % 128 for char in value]

    model.tokenizer = Tokenizer()
    a, b = NanoJevSelector(model, "sampling", 123), NanoJevSelector(model, "sampling", 123)
    assert [a(observation, goal, saved, []).candidate_id for _ in range(8)] == [
        b(observation, goal, saved, []).candidate_id for _ in range(8)]
    selected = NanoJevSelector(model, "argmax", 3)(observation, goal, saved, [])
    assert selected.probabilities is not None
    assert selected.probabilities["saved-1"] == 0 and selected.actor_eligible
    assert selected.candidate_id == max(selected.probabilities, key=selected.probabilities.__getitem__)
    assert selected.logprob == pytest.approx(torch.tensor(selected.probabilities[selected.candidate_id]).log().item())
    single = saved.model_copy(update={"mask": [False, True, False]})
    selected = a(observation, goal, single, [])
    assert selected.candidate_id == "saved-1" and not selected.actor_eligible
    assert selected.probabilities == {"saved-0": 0., "saved-1": 1., "saved-2": 0.}
    assert selected.logprob == 0


def test_smoke_model_missing_bundle_fails_explicitly_through_cli(tmp_path: Path) -> None:
    pytest.importorskip("torch", reason="optional model dependencies are required for the missing-bundle path")
    import subprocess
    import yaml
    config = {"backend": "mock", "fixture": str(Path("fixtures/mock_episode.json").resolve()),
              "goal": {"goal_id": "wood", "kind": "collect", "target": "oak_log", "quantity": 1},
              "model": {"checkpoint": "missing"}}
    path = tmp_path / "model.yaml"
    path.write_text(yaml.safe_dump(config))
    process = subprocess.run(["mc-diamond", "smoke-model", "--config", str(path)], capture_output=True, text=True, timeout=30)
    assert process.returncode == 2
    output = [json.loads(line) for line in process.stdout.splitlines()]
    assert output[-1]["type"] == "model_summary"
    assert output[-1]["data"]["model_verified"] is False
    assert "best.safetensors" in output[-1]["data"]["error"]
    assert not any(row["type"] == "reset" for row in output)


def test_bad_head_checkpoint_does_not_partially_replace_public_actor(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    from safetensors.torch import save_file
    from mc_diamond.nanojev import REVISION, WEIGHTS_SHA256, parameter_hash
    model = tiny_adapter()
    before = parameter_hash(model.choice)
    heads = {k: v.clone() for k, v in model.heads().items()}
    heads["choice.scalar.weight"] += 1
    heads["critics.full.0.weight"] = torch.zeros(1)
    path = tmp_path / "bad.safetensors"
    save_file(heads, str(path), metadata={"revision": REVISION, "initial_weights_sha256": WEIGHTS_SHA256})
    with pytest.raises(ValueError, match="shape"):
        model.load_heads(path)
    assert parameter_hash(model.choice) == before


def test_public_tokenizer_segments_and_eos_never_silently_truncate() -> None:
    pytest.importorskip("torch")
    from mc_diamond.model_input import choice_input
    from mc_diamond.nanojev import tokenize
    observation, goal, saved = inputs()

    class Tokenizer:
        eos_token_id = 99

        def encode(self, value: str, add_special_tokens: bool) -> list[int]:
            assert not add_special_tokens
            return [len(value)]

    encoded = choice_input(observation, goal, saved)
    paths = tokenize(encoded, Tokenizer(), 4)
    assert all(len(p) == 4 and p[-1] == 99 for p in paths)
    with pytest.raises(ValueError, match="not truncated"):
        tokenize(encoded, Tokenizer(), 3)


def test_memory_summary_keeps_rare_resources_hazards_and_facilities_beside_abundant_floor() -> None:
    """#44: nearest-first alone dropped observed ores behind floor; every kind now gets an even share of 256 cells."""
    from mc_diamond.model_input import SUMMARY_CELLS, memory_summary, public_state
    from mc_diamond.planner import messages
    observation, goal, _ = inputs()
    floor = [{"block": "stone", "position": [float(x), 63.0, float(z)], "support": True, "visible": x < 10}
             for x in range(-20, 20) for z in range(-20, 20)]  # 1,600 floor cells, all nearer than the rest
    rare = [{"block": "iron_ore", "position": [30.0, 60.0, float(z)], "support": True, "visible": z != 0} for z in range(4)]
    rare += [{"block": "lava", "position": [-31.0, 62.0, 0.0], "hazard": True},
             {"block": "crafting_table", "position": [25.0, 64.0, 5.0], "support": True, "visible": False}]
    air = [{"block": "air", "position": [0.0, 64.0, 0.0], "passable": True}]
    observation = Observation.model_validate({**observation.model_dump(), "observed_map": floor + rare + air})

    summary = memory_summary(observation)
    kinds = {kind["block"]: kind for kind in summary}
    assert set(kinds) == {"stone", "iron_ore", "lava", "crafting_table"}  # air is never summarized
    assert sum(len(k["now"]) + len(k["past"]) for k in summary) == SUMMARY_CELLS == 256
    assert kinds["iron_ore"]["now"] == [[30, 60, 1], [30, 60, 2], [30, 60, 3]] and kinds["iron_ore"]["past"] == [[30, 60, 0]]
    assert kinds["crafting_table"]["past"] == [[25, 64, 5]] and kinds["lava"]["hazard"] is True
    assert (kinds["stone"]["total"], len(kinds["stone"]["now"]) + len(kinds["stone"]["past"])) == (1600, 250)
    nearest = kinds["stone"]["now"][0]
    assert abs(nearest[0]) <= 1 and abs(nearest[2]) <= 1  # the floor share is still nearest first

    # One meaning for every model: the planner and NanoJev/Jev carry the same state and summary.
    state = public_state(observation)
    assert state["memory"] == summary and "observed_map" not in state
    planner = json.loads(messages(observation, goal, None)[1]["content"])["observation"]
    assert planner == state
    from mc_diamond.model_input import choice_input
    candidate = Candidate(candidate_id="c", action_kind="wait", params={}, max_ticks=20, stop_rule_id="elapsed",
                          source_obs_id=observation.obs_id, description="Wait")
    encoded = choice_input(observation, goal, CandidateSet(candidates=[candidate], mask=[True], generated=1))
    assert {k: v for k, v in json.loads(encoded.payload["states"][0]["state"]).items() if k != "goal"} == state


def test_memory_summary_with_more_kinds_than_cells_keeps_the_rarest_kinds() -> None:
    from mc_diamond.model_input import SUMMARY_CELLS, memory_summary
    observation, _, _ = inputs()
    many = [{"block": f"kind_{k:03d}", "position": [float(k), 70.0, float(n)]} for k in range(300) for n in range(1 + (k >= 150))]
    observation = Observation.model_validate({**observation.model_dump(), "observed_map": many})
    shown = {k["block"]: len(k["now"]) for k in memory_summary(observation)}
    assert sum(shown.values()) == SUMMARY_CELLS
    assert all(shown[f"kind_{k:03d}"] == 1 for k in range(150))  # single-cell kinds first, never squeezed to zero
