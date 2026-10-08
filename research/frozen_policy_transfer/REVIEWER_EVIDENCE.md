# Stateful Action Contracts: Frozen-Policy Transfer Across Controller Reference Frames

**Research evidence dossier · 9 October 2026 · Public reviewer edition**  
**Stage: reproducible mechanistic *preprint candidate*, not an accepted paper.**

## Abstract (method and experiments, with explicit scope)

A robot action's meaning depends not only on its numerical components but also
on the controller state against which the components are interpreted. We study
training-free transfer of two released frozen PPO policies from ManiSkill's
achieved-pose-relative `pd_ee_delta_pose` controller to its
previous-target-relative `pd_ee_target_delta_pose` controller. A stateful
compiler projects each target-controller observation into the frozen
source-policy input contract, decodes the intended source end-effector goal,
and inverts the destination controller using its **actual prior target pose**.
Commands that exceed the target's normalized translation-box and rotation-ball
bounds are either refused (exact-only) or **explicitly labeled inexact**
after bounded projection.

The central controlled experiment replaces the prior-target state in the
compiler by the current achieved pose while preserving the same bounded
projection code. On 32 preregistered new PickCube seeds, the complete
compiler succeeds in **31/32** closed-loop episodes versus **4/32** for
this memory-blind ablation, with **27 paired full-only and zero
blind-only successes**. On a separately precommitted 32-seed PushCube
cohort and distinct frozen PPO checkpoint, the stateful compiler succeeds
in **29/32** versus **20/32** for the already implemented stateless
bounded control, with **11 full-only and two stateless-only successes**.
The PushCube ablation contrast was analyzed post hoc, whereas the PickCube
mechanism threshold was committed before execution. These experiments
demonstrate that live controller target memory materially matters for
reproducing successful behavior **in these two simulated tasks**; they do not
establish novel controller algebra, physical safety, VLA generality or
third-party adoption.

## Why the action-space mismatch is not solved by shape checking

For the source robot controller, the policy's normalized six-dimensional
Cartesian command produces a desired goal relative to the **achieved**
end-effector pose `T_t`:

```text
source_policy(obs_source_t) ──a_t──> F_source(T_t, a_t) = desired_goal_t
```

For the destination controller, the same nominal action represents a change
relative to the **previous commanded target** `G_{t-1}`, not to `T_t`:

```text
desired_goal_t + actual_previous_target_(t-1)
           │
           └─> F_target_inverse(G_(t-1), desired_goal_t) = target_action_t
```

A memory-blind substitute uses the achieved pose in place of the *actual
previous target*, even though target tracking and commanded target may
diverge. This corrupts the command semantics and silently accumulates
errors. If the computed target-normalized action is not representable under
the current controller's action bounds, exact authorization **refuses**.
A separate experimental branch projects into a bounded native action set
and labels that operation `NOT_EXACT`.

All policies are pretrained by a third party and are **frozen**. The
controller is an unchanged genuine ManiSkill controller; the compiler
reads the live source/target semantics and reuses the existing
model and task observations. In exact notation:

```text
G*_t = F_source(T_t, a_t)
u*_t = F_target_inverse(G_(t-1), G*_t)
u_t = u*_t       if u*_t lies in target feasible set
    = projection(u*_t)  only in explicitly inexact experimental mode
    = REFUSED      if exact-only and u*_t is infeasible
```

This formula is **known control-geometry arithmetic**, not claimed as a
new fundamental rotation formula. The result of interest is **conditional
closed-loop transfer**, plus a counterfactual probe that isolates
controller-memory dependence from simple numeric clipping.

## Frozen task-level outcomes

All numbers are **real ManiSkill PhysX CPU closed-loop task outcomes**, not
successful demonstration-file replay counts.

| Task and distinct released PPO | Observation cohort | Native PPO | Naive target | Exact-only target | Stateful bounded | Memory-blind bounded |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| PickCube | exposed development seeds 20001–20032 | 31/32 | 3/32 | 5/32 | 32/32 | not tested in this cohort |
| PickCube | precommitted task holdout 21001–21032 | 31/32 | 0/32 | 3/32 | 32/32 | not tested in this cohort |
| **PickCube** | **preregistered mechanism ablation 22001–22032** | **31/32** | **4/32** | **9/32** | **31/32** | **4/32** |
| PushCube | exposed development seeds 40001–40032 | 30/32 | 20/32 | 28/32 | 30/32 | 20/32 |
| **PushCube** | **precommitted task holdout 41001–41032** | **29/32** | **21/32** | **28/32** | **29/32** | **20/32** |

### Direct mechanism comparison (paired, no task pooling)

| Holdout task | Full only | Blind only | Both | Neither | Exact two-sided McNemar p |
| --- | ---: | ---: | ---: | ---: | ---: |
| PickCube (preregistered ablation) | 27 | 0 | 4 | 1 | 0.0000000149011612 |
| PushCube (post-hoc mechanism contrast of frozen task holdout) | 11 | 2 | 18 | 1 | 0.0224609375 |

The second p-value is **exploratory and unadjusted**, not a prospective
second task hypothesis threshold. These two cohorts differ in task
distribution and policy checkpoint and **must not** be statistically
pooled into independent identically distributed episodes. Success
within an episode is a binary achieved-task flag, not a motion-safety
criterion; the test does not correct for the multiple variants,
tasks or research questions screened throughout development.

The PickCube ablation's exact-only policy refused in **23** of 32
episodes, while the full projected policy used **27 non-exact**
bounded steps. The memory-blind bounded policy triggered **zero**
out-of-bounds projections in that cohort, despite using the same
projection code, because substituting the wrong target pose changed
the required command itself. This is an informative side effect of
the controlled mechanism change, not a third-party verified safety
result. For the prior independent PushCube task holdout, full
stateful bounded took **one** non-exact projection step while its
stateless comparator took **zero**.

## Immutable evidence and independent computational audit

- [PickCube pre-treatment memory ablation commitment](https://github.com/lindicaphxag-tech/ManiSkill/commit/1d2767400492759fc612b46efe85a7572a5e679c)
  — all 32 seeds, exact comparison and the ≥12-success net threshold
  frozen before any result.
- [PickCube real 32-episode PhysX execution](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37812437614)
  — source run `37812437614`.
- [PushCube pre-treatment new-seed task holdout](https://github.com/lindicaphxag-tech/ManiSkill/commit/872b633b68499149c7b41685a8d4b453c08f6663)
  — its memory ablation *margin* was not prespecified.
- [PushCube real 32-episode PhysX execution](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37810502800)
  — source run `37810502800`.

**One-command, no GPU reproduction of *statistical conclusions* (not simulation):**

```bash
python research/frozen_policy_transfer/state_memory_mechanism.py
```

All complete per-seed original outcome JSON files and the source-pinned
audit code live directly in this public research branch:

- `research/frozen_policy_transfer/evidence/pickcube_memory_blind_ablation_22001_22032.json`
- `research/frozen_policy_transfer/evidence/pushcube_holdout_41001_41032.json`
- `research/frozen_policy_transfer/state_memory_mechanism.py`

These files are **byte-identical Git blobs** to the source experiment
records, with expected blob commitments embedded in the public CI.
The audited test checks seed IDs, exact source-run and checkpoint hashes,
presence and identity of reported observations, per-seed binary success,
paired discordance and non-exact-step labels. Extra adversarial tests
modify the data to check refusal of forged counts, source identities
and dropped/duplicated episodes.

**Important boundary:** this is an **author-authored independent
calculation on author-generated real simulator data**; it does NOT mean
an unaffiliated third party reproduced the policy deployment or reviewed
the paper. New simulation on an independent machine requires the actual
frozen ManiSkill source and two externally hosted PPO checkpoints.

## Strong novelty veto and next external-review gate

Known action-space design, rotation parametrization, controller delta-mode
semantics, Euclidean-ball action projection and task rescaling are prior art.
See e.g. [ICML 2026, Demystifying Action Space Design for Robotic
Manipulation Policies](https://proceedings.mlr.press/v306/feng26ab.html)
and the official ManiSkill controller documentation. It would be
misleading to claim the first control-mode adapter, first discovered
stateful delta reference frame, or first physically safe correction.

**Potential next mechanism-level work:** under an *unknown source or
destination control contract*, decide with calibrated probes and
bounded intervention risk which live controller state is required, then
synthesize and verify a stateful bridge before authorizing a physical
action. This would require at least two additional task/controller
families, separately trained policies, generic active-system-
identification baselines, motion deviation/risk reporting and strict
no-adaptation/retraining comparisons.

The **most useful independent reviewer action** is reproducing one
non-favorable case, or showing a policy/controller combination where
retrieving live previous target memory provides no advantage or introduces
harm. Favor a verified counterexample over another author-written
aggregate chart.
