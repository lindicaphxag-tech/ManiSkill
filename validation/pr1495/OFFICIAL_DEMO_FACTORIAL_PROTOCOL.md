# PR1495 Official-Demo Four-Cell Factorial — Frozen Extension Protocol

Status: **partially exposed extension; not a prospective-I2 record**

Freeze purpose: commit the unobserved controller-only / combined predictions
before reading those cells' official-demo outcomes.

## Frozen production identities

All four cells share upstream base:

`62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`

| Cell | Frozen commit | Production delta |
|---|---|---|
| old/old | `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` | none |
| controller-only | `5a408084daab6f2b644bcd3e653df11228071d98` | `pd_ee_pose.py` only, blob-identical to upstream #1472 |
| converter-only | `8e6eb8cf28ebe7f0a1c32de7a2898ae814203109` | `conversion.py` only, from #1495 |
| combined | `c282bb1b7d80b506104de31e52c8aba5cdbb62d0` | exactly the two production files above |

Each intervention snapshot is one commit ahead of the same base. No validation
files are part of the production interventions.

## Exposure boundary

Already exposed before this freeze:

- old/old official-demo replay success: **9/10** on the earlier paired run;
- converter-only official-demo replay success: **1/10** on the earlier paired run;
- synthetic/noncommuting SO(3) four-cell mechanism evidence:
  old/old ≈ 5.0767 deg, controller-only ≈ 64.7473 deg,
  converter-only ≈ 66.1280 deg, combined ≈ 4.83e-06 deg.

Not yet read at this freeze:

- controller-only official-demo success vector;
- combined official-demo success vector;
- complete paired action traces for all four cells under `--allow-failure`.

Therefore this document must **not** be described as preregistering the already
observed old/old or converter-only cells.

## Frozen directional hypothesis

The two local defects partially compensate in the old/old stack.

Fixing only one side should expose the remaining mismatch; fixing both should
restore controller-visible semantic agreement.

The frozen behavioral prediction is:

[
S_{combined} ge S_{controller-only}
]

and

[
S_{combined} ge S_{converter-only}.
]

Primary interaction statistic:

[
I =
(S_{combined} - S_{controller-only})
-
(S_{converter-only} - S_{old/old}).
]

Frozen predicted direction:

[
I > 0.
]

Because old/old already exhibited partial cancellation, **combined is not
required to exceed old/old** for the mechanism claim. Physical dynamics,
conversion approximation, IK, and finite-horizon effects can make an
accidentally compensated stack behaviorally competitive even while its internal
semantics are wrong.

## Stronger but falsifiable recovery expectation

The stronger empirical expectation is that the combined cell recovers
substantially from the exposed converter-only 1/10 collapse.

A combined result that remains near converter-only with no corresponding
semantic/action recovery would weaken the claim that the controller and
converter fixes form a useful atomic repair.

## Pairing protocol

- same first 10 official PegInsertionSide source episodes in every cell;
- same raw H5/JSON source;
- `--use-first-env-state`;
- target control mode `pd_ee_delta_pose`;
- state observations;
- `physx_cpu`, one replay env;
- validation-only `render_backend="none"`;
- `--allow-failure` so failed episodes remain saved;
- output order is paired to source episode order;
- H5 and JSON terminal success labels must agree.

## Primary outcomes

1. per-cell 10-bit success vector;
2. per-cell success count / rate;
3. difference-in-differences interaction (I);
4. whether combined >= each single-fix cell;
5. paired normalized action-space L2 deltas.

Normalized action differences are descriptive only. They are **not** converted
into SO(3) physical error because the controller scaling convention is itself an
intervention.

## Falsifiers / interpretation gates

The compensating-fault / atomic-repair interpretation is weakened if:

1. combined is worse than both single-fix cells without an independently
   identified downstream cause;
2. controller-only and converter-only behave indistinguishably from combined
   across both success and paired action traces;
3. source episode pairing is broken;
4. the four production snapshots differ outside the declared controller /
   converter files;
5. H5 and JSON success labels disagree;
6. the result depends on rendered observations or GPU-specific dynamics.

A negative result is retained rather than changing the prediction after the run.

## Claim boundary

This is an official-demo conversion / behavioral causal assay, **not**:

- a Diffusion Policy training result;
- a population success-rate estimate;
- maintained ManiSkill adoption;
- a prospective primary I2;
- proof that all controller/converter interactions behave this way.

