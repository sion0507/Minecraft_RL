# Issue 15 wood pilot implementation plan

> **For agentic workers:** Use superpowers:executing-plans for inline implementation. The user explicitly requested `$implement` on the current branch.

**Goal:** Implement PLAN §7.1 and GitHub #15: fixed four-log NanoJev pilot, two learning rates, 30 evaluation slots, initial actor restoration.

**Architecture:** Reuse run_episode, NanoJevSelector, EpisodeLearner, snapshot reset and the shared server-error retry policy. Retain 128-decision rollouts across episode boundaries rather than updating partial episodes. Keep pilot artifacts separate from main training.

**Tech Stack:** Existing Python/uv/PyTorch and Mineflayer; no new dependencies.

**Spec:** GitHub #15 and #1 body/comments, PLAN §§6.1–6.2, 7.1, 10, 11.3. The user has authorized implementation of this fixed specification; routine design choices need no further approval.

## Global constraints

- Fixed collect oak_log quantity 4, empty G1 snapshot, 3,600 active ticks, no planner/API.
- Same initial actor/critics and training RNG for Choice LR 1e-4 and 3e-4; other PPO settings unchanged.
- 1,024 collected decisions and eight complete 128-decision updates per setting; no partial update on episode end.
- Initial 10 and post-setting 10 each: 30 planned slots, fixed shared seeds, at most one server-error retry, every attempt retained.
- Select by successes, successful-only mean active ticks when tied above zero, error count, default LR. Exclude structurally unusable settings; defer if none.
- Restore original public actor/critics on success and failure. No pilot experiences/checkpoints feed main training.
- A corrective run is explicit, one setting only, maximum once per campaign, 1,024 decisions and 20 slots; persist the reason and selected/default LR.
- Current branch main; no push/merge/issue closure authorized.

## Review focus

- Short successful episodes must not cause partial rollouts or extra updates.
- Failed/cancelled actions and all-zero success results must not bias setting selection or disappear.
- Retry must restore the same snapshot and RNG without training during evaluation.
- Numerical/backend failure must retain remaining planned slots and restore initial heads.
- Existing output and corrective reservation must prevent accidental reruns/overwrite.

### Task 1: Public pilot command and bounded orchestration

**Files:** new src/mc_diamond/wood_pilot.py and tests/test_wood_pilot.py; modify cli.py and learning.py; add configs/wood_pilot.yaml and configs/wood_pilot_mock.yaml plus mock fixture.

- [x] Write a public CLI test for fixed goal, same initial hashes/RNG, 30 slots, complete rollout updates and final restoration using the existing tiny model at the downloaded-model boundary.
- [x] Run the new test and capture RED.
- [x] Implement pilot orchestration with frozen settings, durable manifest/traces and shared execution; keep episode-flush behavior unchanged for smoke-ppo.
- [x] Verify the CLI test and typecheck src/tests.
- [x] Add selection/retry/failure/correction tests one vertical slice at a time; run the touched file regularly.

### Task 2: Actual diagnostics, review and delivery

**Files:** README.md, DECISIONS.md, PROGRESS.md, CONTEXT.md; docs/reviews/issue-15.md; local reports PDFs only.

- [ ] Run actual public NanoJev + Minecraft pilot if prerequisites permit; retain all failures and unrun slots, never substitute mock evidence for actual game.
- [x] Run the full suite once, strict mypy src/tests and diff checks.
- [x] Apply code-review with independent Standards/Spec agents against starting commit f48ccf117c6d4a3b12d67862d022f9bfd113f123; fix material findings and recheck affected tests.
- [ ] Record implementation decisions and separate actual/mock/unrun evidence; create two Korean PDFs in reports, verify fonts/extraction/all rendered pages.
- [ ] Commit to the current branch, verify status and provide commit/PDF links; no publishing or closing issues.
