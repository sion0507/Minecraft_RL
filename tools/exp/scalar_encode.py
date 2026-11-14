"""CPU: the input groups, the 4 context scalars, targets and the run's values of saved decisions (no backbone feature)."""
import glob, json, math, sys, torch
sys.path.insert(0, 'tools/exp')
from critic_inputs import GROUPS, decisions, returns, scalars
out = {k: [] for k in ["context", "target", "predicted", "goal", "episode", *GROUPS]}
for episode, trace in enumerate(sorted(glob.glob(sys.argv[1]))):
    rows = decisions(trace); previous = None
    for row, target in zip(rows, returns(rows)):
        o = json.loads(row["observation"])["data"]; gid = row["goal"]["goal_id"]
        groups, distance = scalars(o, row["goal"], row["saved"]["candidates"], previous[1] if previous and previous[0] == gid else None)
        previous = (gid, distance)
        if target is None: continue
        out["context"].append([float(o["objective_kind"] == "local"), float(o["objective_kind"] == "full"),
                               math.log1p(o["remaining_ticks"]) / math.log1p(36000), math.log1p(row["goal"]["active_budget_ticks"]) / math.log1p(36000)])
        out["target"].append(target); out["predicted"].append(row["selection"]["values"]["local"]); out["goal"].append(gid); out["episode"].append(episode)
        for name, values in groups.items(): out[name].append(values)
    print(trace, len(out["target"]), flush=True)
torch.save({k: v if k == "goal" else torch.tensor(v) for k, v in out.items()}, sys.argv[2]); print("saved", sys.argv[2], len(out["target"]))
