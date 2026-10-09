# Readback-Singleton Contract: true native PhysX fresh-state validation

**Status:** completed original reproducibility / correctness experiment, 9 October 2026. **This is not an upstream ManiSkill defect attribution, no third-party lab endorsement, no robotic hardware safety guarantee, and no VLA/WAM evaluation.**

## Concrete mechanism

When two delivered-arm action acknowledgments are unknown, the private commanded target memory is represented as a finite set of hypotheses. A trustworthy private `target_pose` readback collapses this set to exactly ONE state. Any **cached flag indicating the old belief set had multiple states MUST then be invalidated** before choosing the next controller-native command chart. The original fixed-time comparator in the author's research experiment held on to a pre-readback `maybe_two=True`, mixing an unnecessary single-hypothesis minmax-action branch with the ordinarily expected one-target projection. The research branch fixes that flag only after explicit trusted controller readback and checks the singleton cardinality.

Original phase-query experiment with this confound identified: [completed 64-state native nine-world run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37911547899) and [all-state full original evidence audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912403644). The old fixed/phase discrepancy was specifically observed in original Stack seeds 830004 and 830020, and must not be attributed solely to information-value decision logic.

## Completely unseen confirmatory controller regression

- Pre-outcome source register: [exact 16-state frozen protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/resync-semantic-control-fresh16-20261009/research/READBACK_RESYNC_BELIEF_INVALIDATION_FRESH16_V1.json), PullCube seeds 920001–920008 and StackCube seeds 930001–930008.
- Exact correction plus per-step explicit singleton evidence: [nine-original-controller-world executable code](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/resync-semantic-control-fresh16-20261009/research/frozen_ppo_fixed_resync_corrected.py).
- Full real native PhysX [source execution #37912764218](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912764218): three jobs **SUCCESS** (one frozen source contract plus two task shards), **16 new native reset states × 9 separately stepped controller worlds = 144 real task-world executions**. Two ActionShift pretrained PPOs unchanged, no training or test-seed cherry-picking.
- On StackCube's **eight new original reset states**, the **corrected fixed-t4** and **phase-t4** strategies both made one authoritative target read at step 4; all eight per-seed official success flags and decision-time privileged-read counts matched. Both have **5/8 successful tasks**. The source test fails if any Stack state violates equality or fails the after-read singleton-state condition.
- PullCube 8 new reset states: phase success **8/8 with 5 private target reads**; separately stepped corrected fixed-t4 success **8/8 with 8 target reads**. This is a narrow source test, not statistical proof of noninferiority.
- Physical fault semantics: two **native simulated commanded-arm target holds**, at source steps 2 and 3, with gripper retained; this **does not** simulate real network ACK packet loss, true actuation disconnection, impacts, force/contact safety or collision constraints.

## Scientific outcome and limitations

This validates a concrete *epistemic state → controller command chart* contract. It also **weakens the earlier pure query-timing superiority attribution**: the old fixed baseline had a separate command-path confound. Strong future experiments must compare every new information-gain policy with a **corrected fixed-t4 controller**, not the flawed legacy variant.

Immediate high-return path: transfer this contract into a lightweight *real* pretrained VLA policy runtime (for example, Hugging Face LeRobot SmolVLA) while keeping action-unit normalization, command reference frames and readback privilege budgets explicit. Add a small **future outcome predictor** conditioned on a physically feasible action and each target-memory hypothesis. This will constitute WAM-inspired conditioning **only after implementing and validating genuine future-state predictions**; the current benchmark uses frozen PPO and cannot legitimately be presented as VLA or WAM research.

## Independent external acceptance

A reviewer outside the author's account must actually rerun the frozen code on independently selected new states, verify checkpoint/source hashes and all task outcomes, or integrate a minimal upstream regression before any outside-adoption claim. Author-owned GitHub Actions success is inspectable evidence, **not independent scientific replication or peer review**.
