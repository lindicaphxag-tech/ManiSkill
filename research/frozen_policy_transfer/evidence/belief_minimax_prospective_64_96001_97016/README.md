# 64 originally predeclared Panda PhysX unknown-ACK two-world cases

Eight original JSON files copied BYTE FOR BYTE from successful original source run 37825781536 (commit 157c216deda38707a7f719368852d91964883d59).
Prereg protocol frozen before runner at 495e76e5d95ca0c309449f544b9c61c727b4bd22; Git blob b5b2b03a45919d39aa37e38a20bf1ce2deb557a2.
Includes 32 unique task seeds, each tested in applied and neutral-held unknown ACK conditions, 64 total task×seed×fault records; do not claim 64 independent reset states.
Original success: zero-readback midpoint 43/64, optimistic 48/64, pessimistic 43/64; privileged one-readback 62/64; strict refusal 0/64.
Negative result intentionally preserved: geometrically centered belief does not outperform simple same-information no-readback strategies in pooled task outcome.
Evidence is contributor-run simulated controller target hold, not real network loss, cross-robot frozen policy transfer, independent replication or hardware safety.
Original source artifact checksums/digests and provenance are pinned by .github/workflows/archive-belief-minimax-64-original.yml.
Run: python -m research.audit_belief_minimax_64 --input-dir research/frozen_policy_transfer/evidence/belief_minimax_prospective_64_96001_97016 --output /tmp/minimax-check.json
