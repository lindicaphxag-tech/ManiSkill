# Multi-History Certify-or-Query: action authority with repeated unknown ACKs

**Scientific status:** proposed method and pre-outcome protocol committed *before* any new two-fault original PhysX outcomes were read. This is an author-developed research prototype, not a peer-reviewed theorem, externally adopted original algorithm, real packet-loss experiment, or safe robotic system.

## Why this is a genuinely different research question

The completed [one-ACK two-history PhysX study](frozen_policy_transfer/ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md) maintained two possible *commanded-controller targets*. It demonstrated author-run **60/64** successful official manipulation trials with **15** private controller target reads, versus mandatory private readback **57/64** with **64** reads. [The exact paired reviewer audit](frozen_policy_transfer/review/PAIRED_AUTHORITY_FRONTIER_64.md) verifies the true non-significant 5-versus-2 task-outcome discordance and refuses to claim equal-information superiority.

A subsequent unreliable ACK increases execution histories combinatorially. If (m) commands have independent **applied/held unknown truth**, as many as (2^m) previous target states may be physically possible. The earlier K=2 geodesic-midpoint routine is not an appropriate K≥3 certificate, and a wrong single guessed history can attain task success while misidentifying actual controller memory. This source fork's earlier [32-trial real physical-response failure report](frozen_policy_transfer/PHYSICAL_RESPONSE_32_NEGATIVE_RESULT.md) found **15/32 confidently wrong ACK-history labels** under a simplistic achieved-pose classifier: do not declare belief correctness from success flags.

Our narrower problem is the action authority of a **known, source-correct finite set of possible previous controller targets**. The algorithm does **not** infer missing real acknowledgements from camera/IMU, learn new dynamics, or identify an unknown ABI. It decides if a single native command has a certified commanded-target error envelope simultaneously for *every* supplied credible history. Otherwise it refuses or requests an explicitly counted trusted observation.

### Exact positional minimax authority (arbitrary finite K)

Let the previous commanded-position hypothesis set be (mathcal H_p={p_1,ldots,p_K}), source-implied desired target (d), and controller accepts a common physical native target-position delta (uin[ell,h]) with axiswise native bounds. Under the documented additive target controller (p_i'=p_i+u), minimize:

[
ho_p(u)=max_{i=1}^K|p_i+u-d|_infty.
]

Writing (p_j^-=min_i(p_i)_j) and (p_j^+=max_i(p_i)_j), coordinatewise optimality gives the **exact** solution

[
u_j^star=operatorname{clip}!left(d_j-rac{p_j^-+p_j^+}{2},,ell_j,h_jight),
quad
ho_p^star=max_{i,j}|(p_i)_j+u_j^star-d_j|.
]

This is a classical box-constrained Chebyshev-center calculation, **not a newly invented theorem**. Its important engineering consequence is that even (K=2^m) distinct histories do not require joint translation optimization: a **six-coordinate extremal witness** suffices to determine the exact worst-case positional radius. Computing the extremal witness still requires a trustworthy, complete representation or a separately proved envelope; merely claiming completion from a caller boolean is insufficient.

### SO(3) finite witness: sound but not globally optimal for K≥3

For prior commanded orientations (mathcal H_R={R_1,dots,R_K}subset SO(3)), a verified controller uses the *same* root-left rotation (Delta R) on every hidden history, giving (R_i'=Delta R R_i). Let desired target orientation be (R_d) and (d_{mathrm{SO3}}) denote geodesic rotation angle. A common action has worst-case *commanded-orientation* error:

[
ho_R(Delta R)=max_i d_{mathrm{SO3}}(Delta R R_i,R_d).
]

The triangle inequality gives a **universal necessary lower bound**

[
L_R=rac12max_{i,j}d_{mathrm{SO3}}(R_i,R_j)
le inf_{Delta R}ho_R(Delta R).
]

Our explicitly finite candidate set comprises each prior orientation, every two-pose geodesic midpoint, and the ordinary rotation chordal mean. For every candidate (C), choose (Delta R=R_d C^{-1}), discard native Euler XYZ commands if nonfinite, singular or outside the actual native L2 ball, then replay the verified controller chart for **all K states** to calculate the actual error upper bound (U_R). A candidate can be authorized only when (U_R+epsilonle b_R) and the **exact** position radius (\rho_p^*+epsilonle b_p).

The method supplies conditional **feasible-command certificates**, not a globally minimized orientation radius (the true K-way SO(3) smallest-enclosing geodesic ball may have a different center). If (L_R>b_R), a command is unavoidably impossible without resolving hypotheses; if sampled finite centers fail but (L_Rle b_R), this implementation **has not established impossibility** and must refuse or use explicitly budgeted new evidence. This distinction matters to an original safety/authority methods paper.

### Observability and provable refusal

The complete plausible set of controller states (mathcal H_t) comes from a documented root-frame action-history observer with verified reset target, known applied commands, and explicit branching for each missing ACK. The source fork already has this [uncertain-delivery state machine](action_abi_uncertain_delivery_belief.py) with fail-closed maximum branch count. The new certificate consumes its actual TargetPose hypotheses and **will not silently prune unknown states**, invent trustworthy provenance, use private target getters without counting them, or issue an action when actuator native rotation is unrepresentable.

For acknowledged common commands, rigid left-rotation and position shifts preserve all pairwise target-state separation, so the history-set ambiguity cannot be wished away by repeatedly issuing more open-loop motion. Additional ACK uncertainty can introduce new branches; authoritative readback collapses them with a measurable information cost. This is a standard observability/geometry argument and does **not** mean the public achieved-pose alone identifies a target history.

## New pre-outcome original simulator study

Public fixed protocol [MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json](../MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json), pre-result Git blob `4107c00a5359da78542bbaafa922e2f4196f11fd`. Genuine ManiSkill `physx_cpu`, two independently published and SHA-locked ActionShift PPOs, **NO training**, original reset seeds **230001–230008 PullCube** and **240001–240008 StackCube** (16 new seeds), two actual native arm-command holds at zero-based steps **2 and 4**, both executions acknowledged to the adapter as **UNKNOWN**. Gripper actions and environment dynamics are genuinely stepped. This is NOT live dropped TCP/ROS packets, variable latency or robot hardware.

Seven source/target policy controls were carried over without giving any method secretly free information: source without fault, always-privileged controller target oracle, optimistic no-query, strict exact-only or refuse, bounded no-query K-hypothesis, bounded then selective readback (max **two** trusted target reads), and readback after every unknown ACK (max **two**). The source target update, native projection and learned PPO weights are preserved from the previously audited single-fault simulator. The method's task-success comparators have different information access, which must always be displayed.

The independent source auditor checks every one of 16 registered episodes, source checkpoint hashes, seven official task-success flags, actual two-fault exposure (including failure to reach second fault due to early refusal or trial ending), readback counts, maximal **observed** K, and worst-case target-bound audits. No failed trials or missing fault exposures can be excluded to make a purported success rate higher.

## Go/no-go tests rather than posthoc acclaim

- A real original-model failure in native PhysX is a legitimate falsifier of the **method** or its chart assumptions; no paper-performance claim is published until run log and full-denominator independent audit exist.
- A successful numerical K=4 witness is a **correctness milestone**, not a new successful closed-loop pretrained policy.
- If all candidate actions are rejected or a second fault never occurs, the stated main mechanism is **not validated**, even if source policy task successes look good.
- The existing single-fault seven-arm comparator is historically grounded but not information-/fault-equivalent to a new two-fault experiment. Task failures must be reported without cherry-picking.
- **Necessary for publication:** multiple robot/controller families, independently attested target history/missing-delivery model, matched information and native action budgets against original ActionShift active-belief baselines, high-coverage decisions, correctly identified execution histories and a third-party independently rerun dataset. All are *unproven* by this initial experiment.

**Run the pure contract:** `python -m unittest discover -s tests -p test_multi_history_authority.py -v`.

**Run the original two-fault PhysX:** [workflow](../../.github/workflows/multi-ack-khistory-physx.yml) · [method](../multi_history_authority.py) · [true PhysX seven-arm runner](../frozen_ppo_multi_ack_khistory.py) · [complete original source auditor](../audit_multi_ack_khistory.py). None of those author-owned CI links should be described as independent outside research adoption.
