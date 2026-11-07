"""Actual first-tick oxygen/block and second-tick drop synchronization; no certificate.

The administrator diagnostic loader captures client state immediately after advance,
before pause or console queries. It never changes natural snapshots or policy inputs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from mc_diamond.rpc import RpcSession


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    files = [Path("bridge/minecraft.js"), Path("fixtures/tick_synchronization.cjs"), Path(__file__),
             Path("worlds/server/mods/mc-diamond-pause.jar")]
    (args.output / "manifest.json").write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                                          for p in files}, indent=2))
    passed = True
    with RpcSession(["node", "--require", "./fixtures/tick_synchronization.cjs", "bridge/minecraft.js",
                     "--task", "C4"], 180) as session:
        try:
            for scene in ["water", "furnace", "drop"]:
                result = session._call("clock_trial", {"scene": scene, "delay_seconds": 0, "trial": 1}, admin=True)
                (args.output / (scene + ".json")).write_text(json.dumps(result, indent=2))
                state: Any = result["immediate_sync"]
                valid = (state["client_oxygen"] == state["server_oxygen"] if scene == "water" else
                         state["client_furnace_lit"] == state["server_furnace_lit"] is True if scene == "furnace" else
                         state["client_drop"] is not None and math.dist(state["client_drop"], state["server_drop"]) < 1e-6)
                print(json.dumps({"scene": scene, "passed": valid, **state}), flush=True)
                passed = passed and valid
            assert passed, "State was observed late after the active tick receipt"
        finally:
            restored = session.reset("restored", "restore-1")
            (args.output / "restore.json").write_text(restored.model_dump_json())
            assert restored.active_ticks == 0 and restored.inventory == {} and restored.health == 20


if __name__ == "__main__":
    main()
