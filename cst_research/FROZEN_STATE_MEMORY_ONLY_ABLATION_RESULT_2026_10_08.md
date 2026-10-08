# Isolated state-memory ablation: 32 unseen frozen PPO task episodes

Predeclared exact seeds `30001..30032` and comparison protocol:
[FROZEN_STATE_MEMORY_ONLY_ABLATION_2026_10_08.md](FROZEN_STATE_MEMORY_ONLY_ABLATION_2026_10_08.md)

**Canonical public CI, passed:**
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751599480

## Intervention and context

Official ManiSkill PickCube-v1 / Panda / PhysX CPU, external unchanged
ActionShift PPO checkpoint SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.

All 32 initial projected policy observations match between arms.
An extra seven controller pose features in the destination observation
are verified and excluded from the frozen PPO's 42D input, while
remaining available to controller execution.

The **primary paired comparison** holds the action decoder, reference
frames, normalizations, bounds and bounded-projector algorithm fixed:
- **Stateful:** compile target controller delta with the live *previous
  desired target pose*.
- **Stateless achieved-only:** replace *only* that previous desired
  target pose with current achieved TCP pose. All other computation and
  bounded fallback behavior is identical.

Both independently execute 50-step real physics task rollouts with
the same third-party frozen PPO under each own observation.

## All-arm results

| Method | Task successes |
|---|---:|
| Source PPO original controller | **31/32** |
| Stateful + bounded projection | **32/32** |
| Stateless achieved-only + SAME bounded projection | **2/32** |
| Stateful exact-only / fail-closed | **6/32** |
| Direct native action copy | **2/32** |

Memory-only primary paired effect: **30 episodes succeed only with
stateful controller-memory access; zero succeed only with stateless**.
Stateful bounded projection needed 27 non-exact command steps.
The achieved-only control reported **0 fallback steps** because it did
not accumulate the last target's positional discrepancy; this fact is
part of the semantic intervention, not evidence of a more capable
control chart. Exact-only refused 26 episodes.

No seeds were omitted from the denominator, no PPO training occurred,
and the source itself failed one episode. Do not claim universal
state/action equivalence.

## Interpretation and limits

In this specific target-delta controller, replacing previous target
memory by achieved pose leads to materially different real closed-loop
task outcomes even when ordinary action scaling and projection is
matched. This establishes a strong **implementation-level causal
contrast** for controller history, not universal formal proof or
novelty of known coordinate transforms/clipping.

Before claiming a high-impact research contribution:
- Cross-task replication using a different task and frozen PPO
  ([predeclared PushCube protocol](FROZEN_PUSH_CUBE_MEMORY_CROSS_TASK_PREREG_2026_10_08.md)).
- A separate controller *family* or independent robot platform.
- Disclose per-step physical divergence, action amplitudes and
  nonrepresentability; evaluate alternate feasible-step logic.
- Pin dependencies, independent reproduction, and credible prior-art
  comparison against ActionShift and other stateful controller migration.
- No safety claims about physical robots from CPU simulation alone.
