"""T05 actual Minecraft diagnostics, from the repository root; no models or APIs.

Every invocation needs a new output directory. Finally restore the C4 snapshot.
Preflight production may be unverified; only clock certification establishes pause.
"""

import argparse
import contextlib
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from mc_diamond.episode import run_episode
from mc_diamond.rpc import RpcSession
from mc_diamond.schema import Candidate, EpisodeConfig, Goal
from verify_t04 import InvalidateOnce


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("checks", nargs="*", choices=["clock", "information", "furnace", "production", "boundaries", "g2"])
    args = parser.parse_args()
    checks = args.checks or ["clock", "information", "production", "boundaries", "g2"]
    args.output.mkdir(parents=True, exist_ok=False)
    results: dict[str, Any] = {}
    sources = [*Path("src/mc_diamond").glob("*.py"), Path("src/mc_diamond/recipes.json"),
               *Path("bridge").glob("*.js"), Path(__file__), Path("configs/production.yaml"), Path("configs/g2.yaml")]
    (args.output / "manifest.json").write_text(json.dumps({
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "checks": checks,
        "sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}, indent=2))
    config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/production.yaml").read_text()))
    assert config.command is not None

    def cli(name: str, command: str, config_path: str = "configs/production.yaml",
            fixture: str | None = None) -> dict[str, Any]:
        argv = ["mc-diamond", command, "--config", config_path]
        if fixture:
            argv += ["--diagnostic-fixture", fixture]
        (args.output / (name + "-command.json")).write_text(json.dumps(argv))
        with (args.output / (name + ".jsonl")).open("w") as out, (args.output / (name + ".stderr")).open("w") as err:
            process = subprocess.run(argv, stdout=out, stderr=err, timeout=5400)
        rows = [json.loads(line) for line in (args.output / (name + ".jsonl")).read_text().splitlines()]
        result: dict[str, Any] = {"exit_code": process.returncode, "summary": rows[-1] if rows else None}
        results[name] = result
        data = result["summary"]["data"] if result["summary"] else {}
        print(json.dumps({"check": name, "exit_code": process.returncode,
            **{key: data[key] for key in ["goal_completed", "active_ticks", "decisions", "pause_verified",
                "information_verified", "direct_acquired", "direct_smelted", "reason", "error"] if key in data}}), flush=True)
        return result

    try:
        if "clock" in checks:
            result = cli("verify-clock", "verify-clock")
            assert result["exit_code"] == 0 and result["summary"]["data"]["pause_verified"]
        if "information" in checks:
            result = cli("audit-information", "audit-information")
            assert result["exit_code"] == 0 and result["summary"]["data"]["information_verified"]
        if "furnace" in checks:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                prepared = session._call("information_fixture", {"variant": "ore", "exposed": False,
                    "scope": "production_furnace"}, admin=True)
                assert prepared.get("fixture_ready") is True
                initial = session.policy().observe()
                smelt_config = config.model_copy(update={"max_decisions": 8,
                    "goal": Goal(goal_id="direct-smelt", kind="smelt", target="iron_ingot", quantity=1)})
                with (args.output / "furnace.jsonl").open("w") as out, contextlib.redirect_stdout(out):
                    summary_model = run_episode(smelt_config, session.policy(), lambda: initial,
                        initial.episode_id, initial.attempt_id, macros=True)
                results["furnace"] = {"natural_task": False, "prepared": prepared,
                    "summary": summary_model.model_dump(mode="json")}
                print(json.dumps({"check": "furnace", "goal_completed": summary_model.goal_completed,
                    "ticks": summary_model.active_ticks, "direct_smelted": summary_model.direct_smelted}), flush=True)
                assert summary_model.error is None and summary_model.goal_completed
                assert summary_model.direct_smelted == {"iron_ingot": 1}
        if "production" in checks:
            result = cli("production", "smoke-macros", fixture="production")
            summary = result["summary"]["data"]
            assert summary["goal_completed"] and summary["error"] is None and not summary["invalid"]
            assert summary["provided_inventory"] == {} and summary["direct_crafted"]["iron_pickaxe"] == 1
            assert summary["direct_acquired"]["iron_ore"] >= 3 and summary["direct_smelted"]["iron_ingot"] == 3
            assert result["exit_code"] == (0 if summary["pause_verified"] else 1)
        if "boundaries" in checks:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                for scope in ["production_no_tool", "production_no_fuel", "production_hazard"]:
                    prepared = session._call("information_fixture", {"variant": "ore", "exposed": False, "scope": scope}, admin=True)
                    initial = session.policy().observe()
                    x, y, z = (int(v // 1) for v in initial.position)
                    kind = "mine_visible_cluster" if scope == "production_no_tool" else "furnace_load"
                    params = ({"block": "iron_ore", "blocks": [[x + 1, y, z]], "map_version": initial.map_version}
                              if scope == "production_no_tool" else {"position": [x + 1, y, z], "item": "iron_ore",
                                "quantity": 3, "fuel": "coal", "fuel_quantity": 1, "map_version": initial.map_version})
                    selected = Candidate.model_validate({"candidate_id": scope, "action_kind": kind, "params": params,
                        "max_ticks": 400, "stop_rule_id": "production_or_hazard", "source_obs_id": initial.obs_id, "description": scope})
                    step = session.policy().step(selected)
                    (args.output / (scope + ".json")).write_text(json.dumps({"prepared": prepared,
                        "initial": initial.model_dump(mode="json"), "candidate": selected.model_dump(mode="json"),
                        "step": step.model_dump(mode="json")}, indent=2))
                    assert step.actual_ticks == 1 and not any(e.kind in {"mined", "furnace_loaded", "smelted"} for e in step.events)
                    assert (step.reason == "observed_hazard" and not step.stable_boundary if scope == "production_hazard" else step.invalid)
                    results[scope] = {"passed": True, "reason": step.reason, "ticks": step.actual_ticks}
                cancellation_setup = session._call("information_fixture", {"variant": "ore", "exposed": False,
                    "scope": "production_craft"}, admin=True)
                assert cancellation_setup.get("fixture_ready") is True
                initial = session.policy().observe()
                # Only one deliberately stale selection; no full realtime claim.
                short_config = config.model_copy(update={"max_decisions": 2})
                with (args.output / "cancellation.jsonl").open("w") as out, contextlib.redirect_stdout(out):
                    summary_model = run_episode(short_config, InvalidateOnce(session), lambda: initial,
                        initial.episode_id, initial.attempt_id, macros=True)
                assert summary_model.error is None and summary_model.cancelled_selections == 1
                assert summary_model.decisions == 1 and summary_model.selection_requests == 2
                assert summary_model.goal_completed and summary_model.direct_crafted.get("iron_pickaxe") == 1
                rows = [json.loads(line) for line in (args.output / "cancellation.jsonl").read_text().splitlines()]
                cancelled = next(row["data"] for row in rows if row["type"] == "cancellation")
                assert cancelled["actual_ticks"] == 40 and cancelled["trace_mask"] == 0 and not cancelled["actor_valid"]
                results["cancellation"] = {"passed": True, "natural_task": False,
                    "fixture": "production_craft", "prepared": cancellation_setup,
                    "summary": summary_model.model_dump(mode="json")}
        if "g2" in checks:
            result = cli("g2", "smoke-macros", "configs/g2.yaml")
            summary = result["summary"]["data"]
            assert summary["provided_inventory"] == {"stone_pickaxe": 1} and summary["active_ticks"] <= 12000
            results["g2"]["direct_iron_verified"] = bool(summary["goal_completed"] and summary["direct_acquired"].get("iron_ore", 0) >= 3)
            # #36: a feasibility diagnostic; the fixed selector's iron is recorded, not required.
    finally:
        try:
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                restored = session.reset("restored", "restore-t05")
                assert restored == session.policy().observe()
                (args.output / "restore.json").write_text(restored.model_dump_json())
                assert restored.active_ticks == 0 and restored.inventory == {} and restored.health == 20
                results["reset"] = {"passed": True}
        except Exception as failure:
            results["reset"] = {"passed": False, "error_type": type(failure).__name__}
            raise
        finally:
            (args.output / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
