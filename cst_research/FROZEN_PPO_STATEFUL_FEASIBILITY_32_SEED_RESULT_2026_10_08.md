# Preregistered 32-seed frozen-PPO stateful target-memory transport

**Public preregistration (before the experimental run):**
[FROZEN_PPO_STATEFUL_FEASIBILITY_32_SEED_PREREG_2026_10_08.md](FROZEN_PPO_STATEFUL_FEASIBILITY_32_SEED_PREREG_2026_10_08.md)

**Public experiment:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37749474021

**Exact four-arm implementation:**
https://github.com/lindicaphxag-tech/ManiSkill/blob/validation/frozen-ppo-stateful-feasibility-holdout-20261008/research/frozen_ppo_target_memory.py

32 fixed, unseen episode seeds 18001..18032 inclusive; no seed omitted.
Panda/PickCube-v1 PhysX CPU, frozen externally published ActionShift
PPO, SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
Same seed/initial physical observations across the four separately
executed worlds. Trained 42D observation ABI is reconstructed after
removing the target controller's additional 7D goal memory from the
49D observation; the goal memory is available separately to the adapter.
Each world performs policy inference on **its own changing observation**;
weights are frozen, not trained.

## All 32 episodes — unconditional task success

| Arm | Success | Fraction |
|---|---:|---:|
| Source `pd_ee_delta_pose` PPO | **31/32** | 96.875% |
| Exact controller target-memory adapter, refuse nonrepresentable commands | **3/32** | 9.375% |
| Target-memory adapter + explicitly NON-EXACT Euclidean feasible projection | **32/32** | 100% |
| Raw action copy to `pd_ee_target_delta_pose` | **3/32** | 9.375% |

- Exact memory adapter **refused in 29/32 episodes** upon an impossible
  per-step action. A refusal is not a task success.
- Bounded adapter used **31 projected steps across 29 episodes**,
  explicitly labeled `NOT_EXACT`. Largest required normalized action
  amplitude was **1.6698468477**, outside destination native limits.
- Projection algorithm: component-wise clip of position native actions
  into [-1,1], unit-`l2` projection of native orientation increment,
  with a runtime previous-target-inversion and an unchanged frozen
  policy. It does **not** preserve exact source commanded goal on
  infeasible steps, and it is not formal robot safety.
- **Source failed seed 18027**, while projected target eventually
  completed it at step 31 (source did not succeed within 50 steps).
  This is a single paired counterexample to universal source parity,
  not a general proof the adapter improves a trained PPO.
- Direct-copy succeeded only seeds 18019,18020,18030.

The result supports a specific limited statement: target-history-aware
action compilation plus a feasibility-aware, **nonexact** continuation
can preserve task-level closed-loop competence despite hard controller
action bounds, on this one simulator/task/policy. The naive and strict
refuse controls are all physically executed, including their failures.

**Do not inflate:**
- Do not call 32/32 a hardware safety guarantee, exact trajectory
  equivalence, broad robustness or accepted paper.
- This evidence is only **one task + one third-party PPO + CPU backend**.
- "Action clipping"/projection and "delta target encoding" have substantial
  prior art; innovation cannot be claimed simply from these components.
- The learned-policy test does **not** use the separately researched
  robosuite OSC transaction/rollback component; these are not one end-to-end
  proved system.
- Future work needs cross-task/family results, quantitative task
  trajectory deviation and infeasible-action residual, independent
  replication and source/instrumentation determinism audits.

## Audit source of prior 10014 result

The earlier 32-seed **delta-to-absolute** run had one failure on
10014 (31/32), while a separately instrumented diagnostic run
succeeded, despite identical initial observation fingerprint. The
specific **untouched original code** was repeated in 12 separate
processes, both with and without extra random seeding: the source
succeeded at step 31 all 12 times and the compiled target failed all
12 times.
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37749366189

Therefore the prior failure is reproducible under its original code;
a different instrumentation path changes the execution result.
The *mechanism* for this instrumentation sensitivity is still unknown.
