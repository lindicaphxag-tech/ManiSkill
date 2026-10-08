# Controller action ABI under unknown command delivery: a set-valued authorization boundary

**Preclinical research prototype; pure CPU contract checks only. NO new physical simulator or third-party adoption result is claimed by this file.**

## Previously supported and what it did *not* establish

[Four-task original frozen PPO](frozen_policy_transfer/STATEFUL_ACTION_ABI_FLAGSHIP.md) and [independent-cohort 16-state action-history observer](frozen_policy_transfer/ACTION_HISTORY_OBSERVER_PROSPECTIVE_16.md) show that a deterministic *known* target-controller update can reconstruct a previous target without reading a private controller field, assuming the reset target and all accepted commands are available. A parallel 64-state [shadow observer CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37818985343) reaches the same conclusion. This explicitly **falsifies** the overstatement that the private target getter itself is indispensable.

One unacknowledged or silently dropped command changes that information condition. Instead of mislabeling an unknown prior target as known, this work proposes a **set-valued target-state belief** and an **exact action-authority gate**: a command is authorized only if the *same* legal native action reaches the same desired physical goal for every still-possible controller target.

## Mathematical scope

The supported Panda controller update uses a root-frame position increment and root-aligned Euler rotation:

\[
p_{t+1}=p_t + d_p(u_t), \qquad R_{t+1}=R_\Delta(u_t)\, R_t.
\]

A missing acknowledgement for action \`u_t\` produces **both** plausible states, \`(p_t,R_t)\` and \`(p_{t+1},R_{t+1})\`, not a guessed single target. A fully confirmed accepted action carries all states forward. Explicit negative confirmation keeps all previous states. Exact readback or a documented reset can resynchronize to a singleton.

**No-action-only contraction in this chart:** if the same accepted command \`u\` is applied to two possible prior positions, then

\[
(p_i+d_p(u))-(p_j+d_p(u))=p_i-p_j.
\]

Thus the translational belief diameter cannot decrease by repeating common known root-frame-delta commands. For rotation, left multiplication by \`R_\Delta(u)\` preserves the geodesic distance between \`R_i\` and \`R_j\` on SO(3). An arbitrary controller reset, external target readback, or other informative observation is needed to remove such uncertainty. This is an **identifiability/authority boundary**, not a claim of a new general control theorem.

For desired physical goal \`D\`, the program computes each candidate target-native inverse \`u_i = f^{-1}(G_i,D)\`, refuses if any candidate is out of bounds, and otherwise authorizes only if all \`u_i\` agree within a specified strict numerical tolerance. If candidate actions differ, a single target-native command cannot exactly realize all candidate physical goals under this contract. No blended or projected action is falsely called equivalent.

## Executable contract and falsifiers

- [Belief state implementation](action_abi_uncertain_delivery_belief.py): \`UncertainDeliveryBelief\`, \`BeliefCertificate\`, \`positional_diameter\`. Requires explicit acknowledgement after dispatch; ambiguous dispatch **branches**. Overflowing the finite hypothesis budget fails closed without pruning alternatives.
- [Eight tests](../tests/test_action_abi_uncertain_delivery_belief.py): deterministic exact-case, two-state ambiguity counterexample, invariant diameter, known-negative acknowledgement, explicit readback resynchronization, branch overflow, stale acknowledgement invalidation, unrepresentable physical target and malformed-action denial.
- Zero learning, zero new PPO model, zero new task success claimed. This module does not access simulator ground-truth target during control and is not yet integrated into a live interrupted-trajectory PhysX evaluation.
- It does not certify *hardware safety*, contact forces, IK feasibility, collision avoidance, or the fidelity of command-delivery acknowledgements. One must not call \`acknowledge(applied=True)\` without reliable evidence of accepted application.

**Scientific next gate:** inject dropped, duplicated, delayed and reordered actions into true frozen-PPO PhysX rollouts while recording the real controller target as **audit-only** truth. Compare naive history integration, fail-closed refusal, belief-set exact-authority and an equal-information adaptive state observer. Then port to a second controller implementation. This is the missing L8/L9-relevant mechanism test, **not** something already proven.

## Citation/novelty policy

Finite set-membership observers, robust control, geometric charts and belief-state reasoning are established ideas. The contribution, if it survives new evidence, would be a reproducible *controller action-ABI authorization layer* for policies frozen under other operational semantics. Neither a novel set-membership theorem nor universal robotic safety is asserted without comparison to prior art.
