# Original full-SE3 survived controller memory under TWO unknown ACKs
Source original true official ManiSkill PhysX: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914343195
Actual source run Git SHA e67443e708db863cd46e36b52a19736ca32e54e8
Original prospective protocol git commit 1f68f3d788525e555b9170437161554a20138cde
Source frozen two external released PPOs, PullCube-v1 and StackCube-v1, 32 NEW
registered original reset seeds (860001..860016 and 870001..870016).
Native PD target command updates and TWO physical held native arm commands
at steps 2 and 3; both ACKs unknown to policy adapter. Actual seven
comparator arms and the NEW public full-target history arm were independently
simulated, 8 controller worlds per state, 256 actual PhysX worlds.
8 original four-seed PhysX JSON files, their 8 original source audit JSONs,
and the original complete independent audit JSON have been COPIED BYTE-UNCHANGED.
All 17 files protected by the SHA256SUMS manifest.

THE AUDITED RESULT:
- Public full-target history unique from public achieved XYZ in 10/32 states,
  with zero observed wrong confident full-pose labels.
- NEW fullpose survivor OR true target read: 28/32 official task successes,
  22 actual privileged controller-target decision reads.
- Strong TASK-IDENTITY prechosen selective PullCube / fixed StackCube genuine
  physical comparator: 28/32 task successes, 27 privileged reads.
- Fixed t4 actual target read: 28/32 successes, 32 reads.
- EXACT paired task outcomes against task-aware method: both 28 successes,
  both 4 failures, 0 independent method-only wins.
- 32/32 NEW public-controller worlds have both actual physical t2/t3 faults.

Original first partial-source run 37913956732 had a downstream, AUDIT-ONLY
Python NameError. Its single-variable repair is disclosed in
research/SURVIVOR_FULLPOSE_FIRST_RUN_SOURCE_AMENDMENT.md;
the successful full original run above uses the same original
preregistration, thresholds, full source population and frozen PPOs.
An entirely different cohort remains necessary for independent confirmation.

IMPORTANT NONCLAIMS: Empirical public motion dynamics were not certified
against arbitrary contact, gain shift, noise or different robots. This is NOT
a novel mathematical SO(3) theorem, universal robot/force/collision safety,
trained VLA policy result, network packet loss, official ManiSkill upstream
acceptance, peer-reviewed publication or independently executed outside lab.
