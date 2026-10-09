# Compound-ACK prospective v2 — explicit post-failure correction and NEW states

**Status at freeze:** no v2 simulator outcomes observed; this document is committed before the v2 jobs. It does not modify or conceal the failed v1 native experiment.

## Why v1 stopped, and why this is a method/experiment-contract correction
The first 2026-10-09 native PhysX run [#37897829784](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37897829784) failed on both tasks while checking a conditional setpoint certificate. The issue was that one of the two commanded actions was deliberately replaced by a native **zero/hold fault**, but the post-dispatch audit incorrectly checked the counterfactual *requested* action as though it had executed. No complete task-success denominator was produced in v1. This invalidates any claim of v1 successfully running or satisfying the simulated physical target bound.

The v2 audit records such masked actions explicitly and checks **only physically dispatched actions** after environment stepping. Any dispatched action outside its claimed position/orientation error envelope still raises a fatal exception with task, seed, arm, step, measured residual and certified limit. The audit-only controller target getter remains barred from decision making.

## Frozen test cohort
- 8 entirely **new** state seeds per task: PullCube 380001–380008, StackCube 390001–390008; the earlier 360001/370001 family were **partially inspected in the failed debugging run** and are not reused as an untouched prospective set.
- Unchanged external frozen PPO releases, verified original command semantics and original finite-belief class; 7 matched native PhysX control arms, 50 native steps, 2 consecutive arm target-hold faults at t=2/t=3 with unknown ACK.
- One controller-state query for selective bounded-or-query; mandatory read at t=4 if the episode survives, zero for bounded/no query.
- A conservative multi-history position/SO(3) certificate allows 1–16 explicit target-memory hypotheses. Candidate rotation search is not globally optimal; every authorized command must satisfy the exact source-controller setpoint residual on every enumerated possible memory state.
- Use 0.05 m infinity-norm and 0.05 rad geodesic error budgets. Compare real task success and decision target reads; record maximum belief width and fault-masked authorized commands.
- Real robot collision/force/trajectory safety, teleoperation, true packet loss, second robot embodiments, strong active-sensing baselines and external-lab replication are *not* claimed.
- Do not silently discard false authorizations, failed original tasks, or missing fault-reach worlds. A failure is an experimental result.

## Original-source identity
- Unmodified single-ACK PhysX source Git blob: `1dc653cdc44e422c8340475ad00f828b3a41eb4f`.
- Unmodified 2-state geometry blob: `bb5fd155b7291fb127f94138fca321201c8271c3`.
- Third-party pretrained PPO SHA256, Pull: `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`, Stack: `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`.
