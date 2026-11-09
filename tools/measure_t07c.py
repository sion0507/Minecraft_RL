"""T07C (#38): replay recorded runs through the current candidate generators and measure the shared cap.

No game, model inference or API call. Each recorded observation and goal goes back through `policy_candidates`
(the episode's own generator path) and the counts per kind before and after `allocate` are summed. The recorded
saved sets (old 8 cap) are measured as they were logged. With --tokenizer, candidate texts are also counted in
tokens with the pinned NanoJev tokenizer (Qwen3-0.6B). Only `smoke-macros` logs: the logs do not record the mode,
and every decision is replayed as a macro decision.

Run from the repository root, e.g.
  uv run --with tokenizers==0.21.1 python tools/measure_t07c.py --tokenizer .cache/nanojev/tokenizer.json LOG...
"""

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

from mc_diamond.episode import policy_candidates
from mc_diamond.navigation import escape_candidates
from mc_diamond.schema import Goal, Observation

# NanoJev unified-games-v1 at 047b927b30882a1138fc504821b82ac145a4b81a: tokenizer/tokenizer.json (LFS sha256).
TOKENIZER_SHA256 = "be75606093db2094d7cd20f3c2f385c212750648bd6ea4fb2bf507a6a4c55506"
MICROBATCH_TOKENS, MAX_LENGTH = 32768, 8192  # NanoJev config.json
JEV_LONG_CONTEXT_BYTES = 32000  # OpenRouter Jev guide: text requests above this go to the long-context mode


def fields(candidate: dict[str, Any]) -> dict[str, Any]:
    """What a model would read of one candidate: its kind, parameters and description (the #38 measurement)."""
    return {key: candidate[key] for key in ("action_kind", "params", "description")}


def context(observation: Observation, goal: Goal, kinds: set[str]) -> str:
    """Which generator situation the decision was in, read from the goal and the generated kinds.

    Approximate: a drop pickup (one walk or wait) counts as `walk_only` or `production_or_single`.
    """
    if escape_candidates(observation) is not None:
        return "escape"
    if goal.kind == "descend":
        return "descend"
    if kinds & {"tunnel", "stair_down"}:
        return "ore_search"
    if "mine_visible_cluster" in kinds:
        return "exposed_resource"
    if kinds & {"craft_batch", "furnace_load", "furnace_collect", "place_or_equip", "wait"}:
        return "production_or_single"
    return "walk_only" if kinds else "none"


def decisions(path: Path) -> list[dict[str, Any]]:
    """Per decision: the recorded saved set and the replayed one; only one observation is held at a time."""
    rows: list[dict[str, Any]] = []
    observation: Observation | None = None
    goal: Goal | None = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("{"):
                continue
            record = json.loads(line)
            if record["type"] == "observation":
                observation, goal = Observation.model_validate(record["data"]), None
            elif record["type"] == "goal":
                goal = Goal.model_validate(record["data"])
            elif record["type"] == "candidates" and observation is not None and goal is not None:
                replayed = policy_candidates(observation, goal, macros=True)
                by_kind: dict[str, int] = dict(replayed.truncated)
                for candidate in replayed.candidates:
                    by_kind[candidate.action_kind] = by_kind.get(candidate.action_kind, 0) + 1
                rows.append({"context": context(observation, goal, set(by_kind)),
                             "recorded": record["data"]["candidates"], "by_kind": by_kind,
                             "truncated": replayed.truncated,
                             "kept": [candidate.model_dump(mode="json") for candidate in replayed.candidates]})
                observation = None
    return rows


def spread(values: list[int]) -> dict[str, float]:
    return {"mean": round(statistics.fmean(values), 1), "max": max(values)} if values else {"mean": 0.0, "max": 0}


def per_kind(rows: list[dict[str, Any]], key: str, total: Any = sum) -> dict[str, int]:
    return {kind: total(row[key].get(kind, 0) for row in rows)
            for kind in sorted({kind for row in rows for kind in row[key]})}


def situation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"decisions": len(rows), "generated_max": max(sum(row["by_kind"].values()) for row in rows),
            "over_16": sum(sum(row["by_kind"].values()) > 16 for row in rows),
            "max_by_kind": per_kind(rows, "by_kind", max), "truncated_by_kind": per_kind(rows, "truncated")}


def measure(rows: list[dict[str, Any]], tokens: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "decisions": len(rows),
        "generated_total": spread([sum(row["by_kind"].values()) for row in rows]),
        "over_8": sum(sum(row["by_kind"].values()) > 8 for row in rows),
        "over_16": sum(sum(row["by_kind"].values()) > 16 for row in rows),
        "generated_by_kind": per_kind(rows, "by_kind"),
        "max_by_kind": per_kind(rows, "by_kind", max),
        "truncated_by_kind": per_kind(rows, "truncated"),
        "by_context": {name: situation([row for row in rows if row["context"] == name])
                       for name in sorted({row["context"] for row in rows})},
    }
    for name, key in [("recorded_8", "recorded"), ("replayed_16", "kept")]:
        sets = [[fields(c) for c in row[key]] for row in rows]
        result[name] = {"count": spread([len(cs) for cs in sets]),
                        "candidate_bytes": spread([len(json.dumps(c).encode()) for cs in sets for c in cs]),
                        "set_bytes": spread([len(json.dumps(cs).encode()) for cs in sets])}
        if tokens is not None:
            result[name]["candidate_tokens"] = spread([len(tokens.encode(json.dumps(c)).ids) for cs in sets for c in cs])
            result[name]["set_tokens"] = spread([len(tokens.encode(json.dumps(cs)).ids) for cs in sets])
    return result


def budgets(result: dict[str, Any]) -> list[str]:
    """Markdown rows: what is left for the state summary (plus question) in each model's limit, at 8 and 16."""
    rows = ["|기준|8개(기록)|16개(재생성)|", "|---|---|---|"]
    path = [min(MAX_LENGTH, MICROBATCH_TOKENS // n) for n in (8, 16)]
    if "candidate_tokens" in result["recorded_8"]:
        biggest = [result[k]["candidate_tokens"]["max"] for k in ("recorded_8", "replayed_16")]
        rows.append(f"|NanoJev 경로당 상한(min(8192, 32768/N))|{path[0]}|{path[1]}|")
        rows.append("|후보 하나 토큰(평균/최대)|" + "|".join(
            f"{result[k]['candidate_tokens']['mean']}/{result[k]['candidate_tokens']['max']}" for k in ("recorded_8", "replayed_16")) + "|")
        rows.append(f"|경로당 상태+질문 몫(상한−최대 후보)|{path[0] - biggest[0]}|{path[1] - biggest[1]}|")
        rows.append("|후보 집합 토큰(평균/최대)|" + "|".join(
            f"{result[k]['set_tokens']['mean']}/{result[k]['set_tokens']['max']}" for k in ("recorded_8", "replayed_16")) + "|")
    rows.append("|후보 하나 바이트(평균/최대)|" + "|".join(
        f"{result[k]['candidate_bytes']['mean']}/{result[k]['candidate_bytes']['max']}" for k in ("recorded_8", "replayed_16")) + "|")
    rows.append("|후보 집합 바이트(평균/최대)|" + "|".join(
        f"{result[k]['set_bytes']['mean']}/{result[k]['set_bytes']['max']}" for k in ("recorded_8", "replayed_16")) + "|")
    rows.append("|Jev 32,000바이트에서 상태 몫(최대 집합 기준)|" + "|".join(
        str(JEV_LONG_CONTEXT_BYTES - result[k]["set_bytes"]["max"]) for k in ("recorded_8", "replayed_16")) + "|")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    parser.add_argument("--tokenizer", type=Path, help="NanoJev tokenizer.json (sha256 checked)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    tokens = None
    if args.tokenizer:
        if hashlib.sha256(args.tokenizer.read_bytes()).hexdigest() != TOKENIZER_SHA256:
            raise SystemExit("tokenizer.json is not the pinned NanoJev unified-games-v1 file")
        from tokenizers import Tokenizer  # type: ignore[import-not-found]  # measurement-only, not a project dependency
        tokens = Tokenizer.from_file(str(args.tokenizer))
    per_log: dict[str, Any] = {}
    every: list[dict[str, Any]] = []
    for path in args.logs:
        rows = decisions(path)
        every += rows
        per_log[str(path)] = measure(rows, tokens)
    overall = measure(every, tokens)
    report = {"logs": per_log, "all": overall, "budget_rows": budgets(overall)}
    print(json.dumps(report["all"], ensure_ascii=False, indent=2))
    print("\n".join(report["budget_rows"]))
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
