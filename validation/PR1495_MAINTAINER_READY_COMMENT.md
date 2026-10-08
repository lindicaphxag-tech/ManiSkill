# Copy-ready maintainer handoff for ManiSkill upstream PR #1495

**Write restriction:** The connected GitHub integration returned HTTP 403
`Resource not accessible by integration` when attempting to update
[upstream #1495](https://github.com/mani-skill/ManiSkill/pull/1495).
This file is **not** posted upstream and cannot be counted as maintainer
engagement. The PR author may manually post the following *single*
focused evidence update if appropriate.

---

New source-exact official ManiSkill replay evidence for #1495: I ran the
four code interventions on 32 development source demos and a **separate
precommitted 100-demo original-source holdout (source IDs 100–199)**.

| Arm | Development (32) | Frozen held-out source IDs 100–199 |
|---|---:|---:|
| Current upstream converter + controller | 25/32 | 94/100 |
| Converter #1495 only | 25/32 | 95/100 |
| Controller #1472 only | 0/32 | **0/100** |
| Converter #1495 + controller #1472 | 25/32 | 95/100 |

Actual official simulation replay and uploaded HDF5 evidence:
[32-source workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37806000218) /
[100-source workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752565886).
The [separate owner-authored HDF5/source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37807568126)
checks source cohort identities and the paired 2×2 result.

The result is specifically **source-dependent signed-chart compatibility**:
the proposed controller sign fix alone breaks existing delta-pose demo
replay, while the source-aware converter restores it with the new controller.
The converter alone changes only one of 100 outcomes versus baseline, so
**no large success-rate or learned-policy improvement is claimed**.
There are no positive 2×2 trained Diffusion Policy recovery results yet.

Could you clarify whether source-aware signed mapping in the converter
is an acceptable compatibility fix for current ManiSkill3 despite the
planned controller redesign, or would you prefer the narrower
quaternion→XYZ conversion correction only? The PR itself remains a
focused two-file patch.

---
