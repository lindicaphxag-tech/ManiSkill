# ManiSkill #1495 — maintainer decision packet

This is the current one-page handoff for upstream
[mani-skill/ManiSkill#1495](https://github.com/mani-skill/ManiSkill/pull/1495).

## Decision summary

**Current #1495 is reviewer-ready as a standalone two-file patch.**

The converter no longer hard-codes a particular rotation sign convention. It
probes the active `PDEEPoseController` production action mapper, extracts the
signed axis-separable rotation scale, and encodes the target XYZ-Euler delta in
that active action chart.

Unsupported mappings fail explicitly rather than silently guessing.

## Frozen current identities

- upstream #1495 head:
  `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`
- PR shape:
  **1 commit / 2 files**
- converter blob:
  `438c4c41c7fe067194d8e090b9114ad0b5251128`
- focused test blob:
  `71254e58d690c2d4d8690eea4c6b8f637f157dd4`
- exact #1472 compatibility head:
  `eed9be164797d41540421bda8adb3840377d7087`
- #1472 controller blob:
  `bc4e811f336ef67d0f6cccf30116be238bb4031d`
- #1472 controller-test blob:
  `ce7e6e66cf3e286168d3d82f763307e18b587659`

## Exact-current-head compatibility closure

Canonical public workflow:

**https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37687749068**

The workflow first proves that the production/test blobs are byte-identical to
the current squashed upstream PR head.

### A. Current / legacy mapper

Result:

```text
tests/test_action_conversion.py
13 passed
```

Coverage includes:

- compound XYZ rotations;
- seeded 128-case quaternion/Euler round trip;
- anisotropic signed scales;
- zero-scale rejection;
- non-axis-separable mapping rejection.

### B. Exact #1472 mapper

The second job overlays the exact #1472 controller and controller-test blobs,
verifies their hashes, and runs the same current converter against that mapper.

Result:

```text
tests/test_action_conversion.py
tests/test_pd_ee_pose_controller.py

18 passed
```

Therefore #1472 is a tested compatibility environment, not a prerequisite for
reviewing or merging current #1495.

## Native controller evidence

Kaggle v15 checked out the same exact current head
`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0` on a Tesla T4 and ran the upstream
conversion tests plus a native PickCube controller assay:

```text
14 passed
```

The run records a hashed `pip freeze --all` environment snapshot.

Artifacts:
https://github.com/lindicaphxag-tech/ManiSkill/tree/research/native-delta-pose-assay/research/kaggle_native_assay/results/pr1495_head_v15

Narrow native measurement:

- unsaturated one-step controller-target error:
  **5.36e-9 rad** for current #1495;
- legacy axis-angle baseline:
  **1.06e-3 rad**.

The saturated 16-step case is mixed (**0.228 vs 0.212 rad**), so this packet
makes no broad performance or task-success claim.

## Historical compensating-fault evidence

Earlier converter/controller versions exposed a genuine interaction:

```text
old converter + old controller   ~= 5.0767 deg
old converter + #1472            ~= 64.7473 deg
old #1495 + old controller       ~= 66.1280 deg
old #1495 + #1472                ~= 4.83e-06 deg
```

That result is retained as historical diagnosis, not as the merge argument for
current #1495.

Current #1495 addresses the review concern by asking the active production
mapper which signed chart it actually implements rather than assuming one.

## Single maintainer question

**Is deriving the converter's signed per-axis rotation action scale from the
active `PDEEPoseController._clip_and_scale_action` mapper the intended current
controller contract?**

If yes, the current upstream PR can be reviewed on its existing one-commit,
two-file diff.

## Evidence boundary

This packet establishes:

- exact-current-head regression coverage;
- compatibility with both the current/legacy mapper and exact #1472 mapper;
- one deterministic native-controller reproduction.

It does **not** establish:

- learned-policy task success;
- arbitrary-controller replay equivalence;
- compatibility with a future ManiSkill 4 controller rewrite;
- maintainer acceptance or upstream adoption.

All evidence here is self-authored public evidence until a maintainer or third
party independently validates or retains the patch.
