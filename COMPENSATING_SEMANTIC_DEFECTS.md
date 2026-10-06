# Compensating Semantic Defects in Robot Software

Status: **public research artifact / causal evidence surface**

This branch is intentionally minimal. It does not modify ManiSkill production
code and does not claim upstream adoption. It provides a compact, externally
auditable summary of a real semantic interaction uncovered while validating:

- `mani-skill/ManiSkill#1495` — delta-pose rotation representation repair;
- `mani-skill/ManiSkill#1472` — independent controller rotation-sign repair.

## Core finding

Two locally incorrect semantic boundaries can partially compensate.

In that regime:

1. the current system may look approximately correct;
2. repairing either defect alone can make behavior dramatically worse;
3. repairing both restores the intended local semantics;
4. local semantic correctness still does **not** imply task-level non-regression.

This is the failure mode we call **compensating semantic defects**.

The interaction matters because it falsifies the deployment heuristic:

```text
local repair correctness -> safe singleton activation
```

A safer authorization unit is the **interaction-certified repair set**.

## Frozen code identities

- baseline: `mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- converter repair (#1495):
  `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- controller repair (#1472):
  `VihaanAgarwal/ManiSkill@eed9be164797d41540421bda8adb3840377d7087`

## Evidence 1 — execution replay is non-monotone

On the same first 10 official `PegInsertionSide-v1` motion-planning
demonstrations:

| Cell | Replayed trajectories saved |
| --- | ---: |
| current main | **9/10** |
| converter-only #1495 | **1/10** |
| controller-only #1472 | **0/10** |
| #1472 + #1495 | **8/10** |

Public workflow: `37399675564`.

Interpretation:

- both singleton repairs catastrophically expose the remaining defect;
- the composed repair recovers most replayability;
- the composed repair still does **not** beat the current 9/10 execution
  baseline, so deployment non-regression is not established.

## Evidence 2 — direct semantic-fidelity interaction

A production converter -> production controller assay on official-demo requests
reports approximately:

| Cell | Mean SO(3) target error |
| --- | ---: |
| current main | **0.018963°** |
| converter-only #1495 | **161.489889°** |
| controller-only #1472 | **161.486206°** |
| #1472 + #1495 | **0.017321°** |

Public workflow: `37399675762`.

The current system appears locally healthy because two sign/representation
inconsistencies substantially cancel.

## Evidence 3 — paired immutable request corpora

To remove the objection that each implementation generated a different request
distribution, a later public assay froze two request corpora and evaluated all
four implementations on identical requests within each corpus.

Successful workflow: `37401429882`.

### Baseline-generated corpus

- episodes: 10
- requests: 1,640
- SHA-256:
  `dda14afa5f087cca59d16a4f3eeb0c5101e50a368bca67799ee5afce0e651099`

Mean SO(3) errors:

| Cell | Mean error |
| --- | ---: |
| main | 0.0222448° |
| converter-only | 2.7980051° |
| controller-only | 2.7954694° |
| composed | **0.0162240°** |

Interaction quantities:

- singleton harm H1: +2.7757603°
- singleton harm H2: +2.7732247°
- composed residual R12: -0.0060207°
- semantic epistasis E12: **-5.5550057°**

### Composed-generated corpus

- episodes: 10
- requests: 1,649
- SHA-256:
  `a1eb1ff0ebf93f7d827419b555f287b348d52db74b296b7f30459d7b411932f4`

Mean SO(3) errors:

| Cell | Mean error |
| --- | ---: |
| main | 0.0237997° |
| converter-only | 2.9362814° |
| controller-only | 2.9335909° |
| composed | **0.0166679°** |

Interaction quantities:

- singleton harm H1: +2.9124817°
- singleton harm H2: +2.9097912°
- composed residual R12: -0.0071318°
- semantic epistasis E12: **-5.8294046°**

Both corpora report:

```text
paired_inputs_identical_within_each_corpus = true
strict_compensation_in_both = true
```

So the singleton regressions are not explained by request-distribution drift.

## Repair Interaction Certificate

For a minimizing semantic loss L, evaluate:

- L0 = L(no repair)
- L1 = L(R1)
- L2 = L(R2)
- L12 = L(R1 + R2)

Define:

```text
H1  = L1  - L0
H2  = L2  - L0
R12 = L12 - L0
E12 = L12 - L1 - L2 + L0
```

A strict compensating bundle requires, for tolerance epsilon:

```text
H1 > epsilon
H2 > epsilon
R12 <= epsilon
```

The authorization implication is:

- R1 alone: reject;
- R2 alone: reject;
- R1+R2: advance to an **independent execution-effect gate**.

Semantic interaction evidence is not itself physical execution authority.

## Why this is research-relevant

The result suggests a distinct embodied-repair problem:

> When multiple semantic defects compensate for one another, what evidence is
> required before a locally correct repair is allowed to change executable robot
> behavior?

This differs from ordinary single-bug repair because correctness is
**non-monotone under partial intervention**.

The research direction is therefore not "find more bugs". It is:

1. detect hidden compensation between semantic boundaries;
2. evaluate candidate repair sets factorially;
3. certify repair interactions on frozen identical inputs;
4. authorize repair sets atomically;
5. independently verify execution-domain effects after semantic correctness.

## Reproduction

The full public validation harness is on branch:

`validation/maniskill1495-maintainer-request`

Relevant files there:

- `validation/pr1495/PAIRED_SEMANTIC_FIDELITY_RESULT_V1.md`
- `validation/pr1495/REPAIR_INTERACTION_CERTIFICATE.md`
- `validation/pr1495/REPRODUCTION_CALL.md`
- `validation/pr1495/EVIDENCE_CAPSULE.md`
- `validation/pr1495/capture_rotation_request_corpus.py`
- `validation/pr1495/evaluate_frozen_rotation_requests.py`
- `validation/pr1495/run_paired_semantic_fidelity.sh`

Independent disagreement is useful evidence. A reproduction should retain exact
source SHAs, environment metadata, frozen corpus hashes, raw result JSON, and
episode-level identities.

## Claim boundary

This artifact supports:

- a real production robot-software example of compensating semantic defects;
- non-monotone singleton repair activation;
- paired causal interaction evidence;
- the need to separate semantic correctness from execution authorization.

It does **not** establish:

- Diffusion Policy improvement;
- strict task-level non-regression;
- real-robot safety;
- prospective I2 evidence;
- upstream maintainer adoption;
- novelty of proof-carrying code, semantic repair, or runtime monitoring in the
  abstract.

The upstream PRs remain independent project contributions and should be judged
on their native correctness value.
