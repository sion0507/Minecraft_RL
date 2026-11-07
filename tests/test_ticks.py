"""Scripted tick invariants through shipping policy dispatch, not real Minecraft."""
import json
import subprocess


def test_shipping_tick_dispatch_preserves_each_tick_and_client_barrier() -> None:
    result = subprocess.run(["node", "fixtures/tick_contracts.cjs"], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}


def test_iron_information_fixture_preserves_public_pickup_path() -> None:
    result = subprocess.run(["node", "fixtures/information_iron.cjs"], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}
