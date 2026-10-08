# CST controller-owned target memory transport — four frozen PPO tasks

**Status:** exploratory public CPU simulator evidence with frozen *third-party*
policies, not accepted original-paper novelty or hardware-safety certification.
The method does not train or modify any pretrained actor weights.

## Controlled evidence matrix

All four experiments used genuine official ManiSkill v3/Panda PhysX
CPU physics, `obs_mode=state`, maximum 50 control steps/episode, four
independently executing environment/controller arms per task/seed:

1. original frozen PPO under achieved-relative `pd_ee_delta_pose`;
2. **exact/refuse:** same PPO with stateful
   `pd_ee_target_delta_pose`, compile target-relative action from
   controller's *live previous target*, refusing a command outside
   the controller's representable one-step input set;
3. **project:** same as #2 but approximately **project** out-of-bounds
   commands to the native translation box / rotation unit-ball instead
   of claiming that the original target remains executable;
4. **naive:** same stateful target controller, but directly copy native
   actions rather than accounting for previous-target semantics.

All arms use their **own** current observations for frozen-policy inference.
The target controller appends 7D target-goal memory to proprioception; a
checked ABI projector removes only this specific field from the neural
actor's input. The extra 7D goal memory is *retained and actively used*
by #2/#3 action compilation.

### Frozen independent task checkpoints

Each row uses a different *published third-party* ActionShift PPO
checkpoint from
https://huggingface.co/kattri15/actionshift-baselines,
SHA256-checked against the model card. Each task's exact sample list
was preregistered **before that task's run**.

| Task | Frozen PPO input width | Preselected seeds | Original PPO | Exact/refuse | Memory+project | Naive copy | Strict refusals | Approximate steps |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| **PickCube-v1** | 42 | 20001–20032 | **31/32** | **5/32** | **32/32** | **3/32** | 27 | 30 |
| **PushCube-v1** | 35 | 30001–30032 | **29/32** | **28/32** | **29/32** | **23/32** | 1 | 1 |
| **PullCube-v1** | 35 | 40001–40032 | **31/32** | **17/32** | **31/32** | **12/32** | 14 | 15 |
| **StackCube-v1** | 48 | 50001–50032 | **30/32** | **14/32** | **31/32** | **2/32** | 17 | 21 |
| **Total (descriptive)** | mixed | 128 task-seed groups | **121/128** | **64/128** | **123/128** | **40/128** | 59 | 67 |

One fixed source task seed is tested in each arm. The sums are
**descriptive only**, not an independent i.i.d. 128-episode universal
success estimate across robots, policies or real-world environments.

### Canonical CI and protocols

- PickCube 32-seed:
  [public CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746168558),
  [pre-registration](FROZEN_PPO_MEMORY_32SEED_PILOT_PRE_REG_2026_10_08.md),
  [per-task report](FROZEN_PPO_MEMORY_32SEED_PILOT_RESULT_2026_10_08.md).
- PushCube 32-seed:
  [public CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746854295),
  [pre-registration](PUSHCUBE_FROZEN_STATEFUL_32_PRE_REG_2026_10_08.md),
  [per-task report](PUSHCUBE_FROZEN_STATEFUL_32_RESULT_2026_10_08.md).
- PullCube 32-seed:
  [public CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37747572639).
- StackCube 32-seed:
  [public CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37747596201).
- The Pull+Stack pre-registration, posted before either run:
  [protocol](PULL_STACK_FROZEN_STATEFUL_PILOTS_PRE_REG_2026_10_08.md).
- Exact tested branches in order:
  `validation/frozen-ppo-memory-32-holdout-20261008`,
  `validation/frozen-ppo-pushcube-memory-32-20261008`,
  `validation/frozen-ppo-pullcube-memory-32-20261008`,
  `validation/frozen-ppo-stackcube-memory-32-20261008`.

## The useful mechanism and the honest failure boundary

The *interesting property* is not basic delta/absolute conversion.
Changing `pd_ee_delta_pose` → `pd_ee_target_delta_pose` changes
controller semantics from "increment from achieved pose" to
"increment from **previous desired target pose**." That previous target
state is generally not recoverable from a single physical observation;
the target side must expose it at each step for executable transport.
The same controller-target memory also unexpectedly changes the PPO
observation ABI (+7). The adaptor separates these two roles.

Even with the live memory, exact one-step transport can become
**infeasible** under the target controller's native action limit.
Strict refusal is a correctness decision, not an unsuccessful physical
rollout. A simple native bounded projection admits approximate
execution, with the deviation from the requested goal explicitly
recordable. The four-task results show task-dependent frequency of
this representability issue (one Push refusal versus 27 Pick refusals).

**Do not claim the projected adapter is a new optimizer**: the pilot
implementation clips native position to a box and rotation to a
Euclidean unit ball. The newly separated
[`target_memory_feasibility.py`](target_memory_feasibility.py)
provides local executable pose feasibility and goal-residual witnesses,
with the [108-test CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37747338160).
A separate physical execution/goal-residual checker is being validated;
until it is green, only unit-level witness verification is claimed.

## Reproducibility cautions

- The earlier independent delta→absolute-only 32-seed pilot had
  a compiled target failure on 10014 in its original batch but the
  same nominal seed subsequently succeeded in two separate full
  batch repeats. This limits per-seed determinism claims. Read
  [updated audit](FROZEN_PPO_32_SEED_HOLDOUT_RESULT_2026_10_08.md).
- The four tasks still use the **same Panda robot family and ManiSkill
  controller implementation**. They establish task/policy/observation
  variability, not cross-robot or hardware transfer.
- No protected patient data, real robot trials, independent third-party
  adoption, upstream maintainer merge or acceptance into a research
  venue is claimed.
- Some source PPO episodes failed. We report unconditional results,
  and do not use the projected 123/128 versus source 121/128 as a
  statistically supported source-policy improvement.
- This method was not evaluated on official ActionShift hidden contract
  splits. No numerical comparison with ActionShift's method leaderboard
  is licensed by these tests.
- Controller initialization RNG and solver state can influence outcomes.
  Stable reproducibility requires full physics state fingerprints, pinned
  dependencies and repeat experiments across runners.
- Check ActionShift, stateful refinement, observation/action interface
  adaptation and robotics controller migration prior work before
  asserting conference-level scientific novelty.

## Next decisive work

1. Execute the residual witness in physics and check each compiled
   action against the controller's *actual* updated target memory;
   fail CI when physical goals disagree.
2. Add a second robot/controller implementation family, distinct from
   Panda/MiniSkill, and independently rerun frozen learned policies.
3. Record exact native-state SHA and code/dependency versions for
   repeated matched-state experiments.
4. Obtain a maintainer review of the minimal two-file ManiSkill #429
   bugfix, independently of flagship research.
5. Freeze a final multi-task experiment protocol before submitting
   a research paper. The same author-run exploratory results should
   not be recycled as an unseen final confirmation set.
