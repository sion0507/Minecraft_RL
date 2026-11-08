"""T07 actual Minecraft checks from the repository root; no models or APIs.

Order: clock, information, tunnels (administrator scenes), diamond (constructed fixtures), g4, g2.
Natural g4/g2 are feasibility diagnostics (#36): success is recorded; only an executor stall fails.
Every invocation needs a new output directory. Finally the G4 snapshot is restored and checked.
Without a matching clock certificate these are preflights: pause_verified stays false in the record.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml
from verify_t06 import access_report

from mc_diamond.rpc import RpcSession
from mc_diamond.schema import Candidate, EpisodeConfig

# scope, cells, height, max_ticks, expected reason. Administrator scenes, never a natural task result.
SCENES = [("tunnel_long", 8, 2, 400, "tunnel_completed"), ("tunnel_long", 2, 3, 400, "tunnel_completed"),
          ("tunnel_break", 2, 2, 400, "tool_broken"), ("tunnel_budget", 8, 2, 30, "active_tick_limit"),
          ("tunnel_no_tool", 1, 2, 400, "invalid_tunnel")]


def start(task: str) -> Any:
    return json.loads(Path(f"worlds/snapshots/{task}/snapshot.json").read_text())["position"]


def linked(record: dict[str, Any], events: set[str], tool: str, drop: str) -> bool:
    """Break, server truth, held tool, own drop and acquired event, regardless of the natural flag."""
    return bool(record["server_block_before"] and record["server_air_after"] and record["server_tool"] == tool
                and record["drop_item"] == drop and isinstance(record["drop_entity_id"], int)
                and record["acquired_event_id"] in events)


def tunnel(initial: Any, scope: str, cells: int, height: int, ticks: int) -> Candidate:
    return Candidate.model_validate({"candidate_id": f"{scope}-{cells}-{height}", "action_kind": "tunnel",
        "params": {"direction": [1, 0], "cells": cells, "height": height, "stop_blocks": ["diamond_ore"], "map_version": initial.map_version},
        "max_ticks": ticks, "stop_rule_id": "tunnel_ore_or_hazard", "source_obs_id": initial.obs_id, "description": scope})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("checks", nargs="*", choices=["clock", "information", "tunnels", "diamond", "g4", "g2"])
    args = parser.parse_args()
    checks = args.checks or ["clock", "information", "tunnels", "diamond", "g4", "g2"]
    args.output.mkdir(parents=True, exist_ok=False)
    results: dict[str, Any] = {}
    sources = [*Path("src/mc_diamond").glob("*.py"), Path("src/mc_diamond/recipes.json"), *Path("bridge").glob("*.js"),
               Path(__file__), *Path("configs").glob("*.yaml")]
    (args.output / "manifest.json").write_text(json.dumps({
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "checks": checks,
        "worktree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "snapshots": {task: json.loads(Path(f"worlds/snapshots/{task}/snapshot.json").read_text()) for task in ["G2", "G4"]}}, indent=2))
    failures: list[str] = []
    config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/g4.yaml").read_text()))
    assert config.command is not None

    def cli(name: str, command: str, config_path: str | Path, *extra: str) -> dict[str, Any]:
        argv = ["mc-diamond", command, "--config", str(config_path), *extra]
        (args.output / (name + "-command.json")).write_text(json.dumps(argv))
        with (args.output / (name + ".jsonl")).open("w") as out, (args.output / (name + ".stderr")).open("w") as err:
            process = subprocess.run(argv, stdout=out, stderr=err, timeout=5400)
        rows = [json.loads(line) for line in (args.output / (name + ".jsonl")).read_text().splitlines()]
        result: dict[str, Any] = {"exit_code": process.returncode, "summary": rows[-1] if rows else None,
                                  "admin": next((row["data"] for row in rows if row["type"] == "admin_verification"), None)}
        results[name] = result
        data = result["summary"]["data"] if result["summary"] else {}
        print(json.dumps({"check": name, "exit_code": process.returncode,
            **{key: data[key] for key in ["goal_completed", "diamond_success", "admin_verified", "active_ticks", "decisions",
                "pause_verified", "information_verified", "direct_acquired", "reason", "error"] if key in data}}), flush=True)
        return result

    def events(name: str) -> set[str]:
        rows = [json.loads(line) for line in (args.output / (name + ".jsonl")).read_text().splitlines()]
        return {e["event_id"] for row in rows if row["type"] == "step" for e in row["data"]["events"] if e["kind"] == "acquired"}

    try:
        if "clock" in checks:
            result = cli("verify-clock", "verify-clock", "configs/minecraft.yaml")
            assert result["exit_code"] == 0 and result["summary"]["data"]["pause_verified"]
        if "information" in checks:
            result = cli("audit-information", "audit-information", "configs/minecraft.yaml")
            assert result["exit_code"] == 0 and result["summary"]["data"]["information_verified"]
        if "tunnels" in checks:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                for scope, cells, height, ticks, expected in SCENES:
                    prepared = session._call("information_fixture", {"variant": "ore", "exposed": False, "scope": scope}, admin=True)
                    assert prepared.get("fixture_ready") is True
                    initial = session.policy().observe()
                    step = session.policy().step(tunnel(initial, scope, cells, height, ticks))
                    name = f"{scope}-{cells}x{height}"
                    row: dict[str, Any] = {"natural_task": False, "observed_cells": [len(initial.observed_map),
                        len(step.observation.observed_map)], "prepared": prepared, "reason": step.reason, "ticks": step.actual_ticks,
                        "start": initial.position, "end": step.observation.position, "stable_boundary": step.stable_boundary,
                        "invalid": step.invalid, "truncated": step.truncated, "pause_verified": step.pause_verified,
                        "mined": sum(e.kind == "mined" for e in step.events), "tunneled": sum(e.kind == "tunneled" for e in step.events),
                        "tool": step.observation.tool, "remaining_ticks": step.observation.remaining_ticks}
                    (args.output / f"{name}.json").write_text(json.dumps({"initial": initial.model_dump(mode="json"),
                        "step": step.model_dump(mode="json")}))
                    results[name] = row
                    print(json.dumps({"check": name, **{k: row[k] for k in ["reason", "ticks", "mined", "tunneled", "end",
                        "stable_boundary", "pause_verified"]}}), flush=True)
                    assert step.reason == expected, (name, step.reason)
                    assert step.observation.active_ticks == initial.active_ticks + step.actual_ticks
                    if scope == "tunnel_long":
                        assert step.observation.position[1] == initial.position[1] and step.stable_boundary
                        assert row["tunneled"] == cells and row["mined"] == cells * height
                        assert row["observed_cells"][1] > row["observed_cells"][0], "cutting extends the observation"
                        assert [int(v // 1) for v in step.observation.position] == [int(initial.position[0] // 1) + cells,
                            int(initial.position[1]), int(initial.position[2] // 1)]
                    if scope == "tunnel_break":
                        assert step.observation.tool is None
                    if scope == "tunnel_budget":
                        assert step.truncated and step.actual_ticks == 30 and step.observation.remaining_ticks == 0
                        assert initial.remaining_ticks == 30 and initial.active_ticks == 18000 - 30, "G4 18,000-tick budget"
                    if scope == "tunnel_no_tool":
                        assert step.invalid and step.actual_ticks == 1
                # G2 attempt 1: sand fell into the entered feet cell. The next tunnel must cut the own cell out first.
                prepared = session._call("information_fixture", {"variant": "ore", "exposed": False, "scope": "tunnel_sand"}, admin=True)
                assert prepared.get("fixture_ready") is True
                runs = []
                for _ in range(2):
                    before = session.policy().observe()
                    runs.append((before, session.policy().step(tunnel(before, "tunnel_sand", 2, 2, 400))))
                (args.output / "tunnel_sand.json").write_text(json.dumps([{"initial": a.model_dump(mode="json"),
                    "step": b.model_dump(mode="json")} for a, b in runs]))
                buried, second = runs[1]
                feet = [int(v // 1) for v in buried.position]
                seen = {tuple(int(v) for v in c.position): c.block for c in buried.observed_map}
                mined = [e for e in second.events if e.kind == "mined"]
                row = {"natural_task": False, "first_reason": runs[0][1].reason, "first_ticks": runs[0][1].actual_ticks,
                       "buried_cell": seen.get(tuple(feet)), "reason": second.reason, "ticks": second.actual_ticks,
                       "first_mined": [mined[0].item, mined[0].position] if mined else None,
                       "tunneled": sum(e.kind == "tunneled" for e in second.events), "stable_boundary": second.stable_boundary,
                       "pause_verified": all(s.pause_verified for _, s in runs)}
                results["tunnel_sand"] = row
                print(json.dumps({"check": "tunnel_sand", **row}), flush=True)
                assert row["buried_cell"] == "sand", "the scene must bury the feet cell before the second tunnel"
                assert second.reason == "tunnel_completed" and row["tunneled"] == 2 and second.stable_boundary
                assert row["first_mined"] == ["sand", [float(v) for v in feet]]
        if "diamond" in checks:
            # Constructed fixtures (natural_task=false): the break→drop→pickup link, and a given diamond that never counts.
            # `iron` checks the same link for the stone pickaxe/iron path before the one natural G2 attempt.
            for scope, base, decisions in [("diamond", "g4", 8), ("diamond_given", "g4", 2), ("iron", "g2", 8)]:
                path = args.output / f"{scope}.yaml"
                path.write_text(yaml.safe_dump({**yaml.safe_load(Path(f"configs/{base}.yaml").read_text()), "max_decisions": decisions,
                                                **({"goal": {"goal_id": "iron-link", "kind": "collect", "target": "iron_ore",
                                                             "quantity": 1}} if scope == "iron" else {})}))
                result = cli(scope, "smoke-macros", path, "--diagnostic-fixture", scope)
                summary = result["summary"]["data"]
                assert summary["error"] is None and not summary["diamond_success"] and summary["admin_verified"] == {}
                assert result["admin"]["natural"] is False
                if scope in {"diamond", "iron"}:
                    item, tool = ("diamond", "iron_pickaxe") if scope == "diamond" else ("iron_ore", "stone_pickaxe")
                    assert result["exit_code"] == (0 if summary["pause_verified"] else 1) and summary["goal_completed"]
                    assert summary["direct_acquired"].get(item) == 1
                    assert sum(linked(r, events(scope), tool, item) for r in result["admin"]["records"]) == 1
                else:
                    assert result["exit_code"] == 1 and not summary["goal_completed"] and "diamond" not in summary["direct_acquired"]
                    assert result["admin"]["records"] == []
        for name in [check for check in ["g4", "g2"] if check in checks]:
            result = cli(name, "smoke-macros", "configs/g4.yaml" if name == "g4" else "configs/g2_natural.yaml")
            summary = result["summary"]["data"]
            report = access_report(args.output / f"{name}.jsonl")
            rows = [json.loads(line) for line in (args.output / f"{name}.jsonl").read_text().splitlines()]
            steps = [row["data"] for row in rows if row["type"] == "step"]
            candidates = [row["data"]["candidates"] for row in rows if row["type"] == "candidates"]
            kinds = {c["candidate_id"]: c["action_kind"] for cs in candidates for c in cs}
            chosen: dict[str, int] = {}
            for row in rows:
                if row["type"] == "selection":
                    kind = kinds.get(row["data"]["candidate_id"], "forced_wait")
                    chosen[kind] = chosen.get(kind, 0) + 1
            report.update(tunnels=sum(e["kind"] == "tunneled" for s in steps for e in s["events"]),
                          exposed=[[e["item"], e["position"]] for s in steps for e in s["events"] if e["kind"] == "exposed"],
                          candidate_counts={str(n): sum(len(c) == n for c in candidates) for n in range(9)}, selected_kinds=chosen)
            result["access"] = report
            (args.output / f"{name}-access.json").write_text(json.dumps(report, indent=2))
            provided, limit, item, needed = ({"iron_pickaxe": 1}, 18000, "diamond", 1) if name == "g4" else ({"stone_pickaxe": 1}, 12000, "iron_ore", 3)
            result["direct_verified"] = bool(summary["goal_completed"] and summary["pause_verified"]
                                             and summary["admin_verified"].get(item, 0) >= needed)
            print(json.dumps({"check": name + "-access", "direct_verified": result["direct_verified"], **{k: report[k] for k in
                ["lowest_y", "tunnels", "stairs", "mined", "observed_ores", "exposed", "reasons", "final_durability"]}}), flush=True)
            assert summary["provided_inventory"] == provided and summary["active_ticks"] <= limit and summary["error"] is None
            assert summary["reason"] in {"goal_completed", "active_tick_limit", "wall_time_limit", "repeated_stall"}, summary["reason"]
            assert report["start"] == start("G4" if name == "g4" else "G2"), "fixed snapshot start"
            if summary["reason"] == "repeated_stall":
                failures.append(f"natural {name} ended in repeated_stall: executor defect")
        assert not failures, failures  # Recorded first: an acceptance miss still keeps every artefact and the reset.
    finally:
        try:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                restored = session.reset("restored", "restore-t07")
                assert restored == session.policy().observe()
                (args.output / "restore.json").write_text(restored.model_dump_json())
                assert restored.active_ticks == 0 and restored.inventory == {"iron_pickaxe": 1} and restored.health == 20
                assert restored.position == start("G4") and restored.remaining_ticks == 18000
                results["reset"] = {"passed": True}
        except Exception as failure:
            results["reset"] = {"passed": False, "error_type": type(failure).__name__}
            raise
        finally:
            (args.output / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
