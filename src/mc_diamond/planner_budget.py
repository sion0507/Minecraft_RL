"""Conservative Astra reservations survive failures and restarts; refunds require billing reconciliation."""

import fcntl
import hashlib
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .rpc import EpisodeError
from .schema import AstraPlannerConfig, ErrorInfo


@contextmanager
def _ledger(config: AstraPlannerConfig, path: Path) -> Iterator[dict[str, Any]]:
    identity = config.model_dump(exclude={"budget_file"})
    signature = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            try:
                previous = json.loads(path.read_text())
                used = Decimal(previous["reserved_usd"])
                reported = Decimal(previous.get("reported_cost_usd", "0"))
                if (previous["signature"] != signature or type(previous["calls"]) is not int or previous["calls"] < 0
                        or not used.is_finite() or used < 0 or not reported.is_finite() or reported < 0
                        or type(previous.get("blocked", False)) is not bool):
                    raise ValueError("Invalid budget")
            except (ValueError, KeyError, TypeError, InvalidOperation):
                raise EpisodeError(ErrorInfo(code="permission_denied", message="Astra ledger invalid or changed; reconcile existing budget")) from None
        else:
            previous = {"signature": signature, "calls": 0, "reserved_usd": "0", "reported_cost_usd": "0", "blocked": False}
        yield previous
        pending = path.with_suffix(path.suffix + ".tmp")
        with pending.open("w") as handle:
            json.dump(previous, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def reserve(config: AstraPlannerConfig, path: Path) -> None:
    with _ledger(config, path) as state:
        total = Decimal(state["reserved_usd"]) + Decimal(str(config.request_usd_ceiling))
        if state.get("blocked") or state["calls"] >= config.max_calls or total > Decimal(str(config.max_usd)):
            raise EpisodeError(ErrorInfo(code="permission_denied", message="Astra budget exhausted or blocked; reconcile billing"))
        state.update(calls=state["calls"] + 1, reserved_usd=str(total))


def record_cost(config: AstraPlannerConfig, path: Path, cost: float) -> None:
    with _ledger(config, path) as state:
        total = Decimal(state.get("reported_cost_usd", "0")) + Decimal(str(cost))
        state.update(reported_cost_usd=str(total), blocked=state.get("blocked", False)
                     or cost > config.request_usd_ceiling or total > Decimal(str(config.max_usd)))
