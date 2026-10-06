# Paired Semantic-Fidelity Result V2 — Episode-Cluster Interaction Certificate

Status: **public paired real-stack semantic evidence with episode-cluster uncertainty**

Successful workflow: **37401619096**  
Job: `paired-semantic-fidelity`  
Public fork: `lindicaphxag-tech/ManiSkill`  
Task source: official `PegInsertionSide-v1` motion-planning demonstrations

This V2 record supersedes the *statistical status* of
`PAIRED_SEMANTIC_FIDELITY_RESULT_V1.md` while leaving V1 immutable as the
point-estimate history. V2 does not supersede the execution/replay gate.

## Frozen four-cell comparison

- main: `mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- converter-only: `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- controller-only: `VihaanAgarwal/ManiSkill@eed9be164797d41540421bda8adb3840377d7087`
- composed: exact #1472 + #1495 code composition

Every cell is evaluated offline on **identical requests within a corpus**:
delta pose, episode identity, within-episode order, and controller normalization
context are held fixed.

The inferential unit is the **episode**, not the control call. Confidence
intervals use episode-cluster bootstrap over 10 trajectory clusters.

## Corpus A — baseline-generated

Corpus SHA-256:
`dda14afa5f087cca59d16a4f3eeb0c5101e50a368bca67799ee5afce0e651099`

- episodes: 10
- requests: 1,640

Episode-weighted mean SO(3) target error:

| Cell | Mean error |
|---|---:|
| main | 0.0198999° |
| converter-only | 2.7191730° |
| controller-only | 2.7166088° |
| composed | **0.0139691°** |

Paired episode-cluster effects (95% bootstrap interval):

| Effect | Episode mean | 95% CI |
|---|---:|---:|
| converter − main | +2.69927° | **[+2.15905°, +3.23113°]** |
| controller − main | +2.69671° | **[+2.14994°, +3.22807°]** |
| composed − main | −0.005931° | **[−0.006924°, −0.005170°]** |
| composed − converter | −2.70520° | **[−3.21805°, −2.14137°]** |
| composed − controller | −2.70264° | **[−3.22394°, −2.15321°]** |

Additional frozen summaries:

- `strict_compensating_bundle_episode_weighted = true`
- fraction of calls where both singleton repairs are worse than main:
  **0.9134**
- fraction of calls where composed is no worse than main:
  **1.0**

## Corpus B — composed-generated

Corpus SHA-256:
`a1eb1ff0ebf93f7d827419b555f287b348d52db74b296b7f30459d7b411932f4`

- episodes: 10
- requests: 1,649

Episode-weighted mean SO(3) target error:

| Cell | Mean error |
|---|---:|
| main | 0.0212494° |
| converter-only | 2.8296431° |
| controller-only | 2.8268872° |
| composed | **0.0143369°** |

Paired episode-cluster effects (95% bootstrap interval):

| Effect | Episode mean | 95% CI |
|---|---:|---:|
| converter − main | +2.80839° | **[+2.16896°, +3.51378°]** |
| controller − main | +2.80564° | **[+2.16613°, +3.49495°]** |
| composed − main | −0.006912° | **[−0.008637°, −0.005524°]** |
| composed − converter | −2.81531° | **[−3.50526°, −2.15717°]** |
| composed − controller | −2.81255° | **[−3.52183°, −2.17933°]** |

Additional frozen summaries:

- `strict_compensating_bundle_episode_weighted = true`
- fraction of calls where both singleton repairs are worse than main:
  **0.9072**
- fraction of calls where composed is no worse than main:
  **1.0**

## Statistical conclusion

Across **two independently generated request distributions**, the
episode-cluster bootstrap supports the same interaction structure:

1. the converter-only repair is materially worse than current main;
2. the controller-only repair is materially worse than current main;
3. the composed repair has lower semantic error than current main;
4. both singleton-harm intervals remain entirely above zero;
5. the composed-minus-main interval remains entirely below zero.

Thus the compensating interaction is not an artifact of treating thousands of
temporally correlated control calls as IID observations.

This is evidence for a **semantic repair interaction certificate**:

`locally correct R1 + locally correct R2 + compensating latent defects
=> singleton activation is not a safe deployment unit`.

## Relation to semantic epistasis

For a minimizing semantic loss `L`, define:

- `H1 = L(R1) - L(∅)`
- `H2 = L(R2) - L(∅)`
- `R12 = L(R1⊕R2) - L(∅)`
- `E12 = L(R1⊕R2) - L(R1) - L(R2) + L(∅)`

The call-weighted point estimates from the two frozen corpora yield strongly
negative second-order interaction terms (approximately −5.56° and −5.83°),
consistent with compensating semantic epistasis. V2's primary inferential claim,
however, is based on the episode-cluster paired contrasts above rather than on
per-call pseudo-replication.

## Deployment boundary

This statistical result authorizes **neither** singleton deployment nor the
composed repair by itself.

The official-demo replay gate remains separate. Existing public replay evidence
shows that singleton repairs collapse replayability while the composed repair
recovers substantially, but composed has not yet established strict
execution-domain non-regression versus main.

Therefore the current authorization logic is:

```text
semantic interaction gate:
  R1 alone     -> reject
  R2 alone     -> reject
  R1 + R2      -> advance

execution-domain gate:
  R1 + R2      -> still pending / not yet authorized
```

This separation is itself a central systems result:

**semantic restoration and task-level non-regression are orthogonal deployment
obligations.**

## Claim boundary

- paired identical requests within each corpus: **yes**
- two frozen request distributions: **yes**
- episode-cluster bootstrap: **yes**
- confidence-supported singleton harm: **yes**
- confidence-supported composed semantic improvement: **yes**
- external maintainer adoption: **no**
- independent external reproduction: **no**
- task-level composed non-regression: **not established**
- Diffusion Policy improvement: **not claimed**
- prospective I2: **no**
- real-robot safety: **no**
