# Frozen Diffusion/VQ-BeT transfer pilot — **ZERO TRANSFER UTILITY**

**Complete owner-run prospective pilot, 2026-10-08.** Its 13 frozen
PushT state probes and final aggregate completed successfully in GitHub Actions
[run #37714189503](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37714189503).
Scientific decision: **ZERO_UTILITY_NO_TRANSFER**. A green CI run is
not evidence of a successful embodied-policy transfer mechanism.

## All original outcomes, no state removed

| Item | Frozen outcome |
|---|---:|
| Calibration restored-state clusters | 9/9 completed |
| Held-out test restored-state clusters | 4/4 completed |
| Dependent held-out A/B observations | 8/8 |
| Frozen official policy first-action queries | **702** |
| State-block conformal alpha / k | 0.10 / 9 of 9 |
| Calibrated absolute response radius | **2.4039358761581013** |
| Frozen permitted physical response-gap tolerance | **1.0** |
| Test states with both policy stability flags passing | **0/4** |
| Test requests rejected as invalid local model | **8/8** |
| **Actual authorized cross-policy transfers** | **0/8** |
| False authorized transfers | 0/8, **at zero action coverage** |
| Empirical state-block interval coverage | 4/4, tiny sample |
| Uncalibrated nominal-Jacobian classification errors | 2/8, **different coverage** |
| Independent external experimental replication | **0** |

All 13 states were retained: calibration seeds
`211,223,227,229,233,239,241,251,257`; test seeds
`263,269,271,277`. No invalid or stochastic state was discarded.

**Two separate substantive obstacles, not one:**

1. **Identification validity.** Diffusion failed the original fixed stability
   proxy on **13/13 states**; VQ-BeT passed on 10/13 (7/9 calibration,
   3/4 test), so the pair had **0/4 valid test states**. The original runner
   properly rejected all eight requests as `REJECT_INVALID_LOCAL_MODEL`.
2. **Calibrated uncertainty.** The nine-state cluster maximum conformal
   radius `q = 2.4039` exceeds the preregistered tolerance `tau = 1.0`.
   Because the predicted response gap is nonnegative, every putative upper
   interval is `center + q >= q > tau`. Thus, **even with the validity
   flag overridden**, the unchanged calibrated interval could not justify
   a `STATISTICALLY_SIMILAR` action transfer. This is a mathematical
   observation about the *frozen* test, NOT an authorization to relax the
   gate or adjust `tau` after seeing these results.

No causal attribution beyond the observed flags/interval is established.
Improving stochastic or locality identifiability is now a separate
*unvalidated research question*, not a solution already demonstrated.

## Evidence chain

- Original source head: `bb22b80023a714a040756736db021df8c42e488e`
  ([PR #46](https://github.com/lindicaphxag-tech/ManiSkill/pull/46)).
- Complete [original GitHub Actions run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37714189503);
  original aggregate artifact `11524246270`, ZIP SHA-256
  `3725aa270cdf234e5dbb0f13ab797a2fe15c1ed40b655f4a3eb1f88807e769ad`.
- Original preregistration protocol Git blob SHA-1
  `b3ec5e5f4b6226c03d169ff857a97efe2a71d5c8`
  and SHA-256 `d64701bbe614ac2c829135bd8e9bcca685bf61410ec7b746878dc9db06c186b1`.
- All **13 original per-state JSON reports**, untouched `aggregate_original.json`,
  `protocol_frozen.json`, original `evaluator_at_source.py`, and immutable
  source/CI [manifest.json](./manifest.json) live here, not behind the
  90-day artifact retention deadline.
- The independent **reporting-semantic correction** was publicly identified
  *before* outcomes completed and merged as [PR #47](https://github.com/lindicaphxag-tech/ManiSkill/pull/47). In robotics,
  `STATISTICALLY_DISTINCT` means **do not transfer**, not a successful
  authorization. The correction preserved the original pilot output and
  reports both actual transfer coverage and classification coverage.

## One-command replay

From the repository root:

```bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_fresh13_archive_replay.py
python -m research.crg_core.evidence.conformal_fresh_13state_v1.replay_archive \
  --output /tmp/crg-fresh13-readonly-replay.json
```

The archive re-runs a **byte-for-byte copy** of the original source
evaluator against all 13 state JSONs, compares all original scientific numerical fields to within 1e-10 while
preserving the original calibration SHA-256 separately from the new float-
serialization SHA-256. The two byte hashes may differ across NumPy/BLAS
versions even when the numerical results and decisions agree. It then runs
the pre-outcome transfer
authorization ledger. It fails on a missing seed, changed protocol, changed
evaluator, materially altered response/score or fabricated success. A
byte-identical calibration digest is not asserted unless actually observed.
This is **owner-side reproducibility of the arithmetic**, not independent
third-party provenance verification.

## Research conclusions and statistical limits

The observed empirical whole-state interval coverage is 4/4 but there are
**only four independent test state clusters**, so it cannot establish
generalized 90% real-world coverage, conditional-on-authorization error
bounds, or absence of unsafe actions. The per-request gap is the **mean
of three RNG-seeded first-action physical responses**, not a sampled
single-rollout collision indicator.

This pilot was run under an explicitly post-run-amended Pymunk 4-ULP
state restoration protocol. Calibration seed **211** also appeared in an
earlier separate five-state locality experiment; it was not in the historical
10-state cross-policy bank, but calibration was **not fully historically
unseen** across the whole research program. The four test seeds remained
distinct from both cited historical banks.

A follow-on mechanism must be evaluated on newly frozen, unexamined states,
and preferably another policy family/task, before making a stronger claim.
The correct target is **nonzero, useful transfer coverage with bounded
observed error at matched query budgets and adequate experimental power**.
Never turn this `ZERO_UTILITY_NO_TRANSFER` result into a positive
safety or performance claim by posthoc changes to thresholds or seeds.

**External upstream merged credit gained here: zero.** The result is an
honestly falsified, publicly reproducible research artifact.
