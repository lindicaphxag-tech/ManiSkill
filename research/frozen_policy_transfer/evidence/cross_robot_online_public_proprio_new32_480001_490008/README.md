# Genuine native PhysX Panda+xArm6 ONLINE public-proprioception hidden ACK inference

Owner-executed robot control SEMANTICS and physical target POSITION correction result, NOT independently reproduced, peer-reviewed or robot safety validated.
Frozen before-outcome protocol commit 5cce4d517297b91fb5d7d51c60b0a95d81c7b3e1, Git blob 0cb66afc8a9c362ee764a83b7e558069ef6bd09c.
First complete successful 8-job original PhysX run 37905560363, exact code HEAD 309aa87e533a5f42c27fba17be721a3af965162c.
Original seven-JSON full source aggregate artifact 11603704402, original GitHub ZIP digest sha256:92d5a8948709084fb4db4c0d9800f7eaed03e17d6ace1479b51af463f440d375.
The 7 original unmodified JSONs contain 2 complete eight-seed×two-truth calibration sets, 4 full four-seed×two-truth×3 true-physical-controller blind test shards, and 1 independent audited full-32 result. SHA256SUMS pins each copied file.

Calibration: Panda 420001–420008, xArm6_robotiq 430001–430008 (already exposed earlier), each both applied and held. One robot-specific empirical public achieved XYZ response envelope per robot, margin precommitted 2mm. Not a physical safety bound.
BLIND new test: Panda 480001–480008 and actual xArm6_robotiq 490001–490008, each with applied and held true ACK-unknown deliveries. 16 unique robot reset seeds × two truths = 32 original independent controller-truth cases (not 32 independent trained policies).
Test each trial in three ACTUAL native PhysX controller worlds; probe t3 via native zero, classify based only on public achieved XYZ end-t3 minus end-t1; correct a desired commanded target POSITION with a physical native 6D action; audit private target only AFTER that correction, never for blind decision.
Panda empirical online observer 16/16 physically corrected commanded target positions to <=0.0001m, wrong confident 0/16, refuse 0/16; optimistic 8/16, pessimistic 8/16.
xArm6 Robotiq empirical online observer 16/16, wrong 0/16, refuse 0/16; optimistic 8/16, pessimistic 8/16.
Total public-only within-robot calibrated one-probe observer 32/32 target-POSITION correction, zero observed wrong confidential ACK labels; fixed guesses each 16/32. NOT PickCube task success, NOT achieved position servo/collision/force/contact safety or full SO(3) commanded target restoration.

First technical CI 37905151389 failed before real xArm6 trial because missing xArm6 URDF robot asset and interactive prompt. Fixed by existing source-proven xArm6 asset downloader, with no changes to frozen unseen seeds, action script, classifier radius or robot chart. The successful full 37905560363 is the first complete source. Duplicate push/PR test executions do not count as independent lab repetition.
Not generalized to different command amplitudes, timings, unknown controller semantics, cross-robot PPO/VLA policy transfer, actual network loss, external robot platforms or independently labelled researchers. Calibration learned truth-labelled earlier physical examples; zero observed error on 32 cases cannot imply population error zero.

Recalculate all 32 original truth cases from root: python -m research.audit_cross_robot_online_ack32 --input-dir research/frozen_policy_transfer/evidence/cross_robot_online_public_proprio_new32_480001_490008 --output /tmp/independent.json
Check source-byte integrity in archive: sha256sum -c SHA256SUMS
