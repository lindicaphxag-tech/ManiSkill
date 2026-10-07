# Action-sign compatibility audit

This is a static derivation from the public PR heads, not an empirical robot
rollout. The earlier version of this note was wrong: it analyzed unpublished
local branch `034e40c` as if that were the public #1495 head. It was not.

The public #1495 head before the follow-up update was `cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b`. It converts the inverse relative quaternion to the XYZ Euler representation consumed by `PDEEPoseController`; its commit message explicitly makes the conversion follow controller sign fix #1472. It returns the positive XYZ Euler vector. #1472 changes controller rotation scaling from negative `rot_lower` to positive `rot_upper`, so that representation is intended to be applied after the controller fix.

The updated public #1495 head is `875ae4d8777678119b2f192ee186c6c15e6894d5`. It probes `_clip_and_scale_action` with unit basis actions and caches each effective rotation scale, then divides the desired XYZ Euler vector by that signed scale. This makes the encoding follow the active controller implementation whether the scale is the legacy negative lower bound or the corrected positive upper bound. Regression coverage exercises both signs. The focused test file passed locally on the exact updated PR head: 9 passed, 1 warning.

The assay's treatment applies the two changed files from #1472 (`eed9be164797d41540421bda8adb3840377d7087`) on top of #1495: the one-line `rot_lower` to `rot_upper` fix and the PR's added controller tests. GitHub exposes this PR head as a root-shaped commit, so cherry-picking that commit incorrectly treats repository files as additions and conflicts. The runner instead checks the exact expected source context, applies the one-line change, and retrieves the pinned PR test file from that commit. The paired assay must still be interpreted empirically: replay and training execute on Kaggle, and this static sign analysis does not establish policy improvement.

## Evidence validity

Kernel v4 replayed raw demonstrations only once under the frozen base and reused
that converted dataset for both arms. Since the action converter changes, this
confounds the comparison. v4 policy metrics are excluded from evidence. The
prepared v5 runner regenerates the converted dataset independently under each
arm and records HDF5 and metadata SHA-256 hashes before training.
