"""Planned evaluation slots (PLAN §9.3–9.5, §10): one result per planned slot, whatever happens to its attempts.

Only a server error (backend crash, RPC timeout or protocol fault) is retried, once, with the same snapshot and seed.
Behaviour failures, deaths, search failures and contract errors keep their first attempt. Unrun slots (budget stop,
unavailable reference group) stay in the denominator with success 0. External API internal randomness is never
restored, only the local seed.
"""

import hashlib
import math
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Annotated, Literal, Self

import yaml
from pydantic import Field, model_validator

from .episode import run_episode
from .navigation import SAFE_BAND
from .rpc import EpisodeError, RpcSession
from .rule_selector import rule_select
from .schema import CandidateSet, Contract, EpisodeConfig, EpisodeSummary, Goal, Observation, SelectionResult
from .selectors import Selector, first_candidate

Group = Literal["A", "B", "J", "F", "S"]
Task = Literal["C4", "G4"]
SERVER_ERRORS = {"backend_error", "timeout", "protocol_error"}
PRICED = {"J", "F"}  # Jev API calls; Astra planner costs join in T09/T11
EXTERNAL_RNG_NOTE = "Local seeds are restored on retry; external API internal randomness is not."


class EvaluationConfig(Contract):
    episodes: dict[Task, str]  # EpisodeConfig paths, relative to this file
    scale: Literal["core", "reduced"] = "core"  # 28 or 20 core slots, fixed before any result (§9.3)
    evaluation_seeds: list[int] = Field(min_length=5, max_length=5)
    g4_seeds: list[int] = Field(min_length=3, max_length=3)
    fixed_seed: int = 0  # deterministic slots: A/B argmax and S
    jev_available: bool = True
    astra_available: bool = True
    jev_mode: Literal["native_choice", "sampling"] = "native_choice"  # fixed in T11 from the actual API
    budget_usd: Annotated[float, Field(ge=0)] = 5.0
    mock_cost_per_decision_usd: Annotated[float, Field(ge=0)] = 0.0  # mock J/F only

    @model_validator(mode="after")
    def distinct_seeds(self) -> Self:
        if len(set(self.evaluation_seeds)) != 5 or len(set(self.g4_seeds)) != 3:
            raise ValueError("evaluation seeds must be distinct")
        return self


class Slot(Contract):
    slot_id: str
    table: Literal["core_c4", "g4", "s"]
    group: Group
    task: Task
    mode: Literal["sampling", "argmax", "native_choice", "rule_deterministic"]
    seed: int


class Attempt(Contract):
    attempt_id: str
    number: int
    seed: int
    snapshot: str
    reason: str
    error_code: str | None
    success: bool
    highest_stage: int
    active_ticks: int
    wall_seconds: float
    selections: int
    planner_calls: int
    cost_usd: float


class SlotResult(Contract):
    slot: Slot
    attempts: list[Attempt]
    outcome: Literal["success", "failure", "error", "not_run"]
    success: bool
    retry: Literal["none", "used", "not_run_budget"]
    first_error: str | None
    not_run_reason: str | None


def schedule(config: EvaluationConfig) -> list[Slot]:
    """Every planned slot: core C4 22/14, G4 6, then the separate S slot (29/21 in total)."""
    runs = 5 if config.scale == "core" else 3
    slots: list[Slot] = []

    def add(table: Literal["core_c4", "g4", "s"], group: Group, task: Task,
            mode: Literal["sampling", "argmax", "native_choice", "rule_deterministic"], seeds: Sequence[int]) -> None:
        for index, seed in enumerate(seeds, 1):
            slots.append(Slot(slot_id=f"{table}-{group}-{mode}-{index}", table=table, group=group, task=task, mode=mode,
                              seed=seed))

    pair: tuple[Group, Group] = ("A", "B")
    for group in pair:
        add("core_c4", group, "C4", "sampling", config.evaluation_seeds[:runs])  # A and B share one seed list
        add("core_c4", group, "C4", "argmax", [config.fixed_seed])
    for group in ("J", "F"):
        add("core_c4", group, "C4", config.jev_mode, config.evaluation_seeds[:runs])
    for group in pair:
        add("g4", group, "G4", "sampling", config.g4_seeds)
    add("s", "S", "C4", "rule_deterministic", [config.fixed_seed])
    return slots


def highest_stage(summary: EpisodeSummary) -> int:
    """PLAN §10 stage from the episode's own direct events: 1 log, 2 stone pickaxe, 3 iron, 4 iron pickaxe,
    5 safe mining zone (a 20-tick safe hold at y=5-12), 6 diamond."""
    reached = [
        any(item.endswith("_log") and count for item, count in summary.direct_acquired.items()),
        summary.direct_crafted.get("stone_pickaxe", 0) > 0,
        summary.direct_acquired.get("iron_ore", 0) > 0,
        summary.direct_crafted.get("iron_pickaxe", 0) > 0,
        any(event.kind == "safe_hold" and event.quantity >= 20 and event.position is not None
            and SAFE_BAND[0] <= math.floor(event.position[1]) <= SAFE_BAND[1]
            for step in summary.macro_steps for event in step.events),
        summary.diamond_success,
    ]
    return max((stage for stage, ok in enumerate(reached, 1) if ok), default=0)


class Tally:
    """Wraps one attempt's selector: counts its selections and adds the (mock) per-decision API cost."""

    def __init__(self, select: Selector, cost: float) -> None:
        self.select, self.cost, self.selections, self.spent = select, cost, 0, 0.0

    def __call__(self, observation: Observation, goal: Goal, saved: CandidateSet, failures: Sequence[str]) -> SelectionResult:
        chosen = self.select(observation, goal, saved, failures)
        self.selections += 1
        if self.cost:
            self.spent += self.cost
            chosen = chosen.model_copy(update={"usage": {"cost_usd": self.cost}})
        return chosen


def selector(slot: Slot, config: EvaluationConfig, backend: str) -> Tally:
    if slot.group == "S":
        return Tally(rule_select, 0.0)
    if backend != "mock":
        raise ValueError("A/B (T10) and J/F (T11) selectors are not connected; only S runs on the actual backend")
    # ponytail: mock stand-ins for NanoJev and Jev; T10/T11 replace them with seeded sampling and API selectors.
    return Tally(first_candidate, config.mock_cost_per_decision_usd if slot.group in PRICED else 0.0)


def command(episode: EpisodeConfig, path: Path) -> list[str]:
    if episode.backend == "mock":
        assert episode.fixture is not None
        return [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str((path.parent / episode.fixture).resolve())]
    assert episode.command is not None
    return episode.command


def snapshot(episode: EpisodeConfig, path: Path, task: Task) -> str:
    """The reset state each attempt starts from: the task snapshot file, or the mock fixture."""
    source = (path.parent / episode.fixture) if episode.fixture else Path(f"worlds/snapshots/{task}/snapshot.json")
    return f"{source}:{hashlib.sha256(source.read_bytes()).hexdigest()}" if source.exists() else f"{source}:missing"


def run_attempt(slot: Slot, number: int, config: EvaluationConfig, episode: EpisodeConfig, path: Path,
                emit: Callable[[str, dict[str, object]], None]) -> tuple[Attempt, float]:
    attempt_id = f"{slot.slot_id}:{number}"
    tally = selector(slot, config, episode.backend)
    try:
        with RpcSession(command(episode, path), episode.rpc_timeout_seconds) as session:
            summary = run_episode(episode, session.policy(), lambda: session.reset(slot.slot_id, attempt_id),
                                  slot.slot_id, attempt_id, macros=True, select=tally,
                                  verification=lambda: session._call("verification_log", {}, admin=True))
    except EpisodeError as failure:  # the backend never started: still an attempt with its error
        emit("error", failure.error.model_dump(mode="json"))
        summary = EpisodeSummary(episode_id=slot.slot_id, attempt_id=attempt_id, backend=episode.backend,
                                 clock_mode="mock" if episode.backend == "mock" else "unverified", goal_completed=False,
                                 terminated=False, truncated=False, invalid=False, reason=failure.error.code,
                                 error=failure.error, active_ticks=0, wall_seconds=0.0, decisions=0, reward_total=0.0)
    success = summary.error is None and (summary.diamond_success if episode.goal.kind == "mine_diamond"
                                         else summary.goal_completed)  # non-diamond tasks are mock/smoke only
    return Attempt(attempt_id=attempt_id, number=number, seed=slot.seed, snapshot=snapshot(episode, path, slot.task),
                   reason=summary.reason, error_code=summary.error.code if summary.error else None, success=success,
                   highest_stage=highest_stage(summary), active_ticks=summary.active_ticks,
                   wall_seconds=summary.wall_seconds, selections=tally.selections,
                   planner_calls=summary.planner_initial_requests + summary.planner_regeneration_requests,
                   cost_usd=tally.spent), tally.spent


def evaluate(config: EvaluationConfig, path: Path, groups: set[str], tasks: set[str],
             emit: Callable[[str, dict[str, object]], None]) -> dict[str, object]:
    files = {task: path.parent / name for task, name in config.episodes.items()}
    episodes = {task: EpisodeConfig.model_validate(yaml.safe_load(file.read_text(encoding="utf-8"))) for task, file in files.items()}
    chosen = [slot for slot in schedule(config) if slot.group in groups and slot.task in tasks]
    for slot in chosen:
        selector(slot, config, episodes[slot.task].backend)  # refuse unconnected selectors before any attempt
    spent = 0.0
    results: list[SlotResult] = []
    for slot in chosen:
        episode = episodes[slot.task]
        attempts: list[Attempt] = []
        unavailable = ("jev_unavailable" if slot.group in PRICED and not config.jev_available
                       else "astra_unavailable" if slot.group == "F" and not config.astra_available else None)
        retry: Literal["none", "used", "not_run_budget"] = "none"
        for number in (1, 2):
            if unavailable:
                break
            if slot.group in PRICED and spent >= config.budget_usd:
                retry = "not_run_budget" if number == 2 else retry
                break
            attempt, cost = run_attempt(slot, number, config, episode, files[slot.task], emit)
            spent += cost
            attempts.append(attempt)
            if attempt.error_code not in SERVER_ERRORS:
                break
            retry = "used" if number == 1 else retry
        last = attempts[-1] if attempts else None
        outcome: Literal["success", "failure", "error", "not_run"] = (
            "not_run" if last is None else "success" if last.success else "error" if last.error_code else "failure")
        result = SlotResult(slot=slot, attempts=attempts, outcome=outcome, success=outcome == "success", retry=retry,
                            first_error=attempts[0].error_code if attempts else None,
                            not_run_reason=None if attempts else unavailable or "budget_stopped")
        results.append(result)
        emit("slot_result", result.model_dump(mode="json"))
    return summarize(results, spent, config, {episode.backend for episode in episodes.values()})


def summarize(results: list[SlotResult], spent: float, config: EvaluationConfig, backends: set[str]) -> dict[str, object]:
    tables: dict[str, dict[str, object]] = {}
    for table in ("core_c4", "g4", "s"):
        rows = [r for r in results if r.slot.table == table]
        if not rows:
            continue
        attempts = [a for r in rows for a in r.attempts]
        tables[table] = {"planned": len(rows), "successes": sum(r.success for r in rows),
                         "failures": sum(r.outcome == "failure" for r in rows),
                         "errors": sum(r.outcome == "error" for r in rows), "not_run": sum(r.outcome == "not_run" for r in rows),
                         "attempts": len(attempts), "retries_used": sum(r.retry == "used" for r in rows),
                         "retries_not_run": sum(r.retry == "not_run_budget" for r in rows),
                         "active_ticks": sum(a.active_ticks for a in attempts),
                         "wall_seconds": sum(a.wall_seconds for a in attempts), "cost_usd": sum(a.cost_usd for a in attempts)}
    summary: dict[str, object] = {"tables": tables, "spent_usd": spent, "budget_usd": config.budget_usd,
                                  "scale": config.scale, "mock": "mock" in backends, "note": EXTERNAL_RNG_NOTE}
    s = next((r for r in results if r.slot.table == "s"), None)
    if s is not None:
        attempts = s.attempts
        summary["s_diagnostic"] = {
            "success": f"{int(s.success)}/1", "outcome": s.outcome,
            "highest_stage": attempts[-1].highest_stage if attempts else 0,
            "active_ticks": sum(a.active_ticks for a in attempts), "wall_seconds": sum(a.wall_seconds for a in attempts),
            "selections": sum(a.selections for a in attempts), "planner_calls": sum(a.planner_calls for a in attempts),
            "failure_reason": None if s.success else (attempts[-1].reason if attempts else s.not_run_reason),
            "cost_usd": sum(a.cost_usd for a in attempts)}
    return summary


def main(path: Path, groups: str, task: str, emit: Callable[[str, dict[str, object]], None]) -> int:
    config = EvaluationConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    summary = evaluate(config, path, set(groups.split(",")), set(task.split(",")), emit)
    emit("evaluation_summary", summary)
    return 0

