# Minimal execution receipts for uncertain robot action acknowledgments

**2026-10-13 • Original research software prototype + source-faithful native PhysX tests.**  
**Novelty scope:** the robot execution-contract application and controlled PhysX study are project-specific. **The fixed-length graph-coloring theorem is classical zero-error functional source coding**, not a newly discovered information-theory theorem. No physical hardware experiment, VLA foundation model training or end-task success improvement is claimed.

## 1. Scientific problem: the missing variable is actual *executed action*

An embodied policy issues a sequence of target-relative actions. It can know the **command it issued**, yet lack a trustworthy receipt of which actions the controller actually consumed. A camera may observe an end-effector pose, but only at finite precision and under bounded uncertainty. Reconstructing the pose from issued commands without an execution receipt can thus be a partially observable problem.

The original native SO(3) source-model repair hypotheses were **already falsified** as an originality claim: a command-variant-aware reset-relative strong baseline tied on unseen PhysX conditions. This new study does *not* propose another rotation coordinate conversion. It asks a narrower information-theoretic engineering question:

> Given public bounded-error sensor observation and a sender that really knows the executed ACK history, what is the **smallest fixed-length execution receipt** that guarantees a unique correct future target-restoring controller action?

The trust in the sender and bounds in the observer are explicit assumptions; without a truly independent execution agent emitting authenticated receipts, there is no usable runtime protocol.

## 2. Exact finite decision problem and proof

Let H be the finite set of ACK histories, Y(h) the support of public quantized measured observations in history h, and A(h) the correctly source-computed next control command or its equivalence class. Sender sends a finite label c(h), receiver sees (c(h), y) with y in Y(h), and decoder must output A(h) with **zero errors**.

Define confusability graph G with one vertex per h. An undirected edge (h,k) exists precisely when

    Y(h) ∩ Y(k) ≠ ∅   AND   A(h) ≠ A(k).

**Proposition (classical graph-coloring principle).** A fixed-length communication code is zero-error for all supported observations if and only if c is a proper coloring of G. The smallest alphabet is the chromatic number χ(G), requiring ceil(log2 χ(G)) bits.

**Proof, both directions.** If an edge's two histories have the same receipt label, some common y makes the decoder receive identical (c,y) despite different A, impossible for a deterministic correct decoder. Thus adjacent histories must have distinct labels. Conversely if c is a proper coloring, any histories with the same (c,y) have identical A by definition of graph edges, and a decoder may uniquely map (c,y) to A. Minimality is exactly the minimum proper coloring definition. □

This is mathematically known zero-error function computation with side information, not a new Orlitsky–Roche result. The implementation enumerates exact finite quantization supports and finds χ by branch-and-bound; an independent auditor recomputes graphs with a separate exact colorability solver.

**Cost comparator:** 2 historical ACKs cost 2 bits if always sent in full; a 1-bit code saves 1 bit for the specified observation supports. An optimal *no-receipt* Bayesian policy with the **same observation and same generative assumptions** is the proper cost-0 comparator, and its accuracy cannot be misdescribed as guaranteed zero error when some observations alias conflicting required actions.

## 3. Controlled result A: preregistered finite model, NEGATIVE

- [Frozen finite-model registration](EXECUTION_RECEIPT_FINITE_PREREG_20261013.json): H=3/4, two illustrative morphologies, 12 seeded templates, 3 sensor quantizers, 2 registered bounded-error radii = 288 conditions.
- [True original full three-OS test](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38362714720) PASS, including 296 unit/independent exhaustive proofs per OS and all 288 registered scenarios.
- [Independent recomputation of 288 graph color minima and canonical cross-OS artifacts](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363149395) SUCCESS, no after-the-fact changed conditions.
- 111/288 saved >=25% of original ACK bits, while preregistered gate required >=144/288. **Hypothesis failed.** Full transparent [negative report](EXECUTION_RECEIPT_FINITE_288_NEGATIVE_20261013.md). Mathematically zero-error under model assumptions, no empirical novelty superiority claim.

## 4. Controlled result B: native PhysX, passed preregistered engineering information gate

- [Frozen before original PhysX outcomes](PHYSX_REAL_ACK_RECEIPT_PREREG_20261013.json), Git blob `ece6ee56331c5855e6362c5505c8d145bdb968c3`. True simulated native PickCube-v1 with controller `pd_ee_target_delta_pose`, two DIFFERENT native robot controllers Panda and xArm6-robotiq, four **new** reset seed clusters per robot, two action variants, four ACK histories: **64 independently launched original PhysX worlds**. The public observation feature is actual achieved EE orientation relative to the public reset orientation, expressed as SO(3) rotation log. Private controller-target getters are not permitted to make a policy decision.
- For each (robot,seed,variant), all four actual heldout histories are executed in native PhysX, and possible camera/sensor observation supports are **synthetically** quantized under predeclared componentwise radial error bounds: three cell widths (0.005/0.015/0.04 rad) × two error bounds (0.001/0.004 rad).
- Result: **96 registered robot-seed-variant-sensor cells** (48 each robot). [Original complete native-CPU PhysX workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363869998) SUCCESS both jobs. Panda: **32/48** original observation graphs permit saving >=1 ACK bit while retaining unique command decisions; xArm6: **32/48**. **64/96 overall**, beating preregistered >=48/96 plus >=16 in each robot, with no observed alias errors under the registered finite support.
- Original full source implements nonprivileged source-computed *candidate* controller target rotations for each history. Ground-truth ACK is provided only to the trusted sender and audit. This is still a **nonphysical trustworthy sender assumed, not implemented**.
- [Separate original native PhysX quaternion and minimum-color independent artifact audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38364461258): **CHECK FINAL WORKFLOW STATUS BEFORE ASSERTING PASSED**, recomputes actual achieved quaternion differences, synthetic quantization, four-history chromatic minima, full 96-cell denominator and code equivalence without importing the primary implementation.

**Scientific boundary:** multiple sensor/ACK conditions within four native reset seed clusters per robot are repeated samples, not 96 independent robots. No fine-grained native contact safety, success-rate increase, full task recovery, stochastic camera calibration, or real hardware ACK network has been measured. The optimistic communication saving is an **idealized controller/observer contract**.

## 5. Direct comparators and risk of non-novelty

- **Full truthful ACK** (2-bit): guarantees correct mode, higher communication cost.
- **No receipt Bayes decision** (0-bit): optimal given equal allowed observations and a specified prior; may make irreversible wrong corrections under observation alias.
- **Hamming-weight receipt + observation** and greedy exact proper color: inherited low-overhead controls.
- **Optimal finite graph-color codec**: exact minimum bits for this mathematical model, hence cannot claim a rate improvement over another equally informed exact graph method—it is the exact mathematical optimum.
- [Side Information Design in Zero-Error Coding for Computing, Entropy 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11049120/): establishes the known characteristic-graph zero-error coding theory used here.
- [PACE action-chunk execution, 2026](https://arxiv.org/abs/2606.00537): adapts robot replan horizon and shows actual task and physical robot gains, highlighting a standard this finite proof **does not meet**.
- Prior JMLR/NeurIPS Bayesian active control and information acquisition work must be compared before any claim of original recovery policy.

## 6. What would close a PhD-level four-gate flagship?

1. **Discovery:** observe actual alias/confusion of public sensor values and future controller state in real, not only artificially quantized, native systems. Provide a true minimal counterexample and a measured noise/ACK model.
2. **Mechanism:** move beyond restating exact graph coloring—e.g. build an **online authenticated receipt–observation protocol** accounting for delayed receipts, unknown time of application, bounded trust failures and irreversible task costs. Then explicitly compare to full ACK, posterior filters, system ID and modern action-chunk recovery methods at equal network/query budget. Do not call ordinary Bayesian decision or known graph coding a new theorem.
3. **Strong evidence:** actual completed independent full robot tasks and recovered task-level success vs matched baselines, true calibration/collision/timing and robot-reset grouped uncertainty; prospective unseen real simulation morphologies and tasks.
4. **External acceptance:** external maintainer approves/merges a narrowly designed functionality (not the current research branch), or a separate group reproduces a novel claim and a high-quality venue accepts a paper. Fork-only CI is not a fourth gate.

**Result status:** software mathematical correctness complete, native PhysX information-cost gate positive; scientific originality and external approval NOT established. Do not relabel an idealized communication upper bound as a major new mathematically original result.
