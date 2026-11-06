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
    hidden_hazard_peek: Literal[False] = False
    drops: list[ObservedDrop] = Field(default_factory=list)
    furnaces: list[FurnaceState] = Field(default_factory=list)


class Goal(Contract):
    goal_id: Identifier
    kind: Literal["collect", "craft", "smelt"]
    target: Identifier
    quantity: Positive
    source: Literal["fixed"] = "fixed"


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


class CandidateSet(Contract):
    candidates: list[Candidate] = Field(max_length=8)
    mask: list[bool]

    @model_validator(mode="after")
    def validate_set(self) -> Self:
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)) or len(ids) != len(self.mask):
            raise ValueError("duplicate candidates or mismatched mask")
        return self


class ErrorInfo(Contract):
    code: Literal[
        "backend_error", "protocol_error", "timeout", "permission_denied",
        "invalid_request", "invalid_config", "invalid_selection", "invalid_step",
    ]
    message: str
    retryable: bool = False


class SelectionResult(Contract):
    candidate_id: Identifier
    selector_mode: Literal["mock_fixed", "forced_wait", "sampling", "argmax", "native_choice", "fallback"]
    probabilities: dict[Identifier, Annotated[float, Field(ge=0, le=1)]] | None
    latency_seconds: float = Field(ge=0)
    provider: str | None
    model: str | None
    usage: dict[str, Annotated[float, Field(ge=0)]] | None
    retries: Count = 0
    error: ErrorInfo | None = None
    fallback: bool = False


class Event(Contract):
    kind: Literal["acquired", "wait", "moved", "stopped", "mined", "equipped", "failed", "crafted", "placed", "furnace_loaded", "furnace_collected", "smelted"]
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
    diamond_success: Literal[False] = False
    terminated: bool
    truncated: bool
    invalid: bool
    reason: str
    error: ErrorInfo | None
    active_ticks: Count
    wall_seconds: float
    decisions: Count
    actor_transitions: Literal[0] = 0
    reward_total: float
    reward_kind: Literal["smoke_acquisition_count"] = "smoke_acquisition_count"
    provided_inventory: dict[str, Count] = Field(default_factory=dict)
    direct_crafted: dict[str, Count] = Field(default_factory=dict)
    direct_smelted: dict[str, Count] = Field(default_factory=dict)
    direct_acquired: dict[str, Count] = Field(default_factory=dict)


class RpcRequest(Contract):
    request_id: Identifier
    method: Literal["reset", "observe", "step", "prepare_world", "clock_trial", "certify_clock", "information_fixture"]
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


class EpisodeConfig(Contract):
    backend: Literal["mock", "rpc"] = "mock"
    fixture: str | None = None
    command: list[str] | None = None
    rpc_timeout_seconds: float = Field(default=5.0, gt=0, le=180)
    max_decisions: Positive = 8
    goal: Goal

    @model_validator(mode="after")
    def configured_backend(self) -> Self:
        if self.backend == "mock" and (not self.fixture or self.command is not None):
            raise ValueError("mock needs fixture only")
        if self.backend == "rpc" and (not self.command or self.fixture is not None):
            raise ValueError("rpc needs command only")
        return self
