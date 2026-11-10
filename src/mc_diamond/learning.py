"""Saved macro transitions, SMDP GAE and PPO over NanoJev's existing trainable heads."""

import math
from collections.abc import Sequence
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any, Literal, cast

import torch
from torch import Tensor

from .nanojev import NanoJevAdapter, parameter_hash
from .episode import emit, forced_wait_candidate
from .model_input import choice_input
from .rewards import RewardLedger
from .schema import CandidateSet, EpisodeConfig, Goal, Observation, PPOConfig, SelectionResult, StepResult
from .selectors import result


@dataclass(frozen=True)
class State:
    observation: Observation
    goal: Goal
    candidates: CandidateSet
    features: Tensor
    mask: Tensor
    context: Tensor

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation", Observation.model_validate(self.observation.model_dump()))
        object.__setattr__(self, "goal", Goal.model_validate(self.goal.model_dump()))
        object.__setattr__(self, "candidates", CandidateSet.model_validate(self.candidates.model_dump()))
        for key in ("features", "mask", "context"):
            object.__setattr__(self, key, getattr(self, key).detach().clone())
        expected = self.candidates.mask or [True]  # actual forced wait: value only, never an offered choice
        if (self.features.ndim != 2 or self.features.shape[0] != len(expected)
                or self.mask.dtype != torch.bool or self.mask.tolist() != expected or not self.mask.any()
                or self.context.shape != (4,) or not torch.isfinite(self.features).all()
                or not torch.isfinite(self.context).all()
                or any(c.source_obs_id != self.observation.obs_id for c in self.candidates.candidates)):
            raise ValueError("Invalid saved policy state")


@dataclass(frozen=True)
class Transition:
    state: State
    candidate_id: str | None
    old_logprob: float | None
    old_value: float
    reward: float
    discount: float
    next_value: float
    bootstrap: bool
    trace: bool
    actor_valid: bool
    valid: bool
    next_obs_id: str
    trace_break: bool = False
    next_state: State | None = None

    def __post_init__(self) -> None:
        if (not all(math.isfinite(v) for v in [self.old_value, self.reward, self.discount, self.next_value])
                or not 0 <= self.discount <= 1
                or self.old_logprob is not None and (not math.isfinite(self.old_logprob) or self.old_logprob > 0)):
            raise ValueError("Nonfinite or invalid saved transition")
        offered = {c.candidate_id: allowed for c, allowed in zip(self.state.candidates.candidates, self.state.candidates.mask)}
        if self.candidate_id is not None and not offered.get(self.candidate_id):
            raise ValueError("Saved selected ID is not an allowed candidate")
        if self.actor_valid and (not self.valid or self.candidate_id is None or self.old_logprob is None
                                 or sum(self.state.candidates.mask) < 2):
            raise ValueError("Actor requires a valid local policy logprob and multiple saved choices")


def trace_masks(rows: list[Transition]) -> list[bool]:
    masks = []
    for row, following in zip(rows, rows[1:]):
        a, b = row.state.observation, following.state.observation
        masks.append(row.valid and row.bootstrap and row.trace and not row.trace_break and following.valid
            and not following.trace_break and (a.episode_id, a.attempt_id, a.objective_kind, row.next_obs_id)
            == (b.episode_id, b.attempt_id, b.objective_kind, b.obs_id)
            and (a.objective_kind == "full" or row.state.goal == following.state.goal))
    return masks + [False] if rows else []


def advantages(rows: list[Transition], gae_lambda: float = .95) -> tuple[list[float], list[float]]:
    if not 0 <= gae_lambda <= 1:
        raise ValueError("GAE lambda must be in [0, 1]")
    result = [0.] * len(rows)
    masks = trace_masks(rows)
    for index in range(len(rows) - 1, -1, -1):
        row = rows[index]
        if row.valid:
            delta = row.reward + row.discount * row.bootstrap * row.next_value - row.old_value
            result[index] = delta + row.discount * gae_lambda * (result[index + 1] if masks[index] else 0.)
    return result, [adv + row.old_value if row.valid else 0. for row, adv in zip(rows, result)]


class PPO:
    def __init__(self, model: NanoJevAdapter, config: PPOConfig) -> None:
        self.model, self.config = model, config
        self.optimizer = torch.optim.Adam([
            {"params": model.choice.parameters(), "lr": config.choice_lr},
            {"params": model.critics.parameters(), "lr": config.value_lr}])

    def evaluate(self, row: Transition) -> tuple[Tensor, Tensor, Tensor, bool]:
        state = row.state
        selected = next((j for j, c in enumerate(state.candidates.candidates) if c.candidate_id == row.candidate_id),
                        int(state.mask.nonzero()[0]))
        return self.model.evaluate_actions(state.features, state.mask, state.context, state.observation.objective_kind, selected)

    def update(self, rows: list[Transition]) -> dict[str, Any]:
        adv, targets = advantages(rows, self.config.gae_lambda)
        indices = [i for i, row in enumerate(rows) if row.valid]
        actors = [i for i in indices if rows[i].actor_valid and not self.config.critic_only]
        initial_choice = parameter_hash(self.model.choice)
        initial_critic = parameter_hash(self.model.critics)
        normalized = dict(zip(actors, [adv[i] for i in actors]))
        if actors:
            values = torch.tensor([adv[i] for i in actors], dtype=torch.float64)
            normalized = dict(zip(actors, ((values - values.mean()) / (values.std(unbiased=False) + 1e-8)).tolist()))
        with torch.no_grad():
            ratios = [float((self.evaluate(rows[i])[0] - cast(float, rows[i].old_logprob)).exp()) for i in actors]
        if not all(math.isfinite(ratio) for ratio in ratios):
            raise ValueError("Nonfinite PPO ratio")
        losses, norms, policy_losses = [], [], []
        self.model.train()
        for _ in range(self.config.epochs):
            # A permutation only changes minibatch order; candidate order inside a saved decision never changes.
            order = [indices[i] for i in torch.randperm(len(indices)).tolist()]
            for offset in range(0, len(order), self.config.minibatch):
                batch = order[offset:offset + self.config.minibatch]
                critic_losses, actor_losses, entropies = [], [], []
                for i in batch:
                    row = rows[i]
                    logprob, entropy, value, _ = self.evaluate(row)
                    critic_losses.append((value - targets[i]).square())
                    if i in normalized:
                        assert row.old_logprob is not None
                        ratio = (logprob - row.old_logprob).exp()
                        unclipped = ratio * normalized[i]
                        clipped = ratio.clamp(1 - self.config.clip, 1 + self.config.clip) * normalized[i]
                        actor_losses.append(-torch.minimum(unclipped, clipped))
                        entropies.append(entropy)
                loss = self.config.value_coefficient * torch.stack(critic_losses).mean()
                if actor_losses:
                    policy_loss = torch.stack(actor_losses).mean()
                    policy_losses.append(float(policy_loss.detach()))
                    loss = loss + policy_loss - self.config.entropy * torch.stack(entropies).mean()
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite PPO loss")
                self.optimizer.zero_grad(set_to_none=True)
                cast(Any, loss).backward()
                norm = torch.nn.utils.clip_grad_norm_([p for p in self.model.parameters() if p.requires_grad],
                                                     self.config.grad_norm, error_if_nonfinite=True)
                self.optimizer.step()
                losses.append(float(loss.detach()))
                norms.append(float(norm))
        return {"valid_transitions": len(indices), "actor_transitions": len(actors), "actor_skipped": not actors,
                "initial_ratios": ratios, "advantages": adv, "returns": targets, "trace_masks": trace_masks(rows),
                "policy_losses": policy_losses,
                "losses": losses, "gradient_norms": norms,
                "choice_changed": initial_choice != parameter_hash(self.model.choice),
                "critic_changed": initial_critic != parameter_hash(self.model.critics),
                "config": self.config.model_dump()}


class EpisodeLearner:
    def __init__(self, model: NanoJevAdapter, config: PPOConfig, seed: int) -> None:
        self.model, self.config = model, config
        self.ppo = PPO(model, config)
        self.generator = torch.Generator(device=next(model.parameters()).device).manual_seed(seed)
        self.rows: list[Transition] = []
        self.pending: Transition | None = None
        self.current: State | None = None
        self.ledger: RewardLedger | None = None
        self.reward_kind: Literal["local", "full"] = "local"
        self.actor_transitions = self.valid_transitions = self.excluded_transitions = self.updates = 0

    @property
    def needs_bootstrap(self) -> bool:
        return self.pending is not None

    def reset(self, observation: Observation) -> None:
        if self.pending is not None:
            raise ValueError("Finish the previous episode before resetting the reward ledger")
        self.ledger = RewardLedger(observation)
        self.reward_kind = observation.objective_kind
        self.current = None

    def begin(self, observation: Observation, goal: Goal, saved: CandidateSet) -> None:
        value_candidates = saved if saved.candidates else CandidateSet(
            candidates=[forced_wait_candidate(observation)], mask=[True], generated=1)
        encoded = choice_input(observation, goal, value_candidates)
        features = self.model.encode_candidates(encoded)
        state = State(observation, goal, saved, features, torch.tensor(encoded.mask, device=features.device),
                      torch.tensor(encoded.context, device=features.device))
        if self.pending is not None:
            with torch.no_grad():
                _, values = self.model.score_features(state.features, state.mask, state.context)
            self.append(replace(self.pending, next_value=float(values[self.reward_kind]), next_state=state))
            self.pending = None
        # Update before sampling the next action, so its logprob belongs to the new policy.
        if len(self.rows) >= self.config.rollout:
            self.update()
        self.current = state

    def select(self, observation: Observation, goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
        state = self.current
        if state is None or (observation, goal, saved) != (state.observation, state.goal, state.candidates):
            raise ValueError("Selection must use the saved decision state")
        with torch.no_grad():
            logits, values = self.model.score_features(state.features, state.mask, state.context)
            probabilities = logits.softmax(-1)
            index = int(torch.multinomial(probabilities, 1, generator=self.generator))
        return result(saved.candidates[index], "sampling", provider="local", model="C-Tianyu/NanoJev",
            probabilities=dict(zip([c.candidate_id for c in saved.candidates], probabilities.cpu().tolist())),
            logprob=float(logits.log_softmax(-1)[index]), values={k: float(v) for k, v in values.items()},
            actor_eligible=int(state.mask.sum()) > 1)

    def record(self, selection: SelectionResult, step: StepResult, *, goal_completed: bool) -> dict[str, Any]:
        state, ledger = self.current, self.ledger
        if state is None or ledger is None:
            raise ValueError("Learning record requires reset and a saved decision")
        reward = ledger.compute(state.observation, state.goal, step, goal_completed=goal_completed)
        with torch.no_grad():
            _, values = self.model.score_features(state.features, state.mask, state.context)
        valid = not step.invalid and step.stable_boundary and step.clock_mode in {"mock", "paused"}
        offered = any(c.candidate_id == selection.candidate_id for c in state.candidates.candidates)
        own = (selection.selector_mode == "sampling" and selection.provider == "local" and not selection.fallback
               and selection.error is None)
        actor = (valid and own and selection.actor_eligible and sum(state.candidates.mask) > 1
                 and not step.cancelled and not self.config.critic_only)
        exclusion = ("invalid" if not valid else "cancelled" if step.cancelled else "critic_only" if self.config.critic_only
            else "no_candidates" if not offered else "single_candidate" if sum(state.candidates.mask) < 2
            else "fallback" if not own else None)
        row = Transition(state, selection.candidate_id if offered else None, selection.logprob if own else None,
            float(values[self.reward_kind]), reward.discounted, reward.discount, 0., not reward.terminal, not step.cancelled,
            actor, valid, step.observation.obs_id, trace_break=step.cancelled or selection.fallback)
        if row.bootstrap and valid:
            self.pending = row
        else:
            self.append(row)
        return {"value": reward.total, "kind": self.reward_kind, "discounted": reward.discounted,
            "discount": reward.discount, "components": reward.components, "task_terminal": reward.terminal,
            "actor_valid": actor, "actor_exclusion_reason": exclusion, "trace_mask": int(row.trace and not row.trace_break),
            "goal_id": state.goal.goal_id, "goal_source": state.goal.source,
            "sparse_reward_timing": "returned_boundary_last_tick"}

    def append(self, row: Transition) -> None:
        self.rows.append(row)
        self.valid_transitions += row.valid
        self.actor_transitions += row.actor_valid
        self.excluded_transitions += not row.valid
        emit("transition", {"observation": row.state.observation.model_dump(mode="json"),
            "goal": row.state.goal.model_dump(mode="json"), "candidates": row.state.candidates.model_dump(mode="json"),
            **{f.name: getattr(row, f.name) for f in fields(row) if f.name not in {"state", "next_state"}},
            "next_state": None if row.next_state is None else {
                "observation": row.next_state.observation.model_dump(mode="json"),
                "goal": row.next_state.goal.model_dump(mode="json"),
                "candidates": row.next_state.candidates.model_dump(mode="json")}})

    def update(self) -> None:
        if self.rows:
            report = self.ppo.update(self.rows)
            self.updates += bool(report["valid_transitions"])
            emit("ppo_update", {"update": self.updates, **report})
            self.rows.clear()

    def finish(self) -> None:
        if self.pending is not None:
            # No reliable next goal/candidates: retain diagnostics, exclude the incomplete transition.
            self.append(replace(self.pending, valid=False, actor_valid=False, bootstrap=False, trace=False))
            self.pending = None
        self.update()


def smoke_ppo(config: EpisodeConfig, config_path: Path) -> int:
    """One short diagnostic episode; never the locked main training or a saved pilot actor."""
    import sys
    import time
    from uuid import uuid4
    from .episode import run_episode
    from .model_input import INPUT_HASH
    from .nanojev import REVISION, WEIGHTS_SHA256
    from .planner import load_planner
    from .rpc import EpisodeError, RpcSession
    from .schema import ModelConfig

    started = time.monotonic()
    learner: EpisodeLearner | None = None
    try:
        settings = config.model or ModelConfig()
        if settings.mode != "sampling" or config.planner is not None and config.planner.backend == "astra":
            raise ValueError("PPO requires local sampling and never uses a paid external planner")
        torch.manual_seed(settings.seed)
        model = NanoJevAdapter.load((config_path.parent / settings.checkpoint).resolve())
        initial = {"backbone": parameter_hash(model.backbone), "choice": parameter_hash(model.choice),
                   "critics": parameter_hash(model.critics)}
        emit("learning_loaded", {"model": "C-Tianyu/NanoJev", "revision": REVISION,
            "initial_weights_sha256": WEIGHTS_SHA256, "input_hash": INPUT_HASH, "seed": settings.seed,
            "ppo": config.ppo.model_dump(), "environment_backend": config.backend})
        learner = EpisodeLearner(model, config.ppo, settings.seed)
        command = config.command
        if config.backend == "mock":
            assert config.fixture is not None
            command = [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture",
                       str((config_path.parent / config.fixture).resolve())]
        assert command is not None
        planner = load_planner(config.planner, config_path, emit) if config.planner else None
        episode_id, attempt_id = str(uuid4()), str(uuid4())
        with RpcSession(command, config.rpc_timeout_seconds) as session:
            summary = run_episode(config, session.policy(), lambda: session.reset(episode_id, attempt_id), episode_id, attempt_id,
                macros=True, select=learner.select, planner=planner, verification=session.verification_log, learning=learner)
        body_unchanged = initial["backbone"] == parameter_hash(model.backbone)
        okay = (not summary.error and not summary.invalid and learner.updates > 0 and body_unchanged
                and (config.backend == "mock" or summary.pause_verified))
        emit("learning_summary", {"learning_verified": okay, "environment_backend": config.backend,
            "model_backend": "public_nanojev", "valid_transitions": learner.valid_transitions,
            "actor_transitions": learner.actor_transitions, "excluded_transitions": learner.excluded_transitions,
            "updates": learner.updates, "backbone_unchanged": body_unchanged,
            "choice_changed": initial["choice"] != parameter_hash(model.choice),
            "critic_changed": initial["critics"] != parameter_hash(model.critics),
            "reward_total": summary.reward_total, "reward_kind": learner.reward_kind,
            "wall_seconds": time.monotonic() - started, "saved_actor": False,
            "error": None if okay else "Episode/clock validation or learning update failed"})
        return 0 if okay else 1
    except (ImportError, OSError, ValueError, RuntimeError, EpisodeError) as failure:
        emit("learning_summary", {"learning_verified": False, "environment_backend": config.backend,
            "valid_transitions": learner.valid_transitions if learner else 0,
            "actor_transitions": learner.actor_transitions if learner else 0,
            "updates": learner.updates if learner else 0, "saved_actor": False,
            "wall_seconds": time.monotonic() - started, "error": str(failure)})
        print(f"smoke-ppo failed: {failure}", file=sys.stderr)
        return 1 if learner else 2
