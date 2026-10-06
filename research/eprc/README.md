# DEC / CRG — physical repairability of frozen robot policies

This public, fork-only capsule asks one deployment question:

> **Before executing a correction, can a frozen robot policy determine what is
> physically repairable, what is not, and which additional intervention would
> resolve the uncertainty?**

It is self-authored and counts as **zero external adoption**.

**Start here:** [one-page research capsule](./RESEARCH_CAPSULE.md) · [claims & falsifiers](./CLAIMS_AND_FALSIFIERS.md) · [independent replication format](./evidence/replications/README.md)

## Core contribution chain

### 1. Differential Execution Contract (DEC)

Controlled physical support interventions identify a black-box action response,
which is lifted through controller semantics into canonical physical-command
space:

```text
physical support perturbation
        -> frozen-policy action response
        -> semantic/controller lift
        -> representation-invariant local physical contract
```

Equivalent behavior can therefore be compared across absolute, delta, target-
relative, or other locally invertible action charts without comparing raw action
tensors.

### 2. Counterfactual Repairability Geometry (CRG)

DEC is converted from a descriptive object into a constructive repair set.
CRG restricts correction to the intervention-identified policy response image,
the current controller authority, and a certified local trust region.

For each requested physical correction it returns one of:

- **CERTIFIED_REPAIR** — a policy-consistent correction is supported;
- **CERTIFIED_IMPOSSIBLE** — no admissible local correction can satisfy the
  tolerance;
- **INCONCLUSIVE** — evidence is insufficient, so the runtime must not guess.

Rejections are further decomposed into robot-, policy-, authority-, or
model-limited bottlenecks.

### 3. Active Minimal Repair Certificate (AMRC)

When CRG is inconclusive, AMRC does **not** estimate the entire local Jacobian
again. It chooses only the next physical counterfactual probes that most quickly
resolve the concrete repair request and stops at the first valid certificate.

A symmetric probe costs two black-box policy evaluations, so query cost is
reported explicitly.

The CPU mechanism gate is green in public CI:
`EPRC Contract Capsule / run 37409424699`.

## Real frozen-policy gate

The branch contains an exact-state, paired-randomness probe for the official
`lerobot/vqbet_pusht` checkpoint. It freezes:

- model revision and LeRobot training-runtime commit;
- PushT state-restoration protocol;
- physical block x/y/theta intervention units;
- five RNG replicates;
- held-out disturbance;
- robust CRG tolerance and trust radius.

The report also emits an AMRC next-probe plan when evidence is inconclusive.
Planned probes are explicitly labeled as **not executed evidence** until their
observations are collected.

A historical Diffusion PushT artifact is retained even though raw CASJ
correction was harmful in the examined states. Those negative cases are part of
the motivation for CRG: a local derivative is not automatically a repair
certificate.

## LeRobot integration surface

`research/eprc/lerobot_plugin` is a standalone ProcessorStep package. CI
installs the exact current head of `huggingface/lerobot#4592`, installs the
EPRC wheel, invokes LeRobot's real third-party discovery, and executes a
fail-closed REJECT path.

This is compatibility evidence, **not LeRobot adoption**.

## 5-minute contract reproduction

```bash
python -m pytest -q \
  tests/test_eprc_runtime.py \
  tests/test_eprc_contract_signature.py \
  tests/test_eprc_repairability_geometry.py \
  tests/test_eprc_active_minimal_certificate.py

python research/eprc/reproduce.py \
  research/eprc/evidence/replication_example.json \
  --expect REPAIR
```

No simulator or GPU is required for the contract-level capsule.

## Independent replication

Issues are disabled on this fork, so independent results are accepted through
ordinary pull requests adding one digest-bound JSON record under:

`research/eprc/evidence/replications/`

Seal a record with:

```bash
python research/eprc/seal_replication.py path/to/record.json
```

Positive results are not required. Clean rejection, instability, false accept,
or false reject results are retained. Self-authored records are rejected as
independent evidence.

## Claim boundary

This project does **not** claim invention of Jacobians, nullspaces, compressed
sensing, equivariance, controller conversion, constrained optimization, active
learning, runtime safety filtering, or frozen-policy recovery.

The narrow claim under test is:

> intervention-identified, representation-invariant **physical repairability**
> can support constructive repair, impossibility certificates, and
> request-conditioned minimal probing for frozen robot policies.

## Kill gates

The flagship claim is rejected if any of the following survive fair testing:

1. perturbation magnitude or controller headroom predicts closed-loop recovery
   as well as CRG;
2. generic controller-space projection matches CRG repair success and false-
   accept rate;
3. AMRC does not reduce policy queries versus fixed/coded probing at matched
   certificate validity;
4. DEC is unstable across repeated frozen-policy probes;
5. semantic lifting does not improve transfer across controller/action charts;
6. a second policy family fails the frozen cross-policy gate.

## External-recognition gates

Self-authored CI, forks, stars, and internal merges do not count.

- **L8 trigger:** result-bearing third-party reproduction or adoption/merge by a
  maintained robotics runtime.
- **L9 trigger:** independent implementation/comparison plus sustained external
  use, citation, or ecosystem adoption.
