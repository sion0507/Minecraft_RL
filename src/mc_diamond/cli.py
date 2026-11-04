import argparse
import sys
from pathlib import Path
from uuid import uuid4

import yaml
from pydantic import ValidationError

from .episode import emit, run_episode
from .doctor import doctor
from .clock import verify_clock
from .information import audit_information
from .rpc import EpisodeError, RpcSession
from .schema import EpisodeConfig, EpisodeSummary, ErrorInfo


def main() -> int:
    parser = argparse.ArgumentParser(prog="mc-diamond")
    parser.add_argument("command", choices=["doctor", "smoke-episode", "smoke-movement", "smoke-macros", "verify-clock", "prepare-world", "audit-information"])
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.config.open(encoding="utf-8") as handle:
            config = EpisodeConfig.model_validate(yaml.safe_load(handle))
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
                emit("world_prepared", {**session._call("prepare_world", {}, admin=True)})
                return 0
            if args.command == "verify-clock":
                return 0 if verify_clock(session) else 1
            if args.command == "audit-information":
                return 0 if audit_information(session) else 1
            summary = run_episode(config, session.policy(), lambda: session.reset(episode_id, attempt_id),
                                  episode_id, attempt_id, movement=args.command == "smoke-movement",
                                  macros=args.command == "smoke-macros")
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
