# Independent replication challenge — unknown robot ACKs, public motion, and false authority

**Open research artifact · 9 October 2026 · author-operated physical simulation, independent scientific replication NOT yet achieved**

## What external investigators should actually test

A robot's native controller may remember its last **commanded target**, distinct from achieved end-effector pose. If command execution acknowledgements are missing, several complete commanded-target histories are physically possible. An achieved-motion observer may identify one without reading the internal target—but prior real PhysX experiments show it can confidently select the WRONG history under model misspecification.

The scientific contribution is an experimentally grounded **tradeoff among public-model coverage, unique latent target identification, privileged target reads and official frozen PPO manipulation task completion**. It is **not** an already accepted, safe, policy-general VLA or new statistical theorem.

## Four original before-outcome, disjoint physical reset populations

| Actual ManiSkill PPO native-PhysX experiment | Real task outcomes | Genuine counterexample |
|:--|:--|:--|
| First unknown ACK physically mixed, second held; [source-audited run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314) | Public observer 58/64 tasks, **31** target reads; task-selected strong 58/64, **58** reads; zero-read always-held 43/64 | Second ACK truth fixed, so limited fault generalization |
| Both physical ACK execution truths mixed; [original failed run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917629944) and [successful **source-only** repair](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37918333602) | Public observer 58/64, **46** reads vs strong 57/64, 62 reads | **2/18** confident histories WRONG; original native StackCube HA resets 890005/890017 |
| Two consecutive equal-actuation known-delivered zero probe steps; [genuine 640-world audited experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989) | One public probe: 48/64, 41 reads; two: 48/64, 43 reads | **NEGATIVE:** extra 128 public observations, no task gain or demonstrated reliability gain |
| Prior OLD true-score response coverage calibration, followed by separate NEW64; [genuine 640-world audited experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924240294) | Old narrow: 58/64, 51 reads; calibrated: 58/64, 53 reads; both zero wrong confident | **NEW discovered distinction:** model true-history miscoverage **12/64 vs 6/64**, but 0 wrong-authority in both; model coverage and policy outcomes differ |

**Do NOT pool outcomes across these studies**: different seeds and some different physically executed neutral action time budgets. The zero-confidence-error counts in 64 episodes do not certify zero error on real hardware.

## Full primary sources rather than screenshots or report-only metrics

- [Original full-body-ACK source, including false positive histories 890005/890017](frozen_policy_transfer/evidence/four_joint_truths_first_physx64_880001_890032/) — failed production CI retained, independent source-only audit verifies all original true PhysX episodes.
- [Original independent new 640-world single/double physical probe experiment, 17 original JSONs and SHA256SUMS](frozen_policy_transfer/evidence/dual_probe_vs_single_physx_original64_900001_910032/) — honest negative result.
- [Original independent new 640-world true-history calibration experiment, 17 original JSONs and SHA256SUMS](frozen_policy_transfer/evidence/validity_first_prior32_new64_physx_original_940001_950032/).
- [Single-line original-response miscoverage auditor](audit_true_response_model_miscoverage_original640.py) requiring **exact Git blob ID** for the original audit JSON; [verification CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925393574).
- [Frozen response-model source and short explicit assumptions/proof](VALIDITY_FIRST_AUTHORITY_PROOF_AND_LIMITS.md).
- [Current paper manuscript v1.8: positive, false-confidence failure, two different negative prospective tests](frozen_policy_transfer/WHEN_DID_THE_COMMAND_EXECUTE_MANUSCRIPT_V1_8.md).

### Source-only independent review in a CPU Python environment

From the named branch root of this public GitHub repository, no ManiSkill installation or GPU is needed to verify the recorded physical outcomes' **source integrity**:

```bash
git checkout research/validity-first-conformal-ack-new64-20261009
cd research/frozen_policy_transfer/evidence/validity_first_prior32_new64_physx_original_940001_950032
sha256sum --check SHA256SUMS
cd ../../../..
python -m research.source_audit_prior_true_residual_calibration
python -m research.audit_true_response_model_miscoverage_original640
```

This verifies data and recomputes **true controller target residual coverage**, not new physical simulation and NOT external replication.

### A genuine independent physical-science replication requires more

For independent evaluation, an outside group should independently choose new precommitted reset seeds, execute the actual native ManiSkill/PhysX policy rollouts on their **own** GitHub fork or workstation, verify frozen PPO/checkpoint hashes, publish full original source including failures, and compare the same physically executed task trajectories among all declared controls. The existing [external native physical workflow](../.github/workflows/outside-dual-probe-replication.yml) is an illustrative source-locked reviewer entry; manual dispatch on GitHub requires the workflow on the investigator's fork's **default branch**, and installing the workflow does NOT count as a third-party reproduction.

The next scientifically decisive challenge would be to **induce a new independently specified controller/contact/observation regime** (e.g., different mechanical gain and load, or achieved pose from a real sensor), freeze it in advance, and ask whether a physical-response validity discriminator abstains in correctly identified model-invalid states *before* a wrong commanded-target history is acted upon. A task/physics matched ActionShift-style active probing baseline must be given the **same sensor, privileged target getter, actuation and wall-clock budgets**; the original ActionShift benchmark studies a different hidden action-ABI problem and is not already an implemented direct unknown-ACK baseline.

## What NOT to claim

No actual damaged/lost ROS command packets, no hardware physical safety or collision/force certificate, no generalization to arbitrary VLA embeddings, no statistically proven task noninferiority, no guaranteed future model-coverage under contact/dynamics OOD, no officially accepted upstream robotics feature, no independently reported third-party lab result, and no accepted top-tier paper. Those require new evidence, not rhetorical levels L8/L9.

**Outside reviewer response requested:** please report one independently reproduced task and residual table with your own fresh seed commitment, or an actual source-specific counterexample to our target-history belief assumptions. A missing ACK and an ambiguous controller target should not be silently treated as a known applied command.
