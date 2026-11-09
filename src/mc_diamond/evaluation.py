"""Planned evaluation slots (PLAN §9.3–9.5, §10): one result per planned slot, whatever happens to its attempts.

Only a server error (backend crash, RPC timeout or protocol fault) is retried, once, with the same snapshot and seed.
Behaviour failures, deaths, search failures and contract errors keep their first attempt. Unrun slots (budget stop,
unavailable reference group) stay in the denominator with success 0. External API internal randomness is never
restored, only the local seed.
"""

import hashlib
import math
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Annotated, Literal, Self, get_args

import yaml
from pydantic import Field, model_validator

from .episode import error_summary, run_episode
from .navigation import SAFE_BAND
from .rpc import EpisodeError, RpcSession
from .rule_selector import rule_select
from .schema import CandidateSet, Contract, EpisodeConfig, EpisodeSummary, Goal, Observation, SelectionResult
from .selectors import Selector, first_candidate

Group = Literal["A", "B", "J", "F", "S"]
Task = Literal["C4", "G4"]
Table = Literal["core_c4", "g4", "s"]
Mode = Literal["sampling", "argmax", "native_choice", "rule_deterministic"]
Outcome = Literal["success", "failure", "error", "not_run"]
GROUPS, TASKS, TABLES = set(get_args(Group)), set(get_args(Task)), get_args(Table)
SNAPSHOTS = Path(__file__).resolve().parents[2] / "worlds" / "snapshots"
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
    budget_usd: Annotated[float, Field(ge=0)] = 5.0  # the whole Jev cap: connection, diagnostics, J/F and failures
    jev_spent_usd: Annotated[float, Field(ge=0)] = 0.0  # already spent before this run (T11 keeps the ledger)
    mock_cost_per_decision_usd: Annotated[float, Field(ge=0)] = 0.0  # mock J/F only

    @model_validator(mode="after")
    def distinct_seeds(self) -> Self:
        if len(set(self.evaluation_seeds)) != 5 or len(set(self.g4_seeds)) != 3:
            raise ValueError("evaluation seeds must be distinct")
        return self


class Slot(Contract):
    slot_id: str
    table: Table
    group: Group
    task: Task
    mode: Mode
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
    outcome: Outcome
    success: bool
    retry: Literal["none", "used", "not_run_budget"]
    first_error: str | None
    not_run_reason: str | None


def schedule(config: EvaluationConfig) -> list[Slot]:
    """Every planned slot: core C4 22/14, G4 6, then the separate S slot (29/21 in total).

    Groups interleave by evaluation block (§9.3): block i runs A, B, J, F with the i-th shared seed.
    """
    runs = 5 if config.scale == "core" else 3

    def slot(table: Table, group: Group, task: Task, mode: Mode, index: int, seed: int) -> Slot:
        return Slot(slot_id=f"{table}-{group}-{mode}-{index}", table=table, group=group, task=task, mode=mode, seed=seed)

    main: list[tuple[Group, Mode]] = [("A", "sampling"), ("B", "sampling"), ("J", config.jev_mode), ("F", config.jev_mode)]
    pair: list[Group] = ["A", "B"]
    return ([slot("core_c4", group, "C4", mode, i, seed)
             for i, seed in enumerate(config.evaluation_seeds[:runs], 1) for group, mode in main]
            + [slot("core_c4", group, "C4", "argmax", 1, config.fixed_seed) for group in pair]
            + [slot("g4", group, "G4", "sampling", i, seed) for i, seed in enumerate(config.g4_seeds, 1) for group in pair]
            + [slot("s", "S", "C4", "rule_deterministic", 1, config.fixed_seed)])


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


class CountingSelector:
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


def attempt_selector(slot: Slot, config: EvaluationConfig, backend: str) -> CountingSelector:
    if slot.group == "S":
        return CountingSelector(rule_select, 0.0)
    if backend != "mock":
        raise ValueError("A/B (T10) and J/F (T11) selectors are not connected; only S runs on the actual backend")
    # ponytail: mock stand-ins for NanoJev and Jev; T10/T11 replace them with seeded sampling and API selectors.
    return CountingSelector(first_candidate, config.mock_cost_per_decision_usd if slot.group in PRICED else 0.0)


def bridge_command(episode: EpisodeConfig, path: Path) -> list[str]:
    if episode.backend == "mock":
        assert episode.fixture is not None
        return [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str((path.parent / episode.fixture).resolve())]
    assert episode.command is not None
    return episode.command


def reset_state(episode: EpisodeConfig, path: Path, task: Task) -> str:
    """The reset state each attempt starts from: the task snapshot file (or the mock fixture) and its hash.

    A missing file raises: no slot runs without a known reset state."""
    source = (path.parent / episode.fixture) if episode.fixture else SNAPSHOTS / task / "snapshot.json"
    return f"{source.name}:{hashlib.sha256(source.read_bytes()).hexdigest()}"


def run_attempt(slot: Slot, number: int, config: EvaluationConfig, episode: EpisodeConfig, path: Path,
                emit: Callable[[str, dict[str, object]], None]) -> tuple[Attempt, float]:
    attempt_id = f"{slot.slot_id}:{number}"
    tally = attempt_selector(slot, config, episode.backend)
    started = time.monotonic()
    try:
        with RpcSession(bridge_command(episode, path), episode.rpc_timeout_seconds) as session:
            summary = run_episode(episode, session.policy(), lambda: session.reset(slot.slot_id, attempt_id),
                                  slot.slot_id, attempt_id, macros=True, select=tally, verification=session.verification_log)
    except EpisodeError as failure:  # the backend never started: still an attempt with its error and time
        emit("error", failure.error.model_dump(mode="json"))
        summary = error_summary(episode, slot.slot_id, attempt_id, failure.error, time.monotonic() - started)
    success = summary.error is None and (summary.diamond_success if episode.goal.kind == "mine_diamond"
                                         else summary.goal_completed)  # non-diamond tasks are mock/smoke only
    return Attempt(attempt_id=attempt_id, number=number, seed=slot.seed, snapshot=reset_state(episode, path, slot.task),
                   reason=summary.reason, error_code=summary.error.code if summary.error else None, success=success,
                   highest_stage=highest_stage(summary), active_ticks=summary.active_ticks,
                   wall_seconds=summary.wall_seconds, selections=tally.selections,
                   planner_calls=summary.planner_initial_requests + summary.planner_regeneration_requests,
                   cost_usd=tally.spent), tally.spent


def evaluate(config: EvaluationConfig, path: Path, groups: set[str], tasks: set[str],
             emit: Callable[[str, dict[str, object]], None]) -> dict[str, object]:
    files = {task: path.parent / name for task, name in config.episodes.items()}
    episodes = {task: EpisodeConfig.model_validate(yaml.safe_load(file.read_text(encoding="utf-8"))) for task, file in files.items()}
    if not groups <= GROUPS or not tasks <= TASKS:
        raise ValueError(f"groups must be within {sorted(GROUPS)} and tasks within {sorted(TASKS)}")
    chosen = [slot for slot in schedule(config) if slot.group in groups and slot.task in tasks]
    for slot in chosen:  # refuse unconnected selectors and unknown reset states before any attempt
        attempt_selector(slot, config, episodes[slot.task].backend)
        reset_state(episodes[slot.task], files[slot.task], slot.task)
    spent = config.jev_spent_usd
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
        outcome: Outcome = (
            "not_run" if last is None else "success" if last.success else "error" if last.error_code else "failure")
        result = SlotResult(slot=slot, attempts=attempts, outcome=outcome, success=outcome == "success", retry=retry,
                            first_error=attempts[0].error_code if attempts else None,
                            not_run_reason=None if attempts else unavailable or "budget_stopped")
        results.append(result)
        emit("slot_result", result.model_dump(mode="json"))
    return summarize(results, spent, config, {episode.backend for episode in episodes.values()})


def summarize(results: list[SlotResult], spent: float, config: EvaluationConfig, backends: set[str]) -> dict[str, object]:
    tables: dict[str, dict[str, object]] = {}
    for table in TABLES:
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
            "api_cost_usd": sum(a.cost_usd for a in attempts),
            "cost_usd": None}  # 7B planning and GPU/PC cost are not measured yet (T19); never shown as 0 (§11.1.2)
    return summary


def main(path: Path, groups: str, task: str, emit: Callable[[str, dict[str, object]], None]) -> int:
    config = EvaluationConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    summary = evaluate(config, path, set(groups.split(",")), set(task.split(",")), emit)
    emit("evaluation_summary", summary)
    return 0

