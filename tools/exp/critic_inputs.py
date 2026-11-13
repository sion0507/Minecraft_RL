"""Which extra critic input helps? Offline, on saved decisions (no game): one input group at a time.

    encode: frozen-backbone features (mean over offered candidates, what the critic head sees) + candidate input groups
            + the return the run's critic was trained on, for every saved decision.
    fit:    the critic head (same shape as NanoJevAdapter.critics) refit per input variant, episodes held out in turn;
            explained variance of the held-out returns, per sub-goal (pooled EV mostly measures telling sub-goals apart).

    python tools/exp/critic_inputs.py encode --traces 'artifacts/exp/T-train-stone_pick/train-*.jsonl.gz' --output artifacts/exp/critic-T.pt
    python tools/exp/critic_inputs.py fit --data artifacts/exp/critic-T.pt --output artifacts/exp/critic-T.json
"""
import argparse
import glob
import gzip
import json
import math
import statistics
from pathlib import Path
from typing import Any

import torch

GROUPS = ["visible", "stage", "distance", "steps", "height", "angle", "progress", "holdings", "durability"]
GEOMETRY = ["distance", "steps", "height", "angle", "progress"]  # also tried on top of `visible`, to see what they add to it
STAGES = ["Mine ", "Approach exposed", "Walk toward exposed", "Walk toward remembered"]


def facing(yaw: float, pitch: float) -> list[float]:
    """Mineflayer: yaw 0 looks north (-z) and grows counter-clockwise, pitch is positive upward."""
    return [-math.sin(yaw) * math.cos(pitch), math.sin(pitch), -math.cos(yaw) * math.cos(pitch)]


def angle(a: list[float], b: list[float]) -> float:
    norm = math.hypot(*a) * math.hypot(*b)
    return math.acos(max(-1., min(1., sum(x * y for x, y in zip(a, b)) / norm))) / math.pi if norm else .5


def scalars(observation: dict[str, Any], goal: dict[str, Any], candidates: list[dict[str, Any]],
            previous: float | None) -> tuple[dict[str, list[float]], float | None]:
    """Input groups for one decision, each already scaled to about [-1, 1], and the distance to carry to the next one."""
    block = {"cobblestone": "stone", "diamond": "diamond_ore"}.get(goal["target"], goal["target"])
    position = observation["position"]
    eye = [position[0], position[1] + 1.62, position[2]]
    cells = [c for c in observation["observed_map"] if c["block"] == block] if goal["kind"] == "collect" else []
    seen = [c["position"] for c in cells if c.get("visible", True)]
    past = [c["position"] for c in cells if not c.get("visible", True)]

    def nearest(points: list[list[float]]) -> tuple[float, list[float]] | None:
        return min(((math.dist(position, p), p) for p in points), default=None)

    near = nearest(seen) or nearest(past)
    texts = [c["description"] for c in candidates]
    stage = next((i for i, start in enumerate(STAGES) if any(t.startswith(start) for t in texts)),
                 2 if seen else 3 if past else 4)
    routes = [len(c["params"]["path"]) for c in candidates if c["description"].startswith("Approach exposed")]
    distance = min(near[0], 32.) / 32 if seen and near else 1.
    to_target = [near[1][i] + .5 - eye[i] for i in range(3)] if near else None
    look = facing(observation.get("yaw", 0.), observation.get("pitch", 0.))
    durability = observation.get("tool_durability")
    groups = {
        "visible": [float(bool(seen)), float(bool(past))],
        "stage": [float(stage == i) for i in range(5)],
        "distance": [distance],
        "steps": [0. if stage == 0 else min(routes) / 16 if routes else 1.],
        "height": [max(-1., min(1., (near[1][1] - position[1]) / 16)) if near else 0.],
        "angle": [angle(look, to_target) if to_target else .5,
                  angle([look[0], look[2]], [to_target[0], to_target[2]]) if to_target else .5],
        "progress": [(previous - distance) if previous is not None else 0.],
        "holdings": [min(1., observation["inventory"].get(goal["target"], 0) / goal["quantity"])],
        "durability": [min(durability, 131) / 131 if durability else 0., float(durability is not None)],
    }
    return groups, distance


def decisions(trace: str) -> list[dict[str, Any]]:
    """Saved decisions of one episode in order: raw observation line, goal, candidates, selection and reward records."""
    rows: list[dict[str, Any]] = []
    observation = goal = saved = selection = None
    with gzip.open(trace, "rt") as handle:
        for line in handle:
            kind = line[10:line.index('"', 10)]
            if kind == "observation":
                observation = line
            elif kind == "goal":
                goal = json.loads(line)["data"]
            elif kind == "candidates":
                saved = json.loads(line)["data"]
            elif kind == "selection":
                selection = json.loads(line)["data"]
            elif kind == "reward" and observation and goal and saved and selection and saved["candidates"]:
                rows.append({"observation": observation, "goal": goal, "saved": saved, "selection": selection,
                             "reward": json.loads(line)["data"]})
                saved = selection = None
    return rows


def returns(rows: list[dict[str, Any]]) -> list[float | None]:
    """The run's critic target (learning.mc_returns): discounted reward to the end of the current sub-goal."""
    targets: list[float | None] = [None] * len(rows)
    for i in range(len(rows) - 1, -1, -1):
        reward = rows[i]["reward"]
        if reward["task_terminal"]:
            targets[i] = reward["discounted"]
        elif i + 1 < len(rows) and reward["trace_mask"] and rows[i + 1]["goal"] == rows[i]["goal"] and targets[i + 1] is not None:
            targets[i] = reward["discounted"] + reward["discount"] * targets[i + 1]
    return targets


def encode(args: argparse.Namespace) -> None:
    from mc_diamond.model_input import choice_input
    from mc_diamond.nanojev import NanoJevAdapter
    from mc_diamond.schema import CandidateSet, Goal, Observation
    if not args.scalars_only:
        torch.cuda.set_per_process_memory_fraction(args.gpu_fraction)
        model = NanoJevAdapter.load(args.checkpoint.resolve())
        model.eval()
    out: dict[str, Any] = {"features": [], "context": [], "target": [], "predicted": [], "goal": [], "episode": [],
                           **{name: [] for name in GROUPS}}
    for episode, trace in enumerate(sorted(glob.glob(args.traces))):
        rows = decisions(trace)
        previous: tuple[str, float] | None = None
        for row, target in zip(rows, returns(rows)):
            observation = json.loads(row["observation"])["data"]
            goal_id = row["goal"]["goal_id"]
            groups, distance = scalars(observation, row["goal"], row["saved"]["candidates"],
                                       previous[1] if previous and previous[0] == goal_id else None)
            previous = (goal_id, distance)
            if target is None:
                continue
            if not args.scalars_only:
                saved = CandidateSet.model_validate(row["saved"])
                encoded = choice_input(Observation.model_validate(observation), Goal.model_validate(row["goal"]), saved)
                with torch.no_grad():
                    features = model.encode_candidates(encoded)
                out["features"].append(features[torch.tensor(saved.mask, device=features.device)].mean(0).float().cpu())
                out["context"].append(encoded.context)
            out["target"].append(target)
            out["predicted"].append(row["selection"]["values"]["local"])
            out["goal"].append(goal_id)
            out["episode"].append(episode)
            for name, values in groups.items():
                out[name].append(values)
        print(trace, len(out["target"]), flush=True)
        if args.limit and len(out["target"]) >= args.limit:
            break
    data = {key: value if key == "goal" else torch.stack(value) if key == "features" else torch.tensor(value)
            for key, value in out.items() if value}
    torch.save(data, args.output)
    print("saved", args.output, len(out["target"]), "decisions")


def explained(target: torch.Tensor, predicted: torch.Tensor) -> float:
    return float(1 - ((target - predicted) ** 2).sum() / ((target - target.mean()) ** 2).sum().clamp_min(1e-12))


def fit(args: argparse.Namespace) -> None:
    data = torch.load(args.data)
    target, episode, goals = data["target"].float(), data["episode"], data["goal"]
    names = sorted(set(goals))
    goal_rows = {name: torch.tensor([g == name for g in goals]) for name in names}
    scored = [name for name in names if goal_rows[name].sum() >= 100 and target[goal_rows[name]].var() > 1e-6]
    base = torch.cat([data["features"].float(), data["context"].float()], 1)
    extra = {name: data[name].float().reshape(len(target), -1) for name in GROUPS}
    variants: dict[str, torch.Tensor] = {"base": base}
    variants.update({f"+{name}": torch.cat([base, extra[name]], 1) for name in GROUPS})
    variants.update({f"+visible+{name}": torch.cat([base, extra["visible"], extra[name]], 1) for name in GEOMETRY})
    variants["+all"] = torch.cat([base, *extra.values()], 1)
    variants["scalars only"] = torch.cat([data["context"].float(), *extra.values()], 1)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    episodes = sorted(set(episode.tolist()))
    result: dict[str, Any] = {"decisions": len(target), "episodes": len(episodes), "settings": vars(args) | {"data": str(args.data), "output": str(args.output)},
                              "goals": {name: {"decisions": int(goal_rows[name].sum()), "return_mean": float(target[goal_rows[name]].mean()),
                                               "return_sd": float(target[goal_rows[name]].std())} for name in names},
                              "run_critic": {name: explained(target[goal_rows[name]], data["predicted"].float()[goal_rows[name]]) for name in scored}
                              | {"pooled": explained(target, data["predicted"].float())}, "variants": {}}
    for label, inputs in variants.items():
        runs: list[dict[str, float]] = []
        for seed in range(args.seeds):
            generator = torch.Generator().manual_seed(seed)
            order = [episodes[i] for i in torch.randperm(len(episodes), generator=generator).tolist()]
            held = torch.zeros(len(target))
            for fold in range(args.folds):
                test = torch.isin(episode, torch.tensor(order[fold::args.folds]))
                x, y = inputs[~test].to(device), target[~test].to(device)
                torch.manual_seed(seed * 100 + fold)
                head = torch.nn.Sequential(torch.nn.Linear(inputs.shape[1], 256), torch.nn.GELU(), torch.nn.Linear(256, 1)).to(device)
                torch.nn.init.constant_(head[2].bias, float(y.mean()))
                optimizer = torch.optim.Adam(head.parameters(), lr=args.lr)
                for _ in range(args.epochs):
                    for batch in torch.randperm(len(y), device=device).split(32):
                        loss = torch.nn.functional.mse_loss(head(x[batch]).squeeze(-1), y[batch])
                        optimizer.zero_grad()
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(head.parameters(), .5)
                        optimizer.step()
                with torch.no_grad():
                    held[test] = head(inputs[test].to(device)).squeeze(-1).cpu()
            within = 1 - sum(float(((target[goal_rows[n]] - held[goal_rows[n]]) ** 2).sum()) for n in scored) / sum(
                float(((target[goal_rows[n]] - target[goal_rows[n]].mean()) ** 2).sum()) for n in scored)
            runs.append({**{name: explained(target[goal_rows[name]], held[goal_rows[name]]) for name in scored},
                         "within": within, "pooled": explained(target, held)})
        result["variants"][label] = {key: {"mean": statistics.mean(r[key] for r in runs),
                                           "sd": statistics.stdev(r[key] for r in runs) if len(runs) > 1 else 0.} for key in runs[0]}
        print(f"{label:22s} " + " ".join(f"{key.split(':')[-1]} {value['mean']:+.3f}±{value['sd']:.3f}"
                                         for key, value in result["variants"][label].items()), flush=True)
    args.output.write_text(json.dumps(result, indent=1) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("encode")
    one.add_argument("--traces", required=True)
    one.add_argument("--output", type=Path, required=True)
    one.add_argument("--checkpoint", type=Path, default=Path("checkpoints/nanojev"))
    one.add_argument("--gpu-fraction", type=float, default=.45)
    one.add_argument("--limit", type=int, default=0)
    one.add_argument("--scalars-only", action="store_true", help="no model: only the input groups and returns (CPU check)")
    two = commands.add_parser("fit")
    two.add_argument("--data", type=Path, required=True)
    two.add_argument("--output", type=Path, required=True)
    two.add_argument("--folds", type=int, default=5)
    two.add_argument("--seeds", type=int, default=3)
    two.add_argument("--epochs", type=int, default=40)
    two.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()
    encode(args) if args.command == "encode" else fit(args)


if __name__ == "__main__":
    main()
