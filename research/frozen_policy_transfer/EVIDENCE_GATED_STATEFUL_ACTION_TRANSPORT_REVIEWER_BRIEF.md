# Evidence-Gated Stateful Action Transport
## Reviewer brief · public research fork · 9 October 2026

**Research question.** How can an unchanged learned manipulation policy keep acting when two controller modes have numerically identical actions but different *hidden commanded-target memory*, including cases where an earlier command's actual execution is unknown?

**Status.** Owner-operated, source-pinned official ManiSkill PhysX experiments, frozen externally published ActionShift PPOs, multiple failure-mode and ablation checks. **Not peer reviewed**, no independent robotics-lab reproduction, no hardware guarantee, no novel generic POMDP or minimax theorem.

### The mechanism in three sentences

In an achieved-relative controller, the physical target is decoded against the *current measured achieved pose*. In an accumulated-target controller, the same numeric action is decoded against *the previously commanded target*, an internal history state not necessarily recoverable from current achieved pose. A successful adapter must preserve the physical goal **and** justify the state provenance used in the inverse action.

A verified executed-command history permits target reconstruction with a separately implemented observer; if delivery is uncertain, maintain a set of possible target histories rather than silently asserting a single state. For a known bounded target-control chart, an admissible common action can be issued when its worst-case **commanded-setpoint** position/orientation error is within a fixed budget; otherwise a conditional method can spend **one additional authoritative target-state observation** or refuse.

#### Formal decision contract (conditional, not a robot safety certificate)

For an attested controller transition `F`, known candidate previous targets `H_t`, desired source-frame target `D_t`, legal native controls `U`, and declared tolerances `eps`, select a *common* command minimizing the maximum setpoint discrepancy. **Authorize** only if the computed bound is met under *every attested hypothesis*, the actual frame/unit/controller update is verified, and state evidence is not stale or incomplete. Otherwise **query for additional authorized state information or refuse**. This is standard set-membership/robust optimization applied to a very specific controller interface; claimed benefit must be established empirically against strong, equal-information baselines.

### Audited genuine closed-loop evidence, not combined into a single pooled trial

| Study | Precommitted original task states | Crucial paired observation | Interpretation |
| --- | ---: | --- | --- |
| Independently implemented command-history observer | 64 (PullCube + StackCube, separate unseen seeds) | Observer 57/64; continuously privileged memory 57/64; matched achieved-pose substitute 11/64 | Deterministic target history can replace per-action private reads **when acknowledgements are trusted** |
| Missing ACK after actual physical command execution + single privileged recovery read | 16 different states | Recovered observer 16/16; matched memory-blind projection 5/16 | Recovery is possible using **one privileged target-state read**; does not establish sensor-free recovery |
| Unknown physical command execution, two fault truths and zero private readbacks | 64 paired task-truth conditions | Zero-readback midpoint 43/64; optimistic execution assumption 48/64; one target-state read 62/64 | Naive midpoint does **not** outperform the optimistic baseline; negative evidence is part of the result |
| **Fixed-budget robust-or-query** under actual zero-arm-delta injection | **16 new states** | **Selectively query 4 times** versus 16 compulsory queries, **15/16 vs 15/16 task successes**; zero-query robust 11/16; optimistic unverified 6/16 | Promising **information-efficiency** mechanism, but not established for both true/false execution or noisy sensors |
| Executed vs zero-delta controller command, public qpos/qvel evidence | 16 additional two-world states | At fault, the largest joint-position gap exceeds 0.001 rad for every original paired case even with target memory excluded | Existence of *counterfactual physical-motion separation*, **not** inference from one noisy live trace |

**No double counting:** the experiments use different designated seed cohorts and answer different questions; some world-pairs share the same reset seed. Do not turn 16 physical state contrasts into 16 independent robot policies or pretend any result is a new independently trained VLA.

### One-command third-party scrutiny

- [Permanent original observer source rows + SHA-256 manifest](evidence/independent_history_observer_64)
- [Permanent original privileged-ACK recovery rows](evidence/physical_ack_loss_resync_16)
- [A one-command Python-stdlib-only hash and outcome verifier](review/README.md), available after cloning the public fork:
  `python research/frozen_policy_transfer/review/verify_stateful_abi.py`
- [Original frozen bounded-or-query seven-arm real PhysX CI #37826881229](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826881229) (precommitted 16-state protocol and all original source artifacts).
- [Original 64 task-truth-state negative midpoint experiment](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536); permanent [evidence](evidence/belief_minimax_prospective_64_96001_97016).
- [Public-motion two-world original real PhysX run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826808073).
- **Actual new-seed simulator runner:** [External one-click ACK-fault frozen PPO replication](../../.github/workflows/external-ack-frozen-ppo-replication.yml). On a third-party fork: GitHub Actions → select `workflow_dispatch` → choose task, fault truth, and fresh seed interval → preserve complete JSON/artifacts. The workflow's author-run CI passing does **not** prove an outside lab has reproduced anything.

### Mandatory external falsifiers before claiming a strong general method

1. **Both physical fault truths:** command actually executed and neutral-delta replacement, on entirely fresh seed cohorts, with the same frozen 5 cm/0.05 rad command-setpoint tolerance and seven-arm controls. [Preregistered 32-condition protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/robust-or-query-two-truth-32-20261009/research/ACK_BOUNDED_QUERY_TWO_TRUTH_32_PRECOMMIT_V1.json); as of authoring, no final result is claimed.
2. **Equal information budget:** selectivity versus a fixed 4-read policy and a no-private-target state estimator. A continuously privileged model and a one-read oracle are **unequal-information** comparisons.
3. **True active public-sensor inference:** a single actual robot's noisy qpos/qvel trace, demonstrably without target-memory fields, matching a precommitted model-mismatch/noise range. Counterfactual simulator-world separation alone cannot prove active state identification.
4. **Different controller/robot implementations and contact-aware risk:** existing Fetch/XArm6 native setpoint checks do not establish learned policy transfer or safe force/control at contact.
5. **Genuine external execution:** another author/team independently runs fixed methods on new seeds, reports *every* negative, and records their own provenance. Fork cloning by the contributor is not independent adoption.

### Scope and honest claim

The valuable scientific object is **what evidence suffices to authorize an action under hidden controller state and what additional information must be acquired when it does not**. The strongest current *positive* owner-run result is **information-efficient selective controller-state readback**; the strongest *negative* result is that naive zero-readback midpoint adaptation is not reliably better than assuming execution. The desired next method is a model-aware, sensor-trust-aware gate that must **earn** its task-level value on withheld fault truths and matched information-cost baselines.

### External upstream contact and actual adoption status

Officially merged EEG work is separate: [Braindecode NeuroRVQ #1218](https://github.com/braindecode/braindecode/pull/1218) and [tokenizer #1223](https://github.com/braindecode/braindecode/pull/1223) were merged by non-contributor maintainers; Braindecode #1218 additionally received maintainer-run EEG validation. In robotics, [official ManiSkill #1495](https://github.com/mani-skill/ManiSkill/pull/1495) remains open and [ActionShift author's opt-in issue #1](https://github.com/Archerkattri/actionshift/issues/1) awaits external response. Owner-run simulation, source checks and internal fork merges must **never** be counted as robot-method external acceptance.
