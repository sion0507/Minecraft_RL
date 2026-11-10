"""Validated wire contracts; unknown fields never reach policy inputs or logs."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Count = Annotated[int, Field(ge=0)]
Positive = Annotated[int, Field(gt=0)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Surface(Contract):
    block: Identifier
    position: list[float] = Field(min_length=3, max_length=3)
    passable: bool = False
    support: bool = False
    hazard: bool = False
    visible: bool = True


class ObservedDrop(Contract):
    entity_id: int
    item: Identifier
    quantity: Positive
    position: list[float] = Field(min_length=3, max_length=3)


class FurnaceState(Contract):
    position: list[float] = Field(min_length=3, max_length=3)
    input_item: str | None
    input_count: Count
    fuel_item: str | None
    fuel_count: Count
    output_item: str | None
    output_count: Count
    last_observed_tick: Count


class Observation(Contract):
    episode_id: Identifier
    attempt_id: Identifier
    obs_id: Identifier
    active_ticks: Count
    objective_kind: Literal["local", "full"]
    remaining_ticks: Count
    position: list[float] = Field(min_length=3, max_length=3)
    velocity: list[float] = Field(min_length=3, max_length=3)
    health: float = Field(ge=0, le=20)
    oxygen: Count
    on_fire: bool
    on_ground: bool
    in_liquid: bool
    inventory: dict[Identifier, Count]
    tool: str | None
    tool_durability: Count | None
    observed_map: list[Surface]
    history: list[str]
    yaw: float = 0.0
    pitch: float = 0.0
    map_version: Count = 0
    visited: list[list[float]] = Field(default_factory=list)
    # Positions first observed passable this episode; observed_map carries air only near the bot (#44).
    discovered_open: Count = 0
    hidden_hazard_peek: Literal[False] = False
    drops: list[ObservedDrop] = Field(default_factory=list)
    furnaces: list[FurnaceState] = Field(default_factory=list)


GoalSource = Literal["fixed", "planner", "regenerated", "rule_recovery"]


class Goal(Contract):
    goal_id: Identifier
    kind: Literal["collect", "craft", "smelt", "descend", "explore", "escape", "mine_diamond"]
    target: Identifier
    quantity: Positive
    direction: Literal["north", "south", "east", "west"] | None = None
    preconditions: list[str] = Field(default_factory=list)  # what GoalRegistry checked when it adopted the goal
    active_budget_ticks: Positive = 3600  # replan after 3 active minutes at 20 ticks/s (PLAN §5.1)
    completion_rule_id: Identifier | None = None
    source: GoalSource = "fixed"


class PlannerConfig(Contract):
    """Explicitly scripted mock planner replies."""
    backend: Literal["scripted"]
    model: Identifier = "mock-scripted"
    version: Identifier = "fixture"
    outputs: list[str]


class LocalPlannerConfig(Contract):
    backend: Literal["local_7b"]
    model: Literal["Qwen/Qwen2.5-7B-Instruct"] = "Qwen/Qwen2.5-7B-Instruct"
    version: Literal["a09a35458c702b33eeacc393d103063234e8bc28"] = "a09a35458c702b33eeacc393d103063234e8bc28"
    checkpoint: str = "../checkpoints/qwen2.5-7b"
    max_new_tokens: Positive = Field(default=256, le=512)


class AstraPlannerConfig(Contract):
    backend: Literal["astra"]
    provider: Identifier
    model: Identifier
    version: Identifier
    endpoint: str  # chat/completions; actual provider/model support must be verified before approval
    supported_settings: dict[str, JsonValue] = Field(default_factory=dict)
    max_new_tokens: Positive = Field(default=256, le=512)
    timeout_seconds: float = Field(default=60.0, gt=0, le=180)
    approved: bool = False
    approval_reference: str | None = None
    max_calls: Positive
    max_usd: float = Field(gt=0)
    request_usd_ceiling: float = Field(gt=0)  # provider-verified upper bound INCLUDING reasoning and failed calls
    budget_file: str  # persistent across processes, episodes and regenerations
    rates_checked_on: str
    input_usd_per_million: float = Field(ge=0)
    output_usd_per_million: float = Field(ge=0)


PlannerSettings = Annotated[PlannerConfig | LocalPlannerConfig | AstraPlannerConfig, Field(discriminator="backend")]


class GoalOutcome(Contract):
    """GoalStats row: one adopted goal from its decision to its replan trigger or the episode end."""
    goal_id: Identifier
    source: GoalSource
    kind: str
    target: str
    start_tick: Count
    end_tick: Count
    planner_retries: Count  # regeneration requests before this goal was adopted
    macros: Count
    failures: Count
    failure_reasons: dict[str, Count]  # step reason of each failed step
    completed: bool
    end_reason: str
    direct: dict[str, Count]


class Candidate(Contract):
    candidate_id: Identifier
    action_kind: Literal[
        "move_observed", "mine_visible_cluster", "tunnel", "stair_down", "craft_batch",
        "furnace_load", "furnace_collect", "place_or_equip", "wait",
    ]
    params: dict[str, JsonValue]
    max_ticks: Positive = Field(le=400)
    stop_rule_id: Identifier
    source_obs_id: Identifier
    description: str


MAX_CANDIDATES = 16  # PLAN §2 (#38, was 8)
# Slots per kind before the cap; every other kind shares the last one (#38).
SLOTS = {"move_observed": 6, "tunnel": 5, "stair_down": 4, "other": 1}
assert sum(SLOTS.values()) == MAX_CANDIDATES


class CandidateSet(Contract):
    candidates: list[Candidate] = Field(max_length=MAX_CANDIDATES)
    mask: list[bool]
    generated: Count  # candidates before the cap
    truncated: dict[Identifier, Count] = Field(default_factory=dict)  # cut per action kind

    @model_validator(mode="after")
    def validate_set(self) -> Self:
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)) or len(ids) != len(self.mask):
            raise ValueError("duplicate candidates or mismatched mask")
        if self.generated != len(ids) + sum(self.truncated.values()):
            raise ValueError("generated count must equal kept plus truncated")
        return self


def allocate(found: list[Candidate]) -> CandidateSet:
    """The one cap every generator uses: each kind keeps its first `SLOTS`, free slots go to the cut candidates in
    generation order, and the kept candidates stay in generation order."""
    used: dict[str, int] = {}
    keep: list[bool] = []
    for candidate in found:
        kind = candidate.action_kind if candidate.action_kind in SLOTS else "other"
        keep.append(used.get(kind, 0) < SLOTS[kind])
        used[kind] = used.get(kind, 0) + 1
    free = MAX_CANDIDATES - sum(keep)
    for index, kept in enumerate(keep):
        if not kept and free > 0:
            keep[index], free = True, free - 1
    truncated: dict[str, int] = {}
    for candidate, kept in zip(found, keep):
        if not kept:
            truncated[candidate.action_kind] = truncated.get(candidate.action_kind, 0) + 1
    kept_candidates = [candidate for candidate, kept in zip(found, keep) if kept]
    return CandidateSet(candidates=kept_candidates, mask=[True] * len(kept_candidates), generated=len(found),
                        truncated=truncated)


class ErrorInfo(Contract):
    code: Literal[
        "backend_error", "protocol_error", "timeout", "permission_denied",
        "invalid_request", "invalid_config", "invalid_selection", "invalid_step",
        "planner_error", "planner_unavailable",
        "jev_error", "jev_unavailable", "budget_exceeded", "model_response_invalid",
    ]
    message: str
    retryable: bool = False


class SelectionResult(Contract):
    candidate_id: Identifier
    selector_mode: Literal["mock_fixed", "human", "forced_wait", "rule_deterministic", "sampling", "argmax", "native_choice",
                           "fallback"]
    probabilities: dict[Identifier, Annotated[float, Field(ge=0, le=1)]] | None
    latency_seconds: float = Field(ge=0)
    provider: str | None
    model: str | None
    usage: dict[str, Annotated[float, Field(ge=0)]] | None
    retries: Count = 0
    error: ErrorInfo | None = None
    fallback: bool = False
    logprob: float | None = None
    values: dict[Literal["local", "full"], float] | None = None
    actor_eligible: bool = False  # choice eligibility only; smoke episodes never collect PPO experience
    rule_version: str | None = None  # rule selector S only: fixed rules and their hash
    rule_hash: str | None = None
    rule_keys: dict[Identifier, list[float]] | None = None  # per candidate: the lexicographic key S compared


class Event(Contract):
    kind: Literal["acquired", "wait", "moved", "stopped", "mined", "equipped", "failed", "crafted", "placed", "furnace_loaded", "furnace_collected", "smelted",
                  "descended", "tunneled", "exposed", "safe_hold"]
    item: str | None = None
    quantity: Count = 0
    source: Literal["mock", "minecraft"]
    event_id: Identifier | None = None
    position: list[float] | None = Field(default=None, min_length=3, max_length=3)
    entity_id: int | None = None


class StepResult(Contract):
    observation: Observation
    actual_ticks: Count
    events: list[Event]
    terminated: bool
    truncated: bool
    invalid: bool
    reason: Identifier
    clock_mode: Literal["mock", "paused", "realtime", "unverified"]
    pause_verified: bool
    stable_boundary: bool
    wall_seconds: float = Field(ge=0)
    source_obs_id: Identifier | None = None
    map_version: Count = 0
    path: list[list[float]] = Field(default_factory=list)
    stop_evidence: list[str] = Field(default_factory=list)
    distance_moved: float = Field(default=0.0, ge=0)
    cancelled: bool = False

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if sum([self.terminated, self.truncated, self.invalid]) > 1:
            raise ValueError("terminal/truncation/invalid must be distinct")
        if self.pause_verified != (self.clock_mode == "paused"):
            raise ValueError("only verified pause may use paused clock mode")
        return self


class MacroEvidence(Contract):
    candidate_id: Identifier
    source_obs_id: Identifier
    map_version: Count
    events: list[Event]
    reason: Identifier
    actual_ticks: Positive
    wall_seconds: float = Field(ge=0)
    path: list[list[float]]
    stop_evidence: list[str]
    stable_boundary: bool
    distance_moved: float = Field(ge=0)
    cancelled: bool = False
    goal_id: Identifier | None = None
    goal_source: GoalSource | None = None


class EpisodeSummary(Contract):
    episode_id: Identifier
    attempt_id: Identifier
    backend: Literal["mock", "rpc"]
    task: Literal["smoke", "movement_smoke", "macros_smoke"] = "smoke"
    clock_mode: Literal["mock", "paused", "realtime", "unverified"]
    pause_verified: bool = False
    movement_steps: list[MacroEvidence] = Field(default_factory=list)
    macro_steps: list[MacroEvidence] = Field(default_factory=list)
    selection_requests: Count = 0
    cancelled_selections: Count = 0
    movement_completed: bool = False
    distance_moved: float = Field(default=0.0, ge=0)
    goal_completed: bool
    diamond_success: bool = False
    admin_verified: dict[str, Count] = Field(default_factory=dict)
    terminated: bool
    truncated: bool
    invalid: bool
    reason: str
    error: ErrorInfo | None
    active_ticks: Count
    wall_seconds: float
    decisions: Count
    actor_transitions: Count = 0
    reward_total: float
    reward_kind: Literal["smoke_acquisition_count", "local", "full"] = "smoke_acquisition_count"
    provided_inventory: dict[str, Count] = Field(default_factory=dict)
    direct_crafted: dict[str, Count] = Field(default_factory=dict)
    direct_smelted: dict[str, Count] = Field(default_factory=dict)
    direct_acquired: dict[str, Count] = Field(default_factory=dict)
    # Planner accounting (PLAN §5.1): each numerator keeps its own denominator.
    planner_model: str | None = None
    planner_version: str | None = None
    planner_initial_requests: Count = 0
    planner_initial_errors: Count = 0
    planner_regeneration_requests: Count = 0
    planner_regeneration_errors: Count = 0
    rule_recoveries: Count = 0
    goal_decisions: Count = 0
    progress_by_source: dict[str, dict[str, Count]] = Field(default_factory=dict)
    goal_outcomes: list[GoalOutcome] = Field(default_factory=list)


class RpcRequest(Contract):
    request_id: Identifier
    method: Literal["reset", "observe", "step", "prepare_world", "clock_trial", "certify_clock", "information_fixture",
                    "verification_log"]
    payload: dict[str, JsonValue]


class RpcResponse(Contract):
    request_id: Identifier
    result: dict[str, JsonValue] | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def exactly_one_outcome(self) -> Self:
        if (self.result is None) == (self.error is None):
            raise ValueError("response needs exactly one result/error")
        return self


class ModelConfig(Contract):
    checkpoint: str = "../checkpoints/nanojev"  # relative to the episode YAML
    mode: Literal["sampling", "argmax"] = "sampling"
    seed: int = Field(default=11, ge=0, lt=2**63)


class PPOConfig(Contract):
    choice_lr: float = Field(default=1e-4, gt=0)
    value_lr: float = Field(default=1e-4, gt=0)
    clip: float = Field(default=.2, gt=0, lt=1)
    gae_lambda: float = Field(default=.95, ge=0, le=1)
    entropy: float = Field(default=.01, ge=0)
    value_coefficient: float = Field(default=.5, gt=0)
    grad_norm: float = Field(default=.5, gt=0)
    rollout: Positive = 128
    minibatch: Positive = 32
    epochs: Positive = 4
    critic_only: bool = False

class JevConfig(Contract):
    """External Jev selector (T11 #12): the same settings for J and F; only F's planner differs."""
    model: str = "typesafe/jev-1.13"
    mode: Literal["native_choice", "sampling"] = "native_choice"  # sampling only after the distribution is verified
    seed: int = Field(default=11, ge=0, lt=2**63)
    cap_usd: float = Field(default=10.0, ge=0)  # the whole Jev cap: connection, diagnostics, J/F, failures (user 2026-11-10)
    reserve_usd: float = Field(default=0.0, ge=0)  # held back for planned slots (F included) this command does not run
    max_call_usd: float = Field(default=0.001, gt=0)  # held per request before sending; charged for unconfirmed requests
    ledger: str = "~/.local/share/mc-diamond/jev_ledger.jsonl"  # shared by every checkout; never in Git
    timeout_seconds: float = Field(default=60.0, gt=0, le=180)
    network_attempts: int = Field(default=3, ge=1, le=5)


class EpisodeConfig(Contract):
    backend: Literal["mock", "rpc"] = "mock"
    fixture: str | None = None
    command: list[str] | None = None
    rpc_timeout_seconds: float = Field(default=5.0, gt=0, le=180)
    max_decisions: Positive = 8
    wall_limit_seconds: float | None = Field(default=None, gt=0)
    goal: Goal  # the task; without a planner it is also the one fixed goal
    planner: PlannerSettings | None = None
    model: ModelConfig | None = None
    ppo: PPOConfig = Field(default_factory=PPOConfig)
    discovery_reward: float = Field(default=0., ge=0)  # pilot opt-in; PLAN §8.1 defaults are unchanged

    jev: JevConfig | None = None

    @model_validator(mode="after")
    def configured_backend(self) -> Self:
        if self.backend == "mock" and (not self.fixture or self.command is not None):
            raise ValueError("mock needs fixture only")
        if self.backend == "rpc" and (not self.command or self.fixture is not None):
            raise ValueError("rpc needs command only")
        return self
