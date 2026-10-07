# ManiSkill #1495 — maintainer decision packet

This is the current one-page handoff for upstream
[mani-skill/ManiSkill#1495](https://github.com/mani-skill/ManiSkill/pull/1495).

## Recommended current action

**#1495 can now be reviewed independently of #1472.**

The current converter head no longer hard-codes the sign convention implied by
either `rot_lower` or `rot_upper`.  It probes the active controller's
production action mapper for signed, axis-separable rotation scale and encodes
the inverse relative quaternion into that active chart.

This removes the old merge-order dependency on #1472 while preserving an
explicit failure mode for non-axis-separable / zero / non-finite mappers.

## Frozen identities

- upstream #1495 head:
  `875ae4d8777678119b2f192ee186c6c15e6894d5`
- current converter blob:
  `438c4c41c7fe067194d8e090b9114ad0b5251128`
- current focused test blob:
  `363637b0c52828e98fe4956ab8f7bd5af7700344`
- exact #1472 head used as compatibility environment:
  `eed9be164797d41540421bda8adb3840377d7087`
- #1472 controller blob:
  `bc4e811f336ef67d0f6cccf30116be238bb4031d`
- #1472 test blob:
  `ce7e6e66cf3e286168d3d82f763307e18b587659`

## Current-head public compatibility gate

Canonical public workflow:

**https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37682148773**

The workflow has two independent jobs.

### A. Current legacy controller

Before testing, the job proves that the production converter and focused test
are byte-identical to upstream #1495 head.

Result:

```text
tests/test_action_conversion.py
9 passed
```

### B. Real #1472 controller

The second job keeps the exact #1495 converter, then overlays the exact
controller and controller-test blobs from #1472.

Result:

```text
tests/test_action_conversion.py
tests/test_pd_ee_pose_controller.py

14 passed
```

Therefore the current #1495 implementation has one demonstrated property that
the earlier converter-only head did not:

```text
current legacy signed mapper  -> pass
real #1472 positive mapper    -> pass
```

So **#1472 is now a tested compatibility environment, not a prerequisite for
merging #1495**.

## What changed relative to the old evidence packet

The previous packet was bound to converter head
`cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`.

That implementation assumed a particular signed controller scale.  Under the
then-current controller, the converter and controller defects could partially
compensate, so fixing only one side produced a strong interaction.

Those results remain useful evidence of a real compensating-semantic-fault
pattern, but they **must not be used as a merge recommendation for current
#1495**, because current head `875ae4d...` changed the production repair.

The current implementation asks the active mapper what signed chart it
actually implements.

## Historical causal evidence retained

The earlier 2x2 experiment remains useful as a diagnosis of the old boundary:

```text
old converter + old controller   ~= 5.0767 deg
old converter + #1472            ~= 64.7473 deg
old #1495 + old controller       ~= 66.1280 deg
old #1495 + #1472                ~= 4.83e-06 deg
```

This showed why a representation-only patch that assumes a sign convention can
be unsafe when another local defect compensates it.

Current #1495 addresses that exact review concern by deriving the sign/scale
from the production mapper instead of assuming it.

## Remaining evidence boundary

The current compatibility workflow establishes controller-contract correctness
for the focused conversion boundary.

It does **not** yet establish:

- improved learned-policy task success;
- exact replay equality across arbitrary controllers;
- compatibility with a future ManiSkill 4 controller rewrite;
- maintainer adoption.

A paired learned-policy / PegInsertionSide assay remains useful downstream
evidence, but the lack of that result should not be confused with an unresolved
merge-order dependency on #1472.

## Single maintainer question

**Does probing the active `PDEEPoseController` mapper for its signed per-axis
rotation scale match the intended current controller contract?**

If yes, the current #1495 can be reviewed on its own two-file diff.

## Evidence boundary

All validation here is self-authored public evidence.  It is not maintainer
review or upstream adoption.
