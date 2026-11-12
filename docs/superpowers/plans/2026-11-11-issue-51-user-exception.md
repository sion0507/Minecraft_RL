# #51 user-exception continuation

User-approved scope: preserve the original failed gate and mine_oak_log's missing bad-choice samples; reuse the completed information audit, initial10 and fixed96; run4096 training, post10 and initial-head restoration in the background. No PDF work until results, no commit/push/merge/closure.

- [x] RED: public CLI continuation reuses initial records, preserves failed gate, verifies fixed inputs/head/source/config/snapshot, schedules only ten new post slots; reject changed references, extra failed classes, missing reason and duplicate output.
- [x] Implement explicit paired reference/reason arguments and an exclusive user-exception output in the existing signal runner. Retain the ordinary gate and training loop unchanged.
- [x] Verify exact initial public hashes and recreated frozen features/metrics against the original96 states; preserve original artifacts byte-for-byte and save reference hashes/receipt. No initial evaluation or information audit call on continuation.
- [x] Full pytest/mypy and read-only independent review; fix material findings before real execution.
- [x] Launch pinned background train/post chain only; record exception vs original gate, original20 slots vs newpost10, source changes and model/snapshot/config identity. Completion notification once, no polling.
- [x] On completion audit failures/unrun/restoration/time/cost; update Korean documents and two local PDFs. Ask before further decisions or Git publishing/closure.
