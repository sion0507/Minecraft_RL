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
