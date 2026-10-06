# Upstream Handoff — ManiSkill delta-pose rotation semantics

## Decision in one sentence

**Do not merge the converter-only repair (#1495) or controller-only repair (#1472) as an isolated semantic fix until the joint converter/controller boundary passes both semantic-fidelity and execution-domain non-regression gates.**

## Why this matters

The two boundaries currently contain interacting rotation-semantics defects.

On the same first 10 official `PegInsertionSide-v1` motion-planning demonstrations:

| Variant | replay success |
| --- | ---: |
| current main | 9 / 10 |
| converter-only #1495 | 1 / 10 |
| controller-only #1472 | 0 / 10 |
| #1472 + #1495 | 8 / 10 |

Public workflow: `37399675564`.

This means a locally correct repair can make the end-to-end system dramatically worse because another compensating fault remains active.

## Mechanism-level evidence

A direct converter→controller SO(3) fidelity assay using production functions reported:

| Variant | mean rotation error |
| --- | ---: |
| current main | 0.018963° |
| converter-only #1495 | 161.489889° |
| controller-only #1472 | 161.486206° |
| #1472 + #1495 | 0.017321° |

Public workflow: `37399675762`.

Interpretation: main's two faults substantially compensate at the local converter/controller boundary; either singleton exposes the remaining fault; the composed repair restores near-zero semantic error.

This result is mechanism evidence, not policy-performance evidence.

## Stronger paired assay

The follow-up freezes immutable request corpora, hashes them, and evaluates all four implementations on exactly the same requests.

The current version additionally binds every request to:

- source `episode_id`;
- `step_in_episode`;
- controller bounds/configuration;
- corpus SHA-256.

Inference uses **episode-cluster bootstrap**, so temporally correlated control calls are not treated as IID samples.

Current public workflow: `PR1495 paired semantic fidelity`.

## Recommended upstream path

1. Treat #1495 and #1472 as one interaction-sensitive boundary for review.
2. Use direct semantic fidelity to decide whether the representation/sign contract is correct.
3. Use replay non-regression to decide whether the corrected semantics can be activated safely in the current stack.
4. Only after those two gates pass, run the maintainer-requested Diffusion Policy experiment.
5. Retain migration notes for downstream policies/code that may have learned or hard-coded the old sign convention.

## Claim boundary

What is established:
- representation/sign interaction exists;
- singleton activation can be catastrophically non-monotone;
- the composed repair restores local rotation semantics.

What is **not** established:
- composed repair is replay-non-regressive (latest 10-demo result is 8/10 vs main 9/10);
- Diffusion Policy performance improves;
- real-robot safety.

## Public evidence

Validation PR:
https://github.com/lindicaphxag-tech/ManiSkill/pull/1

Evidence capsule:
`validation/pr1495/EVIDENCE_CAPSULE.md`

Direct semantic result:
`validation/pr1495/SEMANTIC_FIDELITY_RESULT_V1.md`

The validation repository intentionally retains negative and null outcomes.
