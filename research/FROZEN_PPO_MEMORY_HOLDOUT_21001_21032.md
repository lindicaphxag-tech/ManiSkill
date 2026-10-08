# Precommitted held-out closed-loop policy transfer: 21001–21032

**Purpose:** confirm or falsify a *previously observed* improvement in
cross-controller policy transfer, not rerun seed 10014 or the exposed
20001–20032 development cohort until a favorable result appears.

## Pre-treatment source freeze

- Research code at experiment design: original branch head
  `2a1c2e739c234098e2d08b0e5633026c05aaf721`; frozen
  `research/frozen_ppo_target_memory.py` blob
  `c1b1b2dcd39e549a91f99540ba9cd05bc7bae51e`.
- Public PPO: fixed Hub `REPO`/`FILENAME`, cryptographically checked
  against `EXPECTED` in existing `frozen_ppo_pickcube_gate.py`.
- Environment: genuine `PickCube-v1`, `physx_cpu`, `state`,
  `reconfiguration_freq=1`, **no retraining**, 50-step horizon.
- Comparison in the same episode seed:
  (1) native `pd_ee_delta_pose` source PPO,
  (2) target `pd_ee_target_delta_pose` with memory-aware **exact-only**
      contract conversion and refusal when outside target action bounds,
  (3) memory-aware target conversion with explicit **approximate bounded
      projection** when out of target action limits, and
  (4) direct-copy action (wrong chart, negative control).
- Observation: target controller's extra 7-value target-pose state is
  verified against its internal live target and omitted to recreate the
  original 42-input checkpoint ABI without deleting task extras.
- **Primary prospective holdout**: every integer seed
  **21001–21032**, specified *here before the source code's seed
  constants are changed and before the new simulator run*.
  No deletions, replacements, subjective 'valid-seed' filters,
  or reruns with preferred seeds.
- Successful task = official environment's `info['success']` true
  at any timestep within its initial 50 physical action steps.
- Per-seed diagnostics: success, horizon, first strict certificate
  refusal, count and magnitude of approximate bounded projections,
  exact initial-observation match, and full frozen checkpoint SHA.
- The 20001–20032 development result (source **31/32**, exact-only
  **5/32**, projected **32/32**, wrong-chart direct **3/32**) is
  **known at freeze time** and never scored as untouched confirmation.
- Four world states are executed with identical initial seed and
  independent world dynamics. This is paired per-seed **task success**,
  not demonstration replay. There remains one policy checkpoint and
  one task family; no cross-policy/world generalization follows.

## Pre-declared acceptance (must check even if null/negative)

1. Confirm the exact 32 seeds and **32 outcomes for all four arms**,
   source checkpoint SHA consistency, and initially matched physical
   task conditions. Fail closed on missing or repeated seeds.
2. Task competence: source must succeed at least **24/32**; else the
   cohort is not evidence of meaningful recovery, regardless of target.
3. Primary useful gain: memory-aware projected target transfer must
   exceed naive direct-copy task success by at least **12 of 32**
   paired episodes in *net count*, with the exact 2×2 discordance
   `projected-only / naive-only` published.
4. Compare projected vs exact-only counts and publish how many
   non-exact bounded projection steps occurred. A successful approximate
   projection is not an exact action-semantic equivalence certificate,
   nor is it a learned correction policy.
5. Report the result even if it fails thresholds; no revised objective
   after seeing these outcomes. CI success merely means the script ran.
6. The winner must have been selected on the development seeds, and
   all holdout seeds must run on *the same existing implementation
   apart from replacing the seed tuple and workflow branch*. No
   architecture, controller, checkpoint or training changes.

## Interpretation boundary

Even if the holdout gate passes, this is **one frozen PPO, PickCube,
state observations, PhysX CPU, one control-mode pair**. It is a
domain-specific **training-free source-target control-semantic
compiler**, not a universal VLA self-repair method. The approximate
action projection may change intended behavior; training-free task
recovery must not be called safe physical actuation or exact semantic
preservation. Future method validation requires independent task
families, checkpoints, held-out controller identities, risk accounting,
real-world source sensors and competitor baselines.

No academic or upstream maintainer acceptance is implied by the
author's own CI or source-controlled freeze.
