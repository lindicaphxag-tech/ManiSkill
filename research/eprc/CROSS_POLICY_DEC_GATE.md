# Pre-registered cross-policy DEC gate

The first real two-policy experiment must be judged by a frozen discriminator, not by a post-hoc plot.

For every held-out disturbance, construct a pair of independently probed policy/controller cases and record whether their runtime decisions agree.

The frozen predictors are:

1. normalized raw action-Jacobian distance;
2. support-set Jaccard distance;
3. static action-representation mismatch;
4. coarse contract-class mismatch;
5. lifted Differential Execution Contract distance.

The target label is exact agreement of PASS / TRANSPORT / REPAIR / REJECT.

## Primary prospective gate

- at least 20 held-out policy-pair disturbances;
- both agreement and disagreement cases must be present;
- DEC distance AUC >= 0.70;
- DEC AUC must exceed every frozen baseline by at least 0.05.

Smaller distance predicts decision agreement. AUC is computed pairwise without an external ML package.

## Why this matters

A method can look convincing if it only shows that two chosen policies have similar Jacobians. The stronger claim is predictive: DEC similarity should tell us whether independently deployed policies make the same runtime adaptation decision on disturbances not used to identify the contract.

If the gate fails, the cross-policy DEC claim is rejected rather than rescued by changing thresholds after seeing results.