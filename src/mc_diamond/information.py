"""Actual fixture audit using the same public observation, candidates and step path."""

import hashlib
import json
import time
from typing import Any

from .episode import emit
from .navigation import generate_descent_candidates, generate_movement_candidates, ore_search_choices
from .macros import generate_wood_candidates
from .production import generate_production_candidates
from .rpc import EpisodeError, RpcSession
from .schema import Candidate, CandidateSet, ErrorInfo, Goal


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


def stair_signature(value: dict[str, Any]) -> dict[str, Any]:
    """Also drop item scatter: the server randomises pickups, hidden terrain does not."""
    result = policy_signature(value)
    def clean(item: Any) -> None:
        if isinstance(item, dict):
            item.pop("drops", None)
            if "inventory" in item:
                item["inventory"].pop("cobblestone", None)
            if "events" in item:
                item["events"] = [event for event in item["events"] if event["kind"] != "acquired"]
            for child in item.values():
                clean(child)
        elif isinstance(item, list):
            for child in item:
                clean(child)
    clean(result)
    return result


def audit_stairs(session: RpcSession, evidence: list[dict[str, Any]]) -> None:
    """Same visible rock, different hidden block: every decision before exposure must match."""
    def stair(scope: str, variant: str, plan: list[int], target: str | None = None,
              kind: str = "stair_down", height: int = 2) -> list[dict[str, Any]]:
        prepared = session._call("information_fixture", {"variant": variant, "exposed": False, "scope": scope}, admin=True)
        if prepared.get("fixture_ready") is not True:
            raise ValueError("Stair fixture was not verified")
        observation = session.policy().observe()
        rows: list[dict[str, Any]] = []
        for stairs in plan:
            # G2/G4 search for iron/diamond with the shared ore search: stairs, then tunnels, the ore on the stop list.
            found = (generate_descent_candidates(observation).candidates if target is None
                     else ore_search_choices(observation, target, 3 if target == "iron_ore" else 1))
            candidates = CandidateSet(candidates=found, mask=[True] * len(found))
            emit("information_stair_observation", observation)
            emit("information_stair_candidates", candidates)
            east = next((c for c in candidates.candidates if c.action_kind == kind and c.params["direction"] == [1, 0]), None)
            if east is None:
                raise ValueError("Stair/tunnel candidate absent")
            # Workload and section are overridden alike: the 8-choice cap may leave the 1x3 option out above the ore layers.
            workload = {"stairs": stairs} if kind == "stair_down" else {"cells": stairs, "height": height}
            selected = east.model_copy(update={"params": {**east.params, **workload}})
            step = session.policy().step(selected)
            emit("information_stair_step", step)
            if (step.invalid or step.cancelled or step.terminated or step.clock_mode != "paused" or not step.pause_verified
                    or not 1 <= step.actual_ticks <= selected.max_ticks or step.source_obs_id != observation.obs_id
                    or step.stop_evidence != [step.observation.obs_id, step.reason]
                    or step.map_version != step.observation.map_version
                    or step.observation.active_ticks != observation.active_ticks + step.actual_ticks
                    or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                    or any(event.source != "minecraft" for event in step.events)):
                raise ValueError("Stair evidence mismatch")
            rows.append(stair_signature({"observation": observation.model_dump(mode="json"),
                "candidates": candidates.model_dump(mode="json"), "selected": selected.model_dump(mode="json"),
                "step": step.model_dump(mode="json")}))
            observation = step.observation
        return rows

    hidden = [stair("stair", variant, [4]) for variant in ["ore", "lava"]]
    if hidden[0] != hidden[1]:
        raise ValueError("Hidden variant changed stair candidates/path/stop/boundary")
    if (hidden[0][0]["step"]["reason"] != "stairs_completed" or not hidden[0][0]["step"]["stable_boundary"]
            or sum(event["kind"] == "descended" for event in hidden[0][0]["step"]["events"]) != 4):
        raise ValueError("Stair workload was not executed")
    evidence.append({"scope": "stair", "exposed": False, "steps": 1, "actual_ticks": hidden[0][0]["step"]["actual_ticks"],
                     "input_sha256": hashlib.sha256(json.dumps(hidden[0], sort_keys=True).encode()).hexdigest()})
    # Positive control: the same block one cut ahead stops only once a cut really opens it.
    for scope, target, item, kind, plan, height in [("stair_exposed", None, "diamond_ore", "stair_down", [1, 2], 2),
                                                    ("stair_iron", "iron_ore", "iron_ore", "stair_down", [1, 2], 2),
                                                    ("tunnel", "diamond_ore", "diamond_ore", "tunnel", [2, 8], 2),
                                                    ("tunnel", "diamond_ore", "diamond_ore", "tunnel", [2, 8], 3),
                                                    ("tunnel_iron", "iron_ore", "iron_ore", "tunnel", [2, 8], 2)]:
        # The tunnel pair's first two cuts never reach the hidden wall cell: an unexposed level search must match too.
        ore, lava = (stair(scope, variant, plan, target, kind, height) for variant in ["ore", "lava"])
        if ore[0] != lava[0] or ore[1]["selected"] != lava[1]["selected"]:
            raise ValueError("Hidden variant changed the decision before exposure")
        if kind == "tunnel" and (ore[0]["step"]["reason"] != "tunnel_completed"
                                 or sum(event["kind"] == "tunneled" for event in ore[0]["step"]["events"]) != 2):
            raise ValueError("Tunnel workload was not executed")
        if (ore[1]["step"]["reason"] != "ore_exposed" or lava[1]["step"]["reason"] != "observed_hazard"
                or ore[1]["step"]["actual_ticks"] != lava[1]["step"]["actual_ticks"]
                or [e["item"] for e in ore[1]["step"]["events"] if e["kind"] == "exposed"] != [item]):
            raise ValueError("Exposure stop mismatch")
        evidence.append({"scope": scope, "height": height, "exposed": True, "steps": 2, "stop_ticks": ore[1]["step"]["actual_ticks"],
                         "input_sha256": hashlib.sha256(json.dumps(ore[0], sort_keys=True).encode()).hexdigest()})


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
        for scope in ["wood_tool", "wood_drop", "empty", "wait20", "wait100", "wait200"]:
            macro_pair: list[list[dict[str, Any]]] = []
            for variant in ["ore", "lava"]:
                fixture_scope = scope if not scope.startswith("wait") else "empty"
                prepared = session._call("information_fixture", {"variant": variant, "exposed": False,
                                         "scope": fixture_scope}, admin=True)
                if prepared.get("fixture_ready") is not True:
                    raise ValueError("Fixture was not verified")
                observation = session.policy().observe()
                steps = []
                for index in range(3 if scope == "wood_drop" else 1):
                    candidates = generate_wood_candidates(observation, goal)
                    if scope == "empty" and candidates.candidates:
                        raise ValueError("Empty fixture has candidates")
                    candidate = (candidates.candidates[0] if scope in {"wood_tool", "wood_drop"} and candidates.candidates
                                 else Candidate(candidate_id=f"{observation.obs_id}:audit-wait", action_kind="wait",
                                     params={}, max_ticks=int(scope[4:]) if scope.startswith("wait") else 20,
                                     stop_rule_id="time_or_hazard", source_obs_id=observation.obs_id,
                                     description="Explicit diagnostic wait"))
                    expected = "place_or_equip" if scope == "wood_tool" else "wait"
                    if candidate.action_kind != expected:
                        raise ValueError("Expected independent equip/wait candidate absent")
                    emit("information_macro_observation", observation)
                    emit("information_macro_candidates", candidates)
                    step = session.policy().step(candidate)
                    emit("information_macro_step", step)
                    if (step.invalid or step.cancelled or step.terminated or not step.stable_boundary
                            or step.clock_mode != "paused" or not step.pause_verified
                            or step.source_obs_id != observation.obs_id
                            or step.stop_evidence != [step.observation.obs_id, step.reason]
                            or step.map_version != step.observation.map_version
                            or step.observation.active_ticks != observation.active_ticks + step.actual_ticks
                            or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                            or not any(event.kind == ("equipped" if scope == "wood_tool" else "wait") for event in step.events)
                            or any(event.source != "minecraft" for event in step.events)
                            or step.reason != ("equip_completed" if scope == "wood_tool" else "wait_completed")
                            or step.actual_ticks != (1 if scope == "wood_tool" else candidate.max_ticks)):
                        raise ValueError("Independent macro evidence mismatch")
                    if scope == "wood_tool" and step.observation.tool != "wooden_axe":
                        raise ValueError("Equipment did not change")
                    steps.append(policy_signature({"observation": observation.model_dump(mode="json"),
                        "candidates": candidates.model_dump(mode="json"), "selected": candidate.model_dump(mode="json"),
                        "step": step.model_dump(mode="json")}))
                    observation = step.observation
                    if scope != "wood_drop" or observation.inventory.get("oak_log", 0):
                        break
                if scope == "wood_drop" and (observation.inventory.get("oak_log") != 1 or
                        sum(event["quantity"] for row in steps for event in row["step"]["events"]
                            if event["kind"] == "acquired") != 1):
                    raise ValueError("Independent owned drop pickup absent")
                macro_pair.append(steps)
                evidence.append({"scope": scope, "exposed": False, "variant": variant,
                    "input_sha256": hashlib.sha256(json.dumps(steps, sort_keys=True).encode()).hexdigest(),
                    "steps": len(steps), "actual_ticks": sum(row["step"]["actual_ticks"] for row in steps)})
            if macro_pair[0] != macro_pair[1]:
                raise ValueError(f"Hidden variant changed {scope} policy evidence")
        for scope in ["production_craft", "production_place", "production_furnace", "iron", "diamond"]:
            production_pair: list[list[dict[str, Any]]] = []
            goal = Goal(goal_id="information-production", kind="smelt" if scope == "production_furnace" else
                        "collect" if scope == "iron" else "mine_diamond" if scope == "diamond" else "craft",
                        target={"production_furnace": "iron_ingot", "iron": "iron_ore", "diamond": "diamond"}.get(scope, "iron_pickaxe"),
                        quantity=1)
            expected_event = {"production_craft": "crafted", "production_place": "placed",
                              "production_furnace": "smelted", "iron": "acquired", "diamond": "acquired"}[scope]
            for variant in ["ore", "lava"]:
                prepared = session._call("information_fixture", {"variant": variant, "exposed": False, "scope": scope}, admin=True)
                if prepared.get("fixture_ready") is not True:
                    raise ValueError("Production fixture was not verified")
                observation = session.policy().observe()
                steps = []
                for index in range(8 if scope == "production_furnace" else 1):
                    candidates = generate_production_candidates(observation, goal)
                    emit("information_production_observation", observation)
                    emit("information_production_candidates", candidates)
                    if not candidates.candidates:
                        raise ValueError("Production candidate absent")
                    candidate = candidates.candidates[0]
                    step = session.policy().step(candidate)
                    emit("information_production_step", step)
                    if (step.invalid or step.cancelled or step.terminated or not step.stable_boundary
                            or step.clock_mode != "paused" or not step.pause_verified
                            or not 1 <= step.actual_ticks <= candidate.max_ticks
                            or step.source_obs_id != observation.obs_id
                            or step.stop_evidence != [step.observation.obs_id, step.reason]
                            or step.map_version != step.observation.map_version
                            or step.observation.active_ticks != observation.active_ticks + step.actual_ticks
                            or step.observation.remaining_ticks != observation.remaining_ticks - step.actual_ticks
                            or not step.events or any(e.source != "minecraft" for e in step.events)):
                        raise ValueError("Production evidence mismatch")
                    steps.append(policy_signature({"observation": observation.model_dump(mode="json"),
                        "candidates": candidates.model_dump(mode="json"), "selected": candidate.model_dump(mode="json"),
                        "step": step.model_dump(mode="json")}))
                    observation = step.observation
                    if any(e.kind == expected_event and e.quantity == 1 for e in step.events):
                        break
                else:
                    raise ValueError("Production direct event absent")
                if scope == "production_furnace" and not any(row["selected"]["action_kind"] == "furnace_load" for row in steps):
                    raise ValueError("Furnace loading absent")
                production_pair.append(steps)
                evidence.append({"scope": scope, "exposed": False, "variant": variant,
                    "input_sha256": hashlib.sha256(json.dumps(steps, sort_keys=True).encode()).hexdigest(),
                    "steps": len(steps), "actual_ticks": sum(row["step"]["actual_ticks"] for row in steps)})
            if production_pair[0] != production_pair[1]:
                raise ValueError(f"Hidden variant changed {scope} policy evidence")
        audit_stairs(session, evidence)
    except ValueError:
        error = ErrorInfo(code="invalid_step", message="Information audit evidence mismatch")
    except EpisodeError as failure:
        error = failure.error
    emit("information_summary", {"information_verified": error is None,
         "scope": ["observation", "move_observed", "mine_visible_cluster", "place_or_equip", "wait20", "wait100", "wait200",
                   "drop_pickup", "independent_drop_wait", "zero_candidates", "craft_batch", "facility_place",
                   "furnace_load", "furnace_collect", "iron_mining", "diamond_mining", "stair_down", "stair_exposure",
                   "stair_iron_exposure", "tunnel", "tunnel_exposure", "tunnel_iron_exposure"], "hidden_hazard_peek": False,
         "trials": evidence, "error": error.model_dump(mode="json") if error else None,
         "wall_seconds": time.monotonic() - started})
    return error is None
