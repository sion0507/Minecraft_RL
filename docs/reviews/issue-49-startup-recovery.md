# Issue49 startup recovery — independent Standards / Spec review

Base `af2016d97946d51953a2c36c521c88c4253c0b6c`; reviewed staged diff before commit. Sources: latest user approvals in CONTEXT/DECISIONS, issue49 body/comments, PLAN/AGENTS/GLOSSARY and the2026-11-11 recovery plan. Reviewers were read-only and did not run actual games/models/pilots.

## Standards

P2 found: old Java stdout/stderr could satisfy the replacement child's readiness listener. Waiting for `exit` does not guarantee pipes are drained; the line callback forwarded output to shared listeners and updated `initiallyFrozen` without checking the originating child.

Reproduced with the shipping Server.restore fixture: the killed child's delayed `Done` arrived after8ms and the new child's real `Done` after50ms. RED: restore returned while `freshReady` was false. Fixed by ignoring line callbacks unless `this.process === child`. GREEN: new Java must emit its own readiness; all startup/tick regression cases pass. No other actionable documented-standard violations or baseline smells.

## Spec

No findings. Verified bounded timeout output/jstack capture, owned-child kill/reap, same-snapshot restore retry once, second failure/non-timeout failure stopping, supplemental baseline/config/seed/model/input/head validation, initial evaluation/threshold reuse,10new post slots, original artifact/error preservation and nonzero status for a failed supplement even when oldLR3e-4 remains selectable.

## Verification

- Initial full suite296passed/137.51s.
- Stale-output finding RED→GREEN; startup/tick subset12passed/1.63s.
- Final full suite **297passed/137.04s**; strict `mypy .` **51source files** passed; Node syntax and diff whitespace checks passed.
- Standards1P2 fixed/0unresolved; Spec0findings. No deferred findings.
- Real Java diagnostic, new63-condition clock certificate, information audit/T04/T05 and the LR1e-4 supplement execute separately in the pinned background chain. They are not inferred from the mocked development checks.

## Final real verification and result audit — 2026-11-11

Pinned implementation `de4effb`; no executable source changed after launch. The supplemental chain completed with all six stages exit0: controlled real-Java/jstack startup recovery; new clock63/63; information audit; T04 macros/cancellation/reset; T05 furnace/production/boundaries/cancellation/reset; LR1e-4 supplement. T04 hazard/empty exit1 cases are expected negative checks, not failed stages. Production startup deadline remains45s; the controlled VM only shortened its first deadline to4s. The only new RPC timeout/retry records belong to that controlled diagnostic; no natural startup timeout/native crash/backend failure occurred during supplemental training/evaluation. Original intermittent startup root cause is unresolved.

Offline final audit independently checked all104 original/supplement attempt traces, cached candidates/IDs/order/masks, selection/execution counts, actor exclusions, reset state, progress/discovery diagnostics, completed valid MC targets/EV, registered ranking, pinned source/baseline/public weight hashes, identical initial heads and reported restoration/backbone invariance. Audit `artifacts/issue-49/supplement-20261111-102747/final-audit.json` passed. Original30slots remain20executed/10unrun; supplemental10all executed. LR1e-4 post2/10 vs LR3e-4 post4/10 selects0.0003 by registered success count; the original LR1e-4 backend_error remains in ranking errors. Both usable settings collected1024/eightupdates, first rollout critic-only; actor669/641. Original59unupdated transitions are retained/discarded. Main training/API0.

Development review findings remain Standards1P2 fixed/Spec0/unresolved0. This final evidence audit does not represent a newly delegated code review or a rerun of the historical297pytest/mypy51 checks. No source change justified repeating those checks. Existing oak-drop diagnostics remain in stderr. No added training, pilot, API, push, merge or issue closure. Korean PDFs and PROGRESS/CONTEXT record final selection and PC costs without claiming statistical superiority or GPU-hours.

## Publication verification — 2026-11-11

User explicitly approved push/merge/closing49 and local-main synchronization; follow-up issues are owned by another session and none are created here. Full development pytest297passed/138.05s, strict mypy51files, Node syntax and diff whitespace passed on the publication source tree. No executable source changes since the pinned real verification/audit. Preserved the pre-existing offline trace/probe notes, including separate Jev30-request cost, and clarified that registered LR selection is not evidence of PPO improvement. No game, training or paid API reruns for publication. Remote PR/issue/merge/final-local state are recorded in artifacts/issue-49/publication.json.
