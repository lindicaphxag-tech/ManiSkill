# Low-signal ACK probing: FIRST original 192 PhysX worlds (Panda and xArm6)

**Completed 10 October 2026. Author-operated genuine ManiSkill CPU PhysX. Source-frozen experiment; no independent outside-laboratory replay, learned PPO/VLA task success, hardware safety or official upstream adoption.**

## Design and source identity

Previous fixed zero and +0.15-X probes both identified all 32 heldout ACK fault-truth cases in a high-SNR study, so the new pre-outcome study attenuated the unknown t2 action to 0.08 of its prior magnitude.

- **Robots:** Panda and xArm6 Robotiq, native PickCube-v1 scripted actions
- **Old calibration population:** Panda 680001–680008, xArm6 690001–690008; 8 independent old resets per robot
- **Never-seen test population:** Panda 700001–700008, xArm6 710001–710008; 8 independent fresh resets per robot
- For each seed, **both genuine physical applied/held ACK truths** and **three truly physically executed probes** (zero, native +0.15 X, native +0.15 Y)
- **96 old calibration + 96 heldout real CPU PhysX worlds = 192 actual worlds**, but only **16 independent heldout robot/reset clusters**
- **Probe selection uses calibration data only**, choosing the nonzero X/Y probe with larger mean applied-versus-held public XYZ gap after empirical radius deductions; never sees test truth before decisions
- No private controller-target getter in the classification or t4 action decision; true target accessed only after physical target-correction dispatch for audit
- Same native step counts, X/Y same nominal 0.15 native action norm; zero has no extra commanded arm delta. No matched energy, force, contacts, object manipulation, or certified response model.

[First frozen complete physical run, all original shards and source audit green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37974061810); original first-run source git HEAD ea3e6572fda7f4097595c9333956fd3b227a6a4f, attempt 1. [SHA-locked byte-preserving permanent archive CI green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37975148527). Both results are executed on the author's GitHub infrastructure, not by an independent laboratory.

## Calibration and falsification

| Robot | Calibration-selected probe | Prior response-center distance | Distance minus two empirical response radii |
|---|---|---:|---:|
| Panda | Y | 2.973 mm | **−1.385 mm** |
| xArm6 | X | 3.268 mm | **−0.764 mm** |

Negative margin for both robots: calibration does NOT establish a uniform separation certificate for the two hidden histories. The same eight old resets were used to select probes and fit the response balls, so fitted radii are descriptive and **not valid distribution-free heldout uncertainty bounds**.

**All actually executed never-seen physically stepped heldout outcomes:**

| Correct ACK histories / 16 per robot and probe | zero | X (+0.15) | Y (+0.15) |
|---|---:|---:|---:|
| Panda | **16/16** | **16/16** | **16/16** |
| xArm6 | **16/16** | **16/16** | **16/16** |
| Combined heldout | **32/32** | **32/32** | **32/32** |
| Wrong confident histories | 0 | 0 | 0 |
| Refused classification | 0 | 0 | 0 |
| Actually executed t4 commanded-target XYZ correction within 0.0001m | 32/32 | 32/32 | 32/32 |

Physically measured response gaps (held vs applied histories), mean **millimeters**:

| Robot | zero | X | Y |
|---|---:|---:|---:|
| Panda | 2.964 | 2.996 | 2.962 |
| xArm6 | 3.232 | 3.268 | 3.242 |

Thus **calibration-chosen nonzero probing has no observed correct-decision benefit over the cheaper zero action** in either robot. Panda's chosen Y even reduced the average physical response gap slightly relative to zero, while xArm6's chosen X slightly increased it but still had no decision benefit. All comparisons preserve every fault outcome, including negative and abstention cases.

## Statistical units and epistemic vetoes

[Full original-source reviewer analysis and raw paired-seed ledger](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/evidence/low_signal_first192_20261010/REVIEWER_PAIRED_RESET_AUDIT.json) confirms **all 16 independent heldout seeds had exactly zero change in correctly classified truths** when changing from zero probe to the previously calibration-selected nonzero candidate. Exploratory whole-reset exact sign-flip p=1; robot-stratified grouped bootstrap 95% descriptive paired-gain interval [0,0]. This is **a small-cohort ceiling effect**, not proof of general equivalence.

Zero wrong confident labels across the **eight genuinely independent admitting test reset seeds of one robot** yields a **one-sided 95% upper bound of 31.234%** for any wrong authorization at the seed level, conditional on a strong exchangeability assumption. It does **NOT** demonstrate near-zero population error or robot safety. Two truth worlds per seed are not independent.

[Fail-closed split-conformal sample-size module](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/low-signal-probe-selection-20261010/research/probe_calibration_assurance.py) and its [six OS/Python CI validations](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37974609050) show: a conservative 95% Bonferroni joint non-exclusion rule for two ACK hypotheses requires at least **39 independent calibration residual groups AFTER separately freezing the predictor and probe selector** even to obtain a finite marginal threshold. Here there are eight old groups and probe selection reuses them; there is no defensible formal certificate.

No full policy episode successes, actuation work, force, collision, object contact, latency, real-world packet loss, real VLA transfer, pretrained PPO cross-robot policy, independent adoption or independently rerun physics were assessed.

## Reproduce the exact source without GPU or ManiSkill physics

[First-run complete public archive: six original JSONs, original console logs, git SHA, environment, recomputed aggregate, paired reviewer audit and 24-file SHA256 manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/evidence/low_signal_first192_20261010).

From repo root on this evidence branch:

- Run Python unit test discovery for tests/test_review_low_signal_probe_value.py
- Recompute source-only physical decision audit with module research.low_signal_probe_selection_physx, mode audit, source folder above, and an output JSON.
- Recompute per-reset reviewer comparison with module research.review_low_signal_probe_value and the same archive source folder.

The source files are immutable from the original first complete run. GitHub Actions pass is reproducible **author-controlled CI**, not outside-lab validation.

## Publication decision and next experimental gate

This is a physically real **negative marginal value-of-information experiment**: in the tested regime the zero native action already identifies all ACK truths, and selecting/dispatching X or Y did not improve classification. Even the attenuated 0.08 fault remains too easy to demonstrate information benefits; do not scan and cherry-pick seeds or noise to manufacture a win.

A worthwhile subsequent **new** method study should first develop an independently measured, genuine nonzero-error/abstention regime using *new development seeds*, then freeze a task-aware selector and error-model class prior to sufficient **disjoint** calibration and evaluation populations. Compare same-public-information zero/passive policies, equal-actuation-energy fixed probes, chosen action, and authoritative controller-target readback on true manipulation task completion, decision-time getters, measured actuation/time/energy and wrong-history risk; accept failure as evidence.

**Current L7->L8 assessment:** contributes auditable original causal evidence and falsification discipline. It does not constitute statistically convincing positive active adaptation, a flagship robotics upstream merge, independent research adoption or a main-conference acceptance.
