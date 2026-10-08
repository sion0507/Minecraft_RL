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


class Goal(Contract):
    goal_id: Identifier
    kind: Literal["collect"]
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
    kind: Literal["acquired", "wait"]
    item: str | None = None
    quantity: Count = 0
    source: Literal["mock", "minecraft"]


class StepResult(Contract):
    observation: Observation
    actual_ticks: Count
    events: list[Event]
    terminated: bool
    truncated: bool
    invalid: bool
    reason: Identifier
    clock_mode: Literal["mock", "paused", "realtime"]
    pause_verified: bool
    stable_boundary: bool
    wall_seconds: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if sum([self.terminated, self.truncated, self.invalid]) > 1:
            raise ValueError("terminal/truncation/invalid must be distinct")
        if self.clock_mode == "mock" and self.pause_verified:
            raise ValueError("mock cannot verify actual pause")
        return self


class EpisodeSummary(Contract):
    episode_id: Identifier
    attempt_id: Identifier
    backend: Literal["mock", "rpc"]
    task: Literal["smoke"] = "smoke"
    clock_mode: Literal["mock", "paused", "realtime"]
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


class RpcRequest(Contract):
    request_id: Identifier
    method: Literal["reset", "observe", "step"]
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
    rpc_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    max_decisions: Positive = 8
    goal: Goal

    @model_validator(mode="after")
    def configured_backend(self) -> Self:
        if self.backend == "mock" and (not self.fixture or self.command is not None):
            raise ValueError("mock needs fixture only")
        if self.backend == "rpc" and (not self.command or self.fixture is not None):
            raise ValueError("rpc needs command only")
        return self
