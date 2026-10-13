# Strong-baseline falsification: source SO(3) recovery is NOT independently superior

**2026-10-13 — Original prospective negative result.** Both source-chosen recovery and a command-variant-specific, reset-relative learned SO(3) baseline attained the same frozen-target orientation metric in both independent CPU PhysX robot morphologies. This is a useful technical boundary, **not** a publication-ready novel VLA or physical safety claim.

## Source of truth and protected pre-outcome sequence

1. [Frozen two-variant SO(3) preregistration](../TWO_ACK_SO3_VS_RESET_STRONG_PREREG_20261013.json), Git blob `44f770ecabe87e894eb7a3fa94dde3e94a730734`. It precommitted source/strong reset comparator, two different root-aligned compound XYZ rotation action pairs, native Panda and xArm6, four hidden ACK histories, primary angular endpoint, fresh train/test resets, and the **>=3 of 4 heldout resets per robot with >=0.01 rad advantage over variant-aware reset centroid and lower risk than NO_ACTION** gate.
2. [Original real training PhysX execution](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335064480): 32 real native worlds per robot; 64 training conditions total, four training reset clusters per robot. Training data were never included as test outcomes.
3. [Frozen source-derived and reset-relative training register](../TWO_ACK_SO3_FROZEN_TRAIN_CENTROIDS_20261013.json), Git blob `e078ba7e735874751e4c20b3768bd8bc56924d66`, stored in GitHub before the fresh test. Both per-variant and pooled reset-centroid baselines generated from all training worlds.
4. [Original true-heldout real CPU PhysX execution](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335458988): both robot jobs SUCCESS, **160 registered physical simulation worlds per robot, 320 in total**; only **four genuinely new reset clusters per robot**, each repeated across 2 native command variants ×4 ACK true histories ×5 precommitted policies. No exclusions.
5. [Independent source and outcome audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335861213): SUCCESS, downloaded unchanged original artifacts, independently re-created every public classifier decision and matrix/risk result, checked that each comparison used the same public orientation before selecting actions, and numerically verified the SO(3) analytic reset-template identity on source policy worlds. An *earlier* audit attempt erroneously divided by 40 rather than the correct **32 conditions per robot per policy**, failed, and was corrected before the successful audit. This audit correction did not modify any original simulator outcomes.
6. [SO(3) analytic equivalence warning](TWO_ACK_SO3_ANALYTIC_RESET_EQUIVALENCE_20261013.md) was published **before inspecting the new heldout results**. It proves that comparing source predicted targets under the geodesic metric is exactly equivalent to an action-aware *analytic* reset-relative classifier in this fixed controller chart, by right-invariance of SO(3) geodesic distance. The empirical RESET_SO3_BY_VARIANT baseline approximates this with observed training prototypes and is a nonprivileged fair practical comparator.

## Actual test results

All reported values are means from the **same 32 real physically executed test worlds per robot and policy**, not independent-seed means over 32 independently drawn resets.

| Prospective policy | Panda correct ACK / 32 | xArm6 correct ACK / 32 | Panda mean achieved orientation error (rad) | xArm6 error (rad) |
|---|---:|---:|---:|---:|
| SOURCE_SO3_HYPOTHESES | 32 | 32 | 0.000240175 | 0.000236358 |
| **RESET_SO3_BY_VARIANT (strong)** | **32** | **32** | **0.000240175** | **0.000236358** |
| RESET_SO3_POOLED (weaker) | 24 | 24 | 0.004614601 | 0.004608074 |
| NO_ACTION | n/a | n/a | 0.012802640 | 0.012805392 |
| PRIVILEGED_ORACLE (not deployable) | 32 | 32 | 0.000240175 | 0.000236358 |

**Pre-registered originality gate: failed** for BOTH robots, **0/4** independent heldout reset clusters per morphology pass. The outcomes are consistent with the analytic invariance and show that the weaker pooled baseline was an invalid target for proving source-specific novelty.

For transparency, the official PickCube task-success indicator was **0/32 per policy and per robot** in these 320 conditions (from the original row-level logs). This is an orientation-target restoration assay, NOT actual cube-grasp completion. Do not promote the visible tracking-accuracy differences into real task success or robot safety improvement.

### Full paired independent-reset accounting

| Robot | Heldout seed | Source error (rad) | Variant-aware reset error (rad) | Pooled reset error (rad) | NO_ACTION error (rad) |
|---|---:|---:|---:|---:|---:|
| Panda | 5800201 | .000239780 | .000239780 | .004614641 | .012803441 |
| Panda | 5800202 | .000239861 | .000239861 | .004613548 | .012801884 |
| Panda | 5800203 | .000240298 | .000240298 | .004614996 | .012802685 |
| Panda | 5800204 | .000240762 | .000240762 | .004615219 | .012802551 |
| xArm6 | 5900201 | .000236162 | .000236162 | .004607885 | .012805184 |
| xArm6 | 5900202 | .000236121 | .000236121 | .004607946 | .012805278 |
| xArm6 | 5900203 | .000236323 | .000236323 | .004608075 | .012805467 |
| xArm6 | 5900204 | .000236825 | .000236825 | .004608391 | .012805638 |

## Implications

- Strong engineering: the same-source rotation inversion, multi-robot native controller integration and preregistered two-hidden-ACK history recovery are reproducible.
- **Not unique algorithmic superiority**: fully informed analytic reset centering is mathematically equivalent to source predicted rotations in this target-relative root-aligned SO(3) chart. Empirical variant-matched reset centroids already match the source method and oracle on all new conditions.
- **Not externally confirmed original science**: real PhysX worlds and independent auditing of author's public repository are not independent external lab replication, maintainer Merge, peer-reviewed journal acceptance or hardware safety certification.
- **Insufficient statistical generality**: 8 heldout reset clusters total, two fixed command variants, same simulator/task; the 320 physical conditions are factorial repeats, not 320 unrelated environments/patients.
- **No PickCube task success**: official zero success in this deliberately limited protocol.

## Required fundamentally different scientific contribution

Do **not** further rename relative coordinates as a new ToM/geometry method. Next hypotheses must introduce conditions where information and decision authority differ, not merely reference frame:

- unknown action/controller scale or chart subject to a **precommitted bounded latent contract uncertainty**, with a source-aware set of admissible policies and matched system-identification or Bayesian-filter baseline;
- externally auditable conditional observation model for actual public error signals, with calibrated abstention and query cost; declare all independent reset clusters and risk bounds honestly;
- meaningful actual PickCube or other task completion and collision/motion/contact/cost side effects on fresh tasks/seeds, including failure cases;
- retain **command-aware analytic reset SO(3)** and other strong model-based baselines, not only weak variant-blind centroids;
- only call it a research flagship after novel method, genuinely discriminating study, external expert review, and upstream/public adoption. No new Merge is implied by the present physical evidence.

**Final assessment:** The current mechanism survives code/physics correctness tests but **fails a credible novelty-discrimination test**. Preserving and publishing this negative result is the correct scientific outcome.
