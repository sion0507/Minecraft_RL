import argparse
import sys
from pathlib import Path
from uuid import uuid4

import yaml
from pydantic import ValidationError

from .episode import emit, run_episode
from .doctor import doctor
from .rpc import EpisodeError, RpcSession
from .schema import EpisodeConfig, EpisodeSummary, ErrorInfo


def main() -> int:
    parser = argparse.ArgumentParser(prog="mc-diamond")
    parser.add_argument("command", choices=["doctor", "smoke-episode"])
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
        command = config.command
        if config.backend == "mock":
            assert config.fixture is not None
            fixture = (args.config.parent / config.fixture).resolve()
            command = [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str(fixture)]
        assert command is not None
        episode_id, attempt_id = str(uuid4()), str(uuid4())
        with RpcSession(command, config.rpc_timeout_seconds) as session:
            summary = run_episode(config, session.policy(), lambda: session.reset(episode_id, attempt_id),
                                  episode_id, attempt_id)
        if summary.error or summary.invalid:
            print(f"Episode stopped: {summary.reason}", file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, yaml.YAMLError, ValidationError):
        emit("error", ErrorInfo(code="invalid_config", message="Cannot load valid configuration"))
        print("Cannot load valid configuration", file=sys.stderr)
        return 2
    except EpisodeError as failure:
        emit("error", failure.error)
        emit("summary", EpisodeSummary(
            episode_id=episode_id, attempt_id=attempt_id, backend=config.backend,
            clock_mode="mock", goal_completed=False, terminated=False, truncated=False,
            invalid=False, reason=failure.error.code, error=failure.error,
            active_ticks=0, wall_seconds=0.0, decisions=0, reward_total=0.0,
        ))
        print(failure.error.message, file=sys.stderr)
        return 1
