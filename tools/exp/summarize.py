"""Summarise one exp run directory from summary.json and its traces (no game, no GPU)."""
import gzip, json, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path


def choice_class(candidate: dict) -> str:
    kind, text = candidate["action_kind"], candidate["description"]
    if kind == "move_observed":
        return ("toward" if text.startswith("Walk toward") else "approach" if text.startswith("Approach")
                else "pickup" if text.startswith("Collect") else "explore")
    return {"mine_visible_cluster": "mine", "stair_down": "stairs", "place_or_equip": "equip"}.get(kind, kind)


def decisions(trace: str):
    """(goal_id, candidates, selection) per decision; observation/step lines are skipped unparsed (30 MB each)."""
    goal = cands = None
    with gzip.open(trace, "rt") as handle:
        for line in handle:
            head = line[:28]
            if '"goal"' in head and '"goal_decision"' not in head:
                goal = json.loads(line)["data"]
            elif '"candidates"' in head:
                cands = json.loads(line)["data"]["candidates"]
            elif '"selection"' in head:
                yield goal["goal_id"], cands, json.loads(line)["data"]


def main(directory: Path, policy: bool) -> None:
    summary = json.loads((directory / "summary.json").read_text())
    print(directory.name, "error:", summary["error"], "wall h: %.2f" % (summary.get("wall_seconds", 0) / 3600))
    budgets = [int(t["command"][-1]) if t.get("command") else 0 for t in summary["tasks"]]
    groups = defaultdict(list)
    for row in summary["episodes"]:
        phase = row["phase"]
        groups[(row["task"], phase)].append(row)
    for (task, phase), rows in sorted(groups.items()):
        rows = [r for r in rows if r["valid"]] or rows
        parts = [rows] if phase != "train" else [rows[i * len(rows) // 4:(i + 1) * len(rows) // 4] for i in range(4)]
        for index, part in enumerate(parts):
            if not part:
                continue
            ticks = [r["active_ticks"] if r["success"] else budgets[task] for r in part]
            done = Counter(s["goal"] for r in part for s in r["subgoals"] if s["completed"])
            label = phase if phase != "train" else f"train {index + 1}/4"
            print(f"  task{task} {label:10s} success {sum(r['success'] for r in part)}/{len(part)}  ticks mean {statistics.mean(ticks):.0f} "
                  f"median {statistics.median(ticks):.0f}  decisions/ep {statistics.mean(r['selections'] for r in part):.1f}  subgoals {dict(done)}")
    if not policy:
        return
    # Probability mass the policy put on each choice class, by what the decision offered (multi-candidate decisions only).
    table = defaultdict(lambda: defaultdict(list))
    picked = defaultdict(Counter)
    order = [r for r in summary["episodes"]]
    train = [r for r in order if r["phase"] == "train"]
    for row in order:
        phase = row["phase"]
        if phase == "train":
            phase = f"train {4 * train.index(row) // len(train) + 1}/4"
        for goal_id, cands, selection in decisions(row["trace"]):
            probabilities = selection.get("probabilities")
            if not cands or len(cands) < 2 or not probabilities:
                continue
            classes = [choice_class(c) for c in cands]
            offered = "+".join(sorted(set(classes)))
            mass = Counter()
            for c, name in zip(cands, classes):
                mass[name] += probabilities.get(c["candidate_id"], 0.)
            for name in set(classes):
                table[(goal_id, offered, name)][phase].append((mass[name], classes.count(name) / len(classes)))
            chosen = next((n for c, n in zip(cands, classes) if c["candidate_id"] == selection["candidate_id"]), "?")
            picked[(goal_id, offered, phase)][chosen] += 1
    phases = sorted({p for cell in table.values() for p in cell}, key=lambda p: (p.startswith("after"), p.startswith("train"), p))
    print("\n  policy mass per choice class (mean probability | uniform share | n):")
    for (goal_id, offered, name), cell in sorted(table.items()):
        if sum(len(v) for v in cell.values()) < 8:
            continue
        print(f"  {goal_id} [{offered}] -> {name}: " + "  ".join(
            f"{p}: {statistics.mean(m for m, _ in cell[p]):.2f}|{statistics.mean(u for _, u in cell[p]):.2f}|{len(cell[p])}"
            for p in phases if cell.get(p)))


if __name__ == "__main__":
    main(Path(sys.argv[1]), "--policy" in sys.argv)
