# Issue 49 — Standards / Spec review

Base: `a5ef033a8829e4771c219e86b5752e0eec673d77`. Current main, staged changes reviewed before commit with `git diff --cached <base>`. Reviewers were independent read-only agents. Spec source: GitHub #49 body/comments plus the user's approved endpoint-centred 3D16/current-visibility amendment; PLAN, AGENTS, GLOSSARY and DECISIONS.

## Standards

**P2 — Invalid training attempts can contribute to MC critic diagnostics.** In `src/mc_diamond/wood_pilot.py`, training `mc_critic` aggregated every attempt whereas evaluation filtered `attempt.valid`. A terminal transition could exist before final verification or finish-time processing failed, so its MC samples could contaminate the training summary. This violated the documented completed-valid-episodes rule.

Resolution: reproduced through the public CLI with a tiny downloaded-model stand-in and a failure at the administrator verification boundary after a terminal transition. RED included 32 MC transitions from the invalid attempt; GREEN reports 0 transitions/null EV. Training aggregation now applies the same valid-attempt filter as evaluation. Test: `test_final_verification_failure_excludes_training_attempt_from_mc_ev`.

No other documented-standard violations or actionable baseline smells. Reviewer inspected connected reward/episode/learner wiring, candidate descriptions, bridge budget validation, pilot orchestration/diagnostics, tests/config/docs. No actual game/model/pilot commands.

## Spec

No findings. Reviewed reward defaults/reset/deduplication, positive budget reductions/defaults, 3D16 current-visible endpoint summaries and unchanged candidate metadata, pretraining threshold registration/selection, initialization/seeds/restoration/retries, update probes without sampling/backbone calls, and discounted MC/half/timing diagnostics.

Actual 63-condition clock certification, information audit, physical regressions, public-model pilot and 30 real evaluation slots remain explicitly unrun by user instruction; the issue remains incomplete pending those results.

## Final verification

- Initial complete suite: 285 passed / 118.69 seconds.
- Standards fix: RED→GREEN; final whole-suite **286 passed / 120.46 seconds**, strict mypy src/tests **40 files** passed. `mypy .` remains blocked by an existing ignored loaded-source artifact's relative import. Raw evidence: `artifacts/issue-49/`.
- Standards: 1 P2 fixed, 0 unresolved; Spec: 0 findings. No deferred findings.
