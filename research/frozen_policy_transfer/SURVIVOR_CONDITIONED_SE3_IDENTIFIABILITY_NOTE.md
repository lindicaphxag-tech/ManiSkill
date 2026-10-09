# Why a public XYZ observation may identify a *complete* SE(3) controller target

**Research-method note · 2026-10-09. This is elementary conditional inference, not a new observability theorem, not a formal robot-safety certificate, and not yet evidence of new PPO task success.**

## The real prior implementation's false-negative mechanism

Let `H={h_1,...,h_k}` be a complete, trusted list of possible native accumulated controller targets after two unknown action-delivery receipts. **Each** candidate is a FULL pose `h_i=(p_i,R_i)`, not a translation alone. The older zero-probe controller [original PhysX #37912591209](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912591209) considered public achieved XYZ `y`, pre-probe public achieved XYZ `x`, and the old, empirically estimated position-response model

```
r_i = min_{alpha in [0,1]} || y - x - alpha (p_i-x) ||_2 .
C = { i : r_i <= epsilon_task } .
```

Its accepted-history rule was simultaneously `|C|=1`, every nonwinning `r_j>epsilon_task+0.002m`, and all **original** candidate rotations `R_i` equal to 1e-5rad. The last condition defeats the **purpose of identity inference**: rotations of a hypothesis already excluded by a valid public measurement need not be equal to that of the surviving target. It was explicitly preregistered as a conservative hazard constraint, so changing it is a **new method, not a retrospective bugfix with unchanged protocol**.

The original **32/32** task/truth conditions had **zero** accepted public full-pose candidates under that rule, although a later source-hashed retrospective reanalysis found **12** histories satisfying the original positional singleton+2mm clearance requirement, with **12/12** matching the audit-only actual complete target. The latter 12 were visible before proposing this new rule and are **NOT prospective evidence**.

## Conditional full-pose survivor proposition (ordinary finite-set logic)

Assume:

1. The robot controller's relevant hidden state **is exhaustively represented** by the trusted finite set of complete goal poses `H` under a known native target-update chart, and the true pose lies in this set.
2. An independently valid model implies a public measurement `y` belongs to the uncertainty set `Y_i` for the true member `h_i`.
3. Exactly one member `h_j` has `y∈Y_j`, with the specified numerical and geometric margin.

Then the true index is `j`. The **entire** stored target pose is `h_j=(p_j,R_j)`, including its rotation—even if the other, rejected `R_i` disagree. Proof: the true index is in the compatible index set by (2), and (3) states this set is the singleton `{j}`. The true full pose is already paired to that index by (1). QED.

**What this proof does NOT establish:** assumption (2) on real hardware or outside the empirical calibration distribution; correct physical servo gains; orientation observation; task success after resynchronization; contact safety; an entire robot dynamical state reconstructed from the target pose; or general VLA embodiment transfer.

## Falsifiers that MUST be kept in the study

- **Equal translational targets with different rotations:** one public XYZ trajectory can be compatible with several target histories, so the method must query; the corresponding input is explicitly tested.
- **Wrong response model:** the actual true history may not belong to `C` at all. Separate native PhysX experiments already contain such empirical-envelope model exclusions. Confidently choosing a wrong index **must** be reported as a full-pose error even if the robot task happens to succeed.
- **Incorrect ACK-dependent target recurrence:** a missing candidate or unverified update law invalidates the finite-set premise. Query/refuse rather than assert identification.
- **Malformed quaternion, stale coordinate frame, non-native action chart:** refuse. Do not import a task-specific “rotational posterior” from a private target getter.
- **Near-boundary unique residual:** if a competing candidate lies within the PREDECLARED extra 2mm clearance, do not select a target without trusted readback.

## Independent fresh-seed prospective design

The separately frozen [new experiment protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/survivor-conditioned-so3-new32-20261009/research/SURVIVOR_CONDITIONED_SO3_NEW32_PRECOMMIT_V1.json) commits to **32 entirely new reset states**, unchanged external frozen PPOs, eight actually stepped native-controller policy arms, the same two actual unknown-ACK target holds at step t=2,3 and identical public achieved XYZ observation count. New source seeds are PullCube 860001–860016 and StackCube 870001–870016. The strong **task-aware fixed/readback policy** is a genuinely stepped comparator on each matching seed. The upper bound on accepted public full-pose labels is NOT built from historical outcome statistics; the hard gates require no wrong confident full-pose target, complete fault exposures, and no worse task success than the previously precommitted task-aware comparator.

[Eight new actual PhysX jobs and full independent original-source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37913956732). **Do not advertise positive results until all jobs and complete auditor have finished.** A failure under altered contacts or SO(3)-specific dynamics falsifies the practical empirical model and should be retained.

## Publication scope and related-work positioning

No claim of a novel mathematical observability theorem or novel generic robust optimizer. Related literature already covers active system identification, belief-state filtering and action-interface adaptation, including ActionShift and SPACE. The narrow potentially publishable contribution is **accountable control-state authorization**, where the system explicitly tracks which observable evidence was sufficient to select a native controller history and when it must use an expensive true-target getter. Fair comparisons must charge every extra public observation and private getter access, under the same frozen policy, native fault, task horizon and prospective seed population.

The right scientific result might be NEGATIVE. A genuine outside-lab rerun on their own seeds is still absent.
