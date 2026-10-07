# Public evidence map — Controller-Semantic Transport

This file separates external observations from our method claims.

## External anchors

### ManiSkill #429 — joint delta -> joint position replay failure

Public issue:
https://github.com/mani-skill/ManiSkill/issues/429

Observed external signal:
- reported conversion success is 0% for pd_joint_delta_pos -> pd_joint_pos;
- maintainer StoneT2000 explicitly wrote that fully accurate action-space conversion is highly non-trivial and, if solved, could be conference-worthy;
- maintainer later said 0% sounds like a bug.

Our status:
- a minimal two-file patch exists on branch fix/joint-delta-to-joint-pos-semantics;
- controller-level semantic tests exist;
- full trajectory replay is still pending, so no upstream-fix claim yet.

### ManiSkill #1138 / PR #1495 — rotation representation contract

Issue:
https://github.com/mani-skill/ManiSkill/issues/1138

Our upstream PR:
https://github.com/mani-skill/ManiSkill/pull/1495

External signal:
- the issue reports near-zero Diffusion Policy success under the mismatched rotation representation and a large improvement after correcting it;
- StoneT2000 asked specifically for PegInsertionSide Diffusion Policy curves.

Our status:
- representation-level regression exists;
- frozen 20k-rotation SO(3) mismatch sweep exists;
- the requested PegInsertionSide training result is not yet claimed.

### ManiSkill PR #1472 — independent controller sign bug

https://github.com/mani-skill/ManiSkill/pull/1472

This is a separate upstream contribution by another author. It confirms that controller action semantics can be wrong even after the representation chart is correct: positive normalized rotation is scaled by a negative bound.

Research consequence:
task-level evaluation for #1495 should use a 2x2 converter-representation x controller-sign design rather than attributing a combined gain to one patch.

### robomimic #270 — inverse absolute/delta conversion demand

https://github.com/ARISE-Initiative/robomimic/issues/270

External signal:
the maintainer explicitly said they are happy to accept a PR adding absolute -> delta conversion.

Research consequence:
this is a promising independent stack for testing whether CST's hidden-state / controller-chart abstraction transfers beyond ManiSkill. No external adoption is claimed yet.

### robosuite #754 — independent action-semantics history

https://github.com/ARISE-Initiative/robosuite/pull/754

This merged upstream change added reference-frame handling and desired-vs-achieved goal update behavior to whole-body IK / devices. Its review discussion also exposed persistent previous-target and absolute-vs-delta no-op semantics.

Research consequence:
CST should treat frame and goal-update state as first-class semantic type components. This merged work is prior art / external motivation, not our contribution.

## Evidence hierarchy

The project uses the following order of evidence strength:

1. deterministic semantic witness;
2. frozen property / counterexample sweep;
3. public simulator trajectory preservation;
4. public task-level policy result;
5. maintainer-reviewed upstream patch;
6. merged upstream adoption;
7. second-stack reproduction;
8. independent reuse / citation / publication.

A lower tier may motivate a higher-tier experiment but never substitutes for it.

## Current strongest truthful statement

CST is a public method candidate with exact-family semantics, fail-closed representability, semantic typing, deterministic witnesses, and multiple independent upstream problem anchors.

It does not yet have maintained external adoption or task-level proof that the generalized abstraction improves policy performance.
