# Causal Intent Replay under Unknown ACK — Original PushCube 32-Reset NEGATIVE Result

**2026-10-14 | Original full precommitted actual native PhysX run | Novel task-action intervention tested, not performance improvement | NO external robotics research acceptance**

## Frozen scientific question and complete source

The protocol **PUSHCUBE_CAUSAL_INTENT_REPLAY_FROZEN_BEFORE_TEST_20261014.json** was committed **`1666ec93dcd2128ed49fe4615d92ed6e8f0cf661` BEFORE this real PhysX run**. Source-code methods were then frozen before any new outcomes: the policy stores the two frozen PPO source normalized 6D intents at artificially held command steps 2 and 3. At t4 it makes the same one **paid, true controller-target readback** as the strong corrected fixed policy; then injects either the physically chart-correct unfiltered half-sum or its projection onto the continuing current native motion direction if cosine ≥ 0.25, clipped to legal native translation bounds, preserving the orientation and gripper. It creates a NEW actual controller action, not merely a router over existing readback policies.

- Task: genuine native **PushCube-v1**, Panda PhysX CPU; new independent frozen PPO reset IDs **2026760001–2026760032**, 4 exact 8-ID physical shards.
- Public frozen third-party pretrained source policy: ActionShift `ppo/push_cube_final_ckpt.pt`, revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`, SHA256 `a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`. The PPO is trained on PushCube, **not zero-shot**; this task previously had one geometrical native Pose study but not this task-level delayed-intent method.
- Actual simulator intervention: both source step 2 and source step 3 target-native arm instructions replaced by a **real zero arm hold**, with unchanged gripper. This is **not** lost packets or physical device hardware.
- Official run **[38560009094](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38560009094)**, **ALL 6 jobs SUCCESS**, including the preflight source method tests, **4 physical native eight-reset shards**, and a separate 32-reset full-denominator source auditor.
- Exactly **32 unique independent reset clusters** and **192 actually physically stepped controller worlds**, not 192 independent training samples.
- Original owner-operated shard JSON and full source logs are archived as first-run GitHub artifacts, with **all negative cases retained**. A separate local first-party original-file audit individually verified the four ZIP SHA256 files, all six actual controller policies, 32 original episode outputs, source model SHA, paired outcomes and native t4 action changes. The independent recount is available in the research bundle but is **not an independent outside laboratory repetition**.

## Full original task-level outcome — no cherry-picking

| Source-native actual controller strategy | Official task success | Actual private target reads |
|---|---:|---:|
| Clean source pretrained PPO, no physical fault | 30/32 | 0 |
| Faulted controller with continuously privileged actual target | 30/32 | continuous, never zero-cost |
| Corrected fixed t4 one actual target read | 30/32 | 32 |
| Existing finite K-history certify-or-query | 30/32 | **22** |
| New unconditional delayed-intent replay, one paid t4 read | 30/32 | 32 |
| **New direction-compatible delayed-intent replay, one paid t4 read** | **30/32** | **32** |

**Mechanistic changes did occur:** 32/32 unconditional control worlds and 26/32 direction-compatible worlds issued an actual t4 native controller command different from the separately stepped corrected fixed-readback baseline. In the 32/32 prospective cases, both new strategies physically dispatched **identical first four steps** to the fixed strong baseline before t4. All faulted arms encountered **2/2 true simulator-native target holds** in **32/32 resets**.

**Main outcome:** new direction-compatible recovery has **0 new-only / 0 fixed-only** and **0 new-only / 0 continuously-privileged-oracle-only** binary official task successes (exact exploratory p=1 for both). Against the old 22-read mechanism, the new policy has **1 new-only / 1 old-only** task success; pooled successes tie but the new method consumes **10 more** private reads. Thus the source-frozen joint success+readback **promotion gate FAILED**. The observed 26 new native actions carry no official task-success gain; downstream task utility is not established.

## Interpretation and future hypothesis

**Correct native geometry and even real action alterations do not imply improved task completion.** This is a source-audited four-task-family falsifier of geometry-only repair and simple delayed-command replay. A doctoral-class successor must learn a valid **task-level future viability mechanism** that generates genuinely different task-progress behavior and beats strong actual corrected fixed readback and suitably costed privileged oracle under *new task families/embodiments* and independent source runs. Generic action-direction integral control, Chebyshev geometry or replay is preexisting control intuition and **not** a new theorem.

## External acceptance ledger

- Official GitHub CI completion: YES, same author's account and instrumentation, independently inspectable, **not academic peer review**.
- Outside-lab robotics replication / upstream ManiSkill merged method feature / academic method paper acceptance: **NO**.
- Related but separate: official MOABB maintainer acknowledged the author's **EEG public EDF overlap report** on 2026-10-14, [MOABB #1248 comment #6164538151](https://github.com/NeuroTechX/moabb/issues/1248#issuecomment-6164538151); this is evidence of the EEG data report's practical external relevance, **not an endorsement of this robotics algorithm**.
