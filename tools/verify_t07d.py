"""#54 constructed Minecraft scenes through the shipping RPC; no models/APIs or natural-task claims.

Run before final clock certification for physical preflights, then once on the final fingerprint.
With --information, ore/lava hidden variants must have the same public inputs and execution.
Finally restore the C4 snapshot and close the client/server even when an assertion fails.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from mc_diamond.information import ASCENT_SCENES, ascent_candidate, stair_signature
from mc_diamond.rpc import RpcSession
from mc_diamond.schema import EpisodeConfig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--information", action="store_true")
    parser.add_argument("scenes", nargs="*", choices=ASCENT_SCENES)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    config = EpisodeConfig.model_validate(yaml.safe_load(Path("configs/minecraft.yaml").read_text()))
    assert config.command
    sources = [*Path("bridge").glob("*.js"), *Path("src/mc_diamond").glob("*.py"), Path(__file__)]
    (args.output / "manifest.json").write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}))
    results: dict[str, Any] = {}
    with RpcSession(config.command, config.rpc_timeout_seconds) as session:
        try:
            for scope in args.scenes or ASCENT_SCENES:
                pair = []
                for variant in ["ore", "lava"] if args.information else ["ore"]:
                    prepared = session._call("information_fixture", {"variant": variant, "exposed": False, "scope": scope}, admin=True)
                    assert prepared["fixture_ready"] is True
                    o = session.policy().observe()
                    c = ascent_candidate(scope, o)
                    step = session.policy().step(c)
                    raw = {"natural_task": False, "prepared": prepared, "initial": o.model_dump(mode="json"),
                           "candidate": c.model_dump(mode="json"), "step": step.model_dump(mode="json")}
                    (args.output / f"{scope}-{variant}.json").write_text(json.dumps(raw))
                    pair.append(stair_signature(raw))
                    row = {"reason": step.reason, "ticks": step.actual_ticks, "dig_ticks": step.dig_ticks,
                           "from": o.position, "to": step.observation.position, "stable": step.stable_boundary,
                           "health": step.observation.health, "pause_verified": step.pause_verified}
                    results[f"{scope}-{variant}"] = row
                    print(json.dumps({"scene": scope, "variant": variant, **row}), flush=True)
                    assert not step.invalid and 1 <= step.actual_ticks <= 400 and step.observation.health == o.health
                    expected = {"ascent_pillar": "pillar_completed", "ascent_ledge": "path_completed", "ascent_stair": "stairs_completed",
                                "safe_drop": "path_completed", "recover_table": "cluster_completed", "unsafe_cut": "unsafe_cut"}[scope]
                    assert step.reason == expected, (scope, step.reason)
                    assert step.stable_boundary and step.observation.active_ticks == o.active_ticks + step.actual_ticks
                    if scope in {"ascent_pillar", "ascent_ledge", "ascent_stair", "safe_drop"}:
                        assert step.observation.position[1] - o.position[1] == (-3 if scope == "safe_drop" else 4 if scope == "ascent_pillar" else 2)
                    if scope in {"ascent_pillar", "ascent_ledge"}:
                        assert o.inventory["dirt"] - step.observation.inventory.get("dirt", 0) == (4 if scope == "ascent_pillar" else 1)
                    if scope == "recover_table":
                        assert step.observation.inventory.get("crafting_table", 0) == 1
                    if scope == "unsafe_cut":
                        assert not any(e.kind == "mined" for e in step.events)
                if args.information:
                    assert pair[0] == pair[1], (scope, "hidden terrain changed public execution")
            results["passed"] = True
        finally:
            restored = session.reset("issue54-restored", "finally")
            assert restored.active_ticks == 0 and not restored.inventory and restored.health == 20
            results["reset"] = True
            (args.output / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
