"""Probability saved heads put on each choice class over one fixed set of saved decisions (model only, no game).

The run summaries compare before/after on different states; this scores every head file on the same states.
    python tools/exp/fixed_probe.py --traces 'artifacts/exp/T-train-stone_pick/before-*.jsonl.gz' \
        --heads artifacts/exp/T-train-stone_pick/initial.safetensors artifacts/exp/T-train-stone_pick/final.safetensors \
        --output artifacts/exp/probe-T.json
"""
import argparse
import glob
import gzip
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import torch

from mc_diamond.model_input import choice_input
from mc_diamond.nanojev import NanoJevAdapter
from mc_diamond.schema import CandidateSet, Goal, Observation

sys.path.insert(0, str(Path(__file__).parent))
from summarize import choice_class  # noqa: E402


def saved_decisions(trace: str):
    """(observation, goal, candidates) of every decision that offered at least two candidates."""
    observation = goal = None
    with gzip.open(trace, "rt") as handle:
        for line in handle:
            head = line[:28]
            if '"observation"' in head:
                observation = line
            elif '"goal"' in head and '"goal_decision"' not in head:
                goal = json.loads(line)["data"]
            elif '"candidates"' in head:
                saved = json.loads(line)["data"]
                if len(saved["candidates"]) >= 2 and observation is not None:
                    yield json.loads(observation)["data"], goal, saved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True, help="glob of traces whose decisions are the fixed states")
    parser.add_argument("--heads", type=Path, nargs="+", required=True)
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/nanojev"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--gpu-fraction", type=float, default=.75, help="hard cap on this process (encoding 16 candidates needs several GB)")
    args = parser.parse_args()
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(args.gpu_fraction)
    model = NanoJevAdapter.load(args.checkpoint.resolve())
    model.eval()
    states = []
    for trace in sorted(glob.glob(args.traces)):
        for observation, goal, saved in saved_decisions(trace):
            candidates = CandidateSet.model_validate(saved)
            encoded = choice_input(Observation.model_validate(observation), Goal.model_validate(goal), candidates)
            with torch.no_grad():
                features = model.encode_candidates(encoded)
            classes = [choice_class(c) for c in saved["candidates"]]
            states.append((goal["goal_id"], classes, features, torch.tensor(candidates.mask, device=features.device),
                           torch.tensor(encoded.context, device=features.device)))
            if args.limit and len(states) >= args.limit:
                break
        if args.limit and len(states) >= args.limit:
            break
    print("fixed states:", len(states), flush=True)
    result: dict[str, dict[str, dict[str, float]]] = {}
    for path in args.heads:
        model.load_heads(path)
        model.eval()
        table: dict[str, list[tuple[float, float]]] = defaultdict(list)
        entropy = []
        for goal_id, classes, features, mask, context in states:
            with torch.no_grad():
                probabilities = model.score_features(features, mask, context)[0].float().softmax(-1).tolist()
            entropy.append(-sum(p * torch.log(torch.tensor(max(p, 1e-30))).item() for p in probabilities)
                           / torch.log(torch.tensor(float(len(probabilities)))).item())
            offered = "+".join(sorted(set(classes)))
            for name in set(classes):
                table[f"{goal_id} [{offered}] -> {name}"].append(
                    (sum(p for p, c in zip(probabilities, classes) if c == name), classes.count(name) / len(classes)))
        result[str(path)] = {key: {"probability": statistics.mean(p for p, _ in rows), "uniform": statistics.mean(u for _, u in rows),
                                   "states": len(rows)} for key, rows in table.items()}
        result[str(path)]["normalized_entropy"] = {"probability": statistics.mean(entropy), "uniform": 1., "states": len(entropy)}
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    names = [p.parent.name[:1] + ":" + p.stem.replace("update-", "u") for p in args.heads]
    print("class (uniform share, n) | " + " ".join(f"{n:>9s}" for n in names))
    for key in sorted(result[str(args.heads[0])]):
        first = result[str(args.heads[0])][key]
        if first["states"] >= 5 and first["uniform"] < 1:
            print(f"{key} ({first['uniform']:.2f}, {first['states']}) | "
                  + " ".join(f"{result[str(p)][key]['probability']:9.3f}" for p in args.heads))
    print("normalized entropy | " + " ".join(f"{result[str(p)]['normalized_entropy']['probability']:9.3f}" for p in args.heads))


if __name__ == "__main__":
    main()
