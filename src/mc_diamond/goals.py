"""GoalRegistry (PLAN §5.1): planner goal format, immediate preconditions, completion and the rule recovery goal.

Every group uses these rules unchanged; only the planner backend differs. Fixed configuration goals are task
definitions of the smoke diagnostics, not planner output, so they skip `validate` and keep their chain-resolving
candidates (DECISIONS 2026-11-09 #9).
"""

import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from .navigation import PICKS, SAFE_BAND, hazard_distance
from .production import FUELS, RECIPES
from .schema import Goal, GoalOutcome, Observation, PlannerConfig, StepResult

GOAL_BUDGET_TICKS = 3600  # 3 active minutes at 20 ticks/s
FAILURE_LIMIT = 3
MACRO_LIMIT = 20
ESCAPE_DISTANCE = 3.0
EXPLORE_CELLS = 16
LOGS = ["oak_log", "spruce_log", "birch_log", "jungle_log", "acacia_log", "dark_oak_log"]
TOOLS = {"cobblestone": PICKS, "iron_ore": PICKS[:4], "diamond": PICKS[:3]}  # target: pickaxes that drop it
TARGETS = {
    "collect": {*LOGS, "cobblestone", "iron_ore"},
    "craft": {recipe["item"] for recipe in RECIPES},
    "smelt": {"iron_ingot"},
    "descend": {"safe_mining_zone"},
    "explore": {"space", *LOGS, "iron_ore", "diamond_ore"},
    "escape": {"hazard"},
    "mine_diamond": {"diamond"},
}
MAX_QUANTITY = {"collect": 16, "craft": 8, "smelt": 8}  # every other kind is exactly 1
COMPLETION_EVENT = {"collect": "acquired", "mine_diamond": "acquired", "craft": "crafted", "smelt": "smelted"}
ErrorCode = Literal["invalid_json", "invalid_format", "already_satisfied", "precondition"]


class GoalError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code: ErrorCode = code


def _parse(text: str) -> dict[str, object]:
    try:
        raw = json.loads(text)
    except ValueError:
        raise GoalError("invalid_json", "Planner output is not JSON") from None
    if not isinstance(raw, dict):
        raise GoalError("invalid_json", "Planner output must be one JSON object")
    if not {"kind", "target"} <= set(raw) <= {"kind", "target", "quantity", "direction"}:
        raise GoalError("invalid_format", "Goal needs kind and target, optionally quantity and direction")
    return raw


def _preconditions(goal: Goal, observation: Observation) -> list[str]:
    """Only what the observation shows now: carried items, observed facilities and furnace contents."""
    stock = observation.inventory
    observed = {cell.block for cell in observation.observed_map if cell.visible}
    if goal.kind in {"collect", "mine_diamond"} and goal.target in TOOLS:
        tools = TOOLS[goal.target]
        if not any(stock.get(tool, 0) for tool in tools):
            raise GoalError("precondition", f"{goal.target} needs one of {tools}")
        return [f"tool:{next(tool for tool in tools if stock.get(tool, 0))}"]
    if goal.kind == "descend":
        if not stock.get("iron_pickaxe", 0):
            raise GoalError("precondition", "descend needs a carried iron_pickaxe")
        return ["tool:iron_pickaxe"]
    if goal.kind == "escape":
        if hazard_distance(observation.observed_map, observation.position) >= ESCAPE_DISTANCE:
            raise GoalError("already_satisfied", f"No observed hazard within {ESCAPE_DISTANCE:g} blocks")
        return [f"hazard_within:{ESCAPE_DISTANCE:g}"]
    if goal.kind == "craft":
        need = goal.quantity - stock.get(goal.target, 0)
        for recipe in (r for r in RECIPES if r["item"] == goal.target):
            repeats = math.ceil(need / recipe["count"])
            if all(stock.get(name, 0) >= count * repeats for name, count in recipe["ingredients"].items()):
                if recipe["table"] and not (stock.get("crafting_table", 0) or "crafting_table" in observed):
                    raise GoalError("precondition", f"{goal.target} needs a carried or observed crafting_table")
                return [f"ingredient:{name}*{count * repeats}" for name, count in recipe["ingredients"].items()] + (
                    ["facility:crafting_table"] if recipe["table"] else [])
        raise GoalError("precondition", f"Carried ingredients cannot craft {goal.quantity} {goal.target}")
    if goal.kind == "smelt":
        need = goal.quantity - stock.get(goal.target, 0)
        loaded = sum(f.input_count for f in observation.furnaces if f.input_item == "iron_ore") + sum(
            f.output_count for f in observation.furnaces if f.output_item == "iron_ingot")
        if stock.get("iron_ore", 0) + loaded < need:
            raise GoalError("precondition", f"Smelting {need} iron_ingot needs that much carried or loaded iron_ore")
        fuel = next((name for name, ticks in FUELS.items() if stock.get(name, 0) * ticks >= need * 200), None)
        if fuel is None and not loaded:
            raise GoalError("precondition", "Smelting needs carried fuel")
        if not (stock.get("furnace", 0) or "furnace" in observed):
            raise GoalError("precondition", "Smelting needs a carried or observed furnace")
        return ["ore:iron_ore", f"fuel:{fuel or 'loaded'}", "facility:furnace"]
    return []


def validate(text: str, observation: Observation, goal_id: str,
             source: Literal["planner", "regenerated"]) -> Goal:
    """One planner reply to a goal, or `GoalError` with the reason fed back to the single regeneration."""
    raw = _parse(text)
    kind, target, quantity, direction = raw["kind"], raw["target"], raw.get("quantity", 1), raw.get("direction")
    if not isinstance(kind, str) or kind not in TARGETS or target not in TARGETS[kind]:
        raise GoalError("invalid_format", f"Unknown goal kind/target {kind}/{target}")
    if type(quantity) is not int or not 1 <= quantity <= MAX_QUANTITY.get(kind, 1):
        raise GoalError("invalid_format", f"{kind} quantity must be 1-{MAX_QUANTITY.get(kind, 1)}")
    if direction is not None and (kind != "explore" or direction not in {"north", "south", "east", "west"}):
        raise GoalError("invalid_format", "Only explore takes a direction: north, south, east or west")
    goal = Goal(goal_id=goal_id, kind=kind, target=str(target), quantity=quantity,  # type: ignore[arg-type]
                direction=direction, source=source, completion_rule_id=kind)  # type: ignore[arg-type]
    if kind in MAX_QUANTITY and observation.inventory.get(goal.target, 0) >= quantity:
        # Provided or earlier stock is not a new success (PLAN §5.1); the planner must ask for more.
        raise GoalError("already_satisfied", f"Already holding {quantity} {goal.target}")
    return goal.model_copy(update={"preconditions": _preconditions(goal, observation)})


def recovery_goal(observation: Observation, goal_id: str) -> Goal:
    """The common rule after a failed regeneration: escape an observed hazard, otherwise explore.

    It never picks a step of the production chain, so recovery progress is not planning ability (user decision).
    """
    if hazard_distance(observation.observed_map, observation.position) < ESCAPE_DISTANCE:
        return Goal(goal_id=goal_id, kind="escape", target="hazard", quantity=1, source="rule_recovery",
                    completion_rule_id="escape", preconditions=[f"hazard_within:{ESCAPE_DISTANCE:g}"])
    return Goal(goal_id=goal_id, kind="explore", target="space", quantity=1, source="rule_recovery",
                completion_rule_id="explore")


def completed(goal: Goal, start: Observation, step: StepResult, direct: int) -> bool:
    """The goal's own completion rule; `direct` counts its completion events since the goal started."""
    now = step.observation
    if step.invalid:
        return False
    if goal.kind in COMPLETION_EVENT:
        return direct > 0 and now.inventory.get(goal.target, 0) >= goal.quantity
    if goal.kind in {"descend", "escape"}:
        held = (step.stable_boundary and not step.cancelled
                and any(event.kind == "safe_hold" and event.quantity >= 20 for event in step.events))
        if goal.kind == "escape":
            return held and hazard_distance(now.observed_map, now.position) >= ESCAPE_DISTANCE
        return (held and SAFE_BAND[0] <= math.floor(now.position[1]) <= SAFE_BAND[1]
                and now.inventory.get("iron_pickaxe", 0) >= 1)
    # explore: 16 newly observed open cells, or a newly observed cell of the target resource.
    before = {tuple(cell.position) for cell in start.observed_map}
    new = [cell for cell in now.observed_map if tuple(cell.position) not in before]
    return (sum(cell.passable for cell in new) >= EXPLORE_CELLS
            or (goal.target != "space" and any(cell.block == goal.target for cell in new)))


Ask = Callable[[Observation, Goal, str | None], str]  # (observation, task, error feedback) -> raw planner reply


def scripted_planner(config: PlannerConfig) -> Ask:
    """Mock planner: the configured replies in order, then empty (invalid) replies."""
    replies = iter(config.outputs)
    return lambda _observation, _task, _feedback: next(replies, "")


class Planning:
    """Goal decisions of one episode: one planner request, one regeneration on error, then the rule recovery goal."""

    def __init__(self, task: Goal, ask: Ask | None, model: str | None = None, version: str | None = None) -> None:
        self.task, self.ask, self.model, self.version = task, ask, model, version
        self.counts = {"planner_initial_requests": 0, "planner_initial_errors": 0, "planner_regeneration_requests": 0,
                       "planner_regeneration_errors": 0, "rule_recoveries": 0, "goal_decisions": 0}

    def decide(self, observation: Observation, trigger: str) -> tuple[Goal, dict[str, object]]:
        self.counts["goal_decisions"] += 1
        goal_id = f"{self.task.goal_id}:{self.counts['goal_decisions']}"
        requests: list[dict[str, object]] = []
        if self.ask is None:
            goal = self.task.model_copy(update={"goal_id": goal_id})
        else:
            feedback: str | None = None
            for kind in ("initial", "regeneration"):
                self.counts[f"planner_{kind}_requests"] += 1
                reply = self.ask(observation, self.task, feedback)
                try:
                    goal = validate(reply, observation, goal_id, "planner" if kind == "initial" else "regenerated")
                    requests.append({"kind": kind, "reply": reply, "error": None})
                    break
                except GoalError as error:
                    self.counts[f"planner_{kind}_errors"] += 1
                    feedback = f"{error.code}: {error}"
                    requests.append({"kind": kind, "reply": reply, "error": error.code, "message": str(error)})
            else:
                self.counts["rule_recoveries"] += 1
                goal = recovery_goal(observation, goal_id)
        return goal, {"decision": self.counts["goal_decisions"], "trigger": trigger, "obs_id": observation.obs_id,
                      "source": goal.source, "planner_model": self.model, "planner_version": self.version,
                      "requests": requests, "goal": goal.model_dump(mode="json")}


@dataclass
class ActiveGoal:
    """The adopted goal's counters; `record` returns the first replan trigger a step causes, if any."""
    goal: Goal
    start: Observation
    macros: int = 0
    failures: int = 0
    streak: int = 0
    done: bool = False
    direct: dict[str, int] = field(default_factory=dict)

    def record(self, step: StepResult) -> str | None:
        if not step.cancelled:
            self.macros += 1
            failed = any(event.kind == "failed" for event in step.events)
            self.failures += failed
            self.streak = self.streak + 1 if failed else 0
        for event in step.events:
            if event.kind in {"acquired", "crafted", "smelted"} and event.item:
                key = f"{event.kind}:{event.item}"
                self.direct[key] = self.direct.get(key, 0) + event.quantity
        own = self.direct.get(f"{COMPLETION_EVENT.get(self.goal.kind)}:{self.goal.target}", 0)
        self.done = completed(self.goal, self.start, step, own)
        if self.done:
            return "goal_completed"
        if self.streak >= FAILURE_LIMIT:
            return "consecutive_failures"
        if step.observation.active_ticks - self.start.active_ticks >= self.goal.active_budget_ticks:
            return "goal_time_limit"
        return "macro_limit" if self.macros >= MACRO_LIMIT else None

    def outcome(self, end_tick: int, reason: str) -> GoalOutcome:
        return GoalOutcome(goal_id=self.goal.goal_id, source=self.goal.source, kind=self.goal.kind, target=self.goal.target,
                           start_tick=self.start.active_ticks, end_tick=end_tick, macros=self.macros, failures=self.failures,
                           completed=self.done, end_reason=reason, direct=dict(self.direct))
