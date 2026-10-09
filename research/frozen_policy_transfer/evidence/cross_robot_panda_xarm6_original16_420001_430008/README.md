# Cross-embodiment Panda / xArm6 stateful ACK ambiguity (mechanism, NOT policy transfer)

**Preregistered before any runner implementation**: commit baa0c1f577902e9c1f782c348feaac7a4b3448a9; protocol Git blob 4e10a144cdf5b2a3b5186629e93e1091d879cd64.

ORIGINAL first fully green real PhysX job 37899544825, source Git head 9e59c32043324180b671fa0ac5384917e1f95e3b. Exact 5-JSON original full source ZIP artifact 11600894857 digest sha256:034622fad55b50a8ef13ef1de5036c6a933f51aa43d113eb2bded31f06e4bf10. The five JSONs here are BYTE-FOR-BYTE original physical evidence from that run, not synthetic tests or later rerolled/edited results.

Robot Panda actual native PickCube-v1 target pose controller: new seeds 420001–420008, 8/8 distinct target-hypothesis executions after unknown ACK, maximum per-step after-physics target history reconstruction 1.431e-8 meters; actual end-effector position separation between applied-v-held physical worlds after common zero action probe: 37.61–38.51 mm.

Robot xArm6 Robotiq ORIGINAL distinct URDF/articulation: new seeds 430001–430008, 8/8 distinct target histories, maximum per-step reconstructed target error 1.431e-8 meters; achieved end-effector branch separation 41.55–41.70 mm after common zero-action probe. This robot uses DIFFERENT arm/gripper_active/gripper_passive action contract; no Panda robot substitution was permitted. The original source-complete full auditor checked 16/16 trial conditions across four PhysX shards.

The earlier jobs initially FAILED because xArm6 has different composite action keys, then because CI reused one literal artifact name across shards. Both issues remain publicly verifiable. Only robot-specific native action packing and CI artifact names changed; preregistered seeds, fault, probe and action-history estimator were not tuned to results. The fully sourced 37899544825 run is a technical data-collection rerun, NOT new independent confirmatory seeds.

Limits: THIS DOES NOT RUN A PRETRAINED PANDA PPO ON xArm6. These are controlled scripted native commands, not a new action-learning policy, active classifier or manipulation task-success result. The observer is told the two hypothetical actuator-delivery histories and correctly predicts each corresponding commanded target. It does NOT infer which hidden delivery actually occurred from a SINGLE online physical observation. Controller target state was accessed AFTER actual env.step exclusively for audit. No ROS/network packet loss, hardware/contact/collision safety, unknown controller model recovery or independent lab reproduction.

Verification (stdlib, original branch source script available on public main):
sha256sum -c SHA256SUMS
python -m research.audit_cross_robot_ack_physx --input-dir research/frozen_policy_transfer/evidence/cross_robot_panda_xarm6_original16_420001_430008 --output /tmp/verified_original16.json
