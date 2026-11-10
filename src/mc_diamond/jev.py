"""Existing Jev through OpenRouter's alpha decisions API (T11 #12, PLAN §6.3, §7.3, §11.1.1).

J and F share this selector, its settings, mapping, retries and fallback; F only swaps the planner. Every request,
including failures and retries, goes to one append-only ledger that holds the whole Jev cap.
"""

import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .episode import emit, run_episode
from .model_input import INSTRUCTIONS, choice_input
from .rpc import EpisodeError, RpcSession
from .schema import CandidateSet, EpisodeConfig, ErrorInfo, Goal, JevConfig, Observation, SelectionResult
from .selectors import result

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
KEY_ENDPOINT = "https://openrouter.ai/api/v1/key"
KEY_FILE = Path("~/.config/mc-diamond/jev.env").expanduser()
TRANSIENT = {0, 408, 429, 500, 502, 503, 524, 529}  # 0 = no HTTP answer (network error or timeout)
ACCESS = {401, 402, 403, 404}  # account, credit, permission or model availability: an external cause to record
SUM_TOLERANCE = 1e-3  # published probabilities are rounded decimals

Post = Callable[[str, dict[str, Any] | None], tuple[int, dict[str, Any]]]  # (url, body or None for GET) -> status, JSON


def api_key() -> str | None:
    if os.environ.get("JEV_API_KEY"):
        return os.environ["JEV_API_KEY"].strip()
    if KEY_FILE.exists():
        for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
            name, _, value = line.removeprefix("export ").partition("=")
            if name.strip() == "JEV_API_KEY" and value.strip():
                return value.strip().strip("'\"")
    return None


def http(key: str, timeout: float) -> Post:
    def post(url: str, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), method="GET" if body is None else "POST",
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as failure:
            try:
                return failure.code, json.loads(failure.read() or b"{}")
            except ValueError:
                return failure.code, {"error": {"message": "non-JSON error body"}}
        except (OSError, ValueError) as failure:  # URLError, timeout, reset, bad JSON
            return 0, {"error": {"message": f"{type(failure).__name__}: {failure}"}}
    return post


def scrub(value: Any, key: str | None) -> Any:
    """Original error text for the log, never the key."""
    text = json.dumps(value, ensure_ascii=False)
    return json.loads(text.replace(key, "<redacted>")) if key else value


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    """Append-only JSONL of every Jev request. Confirmed = the provider's usage.cost; any request without it is charged
    `max_call_usd` toward the cap, so unknown costs never let spending pass the cap."""

    def __init__(self, config: JevConfig) -> None:
        self.path = Path(config.ledger).expanduser()
        self.config = config

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def totals(self) -> dict[str, Any]:
        rows = self.entries()
        confirmed = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
        unconfirmed = len(rows) - len(confirmed)
        return {"requests": len(rows), "confirmed_usd": sum(confirmed), "unconfirmed_requests": unconfirmed,
                "charged_usd": sum(confirmed) + unconfirmed * self.config.max_call_usd,
                "cap_usd": self.config.cap_usd, "reserve_usd": self.config.reserve_usd}

    def check(self) -> None:
        totals = self.totals()
        if totals["charged_usd"] + self.config.max_call_usd > self.config.cap_usd - self.config.reserve_usd:
            raise EpisodeError(ErrorInfo(code="budget_exceeded", message=(
                f"Jev ledger {totals['charged_usd']:.6f} + next {self.config.max_call_usd} exceeds cap "
                f"{self.config.cap_usd} - reserve {self.config.reserve_usd}")))

    def record(self, row: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def request_body(model: str, state: str, criteria: dict[str, str]) -> dict[str, Any]:
    return {"model": model, "state": state,
            "questions": {"action": {"type": "choice", "instructions": INSTRUCTIONS, "criteria": criteria}}}


def distribution(answer: dict[str, Any], keys: Sequence[str]) -> dict[str, float] | None:
    """The full distribution over exactly the sent keys, or None: never built from a confidence or a partial map."""
    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict) or set(probabilities) != set(keys):
        return None
    values = probabilities.values()
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0 for v in values):
        return None
    return {k: float(v) for k, v in probabilities.items()} if abs(sum(values) - 1) <= SUM_TOLERANCE else None


class JevSelector:
    """Common ActionSelector for J and F. An invalid answer is re-asked once with the same body, then the fixed common
    fallback (first offered candidate) runs as a recorded model failure. Network errors retry with backoff up to
    `network_attempts` and then stop the episode; nothing silently falls back to NanoJev."""

    def __init__(self, config: JevConfig, post: Post, ledger: Ledger, *, key: str | None = None,
                 sleep: Callable[[float], None] = time.sleep, context: str = "smoke") -> None:
        self.config, self.post, self.ledger, self.key, self.sleep, self.context = config, post, ledger, key, sleep, context
        self.rng = random.Random(config.seed)
        self.answers: list[dict[str, Any]] = []  # validated answers for the access summary
        self.fallbacks = 0

    def call(self, body: dict[str, Any]) -> tuple[dict[str, Any], int]:
        for attempt in range(self.config.network_attempts):
            self.ledger.check()
            started = time.monotonic()
            status, data = self.post(ENDPOINT, body)
            usage: dict[str, Any] = data["usage"] if isinstance(data.get("usage"), dict) else {}
            cost = usage.get("cost")
            self.ledger.record({"time": now(), "context": self.context, "status": status, "model": data.get("model"),
                                "provider": data.get("provider"), "id": data.get("id"),
                                "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                                "cost_usd": cost if isinstance(cost, (int, float)) and status == 200 else None,
                                "latency_seconds": time.monotonic() - started,
                                "error": scrub(data["error"], self.key) if "error" in data else None})
            if status == 200 and "error" not in data:
                return data, attempt
            message = json.dumps(scrub(data.get("error"), self.key), ensure_ascii=False)[:500]
            if status in ACCESS:
                raise EpisodeError(ErrorInfo(code="jev_unavailable", message=f"HTTP {status}: {message}"))
            if status not in TRANSIENT:
                raise EpisodeError(ErrorInfo(code="jev_error", message=f"HTTP {status}: {message}"))
            if attempt + 1 < self.config.network_attempts:
                self.sleep(2.0 ** attempt)
        raise EpisodeError(ErrorInfo(code="jev_error", retryable=True,
                                     message=f"Jev transport failed {self.config.network_attempts} times: HTTP {status}: {message}"))

    def __call__(self, observation: Observation, goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
        encoded = choice_input(observation, goal, saved)
        criteria = encoded.payload["states"][0]["questions"]["action"]["criteria"]
        # The API has no external mask: masked keys are left out; a0… still name the saved index, never a new list.
        keys = {key: cid for (key, cid), allowed in zip(zip(criteria, encoded.candidate_ids), encoded.mask) if allowed}
        first = next(c for c, allowed in zip(saved.candidates, saved.mask) if allowed)
        if len(keys) == 1:  # nothing to choose: no paid request
            return result(first, "native_choice")
        body = request_body(self.config.model, encoded.payload["states"][0]["state"], {k: criteria[k] for k in keys})
        usage: dict[str, float] = {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0}
        problems: list[str] = []
        transport_retries = 0
        for _ask in (1, 2):
            data, retried = self.call(body)
            transport_retries += retried
            reported = data.get("usage") or {}
            usage["requests"] += 1
            for name in ("input_tokens", "output_tokens"):
                usage[name] += reported.get(name) or 0
            usage["cost_usd"] += reported.get("cost") or 0
            answer = (data.get("answers") or {}).get("action")
            if not isinstance(answer, dict) or answer.get("type") != "choice" or not isinstance(answer.get("choice"), str):
                problems.append(f"schema: {json.dumps(answer)[:200]}")
                continue
            if answer["choice"] not in keys:
                problems.append(f"outside_candidates: {answer['choice'][:40]}")
                continue
            probabilities = distribution(answer, list(keys))
            self.answers.append({"model": data.get("model"), "provider": data.get("provider"), "choice": answer["choice"],
                                 "confidence": answer.get("confidence"), "probabilities": answer.get("probabilities"),
                                 "full_distribution": probabilities is not None, "usage": reported})
            chosen, mode = answer["choice"], "native_choice"
            if self.config.mode == "sampling" and probabilities is not None:  # temperature 1 over the verified distribution
                chosen, mode = self.rng.choices(list(probabilities), weights=list(probabilities.values()))[0], "sampling"
            index = encoded.candidate_ids.index(keys[chosen])
            return result(saved.candidates[index], mode, provider=data.get("provider") or "openrouter",
                          model=data.get("model") or self.config.model, usage=usage, retries=len(problems) + transport_retries,
                          probabilities=None if probabilities is None else {
                              cid: probabilities.get(k, 0.0) for k, cid in zip(criteria, encoded.candidate_ids)},
                          logprob=None if probabilities is None or mode != "sampling" else math.log(probabilities[chosen]))
        self.fallbacks += 1
        return result(first, "fallback", fallback=True, provider="openrouter", model=self.config.model, usage=usage,
                      retries=1 + transport_retries,
                      error=ErrorInfo(code="model_response_invalid", message="; ".join(problems)))


def key_usage(post: Post) -> dict[str, Any] | None:
    """Account-side usage for this key (free GET), to cross-check the ledger; None when unavailable."""
    status, data = post(KEY_ENDPOINT, None)
    info = data.get("data") if status == 200 else None
    return {k: info.get(k) for k in ("usage", "limit", "limit_remaining", "is_free_tier")} if isinstance(info, dict) else None


UNVERIFIED_IF_UNAVAILABLE = ["access", "model_id", "response_mapping", "distribution", "usage_and_billing",
                             "Q2_B_vs_J", "Q3_J_vs_F", "Q4_B_vs_F"]


def smoke_jev(config: EpisodeConfig, config_path: Path, post: Post | None = None) -> int:
    """reset→observation→goal→candidates→actual Jev choice→execution→summary, plus the ledger and account usage.

    Exit 0: access verified with valid mapped answers. 1: external unavailability (recorded, J/F not run) or an
    invalid answer/fallback. 2: missing key or configuration error. The mock Minecraft backend is stated as such."""
    settings = config.jev or JevConfig()
    ledger, checked = Ledger(settings), now()
    key = api_key()
    if post is None:
        if key is None:
            emit("jev_summary", {"jev_verified": False, "status": "missing_key", "checked_at": checked,
                                 "error": f"JEV_API_KEY not set and not in {KEY_FILE}", "unverified": UNVERIFIED_IF_UNAVAILABLE})
            return 2
        post = http(key, settings.timeout_seconds)
    before = key_usage(post)
    selector = JevSelector(settings, post, ledger, key=key)
    command = config.command
    if config.backend == "mock":
        assert config.fixture is not None
        command = [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", str((config_path.parent / config.fixture).resolve())]
    assert command is not None
    episode_id, attempt_id = str(uuid4()), str(uuid4())
    spent_before = ledger.totals()
    with RpcSession(command, config.rpc_timeout_seconds) as session:
        summary = run_episode(config, session.policy(), lambda: session.reset(episode_id, attempt_id), episode_id, attempt_id,
                              macros=True, select=selector, verification=session.verification_log)
    after = key_usage(post)
    totals = ledger.totals()
    code = summary.error.code if summary.error else None
    fallbacks = selector.fallbacks
    status = ("unavailable" if code == "jev_unavailable" else "budget_exceeded" if code == "budget_exceeded"
              else "error" if code or summary.invalid else "fallback" if fallbacks or not selector.answers else "verified")
    emit("jev_summary", {
        "jev_verified": status == "verified", "status": status, "checked_at": checked, "endpoint": ENDPOINT,
        "requested_model": settings.model, "served_models": sorted({str(a["model"]) for a in selector.answers}),
        "providers": sorted({str(a["provider"]) for a in selector.answers}), "mode": settings.mode,
        "answers": selector.answers, "full_distributions": sum(a["full_distribution"] for a in selector.answers),
        "choice_is_argmax": sum(a["full_distribution"] and a["choice"] == max(a["probabilities"], key=a["probabilities"].get)
                                for a in selector.answers),
        "fallbacks": fallbacks, "environment_backend": config.backend, "episode_reason": summary.reason,
        "error": summary.error.model_dump(mode="json") if summary.error else None,
        "ledger_this_run_usd": totals["confirmed_usd"] - spent_before["confirmed_usd"], "ledger": totals,
        "ledger_path": str(ledger.path), "account_usage_before": before, "account_usage_after": after,
        "unverified": UNVERIFIED_IF_UNAVAILABLE if status == "unavailable" else []})
    return 0 if status == "verified" else 1
