"""Episode reward ledger (PLAN §8.1), independent of the policy and administrator information.

Time is charged on every executed tick. Sparse events become known at the macro's returned boundary,
so their reward is assigned to its last tick (not spread uniformly over the macro).
"""

import math
from dataclasses import dataclass

from .goals import COMPLETION_EVENT, LOGS, TOOLS
from .navigation import PICKS
from .schema import Goal, Observation, StepResult

PROGRESS = {"log": 1., "crafting_table": 1., "wooden_pickaxe": 1., "stone_pickaxe": 2.,
            "furnace": 2., "iron_ore": 3., "iron_ingot": 3., "iron_pickaxe": 5.}


def progress_key(item: str) -> str:
    return "log" if item in LOGS else item


@dataclass(frozen=True)
class Reward:
    total: float
    discounted: float
    discount: float
    terminal: bool
    components: dict[str, float]


class RewardLedger:
    def __init__(self, initial: Observation, *, discovery_reward: float = 0., pilot_signal: bool = False) -> None:
        if not math.isfinite(discovery_reward) or discovery_reward < 0:
            raise ValueError("Discovery reward must be finite and nonnegative")
        self.discovery_reward = discovery_reward
        self.pilot_signal = pilot_signal and initial.objective_kind == "local"
        self.goal_stock: dict[str, int] = {}
        self.collect_paid: dict[str, int] = {}
        self.local_goals: set[str] = set()
        self.seen_blocks = {cell.block for cell in initial.observed_map if cell.visible}
        self.objective = initial.objective_kind
        self.max_ticks = initial.active_ticks + initial.remaining_ticks
        if self.max_ticks <= 0:
            raise ValueError("Reward ledger needs a positive task tick budget")
        self.gamma = 2 ** (-1 / self.max_ticks)
        self.progress = {progress_key(item) for item, count in initial.inventory.items() if count}
        self.progress_total = self.goal_total = 0.0
        self.completed_goals: set[tuple[str, str]] = set()
        self.goal_eligible: dict[str, bool] = {}
        self.seen_events: set[str] = set()
        self.diamond_mines: set[tuple[float, ...]] = set()
        self.diamond_paid = self.local_paid = self.death_paid = False

    def compute(self, before: Observation, goal: Goal, step: StepResult, *, goal_completed: bool) -> Reward:
        n = step.actual_ticks
        if n <= 0 or step.observation.objective_kind != self.objective:
            raise ValueError("Reward requires executed ticks and the same task objective")
        eligible = self.goal_eligible.setdefault(goal.goal_id,
            goal.kind not in COMPLETION_EVENT or before.inventory.get(goal.target, 0) < goal.quantity)
        rate = -.1 / self.max_ticks if self.objective == "local" else -.001 / 20
        components = {"time": rate * n}
        events = []
        for event in step.events:
            if event.event_id:
                if event.event_id in self.seen_events:
                    continue
                self.seen_events.add(event.event_id)
            events.append(event)
        dead = step.observation.health <= 0
        if dead and not self.death_paid:
            components["death"] = -1. if self.objective == "local" else -20.
            self.death_paid = True
        if any(e.kind == "failed" for e in events):
            components["failure"] = -.01 if self.objective == "local" else -.05
        for event in events:
            if event.kind == "mined" and event.item == "diamond_ore" and event.position and before.tool in PICKS[:3]:
                self.diamond_mines.add(tuple(event.position))
        # acquired is already the bridge's own confirmed mining-drop event. Its position is the spawn point,
        # which the bridge accepts within 2 blocks of the mined block's centre (not equal to its block coordinates).
        diamond = any(e.kind == "acquired" and e.item == "diamond" and e.quantity > 0 and e.position
            and (e.source == "mock" or e.entity_id is not None)
            and any(math.dist(e.position, [v + .5 for v in block]) <= 2 for block in self.diamond_mines) for e in events)
        success = goal_completed and eligible and not step.invalid and not dead
        if goal.kind == "mine_diamond":
            success = success and diamond
        if self.objective == "local":
            visible = {cell.block for cell in step.observation.observed_map if cell.visible}
            needed = {"cobblestone": "stone", "diamond": "diamond_ore", "iron_ingot": "iron_ore"}
            required = {needed.get(goal.target, goal.target)}
            if goal.target in TOOLS and not any(before.inventory.get(pick, 0) for pick in PICKS):
                required.update(LOGS)
            discovered = (visible - self.seen_blocks) & required
            self.seen_blocks.update(visible)
            if self.discovery_reward and discovered:
                components["discovery"] = self.discovery_reward * len(discovered)
            if self.pilot_signal and goal.kind == "collect" and not step.invalid and not dead:
                stock = self.goal_stock.setdefault(goal.goal_id, before.inventory.get(goal.target, 0))
                paid = self.collect_paid.get(goal.goal_id, 0)
                direct = sum(e.quantity for e in events if e.kind == "acquired" and e.item == goal.target)
                units = min(direct, max(0, goal.quantity - stock - paid))
                if units:
                    components["collect"] = units / goal.quantity
                    self.collect_paid[goal.goal_id] = paid + units
            elif self.pilot_signal and success and goal.goal_id not in self.local_goals:
                components["success"] = 1.
                self.local_goals.add(goal.goal_id)
            elif not self.pilot_signal and success and not self.local_paid:
                components["success"], self.local_paid = 1., True
        else:
            if diamond and not self.diamond_paid:
                components["diamond"], self.diamond_paid = 100., True
            for event in events:
                if event.item and event.quantity > 0:
                    key = progress_key(event.item)
                    expected = "acquired" if key in {"log", "iron_ore"} else "smelted" if key == "iron_ingot" else "crafted"
                    if event.kind == expected and key in PROGRESS and key not in self.progress:
                        gain = min(PROGRESS[key], 18 - self.progress_total)
                        self.progress.add(key)
                        self.progress_total += gain
                        components["progress"] = components.get("progress", 0.) + gain
            meaning = (goal.kind.strip().lower(), goal.target.strip().lower())
            if success and meaning not in self.completed_goals and len(self.completed_goals) < 8:
                self.completed_goals.add(meaning)
                self.goal_total += .5
                components["goal"] = .5
        boundary = sum(value for kind, value in components.items() if kind != "time")
        terminal = dead or step.observation.remaining_ticks == 0 or (
            (goal_completed if self.pilot_signal else self.local_paid) if self.objective == "local" else self.diamond_paid)
        shaping = 0.
        if self.pilot_signal and goal.kind == "collect" and not step.invalid:
            shaping = self.gamma ** n * (0. if terminal else potential(step.observation, goal)) - potential(before, goal)
            components["approach"] = shaping
        # expm1 keeps long task budgets accurate when gamma is close to one.
        time_sum = rate * math.expm1(n * math.log(self.gamma)) / math.expm1(math.log(self.gamma))
        return Reward(total=sum(components.values()), discounted=time_sum + self.gamma ** (n - 1) * boundary + shaping,
                      discount=self.gamma ** n,
                      terminal=terminal, components=components)


def potential(observation: Observation, goal: Goal) -> float:
    source = {"cobblestone": "stone", "iron_ore": "iron_ore"}.get(goal.target, goal.target)
    distance = min((math.dist(observation.position, cell.position) for cell in observation.observed_map
                    if cell.visible and cell.block == source), default=32.)
    return -(.3 / 32) * min(distance, 32.)
