# Issue 49 pilot signal implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline. The user explicitly requested implementation and a commit on the current branch, with no actual pilot execution.

**Goal:** Implement #49's discovery reward, reduced pilot budget, common movement descriptions and registered selection/diagnostics.

**Architecture:** Reuse RewardLedger, EpisodeLearner, pilot-wood and the shipping bridge. Opt in through existing episode configuration; retain baseline rewards and task budgets by default. Derive diagnostics from saved public traces/features without extra game or backbone calls.

**Tech Stack:** Existing Python/uv/PyTorch, Node/Mineflayer; no new dependencies.

**Spec:** GitHub #49 and #1 body/comments; PLAN §§4.2, 5.2, 6.1–6.2, 7.1, 8.1, 10. User-approved amendment: endpoint-centred 3D Euclidean radius 16, currently visible non-air cells only, rarest eight kinds with name tie-break. The existing eight-block remembered-cell proposal is superseded.

## Global constraints

- No actual Minecraft/model pilot, training, API or information-audit execution in this task. Tiny-model scripted development checks are allowed.
- Discovery reward defaults to 0; pilot opts into +0.05 once per newly visible required kind, excluding reset-visible kinds. Full rewards unchanged.
- Pilot 1,800 ticks; G1 default 3,600 and all other default budgets unchanged. Only positive integer reductions are accepted.
- Movement description changes no IDs, paths, order or masks and uses only the supplied observation.
- Two LRs, 1,024 decisions/eight updates/first critic-only rollout, 30 planned evaluation slots remain. Actual run awaits user instruction.
- Time tie threshold is 2 × sample SD(initial ten charged slot ticks) × sqrt(2/10); failures cost 1,800. Compare success, time outside threshold, errors, LR.
- Enable faulthandler for future pilot; preserve failures and stop before rerunning after a native crash. This #49 campaign consumes the corrective allowance; no extra corrective campaign.
- Commit locally on current main; no push, merge or issue closure. Update #49's agreed description only.

## Review focus

- Reset-visible and previously seen kinds cannot pay again, including after goal changes or reappearance.
- Current visibility differs from remembered cells; endpoint radius includes vertical distance and deterministic ties.
- Budget options cannot increase a task budget, accept malformed numbers or change defaults.
- Zero variance, failed/unrun slots and unusable settings must not bias ranking; keep threshold in manifest/summary before training.
- Diagnostics must preserve candidate identity, RNG and costs; MC EV excludes incomplete or invalid trajectories rather than calling bootstrapped targets MC.

### Task 1: Discovery reward and shared movement descriptions

- [x] Add numerical RewardLedger tests (default/full, reset, first discovery, duplicate visibility, tools/source mapping) and observe RED.
- [x] Add opt-in reward config and learner wiring; verify affected tests and strict mypy.
- [x] Add public movement CLI tests for endpoint 16-block 3D radius, current visibility, rarest-eight order and unchanged candidate metadata; observe RED then implement.

### Task 2: Pilot budget, selection and diagnostics

- [x] Test shipping bridge budget defaults/reductions/rejection through its existing VM harness; implement --budget-ticks and update pilot configs/fixture/reset guard.
- [x] Test registered ranking with a known initial sample and boundary differences; implement and persist threshold.
- [x] Test fixed-state probabilities/entropy per update, complete-episode discounted MC EV, half summaries, discovery counts and pickaxe/stone ticks with tiny/scripted evidence.
- [x] Enable faulthandler; retain existing output reservation and disallow an extra corrective campaign for #49.

### Task 3: Review and delivery

- [x] Run strict mypy, full pytest once and diff checks; all physical/model effects remain unverified.
- [x] Apply code-review's independent Standards/Spec agents against starting commit a5ef033a8829e4771c219e86b5752e0eec673d77 and fix material findings.
- [x] Update README, DECISIONS, PROGRESS, CONTEXT and review evidence; commit current branch.
- [x] Generate Korean report/code-guide PDFs only in reports (intermediates /tmp); verify extraction, embedded font and every rendered page. Provide both links.

## Delivery evidence

Final pytest 286 passed / 120.46s, strict mypy src/tests40 files passed, Node syntax/diff checks passed. `mypy .` encounters the existing ignored issue15 loaded-source artifact's relative import. Standards P2 invalid-attempt MC aggregation reproduced RED32→GREEN0 and fixed; Spec0, unresolved0. Two Korean PDFs each have2 pages, embedded Korean fonts, extractable Hangul and all-page visual inspection. Final PDFs are regenerated after the local commit to pin its SHA. No actual pilot/clock/audit/model/API execution, push/merge/issue closure. The real acceptance criteria remain pending user execution authorization.
