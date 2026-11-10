"""PLAN §7.1: bounded fixed-goal pilot, isolated from main training and final evaluation."""

import gzip
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import torch

from .episode import emit, error_summary, run_episode
from .evaluation import SERVER_ERRORS, bridge_command, reset_state
from .learning import EpisodeLearner
from .model_input import INPUT_HASH
from .nanojev import REVISION, WEIGHTS_SHA256, NanoJevAdapter, NanoJevSelector, parameter_hash
from .rpc import EpisodeError, RpcSession
from .schema import EpisodeConfig, ErrorInfo, ModelConfig, PPOConfig

DECISIONS = 1024
EVALUATION_SEEDS = list(range(15000, 15010))
LEARNING_RATES = (1e-4, 3e-4)


def write_json(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def hashes(model: NanoJevAdapter) -> dict[str, str]:
    return {name: parameter_hash(module) for name, module in
            [("backbone", model.backbone), ("choice", model.choice), ("critics", model.critics)]}


def attempt(config: EpisodeConfig, path: Path, directory: Path, identity: str, number: int,
            model: NanoJevAdapter, seed: int, snapshot: str,
            learner: EpisodeLearner | None = None) -> dict[str, Any]:
    attempt_id = f"{identity}:{number}"
    started = time.monotonic()
    trace = directory / f"{identity}-{number}.jsonl.gz"
    interrupted = False
    # Full public execution evidence stays on disk; stdout reports bounded phase/attempt summaries.
    with gzip.open(trace, "xt", encoding="utf-8", compresslevel=1) as handle, redirect_stdout(handle):
        try:
            if reset_state(config, path, "G1") != snapshot:
                raise ValueError("G1 reset state changed during pilot")
            with RpcSession(bridge_command(config, path), config.rpc_timeout_seconds) as session:
                def reset() -> Any:
                    observation = session.reset(identity, attempt_id)
                    if (observation.objective_kind != "local" or observation.active_ticks != 0
                            or observation.remaining_ticks != 3600 or observation.inventory):
                        raise ValueError("Wood pilot requires empty local G1 with exactly 3600 active ticks")
                    return observation
                summary = run_episode(config, session.policy(), reset, identity, attempt_id, macros=True,
                    select=learner.select if learner else NanoJevSelector(model, "sampling", seed),
                    verification=session.verification_log, learning=learner)
        except (EpisodeError, OSError, ValueError, RuntimeError) as failure:
            interrupted = True
            error = failure.error if isinstance(failure, EpisodeError) else ErrorInfo(code="invalid_step", message=str(failure))
            emit("error", error)
            summary = error_summary(config, identity, attempt_id, error, time.monotonic() - started)
    if interrupted:
        # error_summary is for pre-start failures; recover work already recorded before a model/PPO exception.
        partial: dict[str, Any] = {"selection_requests": 0, "decisions": 0, "active_ticks": 0,
                                   "reward_total": 0., "direct_acquired": {}, "provided_inventory": {}}
        with gzip.open(trace, "rt", encoding="utf-8") as handle:
            for line in handle:
                event = json.loads(line)
                data = event["data"]
                if event["type"] == "reset":
                    partial["provided_inventory"] = data["inventory"]
                elif event["type"] == "selection":
                    partial["selection_requests"] += 1
                elif event["type"] == "step":
                    partial["decisions"] += not data["cancelled"]
                    partial["active_ticks"] = data["observation"]["active_ticks"]
                    for acquired in data["events"]:
                        if acquired["kind"] == "acquired" and acquired["item"]:
                            item = acquired["item"]
                            partial["direct_acquired"][item] = partial["direct_acquired"].get(item, 0) + acquired["quantity"]
                elif event["type"] == "reward":
                    partial["reward_total"] += data["value"]
        summary = summary.model_copy(update=partial)
    valid = summary.error is None and not summary.invalid and (config.backend == "mock" or summary.pause_verified)
    record = {"attempt_id": attempt_id, "seed": seed, "snapshot": snapshot, "trace": str(trace),
        "success": valid and summary.goal_completed and summary.direct_acquired.get("oak_log", 0) >= 4,
        "valid": valid, "reason": summary.reason,
        "error_code": summary.error.code if summary.error else None if valid else "invalid_step",
        "error": summary.error.model_dump(mode="json") if summary.error else None,
        "active_ticks": summary.active_ticks, "wall_seconds": time.monotonic() - started,
        "collected_decisions": summary.selection_requests, "executed_decisions": summary.decisions,
        "direct_logs": summary.direct_acquired.get("oak_log", 0), "provided_inventory": summary.provided_inventory,
        "planner_calls": summary.planner_initial_requests + summary.planner_regeneration_requests,
        "pause_verified": summary.pause_verified, "reward_total": summary.reward_total,
        "api_cost_usd": 0.0}
    emit("pilot_attempt", record)
    return record


def evaluate(config: EpisodeConfig, path: Path, directory: Path, phase: str, model: NanoJevAdapter | None,
             snapshot: str, *, unavailable: str | None = None) -> list[dict[str, Any]]:
    rows = []
    for index, seed in enumerate(EVALUATION_SEEDS, 1):
        attempts = []
        if unavailable is None:
            assert model is not None
            for number in (1, 2):
                record = attempt(config, path, directory, f"{phase}-eval-{index}", number, model, seed, snapshot)
                attempts.append(record)
                if record["error_code"] not in SERVER_ERRORS:
                    break
        last = attempts[-1] if attempts else None
        row = {"slot_id": f"{phase}-eval-{index}", "phase": phase, "seed": seed,
               "success": bool(last and last["success"]), "attempts": attempts,
               "not_run_reason": unavailable, "first_error": attempts[0]["error_code"] if attempts else None}
        rows.append(row)
        emit("pilot_slot", row)
    return rows


def select_setting(settings: list[dict[str, Any]], evaluations: list[dict[str, Any]]) -> float | None:
    eligible = [setting for setting in settings if setting["usable"]]
    def rank(setting: dict[str, Any]) -> tuple[float, float, int, float]:
        successes = [row["attempts"][-1]["active_ticks"] for row in evaluations
                     if row["phase"] == setting["phase"] and row["success"]]
        return (-len(successes), sum(successes) / len(successes) if successes else 0.,
                len(setting["errors"]), float(setting["choice_lr"]))
    return float(min(eligible, key=rank)["choice_lr"]) if eligible else None


def train_setting(config: EpisodeConfig, path: Path, directory: Path, model: NanoJevAdapter,
                  seed: int, snapshot: str, lr: float) -> dict[str, Any]:
    phase = f"lr-{lr:g}"
    initial = hashes(model)
    torch.manual_seed(seed)
    learner = EpisodeLearner(model, PPOConfig(choice_lr=lr), seed, flush_on_finish=False)
    collected = 0
    episodes: list[dict[str, Any]] = []
    errors: list[str] = []
    while collected < DECISIONS:
        bounded = config.model_copy(update={"max_decisions": min(config.max_decisions, DECISIONS - collected)})
        row = attempt(bounded, path, directory, f"{phase}-train-{len(episodes) + 1}", 1, model, seed, snapshot, learner)
        episodes.append(row)
        collected += row["collected_decisions"]
        if not row["valid"] or row["collected_decisions"] == 0:
            errors.append(row["error_code"] or "no_progress")
            break
    final = hashes(model)
    gradients = [n for report in learner.update_reports for n in report["choice_gradient_norms"]]
    usable = (collected == DECISIONS and learner.updates == 8 and not learner.rows and not errors
              and learner.actor_transitions > 0 and any(n > 0 for n in gradients)
              and initial["backbone"] == final["backbone"] and initial["choice"] != final["choice"]
              and initial["critics"] != final["critics"])
    record = {"phase": phase, "choice_lr": lr, "initial_hashes": initial, "final_hashes": final,
        "collected_decisions": collected, "actor_transitions": learner.actor_transitions,
        "valid_transitions": learner.valid_transitions, "excluded_transitions": learner.excluded_transitions,
        "updates": learner.update_reports, "episodes": episodes, "errors": errors, "usable": usable,
        "backbone_unchanged": initial["backbone"] == final["backbone"],
        "choice_changed": initial["choice"] != final["choice"], "critic_changed": initial["critics"] != final["critics"],
        "unupdated_transitions": len(learner.rows) + int(learner.pending is not None)}
    emit("pilot_setting", record)
    return record


def pilot_wood(config: EpisodeConfig, path: Path, output: Path,
               correction_reason: str | None = None, correction_lr: float | None = None) -> int:
    started = time.monotonic()
    summary: dict[str, Any] = {"mock": config.backend == "mock", "planned_slots": 30, "settings": [], "evaluations": [],
        "selected_choice_lr": None, "restored_initial": False, "main_training_decisions": 0,
        "planner_calls": 0, "api_cost_usd": 0.0, "error": None}
    correction = correction_reason is not None
    directory = output / ("correction" if correction else "baseline")
    model: NanoJevAdapter | None = None
    initial: dict[str, str] = {}
    reserved = False
    rates: tuple[float, ...] = LEARNING_RATES
    snapshot = "unavailable"
    try:
        if (config.planner is not None or config.goal.kind != "collect" or config.goal.target != "oak_log"
                or config.goal.quantity != 4 or config.goal.source != "fixed" or config.ppo != PPOConfig()
                or config.model is not None and config.model.mode != "sampling"):
            raise ValueError("pilot-wood requires fixed collect oak_log=4, no planner, default PPO and sampling")
        if config.backend == "rpc" and (config.command is None or len(config.command) != 4
                or config.command[-2:] != ["--task", "G1"]
                or Path(config.command[1]).resolve() != Path("bridge/minecraft.js").resolve()):
            raise ValueError("Actual pilot requires the natural bridge/minecraft.js --task G1")
        snapshot = reset_state(config, path, "G1")
        if correction:
            if not correction_reason or not correction_reason.strip():
                raise ValueError("Corrective pilot needs the confirmed cause/fix and any LR change reason")
            baseline = output / "baseline" / "summary.json"
            if not baseline.exists():
                raise ValueError("Corrective pilot requires a recorded baseline pilot")
            previous = json.loads(baseline.read_text(encoding="utf-8"))
            manifest = json.loads((baseline.parent / "manifest.json").read_text(encoding="utf-8"))
            if manifest["snapshot"] != snapshot or previous["mock"] != summary["mock"]:
                raise ValueError("Corrective pilot must retain the baseline reset state and backend")
            rates = (correction_lr if correction_lr is not None else previous["selected_choice_lr"] or 1e-4,)
            if not 0 < rates[0] < 1:
                raise ValueError("Invalid corrective Choice LR")
            summary["planned_slots"] = 20
        elif correction_lr is not None:
            raise ValueError("An LR override requires --correction-reason")
        summary["correction_reason"] = correction_reason
        directory.mkdir(parents=True, exist_ok=False)
        reserved = True
        settings = config.model or ModelConfig()
        write_json(directory / "manifest.json", {"snapshot": snapshot, "config": config.model_dump(mode="json"),
            "training_seed": settings.seed, "evaluation_seeds": EVALUATION_SEEDS, "input_hash": INPUT_HASH,
            "revision": REVISION, "weights_sha256": WEIGHTS_SHA256, "decisions_per_setting": DECISIONS,
            "learning_rates": rates, "planned_slots": summary["planned_slots"], "correction_reason": correction_reason})
        torch.manual_seed(settings.seed)
        model = NanoJevAdapter.load((path.parent / settings.checkpoint).resolve())
        initial = hashes(model)
        model.save_heads(directory / "initial.safetensors")
        summary["evaluations"] = evaluate(config, path, directory, "initial", model, snapshot)
        for lr in rates:
            model.load_heads(directory / "initial.safetensors")
            record = train_setting(config, path, directory, model, settings.seed, snapshot, lr)
            summary["settings"].append(record)
            summary["evaluations"].extend(evaluate(config, path, directory, record["phase"], model, snapshot,
                unavailable=None if record["usable"] else "setting_unusable"))
        summary["selected_choice_lr"] = select_setting(summary["settings"], summary["evaluations"])
    except (ImportError, OSError, ValueError, RuntimeError, EpisodeError) as failure:
        summary["error"] = str(failure)
        print(f"pilot-wood failed: {failure}", file=sys.stderr)
    finally:
        if model is not None and (directory / "initial.safetensors").exists():
            model.load_heads(directory / "initial.safetensors")
            model.zero_grad(set_to_none=True)
            model.eval()
            summary["restored_initial"] = hashes(model) == initial
        summary["wall_seconds"] = time.monotonic() - started
    if reserved:
        existing = {row["slot_id"] for row in summary["evaluations"]}
        for phase in ["initial", *(f"lr-{lr:g}" for lr in rates)]:
            if any(row["phase"] == phase for row in summary["evaluations"]):
                continue
            missing = evaluate(config, path, directory, phase, model, snapshot, unavailable="pilot_incomplete")
            summary["evaluations"].extend(row for row in missing if row["slot_id"] not in existing)
        write_json(directory / "summary.json", summary)
    emit("pilot_summary", summary)
    return 0 if summary["selected_choice_lr"] is not None and summary["restored_initial"] and not summary["error"] else 1
