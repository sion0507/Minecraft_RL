"""Measure fixed-scene wait20/100/200 (three repeats), or fit final JSONL logs.

Run from the repository root. Uses only the isolated installed server, no models.
The fixed fixture is administrator prepared, never natural-task success evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any

from mc_diamond.rpc import RpcSession
from mc_diamond.schema import Candidate


def fit(rows: list[dict[str, Any]]) -> dict[str, float]:
    nn = sum(r["decisions"] ** 2 for r in rows)
    nt = sum(r["decisions"] * r["ticks"] for r in rows)
    tt = sum(r["ticks"] ** 2 for r in rows)
    nw = sum(r["decisions"] * r["wall_seconds"] for r in rows)
    tw = sum(r["ticks"] * r["wall_seconds"] for r in rows)
    det = nn * tt - nt * nt
    if det <= 0:
        raise ValueError("Need runs with different ticks per decision")
    return {"seconds_per_decision": (nw * tt - tw * nt) / det,
            "seconds_per_tick": (nn * tw - nt * nw) / det}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--logs", type=Path, nargs="+")
    args = parser.parse_args()
    # Independent numerical example for the same two-parameter regression as #32.
    example = fit([{"decisions": 1, "ticks": t, "wall_seconds": w}
                   for t, w in [(20, 5.18), (100, 21.18), (200, 41.18)]])
    assert abs(example["seconds_per_decision"] - 1.18) < 1e-9
    assert abs(example["seconds_per_tick"] - 0.2) < 1e-9
    args.output.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    sources = [*Path("bridge").glob("*.js"), *Path("bridge/pausemod/src").glob("*.java"), Path(__file__),
               Path("worlds/server/mods/mc-diamond-pause.jar"), Path("worlds/server/server.properties")]
    (args.output / "manifest.json").write_text(json.dumps({
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}, indent=2))
    if args.logs:
        for path in args.logs:
            records = [json.loads(line) for line in path.read_text().splitlines() if line.startswith("{")]
            steps = [r["data"] for r in records if r.get("type") == "step"]
            rows.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "decisions": len(steps), "ticks": sum(s["actual_ticks"] for s in steps),
                         "wall_seconds": sum(s["wall_seconds"] for s in steps)})
    else:
        with RpcSession(["node", "bridge/minecraft.js", "--task", "C4"], 180) as session:
            try:
                prepared = session._call("information_fixture", {
                    "variant": "ore", "exposed": False, "scope": "empty"}, admin=True)
                (args.output / "fixture.json").write_text(json.dumps(prepared))
                with (args.output / "steps.jsonl").open("w") as stream:
                    for ticks in [20, 100, 200] * 3:
                        observation = session.policy().observe()
                        selected = Candidate(candidate_id="timing", action_kind="wait", params={},
                            max_ticks=ticks, stop_rule_id="wait_or_hazard", source_obs_id=observation.obs_id,
                            description="fixed flat timing")
                        start = time.monotonic()
                        step = session.policy().step(selected)
                        stream.write(json.dumps({"type": "step", "data": step.model_dump(mode="json"),
                            "rpc_seconds": time.monotonic() - start}) + "\n")
                        stream.flush()
                        assert step.actual_ticks == ticks and not step.invalid and step.reason == "wait_completed"
                        rows.append({"decisions": 1, "ticks": step.actual_ticks, "wall_seconds": step.wall_seconds})
                        print(json.dumps(rows[-1]), flush=True)
            finally:
                restored = session.reset("restored", "restore-1")
                (args.output / "restore.json").write_text(restored.model_dump_json())
                assert restored.active_ticks == 0 and restored.inventory == {} and restored.health == 20
    result = {"rows": rows, **fit(rows)}
    (args.output / "fit.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
