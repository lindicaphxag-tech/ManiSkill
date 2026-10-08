# Frozen PPO interrupted-delivery experiment — pre-outcome protocol

**Status: UNEXECUTED.** This is an implementation handoff and falsification plan, not
evidence of improved task performance. No outcome or model has been selected from these seeds.

## Scientific question
Under target-relative robot control, known reset and reliable command delivery make the
last commanded target reconstructible. If command delivery or confirmation is missing,
does a set-valued observer reduce **false exact action authorizations**, and at what cost
in task completion compared with full history, naive single-state imputation and
strong bounded-error methods?

## Frozen source stack
- Base: `research/uncertain-delivery-target-belief-20261009`.
- `research/action_abi_uncertain_delivery_belief.py`: existing model-level implementation.
- Independent no-private-getter observer: `research/action_abi_history_observer.py`.
- Third-party ActionShift PPO SHA-256 already fixed in
  `research/ACTION_ABI_HISTORY_OBSERVER_PREDECLARED_V1.json`.
- PhysX CPU; use only publicly disclosed original ManiSkill task success flags.

## Prospective cohorts and fault mechanisms
- PullCube-v1: seeds 92001–92032.
- StackCube-v1: seeds 93001–93032.
- One fault event at the first eligible timestep >= 5 in each task rollout; no
  retrospectively selected action or successful episode filtering.
- `dropped`: dispatched arm command is *not applied to target memory*; controller
  is stepped with a genuine target-neutral/no-op action implementing the unchanged
  target pose, with gripper command controlled and recorded.
- `delayed`: command execution is postponed by exactly one controller step,
  with acknowledgement likewise delayed; define exact FIFO execution order.
- `duplicate`: dispatched target-delta command is applied twice over two real
  simulator steps; record both actual execution times.
- `unknown_ack`: physical delivery is predetermined, but observer is given an
  ambiguous acknowledgement; evaluator truth is audit-only.
- `reordered`: only where a real queue exists; exchange two queued commands and
  log applied order. **Do not pretend a no-op is a network packet drop.**
- Distinguish target-memory state, achieved pose, internal action preprocess,
  root frame, rotation convention, and gripper behavior.

## Matched arms
1. Perfect-delivery oracle (reference, access to actual target memory).
2. Faulted oracle with true target-memory readback (upper bound, privileged).
3. Faulted naive point observer, treating uncertain delivery as applied.
4. Faulted set-belief exact gate, with controller memory **audit-only**.
5. Faulted equal-information interval/minimax observer (strong baseline).
6. Faulted explicit resynchronization; measure required readback frequency.

Any controller `get_state()` or `_target_pose` used in arms 3–6 for
action selection is a PROTOCOL VIOLATION. The identical same-seed source
policy must remain frozen, with identical total simulated action budget.
An exact refusal is a failed/unfinished task unless a preregistered resync
recovers it. Bounded projections must be marked NON-EXACT.

## Primary endpoints
1. **False authorization**: an arm declares an action EXACT but its actual
   executed target differs from intended target beyond 1e-4 m position or
   1e-3 rad orientation after controller stepping, when the intended exact
   reference is actually representable.
2. **Task success**: original ManiSkill `info['success']`, per arm/seed.
3. **Abstention**: episodes and individual commands refused because of ambiguity.
4. Controller target and achieved-pose error distributions, contact/limit
   events when exposed; explicitly record unavailable metrics.
5. Rescue cost: number of resynchronizations, extra actions and lost steps.

Report denominator 32 for each task+fault combination, every seed and all
runtime crashes. Separate task-level uncertainty from matched-pair uncertainty.
Do not pool episodes as independent policies.

## Precommitted interpretation
- Evidence for a safety-relevant *algorithmic authorization improvement*
  requires lower false authorization than naive point history at the
  same online information (not just worse task completion).
- Real task benefit requires superiority to **strong** interval/minimax and
  resync baselines on a prespecified trade-off of false authorizations,
  refusals, and task success. Until tested, no improvement is claimed.
- A fail-closed algorithm returning REFUSE for everything has zero false
  authorizations, but is **not** a successful useful solution.
- If false authorization is impossible for the specified fault because the
  fault is already perfectly observable, report a null mechanism result.
- If simulations do not actually execute the faulted commands in the native
  controller, label all results model-level and reject the robot claim.

## Audit requirements
Permanent pre-outcome commit SHA; pinned installation and third-party
checkpoint SHA; strict executor/analysis split; per-step JSONL with
physical target-memory **audit-only** values; all per-seed episode JSONs,
failure traces, machine/runtime manifest, source bytes hashes, negative results,
and read-only reaggregation CI. No self-authored CI is represented as external
replication or maintained upstream adoption.

## Externalization gate
Only after real PhysX tasks, tests and raw logs complete: offer a minimal
reviewer packet to ManiSkill maintainers or an independent robotics laboratory.
Ask for reproduction or counterexamples, not an endorsement or merge solely
on self-run metrics. A different controller *implementation* is mandatory
before any cross-controller-family generalization.
