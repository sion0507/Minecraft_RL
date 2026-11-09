"""Actual NanoJev diagnostic, followed by execution of the restored public actor.

The optimizer steps use explicit numerical targets, never a claimed Minecraft PPO rollout.
"""

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from .episode import emit, run_episode
from .rpc import EpisodeError, RpcSession
from .schema import EpisodeConfig, ModelConfig


def diagnose(model: Any, encoded: Any, root: Path) -> dict[str, Any]:
    import torch
    from .nanojev import parameter_hash, reference_module, tokenize

    device = next(model.parameters()).device
    mask = torch.tensor(encoded.mask, device=device)
    context = torch.tensor(encoded.context, device=device)
    first = int(mask.nonzero()[0])
    before = {"backbone": parameter_hash(model.backbone), "choice": parameter_hash(model.choice),
              **{kind: parameter_hash(head) for kind, head in model.critics.items()}}
    training, precision = model.training, model.bf16
    reference = reference_module(root, "train_toy_decisions").DecisionModel(model.backbone, "attention").to(device)
    reference.load_state_dict({**{f"backbone.{k}": v for k, v in model.backbone.state_dict().items()}, **model.choice.state_dict()}, strict=True)
    reference.eval()
    predictor = reference_module(root, "predict_toy_decisions")
    # The public predictor accepts 2+ choices and has no external mask: omit disallowed keys for the oracle.
    payload = json.loads(json.dumps(encoded.payload))
    criteria = payload["states"][0]["questions"]["action"]["criteria"]
    payload["states"][0]["questions"]["action"]["criteria"] = {k: v for (k, v), allowed in zip(criteria.items(), encoded.mask) if allowed}
    example = predictor.prepare_examples(payload, model.tokenizer, model.max_length)[0]
    paths = tokenize(encoded, model.tokenizer, model.max_length)
    assert example["leaf_tokens"] == [p for p, allowed in zip(paths, encoded.mask) if allowed], "Public tokenization differs"
    report: dict[str, Any] = {"diagnostic_targets": {"actor": "first valid candidate", "local": 1., "full": -0.5},
                              "training_kind": "numerical_connectivity_only_no_PPO", "tokenization_equal": True,
                              "path_lengths": [len(p) for p in paths], "hash_before": before}
    with tempfile.TemporaryDirectory(prefix="nanojev-heads-") as directory, torch.random.fork_rng(devices=[device.index]):
        checkpoint = Path(directory) / "initial.safetensors"
        model.save_heads(checkpoint)
        try:
            model.eval()
            parity: dict[str, Any] = {}
            for bf16 in (False, True):
                model.bf16 = bf16
                captured: list[Any] = []
                hook = model.backbone.register_forward_hook(lambda _m, _a, output: captured.append(output.last_hidden_state))
                try:
                    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=bf16):
                        expected, _ = reference([example], model.tokenizer.pad_token_id)
                finally:
                    hook.remove()
                lengths = torch.tensor([len(p) for p in example["leaf_tokens"]], device=device)
                expected_features = captured[0][torch.arange(len(lengths), device=device), lengths - 1]
                del captured
                features = model.encode_candidates(encoded)
                with torch.no_grad():
                    logits, _ = model.score_features(features, mask, context)
                torch.testing.assert_close(features[mask], expected_features, rtol=1e-5, atol=1e-5)
                torch.testing.assert_close(logits[mask], expected[0], rtol=1e-4, atol=1e-4)
                parity["bf16" if bf16 else "fp32"] = {"max_logit_error": float((logits[mask] - expected[0]).abs().max()),
                    "max_pooling_error": float((features[mask] - expected_features).abs().max()),
                    "public_logits": expected[0].float().cpu().tolist(), "adapter_logits": logits[mask].cpu().tolist()}
                del expected_features
            report["public_parity"] = parity
            model.bf16 = precision
            features = model.encode_candidates(encoded)
            assert not features.requires_grad and not features.is_inference()
            model.train()
            optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4, weight_decay=0)
            model.zero_grad(set_to_none=True)
            logits, values = model.score_features(features, mask, context)
            loss = -logits.log_softmax(-1)[first] + 0.5 * (values["local"] - 1).square() + 0.5 * (values["full"] + 0.5).square()
            assert torch.isfinite(loss), "Nonfinite diagnostic loss"
            loss.backward()
            gradients = {name: float(parameter.grad.float().norm()) for name, parameter in model.named_parameters()
                         if parameter.requires_grad and parameter.grad is not None}
            assert all(torch.isfinite(torch.tensor(v)) for v in gradients.values())
            assert all(any(k.startswith(prefix) and v > 0 for k, v in gradients.items())
                       for prefix in ("choice.", "critics.local.", "critics.full.")), "Missing Choice/critic gradient"
            assert all(p.grad is None for p in model.backbone.parameters()), "Backbone gradient exists"
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 0.5, error_if_nonfinite=True)
            optimizer.step()
            after = {"backbone": parameter_hash(model.backbone), "choice": parameter_hash(model.choice),
                     **{kind: parameter_hash(head) for kind, head in model.critics.items()}}
            assert before["backbone"] == after["backbone"]
            assert all(before[k] != after[k] for k in ("choice", "local", "full")), "Missing head parameter change"
            report.update(loss=float(loss.detach()), gradient_norms=gradients, hash_after_update=after)
            model.load_heads(checkpoint)
            model.zero_grad(set_to_none=True)
            single_mask = torch.zeros_like(mask)
            single_mask[first] = True
            logprob, entropy, value, eligible = model.evaluate_actions(features, single_mask, context, "full", first)
            assert not eligible and float(logprob.detach()) == 0 and float(entropy.detach()) == 0
            (value - 1).square().backward()  # actor loss is deliberately omitted for forced choices
            assert all(p.grad is None for p in model.choice.parameters())
            assert all(p.grad is None for p in model.critics["local"].parameters())
            torch.optim.AdamW(model.critics["full"].parameters(), lr=1e-4, weight_decay=0).step()
            assert parameter_hash(model.choice) == before["choice"] and parameter_hash(model.critics["local"]) == before["local"]
            assert parameter_hash(model.critics["full"]) != before["full"]
            report.update(single_candidate_probability=1., single_candidate_actor_excluded=True, independent_critic_only_update=True)
        finally:
            model.load_heads(checkpoint)
            model.zero_grad(set_to_none=True)
            model.bf16 = precision
            model.train(training)
        restored = {"backbone": parameter_hash(model.backbone), "choice": parameter_hash(model.choice),
                    **{kind: parameter_hash(head) for kind, head in model.critics.items()}}
        assert restored == before, "Public initial actor/critic restore failed"
        report.update(hash_restored=restored, initial_actor_restored=True, backbone_unchanged=True, features_no_grad=True,
                      dropout_zero=all(getattr(m, "p", 0) == 0 and (not isinstance(m, torch.nn.MultiheadAttention) or m.dropout == 0)
                                       for m in model.modules()))
    return report


def smoke_model(config: EpisodeConfig, config_path: Path) -> int:
    started = time.monotonic()
    settings = config.model or ModelConfig()
    root = (config_path.parent / settings.checkpoint).resolve()
    diagnostic: dict[str, Any] | None = None
    loaded = False
    try:
        import torch
        from .model_input import choice_input
        from .nanojev import FILES, REVISION, WEIGHTS_SHA256, NanoJevAdapter, NanoJevSelector
        torch.manual_seed(settings.seed)
        model = NanoJevAdapter.load(root)
        loaded = True
        selector = NanoJevSelector(model, settings.mode, settings.seed)
        emit("model_loaded", {"model_backend": "public_nanojev", "revision": REVISION, "files_sha256": FILES,
            "initial_weights_sha256": WEIGHTS_SHA256, "seed": settings.seed, "mode": settings.mode,
            "device": torch.cuda.get_device_name(), "torch": torch.__version__, "cuda": torch.version.cuda,
            "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
            "backbone_parameters": sum(p.numel() for p in model.backbone.parameters()),
            "new_random_heads": ["local_critic", "full_critic"], "precision": "float32_storage_bf16_forward"})

        def select(observation: Any, goal: Any, saved: Any, failures: Any) -> Any:
            nonlocal diagnostic
            encoded = choice_input(observation, goal, saved)
            emit("model_input", {"payload": encoded.payload, "candidate_ids": encoded.candidate_ids, "mask": encoded.mask,
                                 "critic_context": encoded.context})
            if diagnostic is None and sum(encoded.mask) >= 2:
                diagnostic = diagnose(model, encoded, root)
                emit("model_diagnostic", diagnostic)
            return selector(observation, goal, saved, failures)

        command = config.command
        if config.backend == "mock":
            assert config.fixture is not None
            command = [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str((config_path.parent / config.fixture).resolve())]
        assert command is not None
        episode_id, attempt_id = str(uuid4()), str(uuid4())
        with RpcSession(command, config.rpc_timeout_seconds) as session:
            summary = run_episode(config, session.policy(), lambda: session.reset(episode_id, attempt_id), episode_id, attempt_id,
                                  macros=True, select=select, verification=session.verification_log)
        verified = diagnostic is not None and not summary.error and not summary.invalid and (
            config.backend == "mock" or summary.pause_verified)
        emit("model_summary", {"model_verified": verified, "model_backend": "public_nanojev", "environment_backend": config.backend,
            "revision": REVISION, "diagnostic_completed": diagnostic is not None, "initial_actor_restored": diagnostic is not None,
            "episode_goal_completed": summary.goal_completed, "wall_seconds": time.monotonic() - started,
            "gpu_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "error": None if verified else "No multi-candidate diagnostic or episode/clock validation failed; model not verified"})
        return 0 if verified else 1
    except (ImportError, OSError, ValueError, RuntimeError, AssertionError, EpisodeError) as failure:
        emit("model_summary", {"model_verified": False, "model_backend": "public_nanojev", "environment_backend": config.backend,
            "diagnostic_completed": False, "wall_seconds": time.monotonic() - started, "error": str(failure),
            "initial_actor_restored": diagnostic is not None})
        print(f"smoke-model failed: {failure}", file=sys.stderr)
        return 1 if loaded else 2
