# Upstream #1495 current-head validation handoff

The connected GitHub integration cannot edit `mani-skill/ManiSkill#1495`
(403), so this is the exact concise update to paste from the contributor account.

## Current exact-head validation

Current upstream PR head:

`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`

Public exact-head validation:

- workflow `37688339474`;
- fork evidence PR `lindicaphxag-tech/ManiSkill#38`;
- Python **3.10 / 3.11 / 3.12 all passed**;
- every job first byte-checks the two production files against that exact PR
  head;
- `tests/test_action_conversion.py`: **13 passed**;
- touched-file `py_compile`: passed;
- `git diff --check`: passed.

Python 3.13 is not included in the GitHub Actions matrix because current Linux
`mplib==0.1.1` is unavailable there. Separate Kaggle exact-head validation has
exercised Python 3.13.

The native-controller and paired semantic evidence remain supplemental and are
kept separate from this code-level gate. In particular, no blanket task
performance improvement is claimed.

Suggested one-line maintainer ask:

> Could you review whether probing the active `PDEEPoseController` action mapper is the right source of truth for trajectory conversion on current main? The current PR head now has exact-head 3.10/3.11/3.12 public validation.
