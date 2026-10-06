# SemRepair Public Evidence Snapshot — 2026-10-06 v1

This branch is a **frozen-by-convention public evidence snapshot** cut from
`1b4c5a78138e4ffa2ca1295eba31df20ec3bc2a9`.

It exists so an external reader can cite/reproduce a stable evidence state
without following the moving validation branch.

## Canonical findings

### 1. ManiSkill: compensating semantic defects

Public paired workflow: `37401619096`.

Two independently generated frozen request corpora were evaluated with identical
requests across all four repair cells. Episode—not control call—is the
inferential unit.

Both corpora support the same interaction:

```text
converter-only  > main semantic error
controller-only > main semantic error
composed        < main semantic error
```

The episode-cluster 95% intervals for both singleton harms stay above zero, and
the composed-minus-main interval stays below zero.

Canonical result:
`validation/pr1495/PAIRED_SEMANTIC_FIDELITY_RESULT_V2.md`.

### 2. ManiSkill: semantic restoration does not imply execution non-regression

Public repeatability workflow: `37407944746`.

Five fresh-process repeats per implementation:

- current main: **9/10 × 5**, identical success set each time;
- clean adapter v2: **8/10 × 5**, identical success set each time.

The execution gate therefore **rejects** the clean adapter under the frozen
protocol even though its local semantic fidelity is stronger.

Canonical result:
`validation/pr1495/MEASUREMENT_QUALIFIED_EXECUTION_RESULT_V1.md`.

### 3. LeRobot: perfect round-trip can be semantically wrong

Pinned upstream:
`huggingface/lerobot@8c920c4270460851cedd2737657584586d3dc66f`.

Public workflow: `37407845159`.

The pinned forward and inverse relative-action helpers share the same positional
prefix assumption. On a valid non-prefix layout:

- one-way semantic L∞ error: **59.7**;
- round-trip L∞ error: **0.0**;
- 32/32 deterministic sweep cases preserve exact round-trip while all 32
  forward semantics fail.

Canonical result:
`validation/crossstack/LEROBOT_MAPPING_COMPENSATION_V1.md`.

The underlying bug belongs to the LeRobot community; this snapshot claims only
the measurement-identifiability consequence.

### 4. GR00T exact-head episode-boundary validation

Upstream PR: `NVIDIA/Isaac-GR00T#786`.

Production head:
`8ca15ac4f3e76f1a4151bfd1f59572d306d99b49`.

Dedicated public validator:
`37380686525` — success on Python 3.10 / 3.12 / 3.13.

This is self-authored exact-head evidence, not maintainer adoption.

### 5. CASJ → independent SemRepair verifier bridge

Public workflow:
`37368957461`.

Python 3.10 / 3.12 / 3.13 all pass the cross-implementation certificate matrix.

This is verifier-independence evidence, not external adoption.

## External-evidence counters at snapshot time

```text
independent third-party reproductions       = 0
upstream-retained SemRepair regressions     = 0
upstream-retained SemRepair production fixes = 0
external SemRepair citations                = 0
resolved prospective I2                     = 0
```

These zeros are part of the snapshot and must not be silently upgraded by
self-authored work.

## Independent reproduction

The lowest-cost reproduction target is the LeRobot self-consistency witness.
The stronger target is the ManiSkill paired semantic-interaction assay.

Public discussion/reproduction surface:
`lindicaphxag-tech/ManiSkill#1`.

Agreement is not required. Disagreement or null evidence with exact provenance
is equally useful.

## Snapshot rule

Do not rewrite this branch to make later results look cleaner.

If evidence changes, create a new versioned snapshot rather than mutating the
claims above.
