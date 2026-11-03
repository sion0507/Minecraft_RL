"""Actual fixture audit using the same public observation, candidates and step path."""

import hashlib
import json
import time
from typing import Any

from .episode import emit
from .navigation import generate_movement_candidates
from .rpc import EpisodeError, RpcSession
from .schema import ErrorInfo


def policy_signature(value: dict[str, Any]) -> dict[str, Any]:
    """Ignore run identities and wall time, never policy state or decision evidence."""
    result: dict[str, Any] = json.loads(json.dumps(value))
    def clean(item: Any) -> None:
        if isinstance(item, dict):
            for name in ["episode_id", "attempt_id", "obs_id", "candidate_id", "source_obs_id", "wall_seconds"]:
                item.pop(name, None)
            if "stop_evidence" in item:
                item["stop_evidence"] = item["stop_evidence"][1:]
            for child in item.values():
                clean(child)
        elif isinstance(item, list):
            for child in item:
                clean(child)
    clean(result)
    return result


def audit_information(session: RpcSession) -> bool:
    started = time.monotonic()
    evidence: list[dict[str, Any]] = []
    error: ErrorInfo | None = None
    try:
        for exposed in [False, True]:
            pair: list[dict[str, Any]] = []
            for variant in ["ore", "lava"]:
                prepared = session._call("information_fixture", {"variant": variant, "exposed": exposed}, admin=True)
                if prepared.get("fixture_ready") is not True:
                    raise ValueError("Fixture was not verified")
                observation = session.policy().observe()
                candidates = generate_movement_candidates(observation)
                emit("information_observation", observation)
                emit("information_candidates", candidates)
                inputs = policy_signature({"observation": observation.model_dump(mode="json"),
                                           "candidates": candidates.model_dump(mode="json")})
                if not exposed and pair and inputs != pair[0]["inputs"]:
                    raise ValueError("Hidden variant changed public observation/candidates/path")
                row: dict[str, Any] = {"inputs": inputs}
                if exposed:
                    target = "diamond_ore" if variant == "ore" else "lava"
                    if not any(cell.block == target for cell in observation.observed_map):
                        raise ValueError("Exposed target was not observed")
                elif candidates.candidates:
                    candidate = candidates.candidates[0]
                    step = session.policy().step(candidate)
                    emit("information_step", step)
                    if (step.invalid or step.terminated or not 1 <= step.actual_ticks <= candidate.max_ticks
                            or not 0 < step.distance_moved <= 16 or not step.pause_verified or not step.stable_boundary
                            or step.clock_mode != "paused" or step.reason != "path_completed"
                            or step.source_obs_id != observation.obs_id or step.path != candidate.params["path"]
                            or step.map_version != step.observation.map_version
                            or step.stop_evidence != [step.observation.obs_id, step.reason]
                            or any(event.source != "minecraft" for event in step.events)
                            or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                            or step.observation.active_ticks != observation.active_ticks + step.actual_ticks):
                        raise ValueError("Movement/clock/evidence was not verified")
                    row["step"] = policy_signature(step.model_dump(mode="json"))
                else:
                    row["step"] = None
                pair.append(row)
                evidence.append({"exposed": exposed, "variant": variant,
                                 "input_sha256": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
                                 "map_cells": len(observation.observed_map), "candidate_count": len(candidates.candidates)})
            if not exposed and (pair[0].get("step") is None or pair[0]["step"] != pair[1].get("step")):
                raise ValueError("Hidden variant changed movement/stop/boundary or movement was absent")
    except ValueError:
        error = ErrorInfo(code="invalid_step", message="Information audit evidence mismatch")
    except EpisodeError as failure:
        error = failure.error
    emit("information_summary", {"information_verified": error is None,
         "scope": ["observation", "move_observed"], "hidden_hazard_peek": False,
         "trials": evidence, "error": error.model_dump(mode="json") if error else None,
         "wall_seconds": time.monotonic() - started})
    return error is None
