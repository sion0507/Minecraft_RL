"""Reproduce T04 diagnostics; starts the installed local Minecraft server, no models.

Run from the repository root: uv run python tools/verify_t04.py --output artifacts/t04-new
Optional checks (in order): clock information macros. Every attempt is retained.
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
from mc_diamond.schema import Candidate, EpisodeConfig, Observation, StepResult


class InvalidateOnce:
    """Advance the real server during one selection; this is not realtime certification."""

    def __init__(self, session: RpcSession) -> None:
        self.policy = session.policy()
        self.pending = True

    def observe(self) -> Observation:
        return self.policy.observe()

    def step(self, candidate: Candidate) -> StepResult:
        if not self.pending:
            return self.policy.step(candidate)
        self.pending = False
        wait = self.policy.step(candidate.model_copy(update={"action_kind": "wait", "params": {}, "max_ticks": 20}))
        cancelled = self.policy.step(candidate)
        assert cancelled.cancelled and cancelled.reason == "candidate_invalidated"
        cancelled.actual_ticks += wait.actual_ticks
        cancelled.wall_seconds += wait.wall_seconds
        cancelled.events = wait.events + cancelled.events
        return cancelled


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("checks", nargs="*", choices=["clock", "information", "macros"])
    args = parser.parse_args()
    checks = args.checks or ["clock", "information", "macros"]
    args.output.mkdir(parents=True, exist_ok=False)
    results: dict[str, Any] = {}
    sources = [Path(name) for name in ["bridge/minecraft.js", "bridge/server.js", "bridge/terrain.js",
               "src/mc_diamond/episode.py", "src/mc_diamond/information.py", "src/mc_diamond/cli.py", __file__]]
    (args.output / "manifest.json").write_text(json.dumps({"checks": checks,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "sources": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}}, indent=2))

    def cli(name: str, command: str, fixture: str | None = None) -> tuple[int, list[dict[str, Any]]]:
        argv = ["mc-diamond", command, "--config", "configs/macros.yaml"]
        if fixture:
            argv += ["--diagnostic-fixture", fixture]
        (args.output / (name + "-command.json")).write_text(json.dumps(argv))
        with (args.output / (name + ".jsonl")).open("w") as stdout, (args.output / (name + ".stderr")).open("w") as stderr:
            process = subprocess.run(argv, stdout=stdout, stderr=stderr, timeout=1800)
        rows = [json.loads(line) for line in (args.output / (name + ".jsonl")).read_text().splitlines()]
        results[name] = {"exit_code": process.returncode, "summary": rows[-1]}
        print(json.dumps({"check": name, "exit_code": process.returncode}), flush=True)
        return process.returncode, rows

    try:
        if "clock" in checks:
            code, rows = cli("verify-clock", "verify-clock")
            assert code == 0 and rows[-1]["data"]["pause_verified"]
        if "information" in checks:
            code, rows = cli("audit-information", "audit-information")
            assert code == 0 and rows[-1]["data"]["information_verified"]
        if "macros" in checks:
            for scope in ["wood", "wood_tool", "wood_break", "wood_hazard", "wood_drop", "empty"]:
                code, rows = cli(scope, "smoke-macros", scope)
                summary = rows[-1]["data"]
                assert rows[-1]["type"] == "summary" and summary["error"] is None and not summary["invalid"]
                assert any(row["type"] == "diagnostic_fixture" and not row["data"]["natural_task"] for row in rows)
                if "clock" in checks:
                    assert summary["pause_verified"] and summary["clock_mode"] == "paused"
                steps = [row["data"] for row in rows if row["type"] == "step"]
                rewards = [row["data"] for row in rows if row["type"] == "reward"]
                assert all(not row["actor_valid"] for row in rewards)
                if scope == "empty":
                    assert not summary["goal_completed"] and code == 1
                    assert all(row["data"]["candidates"] == [] for row in rows if row["type"] == "candidates")
                    assert all(step["actual_ticks"] == 20 and any(e["kind"] == "failed" for e in step["events"]) for step in steps)
                elif scope == "wood_hazard":
                    assert any(step["reason"] == "observed_hazard" and
                               any(e["kind"] == "mined" for e in step["events"]) for step in steps)
                else:
                    assert summary["goal_completed"] and summary["reward_total"] == 1
                    assert code == (0 if summary["pause_verified"] else 1)
                    if scope == "wood_break":
                        assert any(step["reason"] == "tool_broken" and
                                   any(e["kind"] == "mined" for e in step["events"]) for step in steps)
                    if scope == "wood_drop":
                        assert all(row["data"]["candidates"][0]["action_kind"] == "wait"
                                   for row in rows if row["type"] == "candidates")
            config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/macros.yaml").read_text()))
            assert config.command is not None
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                session._call("information_fixture", {"variant": "ore", "exposed": False, "scope": "wood"}, admin=True)
                initial = session.policy().observe()
                with (args.output / "cancellation.jsonl").open("w") as stream, contextlib.redirect_stdout(stream):
                    summary_model = run_episode(config, InvalidateOnce(session), lambda: initial,
                                                initial.episode_id, initial.attempt_id, macros=True)
                assert summary_model.error is None and summary_model.goal_completed and summary_model.cancelled_selections == 1
                rows = [json.loads(line) for line in (args.output / "cancellation.jsonl").read_text().splitlines()]
                cancellation = next(row["data"] for row in rows if row["type"] == "cancellation")
                assert cancellation["actual_ticks"] == 40 and cancellation["trace_mask"] == 0 and not cancellation["actor_valid"]
                assert cancellation["selection"] == next(row["data"] for row in rows if row["type"] == "selection")
                results["cancellation"] = {"passed": True, "summary": summary_model.model_dump(mode="json"),
                                           "scope": "controlled real state advance; not full realtime validation"}
    finally:
        try:
            config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/macros.yaml").read_text()))
            assert config.command is not None
            with RpcSession(config.command, config.rpc_timeout_seconds) as session:
                restored = session.reset("restored", "restore-1")
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
