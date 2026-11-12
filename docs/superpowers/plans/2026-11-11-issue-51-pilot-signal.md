# Issue 51 T14B implementation plan

> Execute inline with superpowers:executing-plans. The user approved #51 and its proposed values, prescribed E → A/B/C → report/approval → D, and requested background completion events. Do not add a design or implementation approval gate before their prescribed D gate.

**Goal:** Determine whether stronger pilot rewards move NanoJev's policy on fixed evaluation states; separately inspect fixed 7B subgoals.

**Architecture:** Keep the existing public episode/RPC/candidate/PPO paths and #49 pilot intact. Add a pilot-only opt-in for the fixed three-goal chain and rewards, and a T14B runner using existing attempt/evaluate/reset/head helpers. Extend PPO only to accept explicit MC targets; warmup and fixed-state diagnostics belong to the pilot.

**Tech stack:** Installed Python/Pydantic/PyTorch/pytest, existing Node/Mineflayer bridge. No dependencies or bridge changes planned.

**Spec:** GitHub #51 body/comments, #1 body/comments, PLAN §§4.2/5.1/6.1–6.2/7.1/8.1–8.2/10; DECISIONS 2026-11-11 #51 confirmed values.

## Constraints and review focus

- Preserve legacy defaults, existing #49 artifacts and public CLI; use `pilot-signal` with its own config/output.
- Rewards: direct acquisitions only, no duplicate completion +1, terminal next potential zero; potential difference is already a transition-discounted reward, never discounted a second time as a last-tick event.
- Chain transitions use the returned observation without reset and terminate local returns, while only the final task completion ends the game episode.
- MC targets require a completed return boundary and reliable adjacency; unfinished tails and cancelled/invalid boundaries must not become fabricated MC targets or actor experience.
- Fixed validation states come exclusively from initial evaluation; unique state/candidate records are saved. Exclude matching position/inventory states from the training split used by the auxiliary critic fit.
- Keep actor sampling RNG intact during diagnostics; cached features and eval mode permit repeated heads without re-encoding or policy sampling.
- Preserve 20 planned evaluation slots, bounded server retries, native failures, all costs and initial head restoration, including exceptions and early signal rejection.

### E — saved-state 7B inspection (first)

- [x] Read required specs/history; confirm parameters in DECISIONS before any execution.
- [x] Reuse/copy the existing local-only draft; preserve source traces and raw replies/observations/model events in a new directory.
- [x] Launch detached GPU-only job with one completion event; no intermediate polling.
- [x] On completion, validate every response and classify immediate feasibility; record tokens/latency/model/prompt hashes and failed examples. No game/API/training.

### A — reward and fixed chain

Files: `schema.py`, `rewards.py`, `episode.py`, `learning.py`; new focused `tests/test_signal_pilot.py`; new `configs/signal_pilot.yaml` (mock fixtures are generated inside tests; no unused shipping mock config).

- [x] Write and observe failing numeric tests for capped direct 1/N, default/full isolation, visible-only potential sign/telescoping/nearest-target disappearance, and terminal potential.
- [x] Implement opt-in rewards and fixed log3 → craft wooden_pickaxe1 → collect cobblestone3 chain in the public episode loop. Keep normal goal planning unchanged.
- [x] Prove same-state progression and return boundaries through public mock CLI; validate invalid config combinations.

### B — MC warmup

Files: `learning.py` explicit optional PPO targets; new `signal_pilot.py` pilot learner; tests in `test_signal_pilot.py`.

- [x] RED → GREEN tests for exact variable-duration MC returns, incomplete tails across rollouts and broken traces.
- [x] Implement cumulative completed-MC critic fitting, local output bias zero, 32 epochs/rollout, latest rollout post-fit EV≥0.3 or eight-rollout cap. Revert to ordinary GAE updates afterward. Preserve total32 updates and actor exclusion.
- [x] Record per-update EV/prediction/target means and cap/threshold reason; verify Choice unchanged during warmup and public initial heads restored afterward.

### C/F — fixed states, signal gate, runner and handoff

Files: new `signal_pilot.py`/`signal_diagnostics.py`, `cli.py`, configs/tests, README/PROGRESS/CONTEXT/DECISIONS.

- [x] RED → GREEN tests for goal-specific text-only classification, masking, uniqueness/split leakage, no-sample signal rejection and exact verdict thresholds.
- [x] Reuse #49 attempts/evaluation for initial10 → return signal gate → LR3e-4/4096 → post10; save every update's pilot-only heads and fixed-state metrics, including2048. Add first-selection distribution and first-divergence classification.
- [x] Add offline auxiliary critic fit (2000 optimizer steps, reports128/2000), disjoint saved-state split, restore live heads/RNG/modes. Handoff documents keep #49 LR choice separate from learning evidence and Jev cost estimates separate from actual C4 measurements.
- [x] Run full pytest, strict mypy, CLI mock validation and diff checks. Request independent code review; fix material findings and rerun affected checks.
- [x] Produce two Korean local-only PDFs; check text extraction, embedded fonts and every rendered page. Report implementation/E/mock/real/unrun state and ask for D approval.

### D — only after explicit user approval

- [ ] Background information audit (reuse clock certificate only if fingerprint remains valid), then one game pilot. Pin source/config/snapshot/model hashes and preserve stdout/stderr/status/one completion notification. No model polling.
- [ ] Audit results, denominator/failures/restoration/costs, update PDFs and ask for post-verdict decisions and any push/merge/closure. Do not make those decisions automatically.
