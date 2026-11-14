"""#54 evaluation only: shared candidates versus their longest legal stair workloads (cap four).

Uses the same slot seeds 15000+i in both modes. Never trains or loads a trained head.
The effective candidate input is logged for the fixed-length control; original IDs are retained.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from mc_diamond.episode import emit
from mc_diamond.exp import UniformSelector, run_one, write_json
from mc_diamond.schema import CandidateSet, EpisodeConfig, allocate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selector", choices=["uniform", "nanojev"], required=True)
    parser.add_argument("--slots", type=int, default=10)
    parser.add_argument("--mode", choices=["choice", "fixed4"], default="choice")
    args = parser.parse_args()
    assert 1 <= args.slots <= 10
    tasks = [(p, EpisodeConfig.model_validate(yaml.safe_load(p.read_text()))) for p in args.config]
    args.output.mkdir(parents=True, exist_ok=False)
    model = None
    if args.selector == "nanojev":
        import torch
        from mc_diamond.nanojev import NanoJevAdapter
        torch.manual_seed(11015)
        path, config = tasks[0]
        assert config.model
        model = NanoJevAdapter.load((path.parent / config.model.checkpoint).resolve())
        model.save_heads(args.output / "initial.safetensors")
    summary: dict[str, Any] = {"selector": args.selector, "mode": args.mode, "planned_slots_per_task": args.slots,
                               "episodes": [], "error": None, "training": False}
    try:
        for index in range(args.slots):
            for task, (path, config) in enumerate(tasks):
                seed = 15000 + index
                if model is None:
                    selector: Any = UniformSelector(seed)
                else:
                    from mc_diamond.nanojev import NanoJevSelector
                    selector = NanoJevSelector(model, "sampling", seed)

                def select(o: Any, goal: Any, saved: CandidateSet, failures: Any) -> Any:
                    effective = saved
                    if args.mode == "fixed4":
                        # Near bedrock or tool exhaustion the legal maximum is below four; never bypass that limit.
                        stair = [c for c in saved.candidates if c.action_kind == "stair_down"]
                        kept = [c for c in saved.candidates if c.action_kind != "stair_down" or
                                c.params["stairs"] == max(s.params["stairs"] for s in stair
                                                         if s.params["direction"] == c.params["direction"])]
                        effective = allocate(kept)
                        assert effective.candidates
                        emit("execution_length_input", {"mode": "fixed4", "candidates": effective.model_dump(mode="json")})
                    return selector(o, goal, effective, failures)

                row = run_one(config, path, args.output, f"task{task}-slot{index + 1}", 1, select)
                summary["episodes"].append({"task": task, "seed": seed, **row})
                write_json(args.output / "summary.json", summary)
                print(json.dumps({"task": task, "slot": index + 1, **{k: row[k] for k in ["success", "active_ticks", "reason"]}}), flush=True)
                if not row["valid"]:
                    raise ValueError(f"Invalid slot {task}/{index + 1}: {row['reason']}")
    except Exception as error:
        summary["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        write_json(args.output / "summary.json", summary)


if __name__ == "__main__":
    main()
