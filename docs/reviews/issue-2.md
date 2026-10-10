# Issue #2 code review — 2026-10-09

Base `3183b52270b8025144b56d955768ca27332e225e`, branch `ticket-2`. Reviewed staged changes before the implementation commit. Two independent read-only reviewers; spec from GitHub #1/#2 and PLAN §§12–14.

## Standards

0 findings. Administrator reset and policy operations use separate channels; schemas reject unknown fields; remote error messages are sanitized; candidates, masks and IDs are logged; invalid experiences produce no actor transitions; mock rewards and diamond success are distinguished from actual research results.
RpcPolicy delegation serves the documented administrator/policy boundary. Deferred game/model/PPO work and npm audit warnings are recorded. No relevant ADR exists.

## Spec

2 P2 findings:

1. PLAN §12 requires the same request ID in result/error. Full request schema validation previously discarded valid IDs on malformed requests such as the role-spoof case. Fixed by independently validating the ID before the complete request; `test_policy_rpc_cannot_reset_or_spoof_administrator` now asserts `p2` on rejection. RED→GREEN confirmed.
2. Issue #2 requires replacing the backend while retaining the public execution flow and distinguishing actual/mock results. Event.source previously accepted only mock. Fixed by allowing minecraft provenance and retaining a strict mock-only fixture backend. `test_rpc_wire_can_carry_actual_backend_provenance` confirms the same CLI flow with scripted external replies. RED→GREEN confirmed; this test establishes wire compatibility, not physical-game behavior.

Final verification: full pytest 17 passed, strict mypy passed for 9 files. No unresolved review finding. Reviewers did not repeat network/GPU checks; author verification and the residual moderate npm audit warnings are recorded in PROGRESS.md.

## Final integration review — 2026-10-10

Compared current Issue #1/#2 (no comments) and `3183b52...5c26f95`, including the separately authorized research/installation documents. Independent Standards and Spec reviewers each found 0 material findings. No implementation changes were needed. Issue #2 delivers environment diagnostics and the reusable mock/public RPC flow; live game/model/PPO work remains in the existing follow-up tickets.

Fresh verification: `UV_CACHE_DIR=.cache/uv .tools/uv run --locked pytest` passed all 17 tests; the corresponding `mypy .` passed all 9 files. Public smoke emitted reset→observation→goal→candidates→selection→step→reward→summary, completed in 1 decision/20 ticks with null probabilities, diagnostic reward 1.0, actor transitions 0 and diamond success false. Actual doctor verified Python/Node/Java/GPU sums of 10 and Mineflayer 4.39.0 import on RTX 5070 Ti. Sandbox GPU access failed and was retried with actual-device access. `nvcc` is still missing, so doctor correctly exits 1 with ready=false; Minecraft/model verification remains false. The documented authentication dependency audit warnings were not re-audited or declared resolved.
