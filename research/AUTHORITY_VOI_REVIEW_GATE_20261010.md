# Authority-aware Value of Information — exact oracle, NOT a robotics result

**Research checkpoint: 2026-10-10.** This branch is a deliberately limited, review-first mathematical/software experiment. The newly committed source and tests establish an **exact finite one-step decision oracle**, and do NOT show improved ManiSkill, PPO, LIBERO, VLA, robotics safety, hardware performance, or independent adoption.

## Factual robot evidence motivating the change

The physically executed prospective 32-reset × four-ACK × ten-arms experiment reported **109/128 identical task success histories** for the public full-history A and strong same-public 0.60 score B, respectively **94 vs 98 actual privileged readbacks**, while both incurred 256 additional public XYZ readings. Descriptive paired inference gives p=0.289, reset bootstrap CI [-1, 9] total reads. This is no persuasive 4-read superiority.

Source: https://github.com/lindicaphxag-tech/ManiSkill/blob/research/reviewer-audit-strong060-20261010/research/frozen_policy_transfer/PROSPECTIVE_STRONG060_FLAGSHIP_RESULTS_20261010.md

Another genuinely run Panda/xArm6 native PhysX low-signal study classified all **32 heldout fault-truth cases with zero, X and Y probes**. The selected nonzero probe contributed **zero additional correct histories** over zero; a genuine negative result.

Source: https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/LOW_SIGNAL_ACTIVE_PROBE_FALSIFICATION_FIRST192_20261010.md

## Exact one-step decision problem

Frozen finite latent controller states h have prior p(h), permitted repairs a have downstream loss L(a,h)>=0, and perfect native target readback costs c_Q. Probes e are specified by frozen state-conditioned likelihoods P_e(o|h), and *all-inclusive* sensing/actuation cost c_e. A probe is assumed *nonintervening*: it observes but does **not** change h or L; this assumption generally **fails for nonzero robot actions**.

No-probe Bayes value is the minimum of (i) a common public repair and (ii) perfect query followed by the best known-state repair.

Under a probe, the exact value adds c_e to the outcome-weighted optimal public repair or state query, chosen separately after every o. Optional model-conditional P(L(a,H)>tau | o)<=rho forbids uncertain repairs. The finite dynamic-programming solution equals explicit exhaustive enumeration of contingent repair/query policies under the specified model. This is **standard one-step decision theory used as a stringent strong baseline**, not a new general POMDP theorem.

The exact action/loss/observation quotient merges only states with strictly identical losses for every action AND strictly identical observation likelihoods under every probe, preserving this model's Bayes values. No tolerance-based or dynamical equivalence is claimed.

## New executed synthetic result (only)

In one intentionally constructed **8-state diagnostic** with two repairs, the max-entropy probe reveals **2 irrelevant bits** and incurs expected task/query cost **2.2** hypothetical units; the task-relevant **1-bit** probe instead incurs **0.2**, and a no-probe readback incurs **2.0**. This diagnostic illustrates why raw information gain cannot substitute for task value. It is **not** a measured 91% robot improvement nor superiority over the exact POMDP oracle.

Eight unit tests check all failure boundaries and 250 seeded random finite models against a separately enumerated full contingent-policy oracle. A 1,000-state / two-action exact-signature reduction to two states tests preservation of task cost and mutual information.

Reproduce from repository root:

    python -m unittest discover -s tests -p test_authority_voi.py -v
    python -m research.authority_voi

## Relevant accepted-paper comparator and novelty barrier

- RSS 2024, **Partially Observable Task and Motion Planning with Uncertainty and Risk Awareness**: https://roboticsproceedings.org/rss20/p118.html
- RSS 2025, **Map Space Belief Prediction for Manipulation-Enhanced Mapping**: https://roboticsproceedings.org/rss21/p039.html
- CoRL 2025, **Belief-Conditioned One-Step Diffusion: Real-Time Trajectory Planning with Just-Enough Sensing**: https://proceedings.mlr.press/v305/puthumanaillam25a.html

Against these papers, a toy entropy counterexample and a one-step oracle are **not a sufficiently original robotics contribution**. This baseline is valuable precisely because it can *falsify* weak methods before expensive research flights.

## Preregistered next gate — do not claim success before running

1. **Causal native dynamics**: replace P_e(o|h) with P_e(h',o|h) from genuinely separately fitted native PhysX response transitions, including contact and commanded-target history updates.
2. **Same-information true comparators**: no probe, identical-energy fixed X/Y, calibrated task-aware active sensing, exact POMDP/finite-belief planning approximation, and perfect native readback; do not privilege the proposed method with additional public sensing.
3. **Disjoint populations**: prefreeze development resets, separately freeze action/model selector, use untouched independent calibration for risk/coverage, then distinct prospective final reset clusters (four ACK truths on one reset are correlated).
4. **Task outcome rather than label-only**: actual completed manipulation tasks, wrong confident authorizations, refusal rate, priv-target reads, public observation cost, actuation effort, contact, wall time. Cluster intervals and negative source-shift subgroups mandatory.
5. **Outside-lab reproducibility**: an unaffiliated operator chooses new seeds and independently reruns physical simulator scenarios. Do not call author-controlled Actions third-party validation.

**Kill rule:** if a correctly implemented strong same-budget controller-query policy or transition-aware VoI planner matches this approach, report the negative result without shifting metrics post hoc. If a real robot probe alters h, the present one-step oracle must not directly execute that probe.
