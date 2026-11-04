"""Actual fixture audit using the same public observation, candidates and step path."""

import hashlib
import json
import time
from typing import Any

from .episode import emit
from .navigation import generate_movement_candidates
from .macros import generate_wood_candidates
from .rpc import EpisodeError, RpcSession
from .schema import ErrorInfo, Goal


def policy_signature(value: dict[str, Any]) -> dict[str, Any]:
    """Ignore run identities and wall time, never policy state or decision evidence."""
    result: dict[str, Any] = json.loads(json.dumps(value))
    def clean(item: Any) -> None:
        if isinstance(item, dict):
            for name in ["episode_id", "attempt_id", "obs_id", "candidate_id", "source_obs_id", "event_id", "entity_id", "wall_seconds"]:
                item.pop(name, None)
            if item.get("kind") == "acquired":
                item.pop("position", None)  # Drop scatter is random; retain item/count and all policy state.
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
        wood_pair: list[dict[str, Any]] = []
        goal = Goal(goal_id="information-wood", kind="collect", target="oak_log", quantity=2)
        for variant in ["ore", "lava"]:
            prepared = session._call("information_fixture", {"variant": variant, "exposed": False, "scope": "wood"}, admin=True)
            if prepared.get("fixture_ready") is not True:
                raise ValueError("Wood fixture was not verified")
            observation = session.policy().observe()
            candidates = generate_wood_candidates(observation, goal)
            emit("information_wood_observation", observation)
            emit("information_wood_candidates", candidates)
            wood_candidate = next((c for c in candidates.candidates if c.action_kind == "mine_visible_cluster"
                              and isinstance(c.params["blocks"], list) and len(c.params["blocks"]) == 2), None)
            if wood_candidate is None:
                raise ValueError("Wood workload candidate absent")
            step = session.policy().step(wood_candidate)
            emit("information_wood_step", step)
            if (step.invalid or step.cancelled or step.terminated or not step.stable_boundary
                    or step.reason != "cluster_completed" or step.clock_mode != "paused"
                    or not step.pause_verified or not 1 <= step.actual_ticks <= wood_candidate.max_ticks
                    or step.source_obs_id != observation.obs_id or step.map_version != step.observation.map_version
                    or step.stop_evidence != [step.observation.obs_id, step.reason]
                    or step.observation.active_ticks != observation.active_ticks + step.actual_ticks
                    or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                    or sum(event.quantity for event in step.events if event.kind == "mined") != 2
                    or sum(event.quantity for event in step.events if event.kind == "acquired" and event.item == "oak_log") != 2
                    or step.observation.inventory.get("oak_log") != 2
                    or any(event.source != "minecraft" for event in step.events)):
                raise ValueError("Wood/clock/evidence was not verified")
            inputs = policy_signature({"observation": observation.model_dump(mode="json"),
                                       "candidates": candidates.model_dump(mode="json")})
            wood_pair.append({"inputs": inputs, "step": policy_signature(step.model_dump(mode="json"))})
            evidence.append({"scope": "wood", "exposed": False, "variant": variant,
                             "input_sha256": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
                             "candidate_count": len(candidates.candidates), "actual_ticks": step.actual_ticks})
        if wood_pair[0] != wood_pair[1]:
            raise ValueError("Hidden variant changed wood candidates/path/stop/boundary")
    except ValueError:
        error = ErrorInfo(code="invalid_step", message="Information audit evidence mismatch")
    except EpisodeError as failure:
        error = failure.error
    emit("information_summary", {"information_verified": error is None,
         "scope": ["observation", "move_observed", "mine_visible_cluster", "drop_pickup"], "hidden_hazard_peek": False,
         "trials": evidence, "error": error.model_dump(mode="json") if error else None,
         "wall_seconds": time.monotonic() - started})
    return error is None
