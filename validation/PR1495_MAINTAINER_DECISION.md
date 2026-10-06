# ManiSkill #1495 — maintainer decision packet

This is a one-page handoff from the public validation work. It is intentionally
separate from the large audit branch.

## Recommended current action

**Do not merge converter-only #1495 as a standalone fix.**

The representation diagnosis is real, but current-main behavior contains a
second controller-sign semantic defect (#1469 / #1472). The defects interact,
and local correctness does not imply safe activation.

## Frozen identities

- current-main validation base:
  `mani-skill/ManiSkill@107c9528b23b55bd276cf723c260a45ae7ce00ec`
- converter-only #1495:
  `lindicaphxag-tech/ManiSkill@cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`
- controller-only #1472:
  `VihaanAgarwal/ManiSkill@eed9be164797d41540421bda8adb3840377d7087`

## 1. Direct semantic fidelity: strict interaction

Canonical workflow: **37401619096**

Two independently generated request corpora, 10 episode clusters each.

| corpus | current main | converter-only | controller-only | composed |
| --- | ---: | ---: | ---: | ---: |
| baseline-generated | 0.0198999° | 2.7191730° | 2.7166088° | **0.0139691°** |
| composed-generated | 0.0212494° | 2.8296431° | 2.8268872° | **0.0143369°** |

Both singleton fixes are worse than current main at the converter→controller
SO(3) boundary. The composed repair is semantically better.

Decision at this gate:

```text
converter-only -> reject
controller-only -> reject
composed        -> advance
```

## 2. Official-demo execution: semantic correctness is not enough

Four-way replay workflow: **37399675564**

| variant | saved official PegInsertionSide replays |
| --- | ---: |
| current main | 9 / 10 |
| converter-only | 1 / 10 |
| controller-only | 0 / 10 |
| composed | 8 / 10 |

The composed pair recovers most execution behavior but remains below main.

The stronger repeatability-qualified comparison then ran five fresh processes:

```text
current main:     {0,1,3,4,5,6,7,8,9} = 9/10, identical in 5/5 repeats
clean adapter v2: {0,3,4,5,6,7,8,9}   = 8/10, identical in 5/5 repeats
```

Canonical repeatability workflow: **37407944746**

Therefore:

```text
semantic improvement != execution non-regression
```

and the clean adapter is currently rejected at the execution-effect gate.

## 3. Strong semantic/execution decoupling

Public workflow: **37467272509**

A frozen source interpolation uses alpha = 0, 0.1, 0.25, 0.5, 1.0.

Semantic SO(3) error improves monotonically:

```text
0.0198999 -> 0.0192890 -> 0.0183792 -> 0.0168820 -> 0.0139691 deg
```

but episode-1 execution is exactly repeatable and non-monotone:

```text
success -> fail -> fail -> success -> fail
```

Five fresh-process repeats agree at every alpha.

This rules out a simple "more semantically correct = monotonically safer task
execution" assumption for this frozen protocol.

## 4. What this means for upstream

The smallest defensible upstream fix should pass both:

```text
semantic contract correctness
AND
qualified execution non-regression
```

Focused unit tests alone are insufficient for this particular coupled boundary.

I would therefore prefer one of two maintainer decisions:

1. **close/supersede #1495** until a joint converter/controller change passes
   both gates; or
2. keep #1495 as a diagnosis surface, but explicitly block standalone merge
   on the interaction with #1472.

## Single question for maintainers

**Would you prefer #1495 to be closed/superseded now, or kept open as the
converter-side diagnosis while a joint minimal fix is developed?**

No merge is being requested from this evidence packet.

## Evidence boundary

All validation above is self-authored public evidence.

It does not count as:
- maintainer review;
- upstream adoption;
- policy-training improvement;
- independent external reuse.

Negative results were retained rather than tuned away.
