# CRG prospective closed-loop benchmark protocol

## Primary question

Does the geometry-defined CRG margin predict whether a frozen robot policy can actually recover from a held-out disturbance?

## No post-hoc threshold tuning

The primary classifier is fixed before outcomes are observed:

- `CRG margin >= 0` => predicted repairable;
- `CRG margin < 0` => predicted unrepairable.

The zero boundary comes from response-image membership plus certified radius slack; it is not selected from rollout labels.

## Frozen trial unit

Each trial stores:

- policy family + immutable checkpoint;
- controller representation + exact runtime config;
- state / episode / seed;
- support intervention and magnitude;
- estimated CASJ / physical repair map digest;
- certified radius;
- CRG signed margin;
- synthesized repair;
- actual closed-loop recovery outcome;
- failure reason if unsuccessful.

## Required baselines

At minimum compare CRG with:

1. perturbation magnitude alone;
2. controller headroom alone;
3. raw action-response norm alone;
4. raw action-Jacobian similarity;
5. support-set overlap;
6. DEC contract-class agreement without CRG geometry;
7. unconstrained linear repair;
8. controller-box projection / generic safety projection when applicable.

## Primary endpoints

1. false-accept rate at the frozen zero threshold;
2. accepted-repair success rate;
3. coverage;
4. AUROC for actual recovery;
5. paired bootstrap AUC difference against each scalar baseline.

## Constructive endpoint

Among trials CRG predicts repairable, compare actual recovery of:

- no repair;
- direct CASJ linear correction;
- unconstrained least-squares correction;
- CRG certified synthesis.

## Cross-policy gate

Use the same disturbance bank on at least two frozen policy families and at least two action/controller charts when feasible. No method-specific disturbance resampling.

## Acceptance gate

CRG should not be promoted to the main paper claim unless all of the following hold on held-out trials:

- zero-threshold false accepts are materially lower than unconstrained repair;
- accepted-repair success exceeds no-repair and direct linear repair;
- CRG AUC exceeds perturbation magnitude and controller headroom;
- representation changes that preserve physical semantics do not materially change the repairability decision;
- negative / null policy families remain reported.

## Kill condition

If disturbance magnitude or controller headroom predicts recovery as well as CRG, or if the zero-threshold boundary is poorly aligned with actual success, the repairability-geometry claim is rejected.