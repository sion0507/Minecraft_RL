"""Critic on scalars only (no backbone feature): each input group alone on the 4 context scalars, and all-but-one.
Same fit and same held-out-by-episode scoring as tools/exp/critic_inputs.py fit. CPU."""
import json, statistics, sys, torch
sys.path.insert(0, 'tools/exp')
from critic_inputs import GROUPS, explained
data = torch.load(sys.argv[1]); lr = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-3
target, episode, goals = data["target"].float(), data["episode"], data["goal"]
names = sorted(set(goals)); rows = {n: torch.tensor([g == n for g in goals]) for n in names}
scored = [n for n in names if rows[n].sum() >= 100 and target[rows[n]].var() > 1e-6]
ctx = data["context"].float(); extra = {n: data[n].float().reshape(len(target), -1) for n in GROUPS}
variants = {"context only": ctx, **{f"ctx+{n}": torch.cat([ctx, extra[n]], 1) for n in GROUPS},
            "ctx+visible+angle": torch.cat([ctx, extra["visible"], extra["angle"]], 1),
            "ctx+visible+distance": torch.cat([ctx, extra["visible"], extra["distance"]], 1),
            "all scalars": torch.cat([ctx, *extra.values()], 1),
            **{f"all-{n}": torch.cat([ctx, *[v for k, v in extra.items() if k != n]], 1) for n in GROUPS}}
episodes = sorted(set(episode.tolist()))
print(sys.argv[1], "decisions", len(target), "lr", lr, {n.split(':')[-1]: (int(rows[n].sum()), round(float(target[rows[n]].mean()), 3), round(float(target[rows[n]].std()), 3)) for n in names})
print("run's own critic   ", " ".join(f"{n.split(':')[-1]} {explained(target[rows[n]], data['predicted'].float()[rows[n]]):+.3f}" for n in scored), f"pooled {explained(target, data['predicted'].float()):+.3f}")
out = {}
for label, inputs in variants.items():
    runs = []
    for seed in range(3):
        g = torch.Generator().manual_seed(seed); order = [episodes[i] for i in torch.randperm(len(episodes), generator=g).tolist()]
        held = torch.zeros(len(target))
        for fold in range(5):
            test = torch.isin(episode, torch.tensor(order[fold::5])); x, y = inputs[~test], target[~test]
            torch.manual_seed(seed * 100 + fold)
            head = torch.nn.Sequential(torch.nn.Linear(inputs.shape[1], 256), torch.nn.GELU(), torch.nn.Linear(256, 1))
            torch.nn.init.constant_(head[2].bias, float(y.mean())); opt = torch.optim.Adam(head.parameters(), lr=lr)
            for _ in range(40):
                for b in torch.randperm(len(y)).split(32):
                    loss = torch.nn.functional.mse_loss(head(x[b]).squeeze(-1), y[b]); opt.zero_grad(); loss.backward()
                    torch.nn.utils.clip_grad_norm_(head.parameters(), .5); opt.step()
            with torch.no_grad(): held[test] = head(inputs[test]).squeeze(-1)
        within = 1 - sum(float(((target[rows[n]] - held[rows[n]]) ** 2).sum()) for n in scored) / sum(float(((target[rows[n]] - target[rows[n]].mean()) ** 2).sum()) for n in scored)
        runs.append({**{n: explained(target[rows[n]], held[rows[n]]) for n in scored}, "within": within, "pooled": explained(target, held)})
    out[label] = {k: (statistics.mean(r[k] for r in runs), statistics.stdev(r[k] for r in runs)) for k in runs[0]}
    print(f"{label:22s} " + " ".join(f"{k.split(':')[-1]} {m:+.3f}±{s:.3f}" for k, (m, s) in out[label].items()), flush=True)
json.dump(out, open(sys.argv[1].replace('.pt', f'-scalars-lr{lr:g}.json'), 'w'), indent=1)
