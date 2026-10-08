# Stateful action-interface transfer: reviewer reproduction packet

**Scope.** We used the published, frozen [ActionShift PPO weights](https://github.com/Archerkattri/actionshift) in official ManiSkill PhysX CPU on PickCube, PushCube, PullCube and StackCube, with no policy updates. This packet concentrates on the strongest two-task **independent action-history observer** mechanism check plus a distinct **unknown-acknowledgement recovery** check.

## 64 NEW-state bounded-or-query verifier (no GPU or simulator needed)

**Current primary flagship evidence:** 64 fresh frozen-policy PhysX states
with the identical locked source adapter and published ActionShift PPO weights.
Two task families, **eight** unmodified permanent source JSONs, and
**one independent zero-dependency statistical-accounting audit**.

Run from the source repository root:

```bash
python research/frozen_policy_transfer/review/verify_stateful_abi.py
```

The same command now covers **three distinct datasets**, without pooling
their participants, fixed seeds or study units: 64 original history-observer
cases, 16 original ACK-recovery cases, **64 genuinely new bounded-or-query
control cases**. Each has its own preserved raw source manifests.

**Primary new64 results, author-run PhysX, not independent reproduction:**
bounded-or-query **60/64**, compulsorily query **57/64**, zero-readback
bounded **47/64**, optimistic execution **42/64**, exact-only **0/64**.
Target readback during decisions **15** vs **64** (76.5625% fewer).
The selective and mandatory arms had **5 vs 2** paired exclusive
successes, not a statistically proven superiority claim. Action source
and original SHA digests:
[frozen results report](../ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md),
[permanent 8-file original archive](../evidence/robust_query_new64_142001_152032),
[successful independent Python 3.11/3.13 auditor CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831125554).

**Reproducibility caution:** the exact experimental runner Git blob
`1dc653cdc44e422c8340475ad00f828b3a41eb4f` was also run again
on the **same** earlier 16 seed states. All 16×7 paired success flags
matched; PullCube original JSON was byte-identical, while StackCube
had 107 floating-point last-bit differences (maximum absolute
`2.220446049250313e-16`) and zero nonnumeric changes. The rerun is
**not** a new prospective sample or independent lab test.
[Source-pinned repeat verifier](../review/compare_original_rerun.py) ·
[completed integrity workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37830812480).
## Reproduce the original score accounting in one command (Python 3.11+)

From the checkout root:

```bash
python research/frozen_policy_transfer/review/verify_stateful_abi.py
```

No GPU, pip install, model checkpoint, simulator or network required. This verifies original on-repository SHA-256s, 64 independently frozen new task states, all six-arm shard provenance, exact input seeds, pairing, projection non-exactness, and 16 physically executed commands with missing acknowledgements followed by a single trusted-state readback. A successful command means **bookkeeping over public, author-generated JSON is reproducible** — not independent rerunning of PhysX.

Original permanent unmodified files:
- [Independent external-observer implementation: 64 new states](../evidence/independent_history_observer_64), source Actions [37821114043](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37821114043).
- [Unknown-ACK with one authoritative target read: 16 new states](../evidence/physical_ack_loss_resync_16), source Actions [37822693649](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37822693649).
- Native simulator project / complete original trial code can be inspected at their source run commits. Do **not** infer new model training or hardware execution.

### Frozen PPO paired outcomes

| PhysX task / different source PPO | State count | Original source | Live-memory projected | Independent history observer | Same-projector achieved-pose substitute |
| --- | ---: | ---: | ---: | ---: | ---: |
| PullCube-v1 | 32 | 30 | 30 | 30 | 11 |
| StackCube-v1 | 32 | 27 | 27 | 27 | 0 |

The independently implemented acknowledged-action target-history recurrence and the live private-goal read had **64/64 paired binary task outcomes in agreement**. This does **not** imply identical physical trajectories, exact policy actions or hardware safety: projection intentionally approximates some commands, and the observer assumes a known initial target, known controller recurrence and reliable action delivery.

### When action delivery is unknown

Additional prespecified study: eight task states per task. After the *actual PhysX env.step* on action 3, the ACK to the action-history observer was made unknown. The observer refused unverified continuation; an **authoritative target controller state read** was then used exactly once to reinitialize the estimate. Both tasks recovered 8/8. This intervention models lost **acknowledgement**, not uncertain actual motor execution, and recovery explicitly requires privileged information. Do not claim no-sensing recovery.

An additional different study uses a public **7D state observation that already contains the target goal**; this is stronger for not calling the private getter, but **it is not a no-privileged-information claim**. Proper deployments need a measured observable/hidden-field contract and a matched-information budget.

## Smallest useful independent external falsification

A maintainer can independently reproduce the *mechanism*, without a new model training:
1. Check out the original tagged ActionShift frozen PPO and target ManiSkill controller mode, preserve exact checkpoint hash.
2. Use a newly selected source-disjoint set of reset seeds. Compare target-controller success under (a) actual previous command target + bounded projection; (b) achieved-pose substitute + identical projection; (c) independently integrated, acknowledged command history + identical projection.
3. Before any cross-run result, pin target ABI semantics, policy input projection, official success flag, episode horizon, seeds and all safety/refusal handling. Publish **every** original seed row, including failed source-policy runs.
4. Deliberately drop an ACK and distinguish: known executed; known *not* executed; unknown delivery. Report false authorization, unnecessary refusals and number of truly independent controller-state observations. Never supply target memory to a claimed unprivileged arm through an unused-looking observation channel.

**Acceptance scope requested:** if useful to ActionShift maintainers, an opt-in stateful-memory controller contract regression **not a new SOTA claim**, with one minimal causal fail/pass and a small, paired, source-pinned simulator manifest. Please accept or reject the proposal based on the project's scientific scope before any large unsolicited feature PR.

**Limits:** author-operated PhysX simulation, same Panda controller family for full policy tasks, published third-party PPOs, no VLA model, no third-party adoption, no hardware or task-safety guarantee. The existing ActionShift work already includes hidden contract identification and action-probe control; the novelty claim is constrained to controller *internal target-state observability and authority* under missing execution receipts.
