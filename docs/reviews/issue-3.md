# Issue #3 review and verification — 2026-11-02

Base main `1de47b7`, working branch `ticket-3`. One independent read-only reviewer inspected the tracked diff and new bridge, pause extension, clock diagnostic and tests. The reviewer did not start the server or alter files. Review preceded the author's final fix pass; there was no second review.

## Important findings and resolution

1. Reset reused `obs-0`, allowing an earlier episode's candidate. Observation IDs now have a fresh UUID per reset. Actual C4 reset rejected the saved candidate and preserved active_ticks=0.
2. Python allowed only two seconds for shutdown, while the bridge could be waiting and Java needed saving time. SIGTERM now interrupts pending work, the owner uses a kernel flock rather than a stale PID lease, and Python allows 15 seconds. A public CLI regression failed with the two-second limit and passed with the fix. Actual server loss/reset verification released the lease.
3. A disconnected bot could return cached observations. End/error handlers now clear connection state; observe/step reject it. Actual termination of the owned Java child produced backend_error rather than cached observation.
4. Root directory symlinks bypassed snapshot hashing and could replace the mutable world with a link. Root/parent directory checks now precede copy/swap. The public CLI test failed before the fix and passes while preserving the original current-world marker.
5. Drop diagnostics compared timestamped console output. They now extract NBT through the same data parser as other state samples. All prescribed drop trials preserved identical NBT across actual delays.
6. An unsupported action on the final tick set both invalid and truncated. Truncation now applies only to supported execution. Actual unsupported execution verified one measured tick and exclusive invalid outcome; the full 36,000-tick boundary was not physically run.

## Verification

- Full pytest: 27 passed; strict mypy: 12 files passed, including the retained local reset self-check script.
- Public real verify-clock: 63 distinct prepared trials, delays 0/5/10 seconds and three repeats per scene, all passed; all raw before/after measurements identical. Wall time 459.35 seconds.
- Preserved failures: Carpet alone reduced Air 281→172 during a five-second frozen wait; first complete run correctly rejected one unprepared fire fixture (62/63). The final fire setup uses 25 real ticks to establish burning.
- Public real smoke: two decisions, 40 measured ticks, pause_verified=true, reward/actor experience zero, no diamond success.
- Actual C4 reset/state restoration, stale candidate rejection, one-tick failure, connection loss; G1–G4 fixed position/inventory/health/time initialization; C4 level.dat time/weather matched its snapshot.

The author's verification addresses the six findings. No separate Minor finding was deferred. Model/PPO/research evaluations, Microsoft authentication and public hosting remain outside T02 and were not exercised. The working tree is uncommitted; no merge-readiness claim covers those future features.

## PR #28 independent two-axis review — 2026-11-03

Pinned original range `1de47b7...29c962d`, then fix range `29c962d...21a63593992eb0b51630a1110c535ed83f85de51`. Separate read-only Standards and Spec agents inspected the full change and connected callers against current #1/#3 bodies/comments and repository rules. Neither reviewer ran Minecraft or claimed GitHub account approval.

### Standards

One P2: missing Fabric Loader/Mixin/intermediary/ASM/remapped runtime jars could preserve an old pause certificate after dependencies changed. Resolved by hashing entire `.fabric`, `libraries`, and `mods` trees plus launcher/game jars with the existing treeHash. A regression checks dependency changes, restoration and new mods. The existing drift fixture was also repaired to use prepared samples with an unchanged success control. Independent fix review: ready, no remaining blockers.

### Spec

No additional concrete blocker or scope creep found. Fixed C4/G1–G4 snapshots, assisted partial-task starts, reset, authority separation, actual wait/failure ticks and pause diagnostic match T02. Independent fix review: ready conditional on successful actual pause revalidation; that condition has now passed.

### Author verification after review fixes

Fresh full pytest 29 passed (9.23s), strict mypy 12 files passed, Node syntax and diff whitespace passed. New actual public verify-clock exited 0: 63/63 distinct prepared trials, before/after measurements exactly equal, position drift zero, all fall samples airborne. Raw `artifacts/issue-3/verify-clock-pr28.jsonl`. New certificate fingerprint `d9aeb6f565cea776a90a4be6912835e2a93c2553520cfb38395af67e231aca50`.

Actual public smoke after reset exited 0: two decisions, 40 measured ticks, 10.97 seconds, both steps pause_verified=true, zero actor transitions/reward, no diamond success. Raw `artifacts/issue-3/smoke-episode-pr28.jsonl`. This verifies reuse of the new certificate under the same runtime. No models/PPO, paid APIs, Microsoft authentication or public hosting were tested. PR review evidence is complete; merge/issue state at this document's preparation remains pending.
