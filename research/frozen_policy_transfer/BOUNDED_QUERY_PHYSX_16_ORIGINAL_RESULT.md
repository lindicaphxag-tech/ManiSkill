# Stateful action-ABI transport under uncertain execution acknowledgement

**Prospective original frozen-PPO PhysX experiment · 9 October 2026 · owner-executed; not independently reproduced.**

## Registered question

After an unknown arm-command acknowledgement, can a valid common **bounded** native command over a complete two-history target belief keep a frozen task policy operating, and can a decision gate avoid spending an otherwise mandatory privileged controller-state readback without losing task success on the observed held-out task population?

**Frozen before source-run implementation:** [precommit b2cc9942daa6bb2edb10797fad91f48554a3a6ce](https://github.com/lindicaphxag-tech/ManiSkill/commit/b2cc9942daa6bb2edb10797fad91f48554a3a6ce), protocol Git blob `36f01321c7f5502f3cc0b188d5201f1c2cedb131`, fixed source checkpoints, fixed 50-step horizon, fixed zero-indexed step-2 arm target hold, fixed 0.05m Cartesian infinity error and 0.05rad SO(3) geodesic target-error budgets. No PPO weight changes.

## Original data and provenance

- Genuine ManiSkill PhysX CPU with released third-party PPO **PullCube-v1** on exactly 122001–122008 (8) and different released PPO **StackCube-v1** on 132001–132008 (8), seven paired control arms per physically matched original reset seed.
- [Complete successful CI source run 37826881229](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826881229): frozen source/protocol CPU check succeeded; both native task job conclusions succeeded; **independent 16-row full-denominator auditor succeeded**.
- [Implemented intervention and source auditable PR #78](https://github.com/lindicaphxag-tech/ManiSkill/pull/78) (self-repository; not third-party upstream adoption).
- Distinct separate [two-history SE(3) native model test](https://github.com/lindicaphxag-tech/ManiSkill/pull/77) passed four controlled native targets and all six cross-platform mathematical checks; this was **not** included as extra frozen-policy task episodes.

All source artifacts are SHA-256 frozen, including every original per-step event and failed task.

| Original unchanged file | SHA-256 |
|---|---|
| PullCube original 8-state JSON | `bcbdcf8eea1f214dd4e6106402f45eaf19bcfe46fbff3edf9b74cad0e31da4cc` |
| StackCube original 8-state JSON | `8c0ff8cd0096562622c515619853c1939ac073d5c77a9deba597921c05d486ac` |
| Full 16-state independent aggregate JSON | `1246afcd6a1b88922a5d1e9f0c73ebb858179a09770d5c2d46032763591955c8` |
| PullCube original unselected execution log | `33871dd3448c762744e2deb3ddc3031bb9880a48a1b6f6d51028ff8b9fe09859` |
| StackCube original unselected execution log | `177fb318f73142870d1f88b19d2c1fc278ff08d8fb14dbe7f6d32bfb602f99c7` |

## Seven actual controller arms and closed-loop native outcomes

| Intervention arm | PullCube 8 seeds | StackCube 8 seeds | Combined (descriptive only) |
|---|---:|---:|---:|
| Original no-fault source PPO | 7/8 | 7/8 | 14/16 |
| Injected fault, optimistic guessed-positive ACK history | 6/8 | 0/8 | 6/16 |
| Fault, finite-belief common-**exact** action or refuse | 0/8 | 0/8 | 0/16 |
| Fault, bounded two-history common action **with zero true target queries** | **8/8** | **3/8** | **11/16** |
| Fault, bounded common action and **one true controller target readback only on refusal** | **8/8** | **7/8** | **15/16** |
| Fault, always spend one privileged target readback on continuation | 8/8 | 7/8 | 15/16 |
| Fault, continuously access the controller's private target (oracle) | 8/8 | 7/8 | 15/16 |

Both original pretrained source competence gates passed (7/8 ≥ 5/8), and every target arm's prespecified native hold fault was executed on all 8 states of both tasks. Six source-arm modes × 16 states = 96 injected arm holds; this **does not** equal 96 independently trained policies or 96 unrelated task populations.

**Information-access cost:** selective arm made **0** task-decision target readbacks on PullCube and **4** on StackCube (4/16 total). Mandatory-readback arm made **8 + 8 = 16**. A 75% reduction in privileged **decision-time** target readbacks was observed while both treatments had 15/16 pooled success. Their success sets were **not identical**: StackCube had one *selective-only* success and one *mandatory-only* success. The full 16-row binary success flags, not just pooled totals, are available in the original aggregate. The original oracle is flagged with **-1 ongoing privileged access** and must NEVER be counted as a zero-query control.

**Robust no-query control:** 48 genuine PullCube and 94 genuine StackCube native control actions were conditionally authorized with bounded uncertainty. The original post-dispatch auditing checks their *commanded-target* position/SO(3) bounds against the real controller. These audit-only target state reads are separately disclosed and **were not fed into the next policy/control decisions**; they do not demonstrate that measuring such errors is free on hardware.

**Paired effect limitation:** Compared with the optimistic arm, the zero-query bounded arm has five exclusive successes and zero opposite exclusive successes across the 16 episodes. This is a small, researcher-operated paired sample and is not a definitive cross-robot or external-lab significance claim. Against mandatory readback, selective information acquisition has 1:1 exclusive success discordance; pooled 15/16 parity is therefore NOT trajectory or per-seed equivalence.

## How the fault and hypotheses were produced

At one frozen action step, the simulator executes a **zero native arm target delta** instead of the computed intended target delta, still applies the same policy gripper action, and advances genuine PhysX time. The adapter does **not** know whether the original issued arm command executed; it keeps both possible previous target-command states in a finite belief. This is an **injected controller target hold and missing informational acknowledgement**, **NOT** a realistic communication network packet-loss channel, physical robot emergency stop, sensor spoofing, or actuator failure.

With each subsequent frozen source action, the adapter reconstructs the intended physical source goal, computes a single native root-frame translation plus root-left rotation command that minimizes the worst-case two-history commanded-target position/SO(3) error, and checks the action's native representability and fixed error budgets. If it fails, the bounded-no-query arm refuses; the selective-query arm pays for **one genuine privileged target readback**, collapses its belief with the true controller target, and continues. No claimed credible memory enclosure is independently signed or inferred from a sensor: the two possibilities come from the exactly known synthetic fault model and deterministic controller recurrence.

## Existing prior art and unproven originality

The minimax positional Chebyshev midpoint, two-rotation SO(3) geodesic midpoint, interval/state-belief estimation and selective sensing are well-known principles, not original theorems. Closest neighbors include [SPACE (2026)](https://arxiv.org/abs/2606.24049) for robot-specific Cartesian action adaptation, [Jaulin (Automatica 2009)](https://doi.org/10.1016/j.automatica.2008.06.013) on robust set-membership estimates, and [Hibbard et al. (Automatica 2023)](https://doi.org/10.1016/j.automatica.2023.111140) for simultaneous action/perception choices over finite beliefs.

The **candidate methodological contribution** is the controller's *last commanded target* as an explicitly authority-bearing state in a frozen policy's action interface, with original source action decoding, documented native action representability, acknowledged command-history branching, target-setpoint error authority, and budgeted privilege escalation. The observed 16-state adaptive result is a convincing feasibility signal, NOT established first-of-kind theory or a finished CoRL/RSS/ICRA paper.

## Unresolved external gates

1. Perform a distinct prospective confirmatory **larger task-state cohort** under unchanged method and fixed information/error budgets; preregister before reading new outcomes, report complete denominators and uncertainties.
2. Actual delayed/lost/reordered native commands and a separate controller/hardware family, not only Panda target holds; do not conflate separately verified Fetch/xArm6 *controller setpoints* with their learned-policy task success.
3. Strong equal-information learned/state estimators, information cost, reward-aware query selection and safety-related **trajectory/IK/force/contact/collision** metrics.
4. Independent outside researcher rerunning original controller physics and adopting the algorithm in a maintained project. [External ActionShift author issue](https://github.com/Archerkattri/actionshift/issues/1) is an invitation, not endorsement.
