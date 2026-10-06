# ManiSkill #429 — ready-upstream maintainer packet

Status: **prepared, not externally submitted**

Production branch:
`fix/issue-429-joint-delta-to-pos-v6-clean`

Production commit:
`b0e1b85d5002ead77fc42a793183e5e0c72e01cb`

Upstream base:
`mani-skill/ManiSkill@62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`

Patch shape:
**1 commit / 2 files / 0 behind**

External issue:
`mani-skill/ManiSkill#429`

Contribution protocol note:
ManiSkill CONTRIBUTING asks contributors to describe the proposed change on the
issue and receive maintainer approval before opening a PR. The connected GitHub
integration cannot post to the upstream issue (HTTP 403), so this packet freezes
the exact proposed message and PR body for a human-authenticated submission.

## Proposed issue follow-up

I traced the remaining 0%-conversion path on current `main`
(`62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`) and found a narrower semantic
mismatch in `from_pd_joint_delta_pos(... -> pd_joint_pos)`.

The source trajectory action is a **normalized delta-q command**. The function
currently decodes that delta into a physical target qpos, but then writes the
physical qpos directly into the target `pd_joint_pos` action slot. When the
target controller also uses normalized actions, that slot is a different
coordinate chart, so the physical target is interpreted as if it were already
normalized.

I prepared a minimal follow-up that performs:

```text
source-native
  -> decode with source action-space bounds
  -> physical delta-q
  -> physical target-qpos
  -> re-encode with target action-space bounds
  -> target-native
```

The patch is 1 commit / 2 files and is based directly on current main. A frozen
differential check verifies the exact production blobs, shows the upstream base
failing the reproducer, and the patched path passing.

I also checked historical #549: it substantially improved joint/EE conversion,
but current main still contains this delta-pos -> normalized absolute-pos chart
mismatch.

Before opening a PR, does this re-encoding match the intended `pd_joint_pos`
conversion contract? If yes, I can send only the minimal patch + regression.

## Proposed PR title

`[BugFix] Re-encode pd_joint_delta_pos targets in pd_joint_pos action space`

## Proposed PR body

Fixes #429.

### Problem

`from_pd_joint_delta_pos(..., output_mode="pd_joint_pos")` currently crosses
three semantic spaces:

1. normalized source delta-joint action;
2. physical joint delta / physical absolute joint target;
3. target controller's native action representation.

Current main correctly constructs the physical absolute target but then passes
that physical qpos directly as the target controller action. When the target
`pd_joint_pos` controller uses normalized actions, this treats a physical qpos
as if it were already a normalized action.

This can make a nominally simple delta-position -> absolute-position conversion
diverge even though both controllers refer to the same physical joint target.

### Fix

- decode the source normalized action using the source controller's actual
  `action_space_low/high`;
- add that physical delta to the source controller's current physical qpos;
- if the destination controller is normalized, re-encode that physical target
  with the destination controller's `action_space_low/high`;
- clip only in the native normalized destination action space;
- retain direct physical qpos output for a non-normalized destination.

### Regression

The regression deliberately uses asymmetric source/destination action boxes so
passing physical qpos through as a normalized action cannot accidentally look
correct.

It checks that:

- a normalized source action decodes to the expected physical delta;
- the physical absolute target is re-encoded into the target controller chart;
- decoding the emitted target-native action reconstructs the same physical
  target;
- out-of-range normalized source inputs are clipped before physical decoding.

### Differential validation

Public validation run:
`37407332478`

The workflow first asserts exact identity of the v6 production patch, then runs
one frozen reproducer against both code cells:

- patched production head: **pass**;
- exact upstream base: **fails at the original NumPy/Torch / action-chart
  boundary**.

The run completed successfully, including the differential-evidence assertion.

### Scope / related work

Historical #549 improved joint-position / delta-position conversion to
end-effector controllers and is already in main. This patch is narrower: it
addresses the still-present `pd_joint_delta_pos -> pd_joint_pos` source/dest
action-chart conversion in current main.

No claim of exact trajectory equivalence across arbitrary controller families is
made.

## Additional research-side evidence (not required for merge)

A separate public assay uses this production path to identify which of three
candidate semantic meanings matches the observed destination action:

1. source-native passthrough;
2. physical-qpos passthrough;
3. destination-chart re-encoding.

A zero action is intentionally uninformative. An asymmetric nonzero probe
separates the three candidates, and the production observation matches
destination-chart re-encoding under an explicit `epsilon=1e-6` numeric
contract.

Public run:
`37408232594` — success.

This extra assay is research evidence only; the upstream PR should remain the
minimal native fix above.

## Claim boundary

Until the maintainer explicitly approves the proposed change and retains a PR,
this is **not** external adoption and must not be counted as an L8/L9 success.
