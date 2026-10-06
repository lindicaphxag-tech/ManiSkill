# DEC / CRG — physical repairability of frozen robot policies

This public research capsule asks one deployment question:

> **Before executing a correction, can a frozen robot policy determine what is
> physically repairable, what is not, and what evidence should be collected
> next?**

It is self-authored and counts as **zero external adoption**.

## Current claim in one line

```text
physical interventions
    -> representation-invariant DEC
    -> model-admissibility gate
    -> CRG repairability certificate
    -> minimal next evidence only when justified
```

The key discipline is fail-closed: a stable derivative is not automatically a
valid repair model.

## Real frozen-policy result

The strongest current witness uses the official frozen
`lerobot/vqbet_pusht` checkpoint under an exact-state PushT intervention
protocol.

Frozen provenance:

- model revision: `390e5e4c079c880b22e873dad53ecfac706bc78a`;
- LeRobot training-runtime commit:
  `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`;
- state reset seed: `17`;
- fine physical probe: `[4 px, 4 px, 0.02 rad]`;
- coarse physical probe: `[8 px, 8 px, 0.04 rad]`;
- held-out disturbance: `[10 px, -6 px, 0.35 rad]`.

Five repeated DEC probes are perfectly stable:

- pairwise DEC signature distances: all **0.0**;
- q95 DEC radius: **0.0**;
- paired policy repeat error: **0.0**.

But the local first-order model does not converge across physical scale:

- coarse→fine drift: **3.0126126299**;
- fine→finer drift: **3.4499882450**;
- contraction ratio: **1.1451814982**;
- frozen contraction threshold: **0.75**.

The robust CRG is therefore **INCONCLUSIVE**, and the prospective router returns:

```text
REJECT_FIRST_ORDER_LOCAL_MODEL
```

rather than authorizing a repair.

Public evidence:

- [base VQ-BeT real-policy run #37460144227](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144227);
- [prospective locality refinement #37460144187](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144187);
- frozen evidence snapshot:
  `artifact/eprc-crg-vqbet-witness-2026-10-06`.

This falsifies the weaker claim that a repeatable CASJ/DEC is sufficient for
runtime repair.

## Prospective five-state result: the richer-model rescue failed

A response-jet extension was then tested prospectively on five disjoint PushT
reset seeds:

`101, 211, 307, 401, 503`.

The promotion rule was frozen before execution. Result:

- first-order locality contracting: **3 / 5** states;
- response-jet upgrades: **0 / 5**;
- jet rescues of failed first-order states: **0 / 5**;
- frozen adjudication: **DROP_JET_FROM_FLAGSHIP**.

[Prospective run #37462465890](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37462465890)

The higher-order jet is therefore **not a flagship contribution**.

The more important result is that repeated-probe stability and scale locality
are independent. The five states populate all four combinations:

| seed | q95 DEC radius | DEC stable | locality ratio | contracts | routing state |
|---:|---:|:---:|---:|:---:|---|
| 101 | 1.43245 | no | 0.35086 | yes | INFORMATION_LIMITED |
| 211 | 0.00000 | yes | 0.65506 | yes | ADMISSIBLE_FIRST_ORDER |
| 307 | 0.18009 | no | 0.66487 | yes | INFORMATION_LIMITED |
| 401 | 0.00000 | yes | 0.90908 | no | LOCALITY_LIMITED |
| 503 | 0.46941 | no | 2.77197 | no | REJECT_LOCAL_MODEL |

Only a state that passes **both** gates may proceed to a first-order CRG
certificate.

## Core objects

### Differential Execution Contract (DEC)

Controlled physical support interventions estimate a black-box action response,
which is lifted through controller semantics into canonical physical-command
space. Equivalent physical behavior can therefore be compared across locally
invertible action/controller representations without comparing raw action
tensors.

### Counterfactual Repairability Geometry (CRG)

CRG restricts correction to the intervention-identified policy response image,
controller authority, and a certified local region.

It returns:

- `CERTIFIED_REPAIR`;
- `CERTIFIED_IMPOSSIBLE`;
- `INCONCLUSIVE`.

Robust impossibility decisions can carry an independently verifiable dual
separation witness.

### Active Minimal Repair Certificate (AMRC)

When the model is admissible but evidence is insufficient, AMRC targets the
specific certificate rather than estimating the full local system uniformly.
Symmetric policy evaluations are counted explicitly.

The certificate-identifiability layer also contains a continuous one-step
optimal probe under its frozen information model; this is experiment-design
machinery, not a claim of new linear algebra.

## External replication

The independent replication challenge is:

https://github.com/lindicaphxag-tech/lindicaphxag-tech/issues/76

The issue is labeled `help wanted`.

A machine-valid external record must bind:

- an independent producer;
- immutable source commit / policy checkpoint / protocol;
- a **real frozen policy**;
- CRG decision counts;
- policy-query cost;
- false accepts / false rejects;
- at least one execution outcome;
- a canonical evidence digest.

Negative results count as external evidence if they satisfy provenance and
completeness gates.

Validator:

```bash
python research/eprc/validate_external_replication.py path/to/record.json
```

Self-authored CI, stars, forks, and synthetic matrices do not satisfy the
external-evidence gate.

## LeRobot integration surface

`research/eprc/lerobot_plugin` is a third-party `ProcessorStep` package.
The compatibility workflow installs the exact current head of
`huggingface/lerobot#4592`, discovers the plugin through LeRobot's real
third-party mechanism, and executes a fail-closed REJECT path.

Current exact-head compatibility is green, but this is **compatibility, not
LeRobot adoption**.

A separate ACT relative-action upstream handoff is being kept outside the
flagship claim; it reuses LeRobot's existing shared relative/absolute processor
semantics and remains unsubmitted until it receives an executable validation
surface and human upstream submission.

## Contract-level reproduction

```bash
python -m pytest -q \
  tests/test_eprc_runtime.py \
  tests/test_eprc_contract_signature.py \
  tests/test_eprc_repairability_geometry.py \
  tests/test_eprc_active_minimal_certificate.py \
  tests/test_eprc_local_model_admissibility.py
```

Latest contract suite on the frozen prospective head:
[run #37462465787](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37462465787) — **success**.

## Claim boundary

This project does **not** claim invention of Jacobians, nullspaces, compressed
sensing, equivariance, convex separation, controller conversion, active
learning, Taylor jets, or frozen-policy recovery.

The current narrow hypothesis is:

> separating intervention identifiability, physical scale-locality, controller
> authority, and repairability produces safer and more query-efficient runtime
> decisions than collapsing them into one confidence score or directly applying
> a local action correction.

## Kill gates

The flagship claim is rejected or narrowed if any of these survive fair,
prospective testing:

1. perturbation magnitude / controller headroom / a scalar uncertainty baseline
   routes repair decisions as well as the two-axis admissibility gate;
2. generic controller-space projection matches CRG at equal false-accept rate;
3. AMRC / certificate-directed probing does not reduce black-box policy queries
   at matched certificate validity;
4. semantic lifting does not improve transfer across controller/action charts;
5. a second frozen policy family fails to provide comparable physical-contract
   evidence under the same protocol;
6. independent replication finds feasible repairs in cases covered by valid
   impossibility certificates.

## External-recognition gates

- **L8 trigger:** at least one result-bearing third-party reproduction or
  maintained robotics-runtime adoption/merge.
- **L9 trigger:** independent implementation/comparison plus sustained external
  citation, reuse, or ecosystem adoption.

Neither is claimed by this self-authored capsule today.
