# Frozen Diffusion/VQ-BeT PushT bank — complete negative result (2026-10-08)

**Outcome: PRIMARY SCIENTIFIC GATE FAILED. This is not a successful cross-policy DEC transfer.**

A GitHub-hosted, frozen-checkpoint experiment compared official DiffusionPolicy and
VQ-BeT on identical PushT interventions, in ten restored environment states
with two held-out A/B physical disturbances per state. All original seeds
(17, 29, 43, 59, 71, 89, 101, 131, 151, 181) and all 20 pairs
were retained; there were no post-hoc state exclusions.

| Frozen metric | Result |
| --- | ---: |
| DEC signature distance vs fresh held-out physical-response distance: Spearman | **0.1449066921** |
| Frozen raw-action-Jacobian distance baseline: Spearman | **0.3471722832** |
| Frozen coarse-class baseline: Spearman | -0.4247953952 |
| Support-set / static-representation baselines | 0 / 0 |
| Frozen DEC minimum | 0.50 |
| Required margin vs best frozen baseline | +0.10 |
| Primary decision | **FAIL** |
| Number of restored-state clusters | 10 |
| Number of dependent A/B observations | 20 |
| States with at least one DEC instability | **10/10** |
| Policy evaluation calls | 540 = 10 states × 2 policies × 27 |
| Owner-run independent external replication | **0** |

Therefore the original strong hypothesis — that DEC distance can transfer
across these two frozen policy families to predict fresh held-out physical
response geometry better than the frozen baselines — is **not supported**.
A successful GitHub Actions run merely confirms execution, not scientific
hypothesis success.

## Raw provenance and permanence

- [Full successful GitHub workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37706099258), run 37706099258.
- Original execution branch/commit: `research/eprc-cross-policy-bank-v1-execution`,
  `8207ac01c56e75ccee19cba0e75eb0978cde37b2`.
- Frozen gate digest: `ae4590eb2a152bfa2367bbe1e8bc204e05721c4481b7422597054c1a160edcd0`.
- Original uploaded aggregate ZIP SHA-256:
  `cc98ac30c1654c98712d4430d9191816d541856a947d51963b184d6fddf196a5`
  (artifact #11520848343; upload retention is limited).
- This directory permanently records **all 10 original per-state JSON outputs**
  extracted from the same successful GitHub Actions job logs, the untouched
  `primary_result.json` values, and the source `manifest.json`.
- Checkpoint revisions, seeds, perturbations, query accounting and source IDs
  are retained in the raw JSON and immutable experiment source commit.
- This archive is **owner-produced**, not independently authenticated experimental evidence.

## Protocol amendment, not erased

The first execution using strict bitwise `block_position` readback could
not complete three frozen seeds (29, 43, 131). The public v2 amendment
permits at most four coordinate-specific float64 ULPs of Pymunk block
position roundtrip discrepancy; other snapshot fields remain strict.
No seeds, frozen cutoffs, controller/policy checkpoint identities, or
held-out perturbations were changed. This is **amended-protocol v2 evidence**,
not a complete untouched original-v1 preregistered study. See
[the recorded amendment](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/eprc-cross-policy-bank-v1-execution/research/eprc/PROSPECTIVE_BANK_RESTORE_AMENDMENT_V2.md).

## Independent reproducibility of the reported arithmetic

From the repository root:

```bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_20case_evidence_replay.py
python -m research.crg_core.evidence.pusht_cross_policy_20case_v2.replay \
  --output clustered_sensitivity.json
```

The replay uses the frozen source's scoring definitions to independently
reconstruct all five Spearman coefficients from these 10 raw state reports.
It fails if any original number differs by over 1e-10, a frozen checkpoint
or protocol is replaced, or a state is missing. The diagnostic extension
runs whole-state bootstrap, leave-one-state-out and A/B-block permutations.
**These diagnostics were added after experiment launch, are exploratory,
and must not be used to change the pre-registered primary result.**

**Statistical unit:** the 20 observations belong to only **10 independent
restored-state clusters**. A and B share the same DEC estimate, so
treating all 20 as 20 independent state trials is pseudoreplication.
With 10 clusters, cluster-resampling uncertainty is substantial.

## Executed clustered sensitivity audit (post-hoc)

The full frozen JSON replay passed public [CRG Core CI](https://github.com/lindicaphxag-tech/ManiSkill/pull/43/checks)
with **33 tests passed** and reproduced all five original primary correlations
to within 1e-10. The executed
[clustered_sensitivity.json](./clustered_sensitivity.json) preserves:

- DEC Spearman state-cluster bootstrap percentile interval (1,024 draws):
  **[-0.3525, 0.5907]**;
- DEC minus best frozen baseline Spearman: **-0.2023**;
- state-cluster bootstrap interval for that margin: **[-0.7909, 0.3417]**;
- one-sided whole-state A/B-block permutation Monte Carlo diagnostic:
  **p=0.3070** (2,048 random permutations);
- all **10 leave-one-state-out** estimates.

All resampling/permutation numbers are **post-hoc exploratory**, not registered
hypothesis tests. The small sample of ten independent states and the
exchangeability assumption limit inferential power. A wide interval should
not be reinterpreted as evidence of equivalence or of a successful repair
method. The original prospective primary gate remains **FAILED**.

## What this result supports and does not support

**Supports:** a complete public falsification of cross-policy DEC-distance
prediction under this frozen setting, including evidence that stability
screening matters and a simpler raw-distance baseline may outperform a
more elaborate signature on unstable derivatives.

**Does not establish:** a universal impossibility of physical contracts,
the causal reason for DEC transfer failure, benefits of a new router, real
robot task success, real-world collision safety, or external adoption.
A fresh prospectively registered study testing when to abstain versus
acquire new evidence is required before claiming a successful remedy.

Maintainer/academic readers may inspect the 12 immutable JSON records,
the original workflow and code, and the independent arithmetic checker
without downloading the large EPRC research branch.
