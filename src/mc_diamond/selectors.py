"""Common ActionSelector contract and the fixed smoke selector; rule selector S lives in `rule_selector`."""

import json
from collections.abc import Callable, Sequence

from .schema import Candidate, CandidateSet, Goal, Observation, SelectionResult

Selector = Callable[[Observation, Goal, CandidateSet, Sequence[str]], SelectionResult]


def result(candidate: Candidate, mode: str, **extra: object) -> SelectionResult:
    return SelectionResult.model_validate({"candidate_id": candidate.candidate_id, "selector_mode": mode,
        "probabilities": None, "latency_seconds": 0.0, "provider": None, "model": None, "usage": None, **extra})


def first_candidate(_observation: Observation, _goal: Goal, saved: CandidateSet, _failures: Sequence[str]) -> SelectionResult:
    return result(saved.candidates[0], "mock_fixed")


def signature(candidate: Candidate) -> str:
    """What makes two candidates of different decisions the same action: kind plus target or direction."""
    params = candidate.params
    path = params.get("path")
    target = (path[-1] if isinstance(path, list) and path else
              {key: params[key] for key in ("block", "blocks", "direction", "item", "position") if key in params})
    return json.dumps([candidate.action_kind, target], sort_keys=True)
