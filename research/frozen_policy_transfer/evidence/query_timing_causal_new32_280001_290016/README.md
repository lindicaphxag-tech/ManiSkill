# Original 32 task-reset physically executed query-time causal intervention

This is contributor-run genuine ManiSkill CPU PhysX simulation, not third-party independent replication or a hardware safety certificate.

Source method frozen preregistration: commit 8535cb64090e0eeaada36ee504786ef737f3a7b5, protocol Git blob bdf19f7c0f75cee1bd0b0f30a3316e7cd29e3acc.
Actual original full green 10-job CI: 37896219598, source commit 26f64c55c92dd8c65f99d17b8f26a9eaae475341.
Original all-9 JSON aggregate ZIP Actions artifact 11600591401, GitHub digest sha256:3a0536500c4e46a75091e026365c0db558c80a4bc725f6d4978549cce10794d3.

All 9 original JSONs were copied byte-for-byte from that original successful original run, and audited by an independent full-denominator stdlib checker. SHA256SUMS pins source bytes individually.

PullCube new seeds 280001–280016: no-query robust 15/16; adaptive target read on demand 16/16, 1 private target read; fixed query at t3 16/16 (16 reads), fixed at t5 16/16 (16), fixed at t6 15/16 (15); source native 16/16.
StackCube new seeds 290001–290016: no-query robust 9/16; adaptive 15/16 (6 reads); fixed t3 15/16 (16 reads), fixed t5 16/16 (16), fixed t6 12/16 (13); native source 14/16.
Pooled: adaptive 31/32 with 7 reads; fixed t3 31/32 with 32 reads; fixed t5 32/32 with 32 reads; fixed t6 27/32 with 28 reads; no-query robust 24/32 with 0 reads.

One earlier same-seed run 37895711069 successfully ran every PhysX experiment but accidentally used identical literal output artifact names for all jobs, so the external complete-source aggregator was incomplete. Only the workflow artifact name expression changed; model, physical method, threshold, seeds and fault were NOT tuned or changed. The successful 37896219598 run is a TECHNICAL COLLECTION RERUN, NOT additional independent new task-state population.

Queries read the controller PRIVATE commanded-target state and thus give EXTRA INFORMATION. Fixed t6 arms may refuse before the intended query. This is native zero-arm-delta simulated fault, NOT real packet loss, full SE(3) state identification, arbitrary robot-policy transfer or collision/contact safety. Exact official native PhysX binary task success is recorded in all eight original shard JSONs. Query timing result does not demonstrate universal optimality; fixed t5 gets one MORE success but consumes 32 vs 7 reads.

Recheck: sha256sum -c SHA256SUMS; python -m research.audit_query_time_causal_fresh32 --input-dir research/frozen_policy_transfer/evidence/query_timing_causal_new32_280001_290016 --output /tmp/recomputed.json.
