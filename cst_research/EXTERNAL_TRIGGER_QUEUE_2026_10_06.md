# External Recognition Trigger Queue — 2026-10-06

This queue is intentionally narrow.  The goal is not PR volume; it is to turn
the CST research line into maintained external evidence.

## Priority 1 — ManiSkill #429

**Status:** diagnosis posted by `lindicaphxag-tech`; maintainer reply pending.

External signal:
- public issue reports 0% `pd_joint_delta_pos -> pd_joint_pos` conversion;
- maintainer previously called fully accurate action-space conversion highly
  non-trivial and potentially conference-worthy.

Ready now:
- minimal branch `fix/joint-delta-to-joint-pos-pr`;
- exactly 2 files / 2 commits;
- focused base-fail / fix-pass regression;
- clean research/upstream separation.

Trigger:
- maintainer confirms semantics or asks for PR.

Next action after trigger:
- open the minimal upstream PR immediately;
- keep CST research code out of the upstream diff;
- respond to review with trajectory/replay evidence, not extra abstraction.

Recognition value: **highest**, because it directly connects the research
question to a real failure in the same stack.

## Priority 2 — robomimic #270

**Status:** maintainer `amandlek` explicitly said "Happy to accept a PR";
no user fork is currently available through the connected GitHub installation.

Ready now:
- tested absolute->delta OSC semantic core;
- inverse action scaling;
- SO(3) inverse composition;
- achieved / desired reference semantics;
- robosuite <=1.4.1 and >=1.5 controller-layout handling;
- explicit saturation evidence;
- staged upstream-style `robosuite_add_delta_actions.py`;
- minimal integration plan for `convert_robosuite.py` and
  `extract_action_dict.py`.

Public full-suite evidence:
- run `37471248763`;
- `75 passed in 3.20s`.

Manual unblock:
- fork `ARISE-Initiative/robomimic` into `lindicaphxag-tech/robomimic`.

Then:
- transplant candidate to a clean branch;
- run actual robomimic dataset delta->absolute->delta replay;
- open PR referencing #270.

Recognition value: **very high**, because the maintainer has already invited the
feature and it provides an independent stack for the CST thesis.

## Priority 3 — LeRobot #3312

**Status:** issue is open and assigned to maintainer `pkooij`; maintainer
explicitly said ACT support is not implemented and invited an ACT PR. No
matching upstream PR is currently found.

Ready now:
- current-main audit;
- ACT-specific relative-action configuration / processor candidate;
- public pinned-current-main validation already recorded in the evidence ledger;
- regression checks default behavior, processor ordering, gripper exclusion and
  action-queue anchor lifetime.

Manual unblock:
- fork `huggingface/lerobot` into `lindicaphxag-tech/lerobot`.

Then:
- transplant only the narrow ACT candidate;
- rerun against latest main;
- open maintainer-invited PR referencing #3312.

Recognition value: **high**, and coherent with CST reference-ownership /
causal-deployability work, but secondary to #429 and robomimic because the CST
flagship should not become a collection of unrelated upstream patches.

## Current recognition boundary

Count as external evidence only after one of:
- maintainer technical response;
- upstream PR review;
- upstream merge;
- maintained downstream use;
- independent reproduction.

Do not count:
- author's fork CI;
- author's own branch;
- staged candidate code;
- issue links without interaction.

Current maintained external adoption of CST: **0**.
Current status: **L8-candidate, not L8 achieved; not L9**.
