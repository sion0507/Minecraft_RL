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
