"""E0: regenerate candidates from saved real observations (no game, no GPU) and classify what each decision offers."""
import gzip, json, sys, glob
from collections import Counter
from mc_diamond.episode import policy_candidates
from mc_diamond.schema import Goal, Observation


def category(cands: list[dict]) -> str:
    kinds = Counter(c["action_kind"] for c in cands)
    text = " ".join(c["description"] for c in cands)
    if len(cands) <= 1:
        return "single_or_none"
    if kinds["mine_visible_cluster"]:
        return "mine_available"
    if kinds["stair_down"] or kinds["tunnel"]:
        return "cut+walk" + ("+toward" if "Walk toward" in text else "")
    if "Approach" in text:
        return "approach"
    if "Walk toward" in text:
        return "toward+walk"
    return "walk_only"


def main(patterns: list[str]) -> None:
    old, new, sizes_old, sizes_new, mine_share_old, mine_share_new = Counter(), Counter(), [], [], [], []
    by_goal: dict[str, Counter] = {}
    for pattern in patterns:
        for name in sorted(glob.glob(pattern)):
            obs = goal = None
            for line in gzip.open(name, "rt"):
                row = json.loads(line)
                kind, data = row["type"], row["data"]
                if kind == "observation":
                    obs = data
                elif kind == "goal":
                    goal = data
                elif kind == "candidates":
                    before = data["candidates"]
                    if EQUIPPED and goal["target"] == "cobblestone" and obs["inventory"].get("wooden_pickaxe"):
                        # The old flow equipped only next to stone; show what the new flow offers once the pick is in hand.
                        obs = {**obs, "tool": "wooden_pickaxe", "tool_durability": obs.get("tool_durability") or 59}
                    after = [c.model_dump(mode="json") for c in policy_candidates(
                        Observation.model_validate(obs), Goal.model_validate(goal), macros=True).candidates]
                    a, b = category(before), category(after)
                    old[(goal["goal_id"], a)] += 1; new[(goal["goal_id"], b)] += 1
                    by_goal.setdefault(goal["goal_id"], Counter())[(a, b)] += 1
                    sizes_old.append(len(before)); sizes_new.append(len(after))
                    for cands, shares in ((before, mine_share_old), (after, mine_share_new)):
                        mines = sum(c["action_kind"] == "mine_visible_cluster" for c in cands)
                        if mines:
                            shares.append(mines / len(cands))
    for goal_id, table in sorted(by_goal.items()):
        total = sum(table.values())
        print(f"\n{goal_id}: {total} decisions")
        for label, counts in (("old", old), ("new", new)):
            row = {c: n for (g, c), n in counts.items() if g == goal_id}
            print("  ", label, ", ".join(f"{c} {n} ({n / total:.0%})" for c, n in sorted(row.items(), key=lambda kv: -kv[1])))
    mean = lambda v: sum(v) / len(v) if v else float("nan")
    print(f"\ncandidates per decision: old {mean(sizes_old):.1f} new {mean(sizes_new):.1f}")
    print(f"share of mine candidates when any is offered: old {mean(mine_share_old):.2f} (n={len(mine_share_old)}) "
          f"new {mean(mine_share_new):.2f} (n={len(mine_share_new)})")


EQUIPPED = "--equipped" in sys.argv
main([a for a in sys.argv[1:] if a != "--equipped"])
