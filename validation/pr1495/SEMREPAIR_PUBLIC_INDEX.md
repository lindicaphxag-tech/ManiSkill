# SemRepair Public Evidence Index

This public ManiSkill fork branch is the externally inspectable evidence surface for the current SemRepair embodied-software study.

## Research question

When latent semantic defects compensate for one another, what evidence is required before a locally correct repair is allowed to change executable robot behavior?

Current authorization model:

[
C_{identity}
\land C_{measure}
\land C_{semantic}
\land C_{interaction}
\land C_{execution}
\Rightarrow Authority.
]

Measurement qualification is:

[
C_{measure}=C_{identifiable}\land C_{repeatable}.
]

## Case A — ManiSkill: interacting converter/controller semantics

### Paired semantic mechanism

Public workflow: `37401619096`

Two independently generated frozen request corpora were evaluated with identical requests across all repair cells and episode-cluster bootstrap.

Both corpora satisfy the strict compensating-repair pattern:

[
L(R_1)>L(\varnothing),\quad
L(R_2)>L(\varnothing),\quad
L(R_1\oplus R_2)\le L(\varnothing).
]

Frozen summary:

- `PAIRED_SEMANTIC_RESULT_V1.md`

### Measurement-qualified execution result

Public workflow: `37407944746`

Five fresh-process repeats per implementation:

- current main: **9/10 × 5**, exact success set
  `{0,1,3,4,5,6,7,8,9}`;
- clean contract adapter v2: **8/10 × 5**, exact success set
  `{0,3,4,5,6,7,8,9}`.

For both variants:

- count variance: 0;
- distinct success sets: 1;
- minimum pairwise Jaccard: 1.0.

Therefore the replay channel passes repeatability qualification, and the clean v2 has a stable execution regression at **episode 1**.

Canonical result:

- `MEASUREMENT_QUALIFIED_EXECUTION_RESULT_V1.md`

Current decision:

[
C_{measure}=PASS,qquad
C_{execution}=FAIL.
]

The clean v2 remains blocked from upstream promotion.

### Stable causal target

The next public mechanism assay traces the stable episode-1 discordance in the same serial first-10 context.

It does not substitute an isolated-episode protocol for the certified replay regime.

## Case B — LeRobot: self-consistency is non-identifying

Real upstream issue:

- `huggingface/lerobot#3863`

Community fix PR:

- `huggingface/lerobot#4111`

Pinned-source public witness:

- workflow `37407845159`
- upstream SHA `8c920c4270460851cedd2737657584586d3dc66f`

The legacy forward and inverse relative-action helpers share the same positional-prefix anchor.

On a valid non-prefix state/action layout:

- forward semantic L∞ error: **59.7**
- round-trip L∞ error: **0.0**

Across 32 deterministic cases:

- maximum round-trip error: **0.0**
- minimum forward semantic error: **65.97**

Thus the evidence channel is repeatable but non-identifying:

[
C_{repeatable}=PASS,qquad
C_{identifiable}=FAIL.
]

A pure round-trip cannot authorize semantic correctness without an external semantic oracle.

## Executable measurement qualification

Public files:

- `measurement_qualification_certificate.py`
- `measurement_case_lerobot.json`
- `measurement_case_maniskill.json`

Public workflow:

- `SemRepair public measurement qualification`

Expected decisions:

- LeRobot round-trip: **reject until external semantic anchor**
- ManiSkill certified replay: **measurement qualified; advance to repair-effect gate**

Passing this gate qualifies the measurement, not the repair.

## Public replication

Independent reproduction is welcome directly in the conversation of fork PR #1.

Useful outcomes include:

- agreement;
- disagreement;
- null results;
- environment-dependent differences.

Please report exact source SHA, environment, protocol, raw output, and any deviation from the frozen design.

## External-recognition boundary

Current counts:

- independent third-party reproductions: **0**
- upstream-retained SemRepair regression tests: **0**
- upstream-retained SemRepair production fixes: **0**
- external citations to this SemRepair result: **0**

Public evidence is not counted as independent adoption.

## Core claim boundary

Supported:

- real cross-stack semantic compensation phenomena in ManiSkill and LeRobot;
- paired, same-input semantic interaction evidence;
- explicit measurement-identifiability and measurement-repeatability gates;
- a repeatability-qualified execution rejection of the current clean ManiSkill v2.

Not supported:

- universal generality across robot software;
- policy-training improvement;
- real-robot safety;
- ManiSkill or LeRobot adoption of SemRepair.
