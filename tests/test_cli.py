import json
import subprocess
import sys
import os
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml


def run_cli(config: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["mc-diamond", "smoke-episode", "--config", str(config)],
                          text=True, capture_output=True, timeout=15)


def fixture_config(tmp_path: Path, fixture: dict[str, Any]) -> Path:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config["fixture"] = str(fixture_path)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def mock_fixture() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text(encoding="utf-8"))
    return result


def records(result: subprocess.CompletedProcess[str]) -> list[dict[str, Any]]:
    return [json.loads(line) for line in result.stdout.splitlines()]


def test_mock_episode_runs_through_public_cli() -> None:
    result = subprocess.run(
        ["mc-diamond", "smoke-episode", "--config", "configs/pilot.yaml"],
        text=True, capture_output=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    records = [json.loads(line) for line in result.stdout.splitlines()]
    assert [record["type"] for record in records] == [
        "reset", "observation", "goal", "candidates", "selection", "step", "reward", "summary"
    ]
    assert records[4]["data"]["candidate_id"] == records[3]["data"]["candidates"][0]["candidate_id"]
    assert records[-1]["data"]["backend"] == "mock"
    assert records[-1]["data"]["goal_completed"] is True
    assert records[-1]["data"]["diamond_success"] is False
    assert records[-1]["data"]["active_ticks"] == 20
    assert records[-1]["data"]["reward_total"] == 1.0
    assert records[4]["data"]["probabilities"] is None


@pytest.mark.parametrize("outcome", ["truncated", "invalid"])
def test_episode_outcomes_stay_distinct(tmp_path: Path, outcome: str) -> None:
    fixture = mock_fixture()
    step = fixture["steps"][0]
    step.update(terminated=False, truncated=False, invalid=False, events=[], reason=outcome)
    step[outcome] = True
    result = run_cli(fixture_config(tmp_path, fixture))
    summary = records(result)[-1]["data"]
    assert result.returncode == (1 if outcome == "invalid" else 0)
    assert summary[outcome] is True
    assert summary["terminated"] is False
    assert summary["goal_completed"] is False
    assert summary["active_ticks"] == 20


def test_backend_error_ends_episode_with_summary(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["steps"] = []
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 1
    output = records(result)
    assert [record["type"] for record in output[-2:]] == ["error", "summary"]
    assert output[-1]["data"]["error"]["code"] == "invalid_request"
    assert output[-1]["data"]["goal_completed"] is False
    assert result.stderr


def test_zero_candidates_force_wait_without_actor_experience(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["initial"]["observed_map"] = []
    fixture["steps"][0].update(events=[{"kind": "wait", "quantity": 0, "source": "mock"}],
                                terminated=False, truncated=True, reason="mock_time_limit")
    fixture["steps"][0]["observation"]["inventory"] = {}
    output = records(run_cli(fixture_config(tmp_path, fixture)))
    assert output[3]["data"] == {"candidates": [], "mask": []}
    assert output[4]["data"]["selector_mode"] == "forced_wait"
    assert output[-1]["data"]["actor_transitions"] == 0
    assert output[-1]["data"]["reward_total"] == 0.0


def test_hidden_fixture_fields_are_rejected_without_logging_values(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["initial"]["world_seed"] = "secret-marker"
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 1
    assert records(result)[-1]["data"]["error"] is not None
    assert "secret-marker" not in result.stdout + result.stderr


@pytest.mark.parametrize("reply, expected", [
    ('print(\'{"request_id":"wrong","result":{}}\', flush=True)', "protocol_error"),
    ('print("not json", flush=True)', "protocol_error"),
    ('import time; time.sleep(5)', "timeout"),
])
def test_rpc_failure_is_bounded_and_reported(tmp_path: Path, reply: str, expected: str) -> None:
    backend = tmp_path / "backend.py"
    backend.write_text(reply, encoding="utf-8")
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend)], rpc_timeout_seconds=0.2)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 1
    assert records(result)[-1]["data"]["error"]["code"] == expected


def test_alternate_rpc_backend_uses_the_same_public_flow(tmp_path: Path) -> None:
    # Alternate RPC entry point: only transport configuration changes, not episode execution.
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, "-m", "mc_diamond.mock_bridge",
                  "--fixture", str(Path("fixtures/mock_episode.json").resolve())])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 0
    assert records(result)[-1]["data"]["clock_mode"] == "mock"


def test_tick_mismatch_cannot_report_completed_goal(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["steps"][0]["observation"]["active_ticks"] = 99
    result = run_cli(fixture_config(tmp_path, fixture))
    summary = records(result)[-1]["data"]
    assert result.returncode == 1
    assert summary["error"]["code"] == "invalid_step"
    assert summary["goal_completed"] is False


def test_doctor_reports_actual_cpu_computation() -> None:
    result = subprocess.run(["mc-diamond", "doctor", "--config", "configs/pilot.yaml"],
                            text=True, capture_output=True, timeout=60)
    output = records(result)
    assert len(output) == 1
    report = output[0]["data"]
    assert output[0]["type"] == "doctor"
    assert report["probes"]["python"]["status"] == "available"
    assert report["probes"]["python"]["computation"] == {"expected": 10, "actual": 10}
    assert report["minecraft_verified"] is False
    assert report["probes"]["gpu"]["status"] in {"available", "missing", "error"}
    assert result.returncode == (0 if report["ready"] else 1)


def test_doctor_distinguishes_missing_tools_and_execution_errors(tmp_path: Path) -> None:
    # A controlled external tool failure, through the same CLI as real hardware probes.
    node = tmp_path / "node"
    node.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    node.chmod(0o755)
    executable = shutil.which("mc-diamond")
    assert executable is not None
    result = subprocess.run([executable, "doctor", "--config", "configs/pilot.yaml"],
                            env={**os.environ, "PATH": str(tmp_path)},
                            text=True, capture_output=True, timeout=60)
    probes = records(result)[0]["data"]["probes"]
    assert result.returncode == 1
    assert probes["node"]["status"] == "error"
    assert probes["java"]["status"] == "missing"
    assert probes["gpu"]["status"] == "missing"


def test_backend_launch_failure_still_has_episode_summary(tmp_path: Path) -> None:
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[str(tmp_path / "missing-backend")])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 1
    output = records(result)
    assert [record["type"] for record in output] == ["error", "summary"]
    assert output[-1]["data"]["error"]["code"] == "backend_error"
    assert output[-1]["data"]["episode_id"]
    assert output[-1]["data"]["attempt_id"]


def test_policy_rpc_cannot_reset_or_spoof_administrator() -> None:
    admin_read, admin_write = os.pipe()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", "fixtures/mock_episode.json",
             "--admin-fd", str(admin_read)], pass_fds=(admin_read,), text=True, capture_output=True,
            input='{"request_id":"p1","method":"reset","payload":{}}\n'
                  '{"request_id":"p2","method":"reset","payload":{},"role":"admin"}\n', timeout=5,
        )
    finally:
        os.close(admin_read)
        os.close(admin_write)
    output = [json.loads(line) for line in result.stdout.splitlines()]
    assert output[0]["error"]["code"] == "permission_denied"
    assert output[1]["error"]["code"] == "invalid_request"
    assert output[1]["request_id"] == "p2"


def test_goal_completion_preserves_acquisitions_across_decisions(tmp_path: Path) -> None:
    fixture = mock_fixture()
    first = fixture["steps"][0]
    first.update(terminated=False, reason="mock_acquisition")
    first["observation"]["inventory"] = {"oak_log": 1}
    last = json.loads(json.dumps(first))
    last.update(terminated=True, reason="mock_goal_completed", events=[{"kind": "wait", "source": "mock"}])
    last["observation"].update(obs_id="obs-2", active_ticks=40, remaining_ticks=60)
    fixture["steps"].append(last)
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 0
    assert records(result)[-1]["data"]["goal_completed"] is True


def test_rpc_wire_can_carry_actual_backend_provenance(tmp_path: Path) -> None:
    # Scripted external RPC replies test compatibility; this is not Minecraft verification.
    fixture = mock_fixture()
    fixture["steps"][0]["events"][0]["source"] = "minecraft"
    fixture["steps"][0]["clock_mode"] = "realtime"
    fixture_path = tmp_path / "wire.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    backend = tmp_path / "backend.py"
    backend.write_text(
        "import argparse,json,os,sys\n"
        "parser=argparse.ArgumentParser();parser.add_argument('--admin-fd',type=int);args=parser.parse_args()\n"
        f"fixture=json.load(open({str(fixture_path)!r}))\n"
        "request=json.loads(os.fdopen(args.admin_fd).readline())\n"
        "ids=request['payload'];observation=fixture['initial'];observation.update(ids)\n"
        "print(json.dumps({'request_id':request['request_id'],'result':observation}),flush=True)\n"
        "for line in sys.stdin:\n"
        " request=json.loads(line)\n"
        " if request['method']=='observe': result=observation\n"
        " else:\n"
        "  result=fixture['steps'][0];result['observation'].update(ids)\n"
        " print(json.dumps({'request_id':request['request_id'],'result':result}),flush=True)\n",
        encoding="utf-8",
    )
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend)])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 0, result.stderr
    output = records(result)
    assert output[5]["data"]["events"][0]["source"] == "minecraft"
    assert output[-1]["data"]["clock_mode"] == "realtime"
    assert output[-1]["data"]["diamond_success"] is False
