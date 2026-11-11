# Issue 49 startup recovery and failed-setting supplement

> **For agentic workers:** Use superpowers:executing-plans inline on the current branch, as already requested. The user authorized this follow-up after the original background run exits; do not ask for approval again.

**Goal:** Preserve timeout evidence, recover a reset-time startup timeout once, then rerun only the failed LR1e-4 setting and complete the registered comparison.

**Architecture:** Extend the existing Server lifecycle and existing pilot-wood correction flags. Startup failure cleanup belongs in start; the sole retry belongs in restore so snapshot validation/swap is repeated. Keep training and evaluation on the shared runner. Reuse the recorded initial ten-slot evaluation and its threshold; reserve a correction directory exclusively for the one supplemental setting.

**Tech Stack:** Existing Node child_process/fs and Python/PyTorch; jstack from installed JDK. No new dependency.

**Spec:** User approvals recorded in DECISIONS/CONTEXT on2026-11-11, GitHub #49/#1, PLAN §§4.2/7.1/8.1/10. Current original run: artifacts/issue-49/real-20261110-232814; source d8eb877. Follow-up starts from af2016d (documentation-only commits after that source).

## Global constraints

- Original pipeline is completed. Preserve its30slots, LR1e-4 failure59decisions/PPO0 and10unrun post slots, LR3e-4 results and every cost.
- Timeout remains45000ms. Keep at most64KiB recent Java output; jstack timeout5000ms/output≤1MiB and kill/reap wait≤5000ms. Diagnostic failure must not silently hang or orphan Java.
- Retry only a startup timeout during restore/reset, at most once. Kill/reap the owned child before another start, restore the same snapshot, stop after the second failure. No mid-episode retry or arbitrary backend/segfault retry.
- Use append-only administrator rpc-errors.log records with timestamp/PID/stage/output/dump status/elapsed duration. None of this reaches policy observations.
- Supplement only failed LR1e-4: public original heads/backbone, same config/snapshot/training/evaluation seeds, fresh optimizer,1024decisions/eightupdates/firstcritic-only. No continuation of the59discarded experiences and no LR3e-4 retraining.
- Reuse original initial10evaluation slots/registered time threshold; execute10new post-LR1e-4 slots only. Show original30-slot run and10-slot supplement separately. Compare new LR1e-4 with original LR3e-4 and retain the original failed LR1e-4 attempt in error/cost accounting. Record different code/fingerprints explicitly.
- New bridge code requires new real63-condition clock certification/information audit/related T04/T05 regressions before the supplement. Any failing preflight stops the chain and sends one completion event. No paid APIs/push/merge/issue closure.

## Review focus

- A failed/missing/timed-out jstack or an unwritable error log cannot leave Java running while a second instance starts.
- Readiness/error/exit/timer listeners must be removed on every start outcome; shutdown prevents retry.
- Snapshot corruption/early process exit/command or policy failures must never enter startup-timeout retry.
- Supplement cannot overwrite/repeat an existing correction, retry a usable setting, change config/seeds/snapshot, or borrow a learned actor.
- Original missing evaluation slots/errors remain visible; a failed supplement must return nonzero even if the old LR3e-4 remains selectable.

### Task1 — Startup diagnostics and one reset retry

- [x] Add a public Server.restore fixture with real temporary snapshots and simulated subprocess/timer boundaries. Observe RED for timeout evidence and one-retry recovery.
- [x] Implement bounded stdout/stderr capture, jstack diagnostic, owned-child SIGKILL/reap, startup listener cleanup and startup-timeout error code.
- [x] Retry restore once only on that code, preserving snapshot validation and logging all attempts. Test second timeout, normal start, early exit, failed dump and cleanup failure.

### Task2 — One failed LR1e-4 supplement

- [x] Add public CLI tests: failed baseline→one fresh LR1e-4 training/post-eval, reuseinitial/threshold, preserve original outputs/hashes, reject mismatched/usable/repeated requests; observe RED.
- [x] Reuse correction-reason/correction-lr flags with baseline manifest/summary/head validation,10-slot supplemental summary and explicit comparison provenance.
- [x] Run targeted files regularly, strict mypy . and the full pytest suite; review Standards/Spec and fix material findings before committing current branch.

Final development verification:297pytest/137.04s, mypy .51files. Standards P2 stale child Done output reproduced RED→GREEN with a current-child guard; Spec0/unresolved0. Real validation and supplement remain separate background tasks below.

### Task3 — Real verification, background supplement and final reporting

- [ ] Record original actual results and updated Korean report/code-guide PDFs; verify fonts/extraction/all pages without rerunning games for reports.
- [ ] Launch pinned background real verification→LR1e-4 supplement, using one completion callback and no model polling. Retain source/command hashes and all stderr/stdout.
- [ ] On the next completion event audit slot/attempt costs, registered selection, probabilities/entropy/MC EV/progress, restoration and backbone invariance; update records and two local PDFs.
