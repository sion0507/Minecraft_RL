"""T06 actual Minecraft diagnostics, from the repository root; no models or APIs.

Every invocation needs a new output directory. Finally restore the G3 snapshot.
Without a matching certificate these are preflights: pause_verified stays false in the record.
"""

import argparse
import contextlib
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from mc_diamond.episode import run_episode
from mc_diamond.rpc import RpcSession
from mc_diamond.schema import Candidate, CandidateSet, EpisodeConfig, SelectionResult
from mc_diamond.selectors import Selector, result

# scope, variant, stairs, max_ticks, expected reason. Administrator scenes, never a natural task result.
SCENES = [("stair", "ore", 4, 400, "stairs_completed"), ("stair_exposed", "ore", 2, 400, "ore_exposed"),
          ("stair_exposed", "lava", 2, 400, "observed_hazard"), ("stair_coal", "ore", 2, 400, "stairs_completed"),
          ("stair_floor", "lava", 2, 400, "observed_hazard"), ("stair_gap", "ore", 1, 400, "unsafe_floor"),
          ("stair_break", "ore", 2, 400, "tool_broken"), ("stair_limit", "ore", 4, 400, "macro_tick_limit"),
          ("stair_budget", "ore", 4, 30, "active_tick_limit"), ("stair_no_tool", "ore", 1, 400, "invalid_stair"),
          ("stair_gravel", "ore", 1, 400, "stairs_completed"), ("stair_hold", "ore", 1, 20, "observed_hazard")]


def prefer(direction: list[int]) -> Selector:
    """Fixed diagnostic selector: hold one heading while the generator offers it."""
    def select(_observation: Any, _goal: Any, saved: CandidateSet, _failures: Any) -> SelectionResult:
        return result(next((c for c in saved.candidates if c.action_kind == "stair_down" and c.params["direction"] == direction),
                           saved.candidates[0]), "mock_fixed")
    return select


def access_report(path: Path) -> dict[str, Any]:
    """Where the run went and what stopped it, recomputed from the public JSONL alone."""
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.startswith("{")]
    steps = [row["data"] for row in rows if row["type"] == "step"]
    first = next(row["data"] for row in rows if row["type"] == "reset")
    final = steps[-1]["observation"] if steps else first
    reasons: dict[str, int] = {}
    timeline = []
    for number, step in enumerate(steps, 1):
        reasons[step["reason"]] = reasons.get(step["reason"], 0) + 1
        timeline.append({"decision": number, "reason": step["reason"], "ticks": step["actual_ticks"],
                         "active_ticks": step["observation"]["active_ticks"], "y": step["observation"]["position"][1],
                         "tool": step["observation"]["tool"], "durability": step["observation"]["tool_durability"],
                         "exposed": [[e["item"], e["position"]] for e in step["events"] if e["kind"] == "exposed"]})
    ores: dict[str, int] = {}
    for cell in final["observed_map"]:
        if cell["block"].endswith("_ore"):
            ores[cell["block"]] = ores.get(cell["block"], 0) + 1
    def first_exposed(item: str) -> float | None:
        return next((row["y"] for row in timeline if any(name == item for name, _ in row["exposed"])), None)
    return {"start": first["position"], "start_inventory": first["inventory"], "final": final["position"],
            "lowest_y": min([first["position"][1], *(row["y"] for row in timeline)]),
            "active_ticks": final["active_ticks"], "wall_seconds": sum(s["wall_seconds"] for s in steps), "decisions": len(steps),
            "reasons": reasons, "stairs": sum(e["kind"] == "descended" for s in steps for e in s["events"]),
            "mined": sum(e["kind"] == "mined" for s in steps for e in s["events"]),
            "observed_cells": len(final["observed_map"]), "visited": len(final["visited"]), "observed_ores": ores,
            "first_iron_exposed_at_y": first_exposed("iron_ore"), "first_diamond_exposed_at_y": first_exposed("diamond_ore"),
            "final_inventory": final["inventory"], "final_tool": final["tool"], "final_durability": final["tool_durability"],
            "unstable_stops": sum(not s["stable_boundary"] for s in steps), "timeline": timeline}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("checks", nargs="*", choices=["clock", "information", "stairs", "g3", "g2", "g2-directions"])
    args = parser.parse_args()
    checks = args.checks or ["clock", "information", "stairs", "g3", "g2"]
    args.output.mkdir(parents=True, exist_ok=False)
    results: dict[str, Any] = {}
    sources = [*Path("src/mc_diamond").glob("*.py"), Path("src/mc_diamond/recipes.json"), *Path("bridge").glob("*.js"),
               Path(__file__), Path("configs/g2.yaml"), Path("configs/g3.yaml"), Path("configs/minecraft.yaml")]
    (args.output / "manifest.json").write_text(json.dumps({
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "checks": checks,
        "worktree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}, indent=2))
    config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/g3.yaml").read_text()))
    assert config.command is not None

    def cli(name: str, command: str, config_path: str) -> dict[str, Any]:
        argv = ["mc-diamond", command, "--config", config_path]
        (args.output / (name + "-command.json")).write_text(json.dumps(argv))
        with (args.output / (name + ".jsonl")).open("w") as out, (args.output / (name + ".stderr")).open("w") as err:
            process = subprocess.run(argv, stdout=out, stderr=err, timeout=5400)
        rows = [json.loads(line) for line in (args.output / (name + ".jsonl")).read_text().splitlines()]
        result: dict[str, Any] = {"exit_code": process.returncode, "summary": rows[-1] if rows else None}
        results[name] = result
        data = result["summary"]["data"] if result["summary"] else {}
        print(json.dumps({"check": name, "exit_code": process.returncode,
            **{key: data[key] for key in ["goal_completed", "active_ticks", "decisions", "pause_verified",
                "information_verified", "direct_acquired", "reason", "error"] if key in data}}), flush=True)
        return result

    try:
        if "clock" in checks:
            result = cli("verify-clock", "verify-clock", "configs/minecraft.yaml")
            assert result["exit_code"] == 0 and result["summary"]["data"]["pause_verified"]
        if "information" in checks:
            result = cli("audit-information", "audit-information", "configs/minecraft.yaml")
            assert result["exit_code"] == 0 and result["summary"]["data"]["information_verified"]
        if "stairs" in checks:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                for scope, variant, stairs, ticks, expected in SCENES:
                    prepared = session._call("information_fixture", {"variant": variant, "exposed": False, "scope": scope}, admin=True)
                    assert prepared.get("fixture_ready") is True
                    initial = session.policy().observe()

                    def stair(source_obs: str, version: int, count: int, limit: int) -> Candidate:
                        return Candidate.model_validate({"candidate_id": f"{scope}-{variant}-{count}", "action_kind": "stair_down",
                            "params": {"direction": [1, 0], "stairs": count, "stop_blocks": ["diamond_ore"], "map_version": version},
                            "max_ticks": limit, "stop_rule_id": "stair_ore_or_hazard", "source_obs_id": source_obs, "description": scope})
                    selected = stair(initial.obs_id, initial.map_version, stairs, ticks)
                    if scope == "stair_hold":
                        selected = selected.model_copy(update={"action_kind": "wait", "params": {}})
                    step = session.policy().step(selected)
                    row: dict[str, Any] = {"natural_task": False, "prepared": prepared, "reason": step.reason, "ticks": step.actual_ticks,
                        "start_y": initial.position[1], "end_y": step.observation.position[1], "stable_boundary": step.stable_boundary,
                        "invalid": step.invalid, "truncated": step.truncated, "pause_verified": step.pause_verified,
                        "health": step.observation.health, "tool": step.observation.tool,
                        "events": [e.kind for e in step.events], "exposed": [[e.item, e.position] for e in step.events if e.kind == "exposed"]}
                    (args.output / f"{scope}-{variant}.json").write_text(json.dumps({"initial": initial.model_dump(mode="json"),
                        "step": step.model_dump(mode="json")}))
                    assert step.reason == expected, (scope, step.reason)
                    assert step.observation.active_ticks == initial.active_ticks + step.actual_ticks
                    if scope == "stair":
                        assert step.observation.position[1] == initial.position[1] - 4 and step.stable_boundary
                    if scope == "stair_exposed" and variant == "ore":
                        assert [e.item for e in step.events if e.kind == "exposed"] == ["diamond_ore"]
                        follow = step.observation
                        again = session.policy().step(stair(follow.obs_id, follow.map_version, 1, 400))
                        row["no_repeat_stop"] = again.reason
                        assert again.reason == "stairs_completed" and not any(e.kind == "exposed" for e in again.events)
                    if scope == "stair_coal":
                        assert any(c.block == "coal_ore" for c in step.observation.observed_map)
                        assert not any(e.kind == "exposed" for e in step.events)
                    if scope == "stair_floor":
                        assert step.observation.position[1] > initial.position[1] - 2, "never stepped onto observed lava"
                    if scope == "stair_gap":
                        assert step.observation.position[1] == initial.position[1] and step.observation.health == 20
                    if scope == "stair_break":
                        assert step.observation.tool is None
                    if scope == "stair_limit":
                        assert step.actual_ticks == 400
                    if scope == "stair_budget":
                        assert step.truncated and step.actual_ticks == 30 and step.observation.remaining_ticks == 0
                    if scope == "stair_hold":
                        assert step.actual_ticks < 20 and not any(e.kind == "safe_hold" for e in step.events)
                    if scope == "stair_no_tool":
                        assert step.invalid and step.actual_ticks == 1
                    results[f"{scope}-{variant}"] = row
                    print(json.dumps({"check": f"{scope}-{variant}", **{k: row[k] for k in ["reason", "ticks", "start_y", "end_y",
                        "stable_boundary", "pause_verified"]}}), flush=True)
        if "g3" in checks:
            result = cli("g3", "smoke-macros", "configs/g3.yaml")
            summary = result["summary"]["data"]
            result["access"] = access_report(args.output / "g3.jsonl")
            (args.output / "g3-access.json").write_text(json.dumps(result["access"], indent=2))
            assert summary["provided_inventory"] == {"iron_pickaxe": 1} and summary["active_ticks"] <= 18000
            assert summary["goal_completed"], "Fixed G3 did not reach and hold the safe band"
        if "g2" in checks:
            # Access only: three direct iron stays a T07 #8 acceptance item, so its miss is reported, not failed.
            result = cli("g2", "smoke-macros", "configs/g2.yaml")
            summary = result["summary"]["data"]
            result["access"] = access_report(args.output / "g2.jsonl")
            result["direct_iron_verified"] = bool(summary["goal_completed"] and summary["direct_acquired"].get("iron_ore", 0) >= 3)
            (args.output / "g2-access.json").write_text(json.dumps(result["access"], indent=2))
            assert summary["provided_inventory"] == {"stone_pickaxe": 1} and summary["active_ticks"] <= 12000
        if "g2-directions" in checks:
            # Same snapshot, start and limits as g2; only the fixed selector's heading differs.
            g2 = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/g2.yaml").read_text()))
            assert g2.command is not None
            for name, direction in [("east", [1, 0]), ("west", [-1, 0]), ("north", [0, -1])]:
                path = args.output / f"g2-{name}.jsonl"
                with RpcSession(g2.command, g2.rpc_timeout_seconds) as session, path.open("w") as out, contextlib.redirect_stdout(out):
                    model = run_episode(g2, session.policy(), lambda: session.reset(f"g2-{name}", "t06"), f"g2-{name}", "t06",
                                        macros=True, select=prefer(direction))
                report = access_report(path)
                (args.output / f"g2-{name}-access.json").write_text(json.dumps(report, indent=2))
                results[f"g2-{name}"] = {"reason": model.reason, "pause_verified": model.pause_verified, "error": model.error is not None,
                    "direct_acquired": model.direct_acquired, "goal_completed": model.goal_completed, "access": report}
                print(json.dumps({"check": f"g2-{name}", "reason": model.reason, "active_ticks": model.active_ticks,
                    "lowest_y": report["lowest_y"], "reasons": report["reasons"], "observed_ores": report["observed_ores"],
                    "pause_verified": model.pause_verified, "iron": model.direct_acquired.get("iron_ore", 0)}), flush=True)
                assert model.provided_inventory == {"stone_pickaxe": 1} and model.active_ticks <= 12000 and model.error is None
    finally:
        try:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                restored = session.reset("restored", "restore-t06")
                assert restored == session.policy().observe()
                (args.output / "restore.json").write_text(restored.model_dump_json())
                assert restored.active_ticks == 0 and restored.inventory == {"iron_pickaxe": 1} and restored.health == 20
                assert restored.position == json.loads(Path("worlds/snapshots/G3/snapshot.json").read_text())["position"]
                assert restored.remaining_ticks == 18000
                results["reset"] = {"passed": True}
        except Exception as failure:
            results["reset"] = {"passed": False, "error_type": type(failure).__name__}
            raise
        finally:
            (args.output / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
