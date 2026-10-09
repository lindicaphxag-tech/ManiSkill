# For an independent robotics researcher: falsify the Panda/xArm public-ACK response result

This is a **scripted genuine ManiSkill native-control** replication artifact,
not an official ManiSkill upstream release, an accepted paper, a real robot
safety demonstration, or an independently validated frozen PPO task adapter.

**Original prospective report (author-run).** Eight uniquely preregistered
Panda and xArm6 Robotiq reset seeds, two explicit command amplitudes (0.6,
1.35), two simulated actual ACK delivery truths: 32 paired robot/scale/truth
conditions, six genuinely stepped native-control comparator worlds each.
Action-conditioned one-labelled-PAIR-per-target-robot response recovered the
controller's target **POSITION** within 0.1mm on 32/32 cases; the fixed-amplitude
prototype recovered 16/32 (16 abstentions), foreign robot unchanged model
0/32 (32 abstentions), blind optimistic/pessimistic 16/32 each (16 false
hidden-history guesses each), and an **unequal-information** trusted-target
read recovered 32/32 using 32 trusted state getter calls. ALL original
frozen source rows and SHA256 hashes are publicly available:

- Original registered protocol:
  [CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json](../CROSS_ROBOT_ACTION_SCALE_32_PRECOMMIT_V1.json)
- Exact author-run actual PhysX:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910505997
- Permanent raw unmodified PhysX sources, negative rows and independent audit:
  [cross_robot_action_scale_ood_new32_610001_620004](./evidence/cross_robot_action_scale_ood_new32_610001_620004/)
- Author-run permanent source archival GREEN:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37911099681

## Run with YOUR own robot, amplitude and fresh seed range

1. **Fork into your own GitHub account or laboratory organization**, enable
   Actions, then select **Outside-investigator selectable Panda xArm ACK
   action-amplitude native PhysX**. Pick `panda` or `xarm6_robotiq`,
   one of FOUR **unseen** action scales `0.45, 0.75, 1.2, 1.45`, and your
   own new `first_seed >=700001` that you have not already run.
2. Set `number_of_reset_seeds=4` (8 truth conditions and 48 separately
   executed real native PhysX comparator worlds) or use 1 for an integration
   smoke. The user-selected values are recorded before model execution.
   Repeat with the OTHER robot and different amplitude(s) when practical.
3. Download `external-investigator-chosen-real-cross-robot-physx-<run id>`.
   It contains the original full native PhysX per-episode JSON, complete
   per-arm successes, wrong history labels, decision-time privileged reads,
   refused commands, SHA256, untouched console and exact environment.
   The original method and calibration source Git blobs must match the
   source-published hashes. Never drop negative examples or silently retry
   until an ACK classifier looks better.
4. To reproduce locally instead of Actions, install the current ManiSkill
   environment and xArm6 URDF asset when needed and run:

```bash
python research/external_cross_robot_ack_reproduction.py \
  --robot xarm6_robotiq \
  --scale 0.75 \
  --first-seed 710001 \
  --count 4 \
  --output-dir outside_robot_reproduction
```

The source program **refuses** to use the old author reset seeds in the
700000+ new-seed interface, reject unknown controller/action amplitudes, and
preserves ALL six physical comparator source rows. The public/class
observation only receives achieved EE XYZ changes and the previously
calibrated class motion model. It does **not** read private target state
before decision. Privileged-target control gets exactly ONE such read;
all arm outcomes are scored AFTER the physical correction.

## What would falsify or limit the scientific argument?

A source record with any **wrong confident ACK guess** is important,
especially from the action-conditioned method. A source record where the
action-conditioned classifier refuses or physically fails to restore the
native commanded target is likewise a counterexample. Differences between
both robot types, across action-amplitude scales or randomly chosen seeds
must be published as-is, including if the action-conditioned model performs
no better than a cheap one-PAIR fixed action model.

**Scientific boundaries.** The labelled one-PAIR initial calibration is
TWO known delivery-truth experiment examples per target robot; it is NOT
label-free, passive, or costless. Achieving a native commanded-target
position tolerance is NOT accomplishing the official PickCube task, matching
the achieved EE trajectory, safe robot contact, maintaining the intended
SO(3) commanded orientation, or successful frozen cross-embodiment PPO/VLA
transfer. The script simulates delivered native commands and physically held
targets with a masked ACK, NOT real network packet loss/reordering.
Empirical response-envelope reliability outside tested gains is unknown.

**External recognition only counts if an unaffiliated lab actually runs
this in its own environment, publishes all source evidence, or if a
maintainer/reviewer independently accepts a contribution.** An author-run
fork smoke or author-owned merge is not external recognition.
