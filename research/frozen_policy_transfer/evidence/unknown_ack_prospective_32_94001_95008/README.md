# Original 32-state prospective lost-ACK controller experiment

Owner-operated ManiSkill PhysX native simulator outcomes, not an independent external replication or physical robot safety proof.
Original prereg protocol: 3ead83ecbb68eb6a405cdf768a42c617f649ddc4; Git blob 3a7273c1a02d13c19e93e618c74fc7068938c7e9.
Original exact-head run: 37824078238, commit 2ea6fabbd4e15ddd5623d51acd9f8874206fc003; archived 5-JSON source ZIP artifact 11570941907 with GitHub digest sha256:96fb570effcff0296df47676edfe78174c3e9c9cd09614b93c084b5fa9a1e3f3.
Four original eight-state task/fault cohorts; same frozen pretrained third-party PPOs; per-seed physical matched baselines in raw JSON.
PullCube ACK unknown but applied: optimistic 6/8, pessimistic 5/8, one trusted private target readback recovery 6/8, repeated privileged memory 6/8, fail-stop 0/8.
PullCube ACK unknown and intended arm command replaced by zero: optimistic 7/8, pessimistic 8/8, recovered 8/8, repeated privileged 8/8, fail-stop 0/8.
StackCube ACK unknown but applied: optimistic 8/8, pessimistic 0/8, recovered 8/8, privileged 8/8, stop 0/8.
StackCube ACK unknown and intended arm command replaced by zero: optimistic 2/8, pessimistic 8/8, recovered 8/8, privileged 8/8, stop 0/8.
Recovery is achieved via ONE PRIVILEGED target-state readback after ambiguous ACK, NOT via inference from achieved pose alone. The continuously privileged oracle is not equal-information control.
Each failed message was modeled by issuing a neutral target-native arm delta in an actual env.step; gripper still received its command. No real network loss or physical safety testing.
Bounded projection steps are NOT_EXACT; task flags do not measure collision or actuator safety.
All four original JSONs and original full audit are byte-for-byte copies, verified against the source Actions archive. Full source, failures and alternate baselines preserved. sha256sum -c SHA256SUMS; python -m research.audit_unknown_ack_physx --input-dir PATH --output /tmp/ack-audit.json.
