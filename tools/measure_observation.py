"""#44 observation measurements from the repository root.

`game`: for each task snapshot, reset and observe three times, then one 20-tick wait; records RPC latency, frame size,
cell counts, the shared summary and which ores are in view. Diagnostic only: never a task result.
`models`: on those saved observations, counts actual Qwen planner and NanoJev Choice tokens for the new summary and the
previous 64-cell rules, then times one real Qwen call and one NanoJev forward per observation on CUDA.
"""

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import yaml

from mc_diamond.episode import policy_candidates
from mc_diamond.model_input import OPEN, choice_input, memory_summary, public_state, text
from mc_diamond.rpc import RpcSession
from mc_diamond.schema import Candidate, EpisodeConfig, Goal, Observation

TASKS = {"C4": "configs/minecraft.yaml", "G1": "configs/planner_minecraft.yaml", "G2": "configs/g2_natural.yaml", "G3": "configs/g3.yaml", "G4": "configs/g4.yaml"}


def legacy_planner_state(observation: Observation) -> dict[str, Any]:
    """Before #44: visible non-air surfaces by distance, 64 dicts (planner.py at e9e84ae)."""
    state = observation.model_dump(exclude={"episode_id", "attempt_id", "obs_id", "observed_map", "visited", "history",
                                            "discovered_open"})
    surfaces = sorted((s for s in observation.observed_map if s.visible and s.block not in OPEN),
                      key=lambda s: (sum((a - b) ** 2 for a, b in zip(s.position, observation.position)), s.position, s.block))
    state.update(observed_surfaces=[s.model_dump() for s in surfaces[:64]], observed_surface_count=len(surfaces),
                 visited_count=len(observation.visited), recent_visited=observation.visited[-32:], recent_results=observation.history[-8:])
    return state


def game(output: Path) -> None:
    results: dict[str, Any] = {}
    for task, config_path in TASKS.items():
        config = EpisodeConfig.model_validate(yaml.safe_load(Path(config_path).read_text()))
        assert config.command is not None and config.goal is not None
        with RpcSession(config.command, config.rpc_timeout_seconds) as session:
            started = time.monotonic()
            initial = session.reset(f"measure-{task}", "1")
            reset_seconds = time.monotonic() - started
            observes = []
            for _ in range(3):
                started = time.monotonic()
                observation = session.policy().observe()
                observes.append(time.monotonic() - started)
            assert observation.observed_map == initial.observed_map, "repeated frozen observation changed"
            wait = Candidate(candidate_id=f"{observation.obs_id}:wait", action_kind="wait", params={}, max_ticks=20,
                             stop_rule_id="elapsed", source_obs_id=observation.obs_id, description="Wait 20 active ticks")
            started = time.monotonic()
            step = session.policy().step(wait)
            step_seconds = time.monotonic() - started
        cells = observation.observed_map
        summary = memory_summary(observation)
        results[task] = {
            "position": observation.position, "reset_seconds": reset_seconds, "observe_seconds": observes,
            "frame_bytes": len(observation.model_dump_json()), "cells": len(cells),
            "air": sum(c.block in OPEN for c in cells), "nonair": sum(c.block not in OPEN for c in cells),
            "visible": sum(c.visible for c in cells), "discovered_open": observation.discovered_open,
            "ores": sorted([c.block, c.position, c.visible, round(math.dist(c.position, observation.position), 1)]
                           for c in cells if c.block.endswith("_ore")),
            "diamond_visible": any(c.block == "diamond_ore" and c.visible for c in cells),
            "summary": [{k: kind[k] for k in ("block", "total")} | {"shown": len(kind["now"]) + len(kind["past"])}
                        for kind in summary],
            "wait": {"seconds": step_seconds, "actual_ticks": step.actual_ticks, "reason": step.reason,
                     "pause_verified": step.pause_verified, "clock_mode": step.clock_mode},
            "goal": config.goal.model_dump(mode="json"),
        }
        (output / f"{task}-observation.json").write_text(observation.model_dump_json())
        print(json.dumps({"task": task, **{k: results[task][k] for k in ("cells", "nonair", "frame_bytes", "observe_seconds",
                                                                     "diamond_visible", "wait")}}), flush=True)
    (output / "game.json").write_text(json.dumps(results, indent=1))


def models(output: Path) -> None:
    import torch
    from transformers import AutoTokenizer

    from mc_diamond.nanojev import NanoJevAdapter, tokenize
    from mc_diamond.planner import PROMPT, LocalPlanner, messages
    from mc_diamond.schema import LocalPlannerConfig

    planner_config = yaml.safe_load(Path("configs/planner_minecraft.yaml").read_text())["planner"]
    qwen_root = Path("checkpoints/qwen2.5-7b")
    qwen = AutoTokenizer.from_pretrained(qwen_root, local_files_only=True)
    calls: list[dict[str, Any]] = []
    planner = LocalPlanner(LocalPlannerConfig.model_validate(planner_config), qwen_root.resolve(), lambda kind, data: calls.append({"kind": kind, **data}))
    nanojev = NanoJevAdapter.load(Path("checkpoints/nanojev"))
    nanojev.eval()
    results: dict[str, Any] = {}
    for path in sorted(output.glob("*-observation.json")):
        task = path.name.split("-")[0]
        observation = Observation.model_validate_json(path.read_text())
        goal = Goal.model_validate(json.loads((output / "game.json").read_text())[task]["goal"])
        legacy = [{"role": "system", "content": PROMPT}, {"role": "user", "content": json.dumps(
            {"observation": legacy_planner_state(observation), "task": goal.model_dump(exclude={"goal_id"}), "feedback": None,
             "knowledge": None}, ensure_ascii=False)}]
        saved = policy_candidates(observation, goal, macros=True)
        count = [len(qwen.apply_chat_template(m, add_generation_prompt=True, tokenize=True, return_dict=True)["input_ids"])
                 for m in (messages(observation, goal, None), legacy)]
        row: dict[str, Any] = {"planner_tokens": count[0], "planner_tokens_old_64_state": count[1],
                               "state_chars": len(text(public_state(observation))), "candidates": len(saved.candidates)}
        if saved.candidates and any(saved.mask):
            paths = tokenize(choice_input(observation, goal, saved), nanojev.tokenizer, nanojev.max_length)
            row["nanojev_path_tokens_max"], row["nanojev_tokens_total"] = max(map(len, paths)), sum(map(len, paths))
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            started = time.monotonic()
            with torch.inference_mode():
                nanojev.encode_candidates(choice_input(observation, goal, saved))
            torch.cuda.synchronize()
            row["nanojev_seconds"], row["nanojev_peak_bytes"] = time.monotonic() - started, torch.cuda.max_memory_allocated()
        planner(observation, goal, None)
        call = calls[-1]
        row["qwen"] = {k: call.get(k) for k in ("input_tokens", "output_tokens", "latency_seconds", "peak_allocated_bytes", "reply")}
        row["cuda_allocated_bytes_with_both_models"] = torch.cuda.memory_allocated()
        results[task] = row
        print(json.dumps({"task": task, **{k: v for k, v in row.items() if k != "qwen"}, "qwen": row["qwen"]}), flush=True)
    (output / "models.json").write_text(json.dumps({"loaded": [c for c in calls if c["kind"] == "planner_loaded"], "results": results}, indent=1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("phase", choices=["game", "models"])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.phase == "game":
        game(args.output)
    else:
        models(args.output)


if __name__ == "__main__":
    main()
