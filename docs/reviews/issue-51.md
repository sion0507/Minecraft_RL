# Issue 51 T14B — independent implementation review

Base: `f63ed87e48e70fa2c20cab38b2048577f5356e2b`; branch `feat/issue-51-pilot-signal`, uncommitted implementation. Review included the new/untracked pilot, diagnostics, config and tests. Spec: #51/#1 body/comments, PLAN, confirmed DECISIONS and 2026-11-11 implementation plan.

One fresh-context, read-only reviewer inspected the entire implementation and rechecked the MC batching and fault-path additions. Critical/Important confirmed runtime defects: **0**.

The reviewer requested a material test: fail after an actual SignalLearner update, then prove complete initial Choice/local critic/full critic restoration, error evidence and all20 planned slots. Added the fault scenario alongside the complete4096/32-update CLI scenario. Both passed in38.21s with tiny model and scripted initial evaluation traces; training/post-evaluation execute the public mock RPC/PPO path. This is development verification, not Minecraft or public-weight learning evidence.

Interpretation: validation states are fixed initial-evaluation inputs; position/inventory exclusions apply to the auxiliary critic's training split. They are not unvisited online-PPO states and do not establish held-out environment/generalization performance. README/handoff/report make this explicit.

Reviewer did not run tests, game/GPU/API calls or alter Git/files. Parent runs final pytest/mypy/diff checks and records exact results in PROGRESS. D remains subject to the user's separate approval; no push, merge or issue closure.

## User-exception continuation and memory retention

The user explicitly authorized4096 training with the original false gate/mine_oak_log missing bad samples preserved. Paired reference/reason CLI arguments, exclusive output and source/config/snapshot/initial-head/fixed-input checks were reviewed read-only. Important finding: reference heads were loaded before a fresh restoration checkpoint existed. Reproduced with a changed referenced critic (restored_initial=false), then fixed by saving fresh public heads before any reference load. Tests now reject changed contract/another failed signal/missing reason/mismatched heads, preserve the original files and verify complete restoration. Both normal/reference-fault continuation paths pass.

During a usage-limit pause an external Claude session already launched exception-20261111-184420; it ended with KeyboardInterrupt/exit130. The later memory patch strips observed maps/next_state from cumulative history only. Independent review found MC identity/trace/goal data, saved critic features/mask/context and position/inventory split preserved; actor PPO still uses full original rollout rows. Current rollout(~128 maps) and fixed validation96 retain maps, so actual peak RAM remains unmeasured. Removed the unsupported test-comment claim of a proven32GB OOM; the recorded termination is KeyboardInterrupt.

Latest full suite316 passed/217.19s, strictmypy54; reviewer did not rerun tests or invoke game/model/API. No unresolved Important/Critical findings. A clean retry is awaiting the user's explicit decision; interrupted experience/optimizer is not resumed or silently discarded from accounting.

## User-exception continuation (2026-11-11)

No sub-agent reviewer was used. A Claude Code session that did not author the continuation (written by the Codex session) read `signal_pilot.py` (reference validation, exclusive output, reseeding, restoration), the MC warm-up batching in `learning.py`, `signal_diagnostics.py` and the four-way CLI test read-only. Blocking defects: **0**. Full pytest 315 passed/210.24s, mypy 54 files. A GPU-only preflight with public weights reproduced the original 96 fixed-state metrics within 1e-6 and exercised the CUDA warm-up fit and auxiliary critic on synthetic transitions (not learning evidence). Residual risk by registered design: a server error during training stops training without retry and leaves post10 unrun.

**Missed defect (found by the real run, 2026-11-11 19:55 KST):** the review above and the first GPU preflight did not catch that `SignalLearner.history` retained every decision's full radius-32 observation (~30 MB each). The real run reached 24 GB RSS at 580/4096 decisions and was interrupted. Fixed by retaining map-free copies; regression test added; pytest 316 passed, mypy 54 files. The preflight reused shared state objects, so it could not have shown the growth; mock observations are too small to show it either.
