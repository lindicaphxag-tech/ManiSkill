# ManiSkill #1495 Interaction Evidence Capsule

This directory records a falsifiable validation trail for the delta-pose rotation conversion issue discussed in upstream ManiSkill issue #1138 and pull request #1495.

## Frozen identities

- Upstream baseline: `mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- Converter repair (#1495): `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- Controller sign repair (#1472): `VihaanAgarwal/ManiSkill@eed9be164797d41540421bda8adb3840377d7087`

The comparison uses the same official `PegInsertionSide-v1` motion-planning demonstrations and the `pd_ee_delta_pose` control path.

## Four-way replay result

Public GitHub Actions run: **37399675564**

| Variant | Saved replayed episodes |
| --- | ---: |
| current main | 9 / 10 |
| converter-only | 1 / 10 |
| controller-only | 0 / 10 |
| composed converter + controller repair | 8 / 10 |

Interpretation:

- Both singleton repairs cause a large execution-domain regression relative to the current main branch.
- Composing the two repairs recovers most replayability.
- The composed repair is still below the current-main replay baseline, so this result does **not** establish execution-domain non-regression.

This is therefore an interaction result, not a merge claim.

## Core falsified implication

The evidence falsifies the naive implication

```
local repair correctness => safe activation
```

for this software boundary.

The current authorization logic is instead treated as a sequence of independent gates:

```
local semantic fidelity
    -> interaction compatibility
    -> execution-domain non-regression
    -> policy-level validation
```

A repair can pass an earlier gate and fail a later one.

## Claim boundary

The replay assay diagnoses trajectory-conversion / controller interaction on official demonstrations. It does **not** measure Diffusion Policy training quality and is not a substitute for the maintainer-requested policy-training experiment.

## Public validation surfaces

The fork validation PR is:

- https://github.com/lindicaphxag-tech/ManiSkill/pull/1

The validation branch contains:

- direct converter-to-controller SO(3) semantic-fidelity measurement;
- controller-aware converter experiments;
- four-way interaction replay;
- paired 100-demo replay with episode-level discordances and exact McNemar statistics;
- exact-source and environment checks.

## Decision rule

Do not upstream or train on a candidate merely because local unit tests pass.

A candidate may advance only when:

1. source / implementation identity is frozen;
2. direct semantic fidelity passes;
3. interaction tests do not reveal a compensating defect that makes singleton activation unsafe;
4. execution-domain replay is non-regressive under a preregistered comparison;
5. only then, policy-level training is used as the final effect test.

Negative and null outcomes are retained.
