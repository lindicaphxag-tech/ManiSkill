# State-cluster conformal transfer — calibration protocol

**Status: runtime prototype; no independent real-policy prospective validation yet.**

The old 10-state/20-observation Diffusion/VQ-BeT study is archived as a
**failed prospective scientific hypothesis test**. Those results were seen
before this code was designed and must not be repurposed as an untouched
confirmatory calibration/test bank.

## Runtime decision with calibrated uncertainty

For a physical correction request h in a fixed canonical support chart,
let c(h) = ||(Ghat_A - Ghat_B)h|| be the predicted response disagreement.

On each independent calibration state i, observe both A/B heldouts and
compute one calibration score per STATE:

E_i = max_{k in A,B} | ||observed_A(i,k)-observed_B(i,k)|| - c_i(h_k) |

With n exchangeable, separately frozen calibration state clusters, select
the k-th ordered E_i, with k=ceil((n+1)(1-alpha)). If k>n, fail closed;
nine independent states is the minimum for alpha=0.1 and 90% state-block
MARGINAL coverage. A/B are two dependent requests per state, not two
independent calibration units.

The uncertainty interval for an unseen request is:
[max(0,c(h)-q), c(h)+q], where q is the calibrated state-block score.

**Statistical assumption and limitation:** with fixed score function,
frozen calibration/test split and exchangeable whole-state blocks, split
conformal predicts marginal coverage for BOTH A/B responses in a new state.
It does not guarantee a response on any particular individual state, nor
a deterministic physical safety bound, controller collision safety,
or independently validated source provenance. This is established
conformal mathematics, not a newly invented theorem.

The method CHANGES runtime action authorization:

- STATISTICALLY_SIMILAR only if the entire interval lies within tolerance;
- STATISTICALLY_DISTINCT only if the entire interval exceeds tolerance;
- ABSTAIN_UNCERTAIN when the interval crosses tolerance;
- REJECT_INVALID_LOCAL_MODEL whenever local-model validity, support,
  or controller authority is missing.

The output always says deterministically_certified=false and
externally_verified=false. Empirical q95 variability is not a sound
worst-case operator-norm uncertainty certificate; do not call this
CERTIFIED_REPAIR or a real-world safe policy.

## Mandatory prospective experiment

Before generating results, freeze: new calibration and test reset seeds
disjoint from the historical 10 seeds, both official checkpoint SHAs,
exact runtime/environment versions, support-chart semantics, alpha,
response tolerance, all failure handling, coverage and query budgets.
Nine or more calibration STATE clusters are needed for alpha=0.1.
Evaluation units are held-out independent state clusters, not individual
A/B records.

Record all intended evaluation states, including invalid restore,
locality-rejected, and model-failed cases. Freeze decisions BEFORE
observing held-out responses. Compare false authorization rates only at
matched nonzero decision coverage and matched policy-query budget.
Always-abstain has zero false authorizations and also zero coverage.

A decisive negative result is zero admissible states, low coverage,
empirical coverage failures, or no useful risk/coverage advantage.
A positive result would require an untouched, externally auditable
fresh-state prospective run and independent replication. This module
and the historical failure alone cannot demonstrate it.

## Test

    python -m pip install numpy pytest
    python -m pytest -q tests/test_crg_paired_state_conformal_transfer.py

Interfaces: fit_state_block_envelope -> screen_new_state_pair ->
audit_heldout_state. The last stage is *after* prediction is frozen
and preserves both A/B errors in the state cluster.
