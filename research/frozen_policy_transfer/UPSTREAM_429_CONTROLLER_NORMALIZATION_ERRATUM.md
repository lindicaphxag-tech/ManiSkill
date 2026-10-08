# Upstream issue #429 — corrected controller-normalization diagnosis

This technical correction documents an **error in an earlier contributor comment** at [official ManiSkill issue #429, comment 6015654790](https://github.com/mani-skill/ManiSkill/issues/429#issuecomment-6015654790).

**Earlier incorrect explanation:** I suggested that conversion `pd_joint_delta_pos -> pd_joint_pos` fails due to unconditional double-normalization of a physical absolute target by the target `PDJointPosController`. The maintained Panda configuration **does not support that assertion**.

**Verified against official ManiSkill main `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`:**

- [`mani_skill/agents/robots/panda/panda.py`](https://github.com/mani-skill/ManiSkill/blob/62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3/mani_skill/agents/robots/panda/panda.py) configures `arm_pd_joint_pos = PDJointPosControllerConfig(..., lower=None, upper=None, normalize_action=False)`.
- The source `arm_pd_joint_delta_pos = PDJointPosControllerConfig(... lower=-0.1, upper=0.1, use_delta=True)` inherits `normalize_action=True` from the base [`pd_joint_pos.py`](https://github.com/mani-skill/ManiSkill/blob/62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3/mani_skill/agents/controllers/pd_joint_pos.py), unless overridden at runtime.
- Thus the *source* normalized `[-1,1]` action must be decoded into the actual physical delta, but the Panda *target* absolute `pd_joint_pos` controller expects physical absolute joint targets, NOT a second normalized encoding. If current source position is `q` and the controller semantics are achieved-relative, the nominal joint target is `q + delta_physical`; representability, controller state, step timing, saturation and true replay still need checking.
- The original report of zero replay success on #429 is **not explained by 'the physical target being normalized a second time'** for this particular Panda target configuration. That root-cause claim is withdrawn; the true cause of the 0% figure is still unverified.

**Engineering follow-up necessary for a credible fix:** source/destination controller configuration and full generated original trajectories, source vs target `qpos`, target `_target_qpos` and actual controller input, action clipping and task-level replay. A one-step identity is NOT an exact replay guarantee.

**GitHub edit-permission limitation:** The connected GitHub integration returned **HTTP 403 Resource not accessible by integration** when attempting to update the author's original upstream issue comment. This document is a public correction in our own contributor fork, but does **not** replace the upstream comment. The original author can edit the original comment directly in the GitHub website.

Separate work: upstream [#1495](https://github.com/mani-skill/ManiSkill/pull/1495) addresses **EE delta-pose rotation encoding**, not this #429 joint-delta-to-absolute-position issue. Do not conflate those two defects.

_Scientific-integrity note: public admission of this false normalization mechanism is more valuable than maintaining an inaccurate upstream explanation._
