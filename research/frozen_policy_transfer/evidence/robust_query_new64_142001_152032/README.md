# Original preregistered 64 NEW-seed frozen PPO bounded-or-query holdout

Exactly eight byte-identical original source CI JSONs from real ManiSkill PhysX CPU run 37828426195, exact original source head d91081d30b3d56824e30dd9b3673b4f6db3b5f96.
Frozen prior to implementation: 9ebb39ef01c06869c60f923cdba5d1e4e5626b1d; prereg Git blob 70a16b787acb4380f9c7109c741a996453be1319.
Frozen original successful code db4fe4dd9d09aaff67c5dcf12213ad737162282d; method and certificate blobs checked by the original evaluation CI.
64 truly NEW distinct reset state IDs (Pull 142001-142032, Stack 152001-152032), never used in the original 16-state discovery; all original failures retained.
Original real simulator task success: bounded-or-selective-query 60/64 using 15 privileged decision target readbacks, mandatory single query 57/64 using 64, zero-readback bounded 47/64, optimistic 42/64.
These task-level results do NOT prove collision/force safety or real network packet loss; only simulated Panda controller arm target-hold at step 2, two released frozen PPOs, author-run outcomes.
The 76.5625 percent reduction is in controller privileged decision readback CALLS, not latency/energy. Paired selective vs mandatory task successes are 5:2; do not claim significance or external reproduction.
The original artifact byte-integrity provenance and destructive source checks are pinned by .github/workflows/archive-robust-query-new64-original.yml.
Verify: sha256sum -c SHA256SUMS; python -m research.audit_new64_bounded_query --input-dir THIS_DIRECTORY --output /tmp/query-verify.json.
