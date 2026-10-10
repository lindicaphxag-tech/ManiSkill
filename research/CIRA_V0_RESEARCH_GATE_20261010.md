# CIRA v0: Intervention-Aware Selective Probe / Controller-Authority Gate

**2026-10-10. Executable research reference, NOT a learned closed-loop robotics method or demonstrated performance improvement.** Scope: paired task-outcome arbitration at one frozen probe decision point.

## Verified original evidence — do not fit to these prospective evaluation resets

- Original [2,560-world physical PhysX experiment PR #164](https://github.com/lindicaphxag-tech/ManiSkill/pull/164): 32 independent reset clusters (16 PullCube + 16 StackCube) x four correlated physically applied/held ACK truths x ZERO/X x 10 authentic controller worlds. Verified original-source audit [run 38015149933](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38015149933).
- Original A complete-history authority: ZERO **109/128** vs X **99/128** official task successes; privileged reads 90 vs 93. B and trustworthy-getter C: ZERO 109/128 vs X 102/128. Under X, A had four wrong confident native SE(3) target-state authorizations (position Linf 26.734–91.674 mm, rotation 0.0199–0.0564 rad). X's actual native commanded target moved about 15 mm. This is causal native-controller-state mutation, not robot task improvement.
- Original early producer and auditor float32 tolerance amendments are disclosed in PR #164; the audit is retrospectively independent source hashing, **not independently repeated physics**.
- [Existing Draft #163](https://github.com/lindicaphxag-tech/ManiSkill/pull/163) already implements exact finite risk-constrained POMDP reference, family-wise robust enumeration and conservative native-target authorization calibration. These are established methods, **not** novel CIRA theory.

## Novelty hypothesis and comparator firewall

H1 (UNPROVEN): *Intervention-specific physical cost and native controller-memory mutation, coupled with independently fitted action-conditioned observation models, produce selective probe/QUERY/repair decisions with better genuinely prospective task success and controlled full SE(3) authority error than identical-cost ZERO, always-getter, ActionShift, and correct action-conditioned constrained POMDP baselines.*

A model validity veto is only as good as the fitted response-model uncertainty set. A Boolean identity attestation in v0 does NOT certify a model or safe action. Do not claim novelty based solely on Hoeffding/CP calibration, Pareto planning, worst-model choice or conditionally skipping X. Those are standard reference ingredients.

## Implemented and locally tested

`research/cira_intervention_gate.py` provides:

1. Matched original-reset paired task utility differences (task success less wrong native-memory authorizations, getters and extra probe steps), each ACK truth averaged *within* an independent cluster.
2. Multiplicity-adjusted one-sided Hoeffding lower bounds on paired benefit, and Clopper–Pearson upper bounds on ANY wrong authority for a reset cluster.
3. Fail-closed refusal on native action ABI mismatch, missing independent action-specific response-model attestation, fitting/calibration reset leakage, unmatched public sensor budget/pre-action state, missing ACK truth, insufficient independent resets or lack of a positive lower utility bound.
4. Physical probe selection and complete SE(3) target authority **remain different decisions**: any selected probe still requires trusted QUERY until a *separately validated* native-target certificate exists. ZERO is a physical step and QUERY consumes resources.
5. Historical original source auditor JSON parser solely for descriptive retrospective analysis, NOT proof an arbitrary JSON passed original artifact provenance verification.

Unit tests use **synthetic constructed outcomes only**, not PhysX or pretrained PPO. To run:
```bash
python -m unittest tests.test_cira_intervention_gate -v
```

## Pre-prospective gates — no shortcut to a journal claim

1. Train native action-conditioned joint (hidden target post-action, public observation) response models on separately sampled Panda and xArm6 PhysX controller resets; validate action ABI contract, response-model support, contact mode and held/applied ACK truth on **disjoint reset clusters**.
2. Replace externally asserted model-validity flag with actual score-based OOD support and learned model-family uncertainty calibration. Add adaptive recoverable action and passive servo-settling to candidate set.
3. Freeze the online router and its reward weights, family ambiguity radii, budget, and model-validation criteria **before** new task results. Original 32 reset clusters are locked negative controls.
4. On new PullCube/StackCube and at least one harder non-ceiling manipulation task, compare ZERO, X/Y, always QUERY, original A/B/C, ActionShift and correctly implemented constrained POMDP. Keep full identical pre-action source policy/ACK faults, equal public observation budget, count all extra actions and trusted reads.
5. Primary endpoint: **official task success without wrong confident full SE(3) memory authorization**, with paired independent-reset CIs. Also report success alone, query and public observation count, total steps/latency, genuinely available contact force/collisions, model support rejection, and controller/robot shift.
6. If a method does not outperform strong controls, retain the falsification benchmark and do not claim an RSS/CoRL/RA-L main-track advance. For journal submission, originality must be learned native intervention semantics **plus** generalizable task performance, not this one-step gate alone.

## Limits

No native PhysX new experiment has been run by this branch. No hardware safety certificate, population error below 10%, ActionShift superiority, accepted publication, or independently reproduced effect is claimed. IEEE RA-L is a potential target only after the above gates pass; RSS/CoRL would require larger originality and strong cross-policy evidence.
