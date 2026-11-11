"""Pilot diagnostics from existing public traces; no game, model encoding or API calls."""

import gzip
import json
import statistics
from pathlib import Path
from typing import Any

from .navigation import PICKS


def trace_diagnostics(trace: Path, discovery_reward: float) -> dict[str, Any]:
    result: dict[str, Any] = {"first_pickaxe_tick": None, "first_stone_visible_tick": None,
        "first_stone_mined_tick": None, "first_cobblestone_tick": None, "discovery_awards": 0,
        "discovery_reward_total": 0., "mc_returns": [], "mc_values": []}
    transitions = []
    evaluated = []
    value = None
    valid = False
    with gzip.open(trace, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            data = row["data"]
            if row["type"] == "selection":
                value = (data.get("values") or {}).get("local")
            if row["type"] in {"reset", "step"}:
                observation = data if row["type"] == "reset" else data["observation"]
                tick = observation["active_ticks"]
                if row["type"] == "step":
                    valid = not data["invalid"] and (data["stable_boundary"] or observation["health"] <= 0
                                                     or observation["remaining_ticks"] == 0)
                if result["first_pickaxe_tick"] is None and any(observation["inventory"].get(pick, 0) for pick in PICKS):
                    result["first_pickaxe_tick"] = tick
                if result["first_stone_visible_tick"] is None and any(
                        c["block"] == "stone" and c.get("visible", True) for c in observation["observed_map"]):
                    result["first_stone_visible_tick"] = tick
                for event in data.get("events", []) if row["type"] == "step" else []:
                    if event["kind"] == "mined" and event.get("item") == "stone" and result["first_stone_mined_tick"] is None:
                        result["first_stone_mined_tick"] = tick
                    if (event["kind"] == "acquired" and event.get("item") == "cobblestone"
                            and result["first_cobblestone_tick"] is None):
                        result["first_cobblestone_tick"] = tick
            elif row["type"] == "reward":
                gain = data.get("components", {}).get("discovery", 0.)
                result["discovery_reward_total"] += gain
                if discovery_reward:
                    result["discovery_awards"] += round(gain / discovery_reward)
                if "discounted" in data:
                    evaluated.append({"reward": data["discounted"], "discount": data["discount"],
                        "old_value": value, "valid": valid and value is not None, "bootstrap": not data["task_terminal"]})
            elif row["type"] == "transition":
                transitions.append({k: data[k] for k in ("reward", "discount", "old_value", "valid", "bootstrap")})
    transitions = transitions or evaluated
    # A truncated/incomplete return needs an unknown future: it is not a Monte Carlo target.
    if transitions and not transitions[-1]["bootstrap"] and all(t["valid"] for t in transitions):
        total = 0.
        for transition in reversed(transitions):
            total = transition["reward"] + transition["discount"] * total
            result["mc_returns"].append(total)
        result["mc_returns"].reverse()
        result["mc_values"] = [t["old_value"] for t in transitions]
    return result


def critic_diagnostics(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    targets = [v for episode in episodes for v in episode["mc_returns"]]
    values = [v for episode in episodes for v in episode["mc_values"]]
    variance = statistics.pvariance(targets) if targets else 0.
    ev = 1 - statistics.pvariance([a - b for a, b in zip(targets, values)]) / variance if variance > 0 else None
    return {"transitions": len(targets), "explained_variance": ev}


def episode_halves(episodes: list[dict[str, Any]], budget: int) -> dict[str, Any]:
    result = {}
    middle = len(episodes) // 2
    for name, rows in (("first", episodes[:middle]), ("last", episodes[middle:])):
        result[name] = {"episodes": len(rows), "successes": sum(r["success"] for r in rows),
            "mean_active_ticks": statistics.mean(r["active_ticks"] for r in rows) if rows else None,
            "mean_charged_ticks": statistics.mean(r["active_ticks"] if r["success"] else budget for r in rows) if rows else None}
    return result
