"""exp/candidate-structure: one pilot runner for any fixed-chain task (evaluate / train / evaluate, traces on disk).

Not the locked main training: public NanoJev heads, pilot rewards, results never initialise a main run.
    python -m mc_diamond.exp --config configs/exp/stone.yaml --output artifacts/exp/name --eval-before 10
"""

import argparse
import gzip
import json
import random
import sys
import time
from collections.abc import Sequence
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import yaml

from .episode import emit, error_summary, run_episode
from .evaluation import SERVER_ERRORS, bridge_command
from .rpc import EpisodeError, RpcSession
from .schema import CandidateSet, EpisodeConfig, ErrorInfo, Goal, Observation, PPOConfig, SelectionResult
from .selectors import Selector, result

EVALUATION_SEED = 15000  # slot i samples with seed 15000+i, as the earlier pilots did


class UniformSelector:
    """The candidate structure alone: every offered candidate equally likely, no model."""

    def __init__(self, seed: int) -> None:
        self.random = random.Random(seed)

    def __call__(self, _observation: Observation, _goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
        share = 1 / len(saved.candidates)
        return result(self.random.choice(saved.candidates), "sampling", provider="uniform",
                      probabilities={c.candidate_id: share for c in saved.candidates})


def write_json(path: Path, data: Any) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=1) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_one(config: EpisodeConfig, path: Path, directory: Path, identity: str, number: int,
            select: Selector, learner: Any = None) -> dict[str, Any]:
    attempt_id = f"{identity}:{number}"
    started = time.monotonic()
    trace = directory / f"{identity}-{number}.jsonl.gz"
    with gzip.open(trace, "xt", encoding="utf-8", compresslevel=1) as handle, redirect_stdout(handle):
        try:
            with RpcSession(bridge_command(config, path), config.rpc_timeout_seconds) as session:
                summary = run_episode(config, session.policy(), lambda: session.reset(identity, attempt_id), identity,
                                      attempt_id, macros=True, select=select, verification=session.verification_log,
                                      learning=learner)
        except (EpisodeError, OSError, ValueError, RuntimeError) as failure:
            error = failure.error if isinstance(failure, EpisodeError) else ErrorInfo(code="invalid_step", message=str(failure))
            emit("error", error)
            summary = error_summary(config, identity, attempt_id, error, time.monotonic() - started)
    valid = summary.error is None and not summary.invalid and (config.backend == "mock" or summary.pause_verified)
    return {"attempt_id": attempt_id, "trace": str(trace), "valid": valid, "success": valid and summary.goal_completed,
            "reason": summary.reason, "error_code": summary.error.code if summary.error else None,
            "error": summary.error.message if summary.error else None,
            "active_ticks": summary.active_ticks, "decisions": summary.decisions, "selections": summary.selection_requests,
            "reward_total": summary.reward_total, "acquired": summary.direct_acquired, "crafted": summary.direct_crafted,
            "subgoals": [{"goal": o.goal_id, "completed": o.completed, "end_tick": o.end_tick, "macros": o.macros}
                         for o in summary.goal_outcomes],
            "wall_seconds": time.monotonic() - started}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, action="append", required=True, help="task config; repeat to mix tasks")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selector", choices=["nanojev", "uniform"], default="nanojev")
    parser.add_argument("--heads", type=Path, help="saved Choice/critic heads to start from")
    parser.add_argument("--eval-before", type=int, default=0)
    parser.add_argument("--train", type=int, default=0, help="decisions to collect")
    parser.add_argument("--eval-after", type=int, default=0)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--entropy", type=float, default=.01)
    parser.add_argument("--rollout", type=int, default=128)
    parser.add_argument("--seed", type=int, default=11015)
    parser.add_argument("--gpu-fraction", type=float, default=.75)
    parser.add_argument("--critic-replay-epochs", type=int, default=0, help="cumulative MC critic fit after each update")
    args = parser.parse_args()
    tasks = [(path, EpisodeConfig.model_validate(yaml.safe_load(path.read_text()))) for path in args.config]
    args.output.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {"args": {k: str(v) if isinstance(v, (Path, list)) else v for k, v in vars(args).items()},
                               "tasks": [c.model_dump(mode="json") for _, c in tasks], "episodes": [], "updates": [],
                               "error": None, "main_training_initializer": False}
    started = time.monotonic()

    def save() -> None:
        summary["wall_seconds"] = time.monotonic() - started
        write_json(args.output / "summary.json", summary)

    model = None
    if args.selector == "nanojev":
        import torch
        from .nanojev import NanoJevAdapter, NanoJevSelector
        # Leave room for another small GPU job on the shared card; cached blocks are released before this cap fails.
        torch.cuda.set_per_process_memory_fraction(args.gpu_fraction)
        torch.manual_seed(args.seed)
        model = NanoJevAdapter.load((tasks[0][0].parent / (tasks[0][1].model.checkpoint if tasks[0][1].model else "")).resolve())
        if args.heads:
            model.load_heads(args.heads)
        model.save_heads(args.output / "initial.safetensors")

    def evaluate(phase: str, slots: int) -> None:
        for index in range(slots):
            for name, (path, config) in enumerate(tasks):
                seed = EVALUATION_SEED + index
                for number in (1, 2):  # server errors only: one retry on the same seed
                    select: Selector = (NanoJevSelector(model, "sampling", seed) if model is not None else UniformSelector(seed))
                    row = run_one(config, path, args.output, f"{phase}-t{name}-{index + 1}", number, select)
                    summary["episodes"].append({"phase": phase, "task": name, "seed": seed, **row})
                    save()
                    print(json.dumps({"phase": phase, "task": name, "slot": index + 1, "success": row["success"],
                                      "ticks": row["active_ticks"], "reason": row["reason"]}), flush=True)
                    if row["error_code"] not in SERVER_ERRORS:
                        break

    try:
        evaluate("before", args.eval_before)
        if args.train:
            if model is None:
                raise ValueError("Training needs the NanoJev selector")
            from .signal_pilot import SignalLearner
            torch.manual_seed(args.seed)
            learner = SignalLearner(model, args.seed, args.output, [],
                                    PPOConfig(choice_lr=args.lr, entropy=args.entropy, rollout=args.rollout),
                                    replay_epochs=args.critic_replay_epochs)
            summary["updates"] = learner.update_reports
            collected = failures = episode = 0
            while collected < args.train and failures < 3:
                path, config = tasks[episode % len(tasks)]
                bounded = config.model_copy(update={"max_decisions": min(config.max_decisions, args.train - collected)})
                row = run_one(bounded, path, args.output, f"train-t{episode % len(tasks)}-{episode + 1}", 1,
                              learner.select, learner)
                episode += 1
                collected += row["selections"]
                failures = 0 if row["valid"] and row["selections"] else failures + 1
                summary["episodes"].append({"phase": "train", "task": (episode - 1) % len(tasks), "update": learner.updates, **row})
                summary["training"] = {"collected": collected, "updates": learner.updates, "warmup_reason": learner.warmup_reason,
                                       "actor_transitions": learner.actor_transitions, "valid_transitions": learner.valid_transitions}
                save()
                print(json.dumps({"phase": "train", "episode": episode, "collected": collected, "updates": learner.updates,
                                  "success": row["success"], "ticks": row["active_ticks"], "reason": row["reason"]}), flush=True)
            model.save_heads(args.output / "final.safetensors")
            if failures >= 3:
                raise ValueError("Three training episodes in a row failed")
        evaluate("after", args.eval_after)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError, TypeError, EpisodeError) as failure:
        summary["error"] = f"{type(failure).__name__}: {failure}"
        print(f"exp failed: {failure}", file=sys.stderr)
    save()
    return 1 if summary["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
