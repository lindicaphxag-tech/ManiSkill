# Measurement-Qualified Execution Result V1

Status: **canonical execution gate for clean controller-contract adapter v2**

## Frozen identities

- current main: `107c9528b23b55bd276cf723c260a45ae7ce00ec`
- contract adapter v2: `bd0e4feae2491a0d433107210ce8c16b8e8fb69a`
- task: `PegInsertionSide-v1`
- backend: `physx_cpu`
- target control mode: `pd_ee_delta_pose`
- `--use-first-env-state`
- `--num-envs 1`
- first 10 official demonstrations

## Repeatability certificate

Public workflow:

- run `37407944746`

Artifact:

- name: `replay-repeatability-certificate`
- artifact ID: `11388196816`
- artifact SHA-256:
  `dc3452caed344a22db55716f77ea1b6d5d12baa89049ca7248a36a8721b9e3f1`

Protocol:

- 5 independent repeats per implementation;
- fresh Python process per repeat;
- identical frozen source SHA per implementation;
- identical replay arguments.

## Current main

All 5 repeats produced exactly the same success set:

[
S_{main}={0,1,3,4,5,6,7,8,9}
]

Therefore:

- success counts: **[9, 9, 9, 9, 9]**
- mean: **9.0 / 10**
- count variance: **0**
- distinct success sets: **1**
- minimum pairwise Jaccard: **1.0**
- exact repeatability: **true**

Episode 2 fails in all five repeats.

## Contract adapter v2

All 5 repeats produced exactly the same success set:

[
S_{v2}={0,3,4,5,6,7,8,9}
]

Therefore:

- success counts: **[8, 8, 8, 8, 8]**
- mean: **8.0 / 10**
- count variance: **0**
- distinct success sets: **1**
- minimum pairwise Jaccard: **1.0**
- exact repeatability: **true**

Episodes 1 and 2 fail in all five repeats.

## Measurement qualification

The replay channel is now qualified for this frozen protocol:

[
C_{identifiable}=PASS
]

because task success is anchored to the environment outcome rather than only to a paired inverse transform, and:

[
C_{repeatable}=PASS
]

because both variants reproduce identical success sets in 5/5 fresh-process repeats.

Thus:

[
C_{measure}=PASS.
]

This is important: the candidate regression is no longer being inferred from an unqualified single replay.

## Paired execution effect

The stable discordance is:

[
S_{main}\setminus S_{v2}={1}
]

while:

[
S_{v2}\setminus S_{main}=arnothing.
]

Episode 1 is therefore the single stable baseline-only success in the frozen 10-demo protocol.

Episode 2 is a shared failure and is not evidence for candidate regression.

## Authorization decision

The clean candidate fails the current execution non-regression gate:

[
C_{execution}=FAIL.
]

Therefore:

[
Authority(R_{v2})=REJECT
]

for upstream promotion under the current evidence.

CPU/value/protocol correctness and controller-sign invariance do **not** override this result.

## Relation to earlier runs

Earlier single public runs reported different aggregate surfaces, including:

- main 9/10 vs candidate 8/10;
- exact 8/10 parity.

Those observations motivated the repeatability audit.

They are retained as historical evidence but are not canonical execution certificates.

The 5-repeat fresh-process certificate is the canonical result for this protocol.

## Next causal target

The stable discriminatory episode is now **episode 1**, not episode 8.

The next mechanism assay should preserve the certified serial first-10 context and compare main vs candidate on episode 1, recording:

- requested delta pose;
- normalized converter action;
- controller-scaled physical action;
- clipping / retry events;
- controller state;
- local converter→controller SO(3) error;
- first divergence;
- terminal task outcome.

A mechanism claim should be frozen before modifying the candidate again.

## Claim boundary

Established:

- exact replay repeatability for this frozen 10-demo CPU protocol;
- main 9/10 vs candidate 8/10 in all five fresh-process repeats;
- stable baseline-only discordance at episode 1;
- execution non-regression failure for clean v2.

Not established:

- cause of the episode-1 regression;
- behavior over all ManiSkill tasks;
- learned-policy effect;
- real-robot safety;
- upstream adoption.
