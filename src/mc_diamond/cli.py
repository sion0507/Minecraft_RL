import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import yaml
from pydantic import ValidationError

from . import evaluation
from .episode import emit, run_episode
from .doctor import doctor
from .clock import verify_clock
from .information import audit_information
from .rpc import EpisodeError, RpcSession
from .schema import CandidateSet, EpisodeConfig, EpisodeSummary, ErrorInfo, Goal, Observation, SelectionResult
from .rule_selector import rule_select
from .selectors import first_candidate, result


def human_select(observation: Observation, _goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
    """#36 feasibility diagnostic: the operator only picks among the generated candidates; code executes and judges."""
    ores = sorted((sum((a - b) ** 2 for a, b in zip(s.position, observation.position)), s.block, [int(v) for v in s.position])
                  for s in observation.observed_map if s.block.endswith("_ore"))
    print(f"\n남은 {observation.remaining_ticks}틱 | 위치 {[round(v, 1) for v in observation.position]} | 체력 {observation.health:g}"
          f" | 도구 {observation.tool} | 인벤토리 {observation.inventory}", file=sys.stderr)
    if ores:
        print("관측한 광석: " + ", ".join(f"{block} {position}" for _, block, position in ores[:10]), file=sys.stderr)
    for index, candidate in enumerate(saved.candidates, 1):
        print(f"  {index}. {candidate.action_kind}: {candidate.description} {json.dumps(candidate.params)[:160]}", file=sys.stderr)
    while True:
        print(f"번호 (1-{len(saved.candidates)}): ", end="", file=sys.stderr, flush=True)
        answer = sys.stdin.readline()
        if not answer:
            raise EOFError("human selector input closed")
        if answer.strip().isdigit() and 1 <= int(answer) <= len(saved.candidates):
            return result(saved.candidates[int(answer) - 1], "human")


def main() -> int:
    parser = argparse.ArgumentParser(prog="mc-diamond")
    parser.add_argument("command", choices=["doctor", "smoke-episode", "smoke-movement", "smoke-macros", "verify-clock", "prepare-world",
                                            "audit-information", "evaluate"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--diagnostic-fixture", choices=["wood", "wood_tool", "wood_break", "wood_hazard", "wood_drop", "empty",
        "production", "production_no_tool", "production_no_fuel", "production_hazard", "iron", "diamond", "diamond_given"])
    place = parser.add_mutually_exclusive_group()
    place.add_argument("--start", type=int, nargs=3, metavar=("X", "Y", "Z"), help="prepare-world: C4-G3 surface start block")
    place.add_argument("--g4", type=int, nargs=3, metavar=("X", "Y", "Z"), help="prepare-world: user-confirmed G4 start block")
    parser.add_argument("--select", choices=["fixed", "human", "rule"], default="fixed",
                        help="human = operator picks candidates (#36 feasibility diagnostic, no wall limit); rule = selector S")
    parser.add_argument("--groups", default="A,B,J,F,S", help="evaluate: comma-separated groups of the planned slots to run")
    parser.add_argument("--task", default="C4,G4", help="evaluate: C4, G4 or both")
    args = parser.parse_args()
    if args.command == "prepare-world" and args.start is None and args.g4 is None:
        parser.error("prepare-world requires --start X Y Z or --g4 X Y Z")
    try:
        if args.command == "evaluate":
            return evaluation.main(args.config, args.groups, args.task, emit)
        with args.config.open(encoding="utf-8") as handle:
            config = EpisodeConfig.model_validate(yaml.safe_load(handle))
        if args.select == "human":
            if args.command != "smoke-macros" or config.backend != "rpc" or args.diagnostic_fixture:
                raise ValueError("The human selector runs only natural actual smoke-macros")
            config = config.model_copy(update={"wall_limit_seconds": None})  # thinking happens while paused
        if args.diagnostic_fixture and (args.command != "smoke-macros" or config.backend != "rpc"):
            raise ValueError("Diagnostic fixtures require actual smoke-macros")
        if args.command == "doctor":
            report = doctor()
            emit("doctor", report)
            for name, probe in report.probes.items():
                if probe.status != "available":
                    print(f"{name}: {probe.status}: {probe.detail}", file=sys.stderr)
            return 0 if report.ready else 1
        if args.command in {"verify-clock", "prepare-world", "audit-information"} and config.backend != "rpc":
            emit("error", ErrorInfo(code="invalid_config", message="Actual Minecraft backend required; use configs/minecraft.yaml"))
            print("Actual Minecraft backend required; use configs/minecraft.yaml", file=sys.stderr)
            return 2
        command = config.command
        if config.backend == "mock":
            assert config.fixture is not None
            fixture = (args.config.parent / config.fixture).resolve()
            command = [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str(fixture)]
        assert command is not None
        episode_id, attempt_id = str(uuid4()), str(uuid4())
        with RpcSession(command, config.rpc_timeout_seconds) as session:
            if args.command == "prepare-world":
                emit("world_prepared", {**session._call("prepare_world", {"start": list(args.start)} if args.start else {"g4": list(args.g4)}, admin=True)})
                return 0
            if args.command == "verify-clock":
                return 0 if verify_clock(session) else 1
            if args.command == "audit-information":
                return 0 if audit_information(session) else 1
            def reset() -> Observation:
                if not args.diagnostic_fixture:
                    return session.reset(episode_id, attempt_id)
                prepared = session._call("information_fixture", {"variant": "ore", "exposed": False,
                    "scope": args.diagnostic_fixture, "episode_id": episode_id, "attempt_id": attempt_id}, admin=True)
                if prepared.get("fixture_ready") is not True:
                    raise ValueError("Diagnostic fixture was not verified")
                emit("diagnostic_fixture", {"scope": args.diagnostic_fixture, "natural_task": False, **prepared})
                return session.policy().observe()
            summary = run_episode(config, session.policy(), reset,
                                  episode_id, attempt_id, movement=args.command == "smoke-movement",
                                  macros=args.command == "smoke-macros",
                                  select={"human": human_select, "rule": rule_select}.get(args.select, first_candidate),
                                  verification=(lambda: session._call("verification_log", {}, admin=True))
                                  if args.command == "smoke-macros" else None)
        if summary.error or summary.invalid:
            print(f"Episode stopped: {summary.reason}", file=sys.stderr)
            return 1
        if summary.clock_mode == "unverified":
            print("Pause unverified; run verify-clock with the actual backend", file=sys.stderr)
            return 1
        if args.command == "smoke-movement" and not summary.movement_completed:
            return 1
        if args.command == "smoke-macros" and not summary.goal_completed:
            return 1
        return 0
    except (OSError, ValueError, yaml.YAMLError, ValidationError):
        emit("error", ErrorInfo(code="invalid_config", message="Cannot load valid configuration"))
        print("Cannot load valid configuration", file=sys.stderr)
        return 2
    except EpisodeError as failure:
        emit("error", failure.error)
        if args.command == "verify-clock":
            emit("clock_summary", {"planned_trials": 63, "pause_verified": False,
                                   "clock_mode": "unverified", "error": failure.error.model_dump(mode="json")})
            return 1
        if args.command == "prepare-world":
            return 1
        if args.command == "audit-information":
            emit("information_summary", {"information_verified": False,
                                        "error": failure.error.model_dump(mode="json")})
            return 1
        emit("summary", EpisodeSummary(
            episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
            clock_mode="mock" if config.backend == "mock" else "unverified", goal_completed=False, terminated=False, truncated=False,
            invalid=False, reason=failure.error.code, error=failure.error,
            active_ticks=0, wall_seconds=0.0, decisions=0, reward_total=0.0,
        ))
        print(failure.error.message, file=sys.stderr)
        return 1
