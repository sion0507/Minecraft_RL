"""Reset-time lifecycle recovery through shipping Server.restore, not actual Minecraft."""

import subprocess

import pytest


@pytest.mark.parametrize("scenario", ["once", "twice", "normal", "dump-missing", "dump-timeout", "early-exit",
                                     "unreaped", "unwritable-log", "invalid-snapshot", "stale-output"])
def test_startup_timeout_records_evidence_reaps_java_and_restores_snapshot_once(scenario: str) -> None:
    run = subprocess.run(["node", "fixtures/server_startup.cjs", scenario], capture_output=True, text=True, timeout=15)
    assert run.returncode == 0, run.stderr
