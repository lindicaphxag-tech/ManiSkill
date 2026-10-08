# Independent Reproduction Call

This public validation branch welcomes **independent reproduction, including disagreement**.

## What to reproduce

The target is the interaction between two ManiSkill delta-pose repairs on official `PegInsertionSide-v1` demonstrations.

Frozen identities:

- baseline: `mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- converter repair: `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- controller repair: `VihaanAgarwal/ManiSkill@eed9be164797d41540421bda8adb3840377d7087`

## Public hypotheses

Latest 10-demo replay evidence:

- main: 9/10
- converter-only: 1/10
- controller-only: 0/10
- composed: 8/10

Direct semantic-fidelity evidence:

- main: ~0.018963° mean SO(3) error
- converter-only: ~161.489889°
- controller-only: ~161.486206°
- composed: ~0.017321°

These values are **not acceptance criteria**. A mismatch is a useful result.

## Strong reproduction protocol

Prefer the paired semantic-fidelity protocol:

1. capture an immutable official-demo request corpus;
2. record `episode_id` and `step_in_episode`;
3. freeze the corpus SHA-256;
4. evaluate all four implementations on identical requests;
5. use episode-level, not per-control-call, statistical resampling;
6. publish raw JSON and environment metadata.

## What to publish

Please retain:

- exact source SHAs;
- Python / OS / simulator backend;
- raw result JSON;
- corpus SHA-256;
- command or workflow used;
- agreement / partial agreement / disagreement;
- any environment deviation.

A useful reproduction may be positive, null, or negative.

## Claim boundary

Independent reproduction would strengthen evidence that the interaction is real and portable. It would not by itself establish learned-policy improvement, physical safety, or upstream adoption.

## Relevant artifacts

- `EVIDENCE_CAPSULE.md`
- `SEMANTIC_FIDELITY_RESULT_V1.md`
- `REPAIR_INTERACTION_CERTIFICATE.md`
- `UPSTREAM_HANDOFF.md`
