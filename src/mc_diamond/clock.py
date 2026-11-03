"""Real administrator diagnostics; scripted tests do not establish physical pause."""

import math
import re
from copy import deepcopy
from typing import Any

from .episode import emit
from .rpc import EpisodeError, RpcSession
from .schema import ErrorInfo

SCENES = ("flat", "furnace", "drop", "lava", "fall", "water", "fire")


def prepared(scene: str, sample: dict[str, Any]) -> bool:
    client, server = sample["client"], sample["server"]
    if not {"velocity", "health", "oxygen", "on_fire", "inventory", "events"} <= client.keys():
        return False
    state = server.get("state", {})
    if not {"Motion", "Health", "Air", "Fire", "Inventory", "FallDistance", "HurtTime"} <= state.keys():
        return False
    def number(key: str) -> float:
        return float(re.sub(r"[bBsSlLfFdD]$", "", state[key]))
    if scene == "water":
        return number("Air") < 300
    if scene in {"fire", "lava"}:
        return number("Fire") > 0 or number("Health") < 20
    if scene == "fall":
        return bool(client["velocity"][1] < 0)
    if scene == "furnace":
        return bool(re.search(r"CookTime: [1-9][0-9]*s", server.get("furnace", "")))
    if scene == "drop":
        return "mc_clock" in server.get("drop", "") and "Age:" in server["drop"]
    return bool(client.get("on_ground"))


def compare(result: dict[str, Any], scene: str, delay: int, trial: int) -> None:
    try:
        if (result["scene"], result["delay_seconds"], result["trial"]) != (scene, delay, trial):
            raise ValueError("Clock trial identity mismatch")
        before, after = deepcopy(result["before"]), deepcopy(result["after"])
        scene_prepared = prepared(scene, before)
        drift: dict[str, float] = {}
        for side in ("client", "server"):
            initial, final = before[side].pop("position"), after[side].pop("position")
            if len(initial) != 3 or len(final) != 3:
                raise ValueError("Invalid clock position")
            delta = math.dist(initial, final)
            if not math.isfinite(delta):
                raise ValueError("Non-finite clock position")
            drift[side] = delta
        result["position_drift"] = drift
        result["scene_prepared"] = scene_prepared
        result["passed"] = (scene_prepared and before == after
                            and all(value <= 0.001 for value in drift.values())
                            and result["executed_ticks"] > 0 and result["wall_seconds"] >= delay)
    except (KeyError, TypeError, ValueError, OverflowError):
        raise EpisodeError(ErrorInfo(code="protocol_error", message="Invalid clock sample")) from None


def verify_clock(session: RpcSession) -> bool:
    passed = 0
    trials = 0
    for scene in SCENES:
        for delay in (0, 5, 10):
            for trial in (1, 2, 3):
                result: dict[str, Any] = session._call("clock_trial", {
                    "scene": scene, "delay_seconds": delay, "trial": trial,
                }, admin=True)
                compare(result, scene, delay, trial)
                passed += result["passed"]
                trials += 1
                emit("clock_trial", result)
    verified = passed == trials == 63
    if verified:
        session._call("certify_clock", {}, admin=True)
    emit("clock_summary", {"trials": trials, "passed": passed, "pause_verified": verified,
                           "clock_mode": "paused" if verified else "unverified",
                           "position_tolerance_blocks": 0.001})
    return verified
