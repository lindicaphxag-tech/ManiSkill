> **Independent contributor's RESEARCH FORK, not the official ManiSkill 3 project.** All controller-repair experiments here are contributor-operated; no ManiSkill maintainer adoption, external lab replication, real hardware or certified collision safety is implied.

## Current research flagship · When did my robot command execute? (9 October 2026)

**Read this first:** [Reviewer manuscript v3.2 — causal PhysX controls, source-authenticated counterexamples, controller-ABI limits and original SmolVLA evidence](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/WHEN_DID_MY_ROBOT_COMMAND_EXECUTE_REVIEWER_V3_2.md). It is an unreviewed research draft, **not** a published or accepted paper.

**Mechanism, not more PRs.** A public frozen PPO drives a stateful *commanded-target-relative* ManiSkill controller. Two unknown command acknowledgements imply four possible complete SE(3) target histories. **BeliefBridge** carries all histories, authorizes one from measured public achieved motion only under a previously fixed empirical response model, and explicitly reads the private controller target when ambiguity remains. It is a **selective-information controller adapter**, not a new trained VLA or a proven collision/force-safe controller.

**New causal experiment with both previously confounded mechanisms held fixed:** [64 new true 2×2-ACK resets, 576 native PhysX controller worlds, 10/10 original and independent audit PASS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925044658). In this later source-registered cohort, the public and fixed-reader arms share **identical pre-t5 physically executed native commands, achieved+target SE(3), and the same post-t5 belief and action compiler**. Complete-history public witness or read: **53/64 tasks, 48 private reads**, 16 public history admissions, zero observed wrong-confident; matched mandatory target reader: **53/64, 64 reads**. This is **25% fewer controller-private reads conditional on these samples**, NOT statistical task noninferiority or equal total sensor cost. [All 16 original physics shard JSONs, byte-verified full audit and SHA256 permanently archived](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/shared-compiler-causal-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_postquery_causal_original64_1480001_1490032) · [source-only original artifact archiver PASS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37925911620) · [research PR #146](https://github.com/lindicaphxag-tech/ManiSkill/pull/146). First source-implementation freeze attempts failed and remain disclosed; the successful code was pinned before this entire successful run.

**Primary actually executed, prospectively frozen experiment** — two independently physically applied/held unknown ACK commands (including a **nonzero t3 action**), four balanced truth combinations, 64 never-used PullCube/StackCube PPO initial states, 576 separately stepped real ManiSkill CPU PhysX controller worlds, all original task failures retained:

| Actually stepped method | Official manipulation task success | Counted privileged target reads |
|---|---:|---:|
| **BeliefBridge full execution-history public evidence + read if ambiguous** | **49/64** | **33** |
| Task-aware, physically executed strong comparator | 49/64 | 51 |
| Fixed authoritative controller read | 49/64 | 64 |

All **49 successful and 15 failed task identities match** the two top methods. BeliefBridge uses **18/51 (35.3%) fewer private reads** and publicly identifies **31/64 full position+orientation histories** with zero *observed* wrong confident labels in this **particular cohort**. The exact *exploratory paired read-count* sign test on immutable original per-episode data gives 24 fewer / 6 more / 34 tied, two-sided `p=0.00143`. This is neither task-success superiority, statistical noninferiority nor full information-cost equivalence: the proposed method consumes extra achieved-XYZ observations.

**Source/technical entry:** [concise technical manuscript v2.1](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/two-by-two-real-nonzero-ack-physx-20261009/research/frozen_policy_transfer/DISCRETE_HISTORY_PUBLIC_PPO_MANUSCRIPT_V2_1.md) · [original 10/10 PhysX and independent audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921809790) · [unchanged original 64 source rows and SHA256 archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/two-by-two-real-nonzero-ack-physx-20261009/research/frozen_policy_transfer/evidence/true_two_by_two_nonzero_ack64_1340001_1350032) · [source-locked paired statistical verification](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924333984) · [physical source identity and forged-source rejection](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37922340636).

### The counterexamples are part of the result, not hidden

- **Equally public-sensed competing method:** a completely new 64-reset/640-native-world true PhysX cohort found BeliefBridge **53/64, 48 private reads, ONE confidently incorrect history**, against a previously frozen same-public-XYZ Bayes-style posterior gate **54/64, 62 reads, zero wrong** and fixed read **54/64, 64 reads**. [Actual complete source-audited run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924335444). Thus query reduction alone is not a reliable recovery guarantee; the Bayesian comparator is ACK-specific, **not official ActionShift/DualABI**.
- **Model-validity stress:** a separately prospective 64-reset/640-world PhysX study tested response-envelope widening calibrated on *different prior physical states*: narrow **58/64, 51 reads, 0 wrong**, versus conservative **58/64, 53 reads, 0 wrong**. No demonstrated gain from naive threshold expansion. [Original physical run and independent source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924240294).
- **Negative repeated-probe result:** two public motion observations did not improve 64 held-out task outcomes over one (**48/64 for both**) and consumed 43 vs 41 private reads in a truly stepped 640-world experiment. [Source-verified real results](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989).
- **Native VLA feasibility is not this result:** a frozen public SmolVLA checkpoint actually succeeded in **4/4** original Task 1 init-state episodes and **1/4** Task 0 episodes (two-task native exploratory pilot, not a full benchmark), but this had **no missing ACK or BeliefBridge recovery**. [Authentic official closed-loop run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924054645). Crucially, the actual LIBERO/robosuite OSC derives its new goal position from achieved EE pose (`self.ee_pos`), **not ManiSkill's accumulated last commanded target**; its source+live-controller diagnostic has passed. [Original native source witness](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924496336). Directly transporting the ManiSkill memory fault to LIBERO would be scientifically invalid.

### What reviewers can verify, and what is still missing

**One-click source-pinned outside-investigator entry:** [native true 2×2 nonzero ACK challenge](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/outside-true-2x2-nonzero-ack-physx.yml), using investigator-selected **new** reset states. Existing CI on the author's fork is author-operated source validation and **does not count as third-party independent replication**. A real external investigator must run the actual PhysX study on their own fork and publicly preserve their own original artifacts.

**Current contribution ceiling:** physically executed, source-auditable evidence that some complete hidden command histories are observable from public motion, allowing selective private-controller reads under a frozen empirical model. **Still required for a strong external method-paper claim:** a *model-validity-aware* response gate avoiding observed false confidence, fair public-sensing/latency/actuation-cost comparisons, a verified additional robot/task-competent checkpoint, real external investigator replication and peer review. No general robot safety or upstream ManiSkill adoption is claimed.

**Relationship to prior art:** ActionShift/ActionABI active identification and belief inference are related; we do **not** claim to invent active probing. Original frozen PPO checkpoints remain attributed to their publishers. This is an **independent contributor research fork**, never the official ManiSkill project.

---

## Representative research · When to read a hidden robot controller target?

**Question.** A frozen manipulation policy controls a stateful action interface, but an arm command may be executed without a trustworthy acknowledgement. The prior commanded target becomes uncertain. Should the adapter keep issuing conservative actions, stop, or pay for one authoritative target-state read? Can it select the *time* of that read based on explicit commanded-target error evidence?

**What we implemented:** a two-history SE(3) commanded-**setpoint** authority checker with a known Panda target/achieved controller chart; a bounded common native command is issued only when all possible prior targets stay within predeclared setpoint-error limits, otherwise the adapter spends one **privileged** target read and resumes the original pretrained PPO. **No new PPO/VLA is trained.** These are known robust-control ingredients; the research contribution being tested is their event-triggered protocol and measured resource–task outcome tradeoff, not a newly invented minimax theorem.

| Original preregistered real-PhysX population | Bounded, no state reads | Evidence-triggered one-read *if needed* | Fixed comparator |
|---|---:|---:|---:|
| **64 new task resets** · PullCube/StackCube, independent cohort | 41/64 | **58/64 · 17 reads** | Predeclared every-fourth-seed t3: 47/64 · 16 reads |
| **32 different NEW task resets** · *actually step-controlled query-time intervention* | 24/32 | **31/32 · 7 reads** | Fixed t3: 31/32 · 32 reads; **fixed t5: 32/32 · 32 reads**; fixed t6: 27/32 · 28 reads |

**Independent second-robot mechanism check (NOT policy transfer):** A separate BEFORE-outcome original PhysX experiment used **two distinct actual robots**, Panda and xArm6 Robotiq, each with 8 new `PickCube-v1` initial states, and genuinely separately stepped native target-action controllers under applied/held unknown-ACK truths. **16/16 had a measurable commanded-target history split**; an action-history observer given each hypothetical command history reconstructed the real post-step controller target to ≤`1.431e-8 m` on both robots. After a common zero-native probe the actual applied-v-held physical end-effector positions differed by **37.61–38.51 mm (Panda)** versus **41.55–41.70 mm (xArm6)**. xArm6's action dictionary requires `gripper_active`/`gripper_passive` instead of Panda's `gripper`: no robot substitution was accepted. **This does not demonstrate an online classifier of which ACK branch actually occurred, pretrained PPO manipulation success on xArm6, or independent outside-lab replication.** [**All pristine original 16 physical records, full zero-leak auditor and SHA256SUMS**](research/frozen_policy_transfer/evidence/cross_robot_panda_xarm6_original16_420001_430008/) · [original full 6-job native PhysX](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37899544825) · [pre-outcome frozen protocol](research/CROSS_EMBODIMENT_ACK_PREOUTCOME_V1.json).

**Read the original, not the narrative:** [32-state eight-controller complete original JSONs + SHA256SUMS](research/frozen_policy_transfer/evidence/query_timing_causal_new32_280001_290016/) · [newest 10-job audited original native PhysX](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896219598) · [before-outcome protocol](research/QUERY_TIME_CAUSAL_FRESH32_PREOUTCOME_V1.json) · [previous 64-state exact pinned source](research/frozen_policy_transfer/evidence/periodic_query_placebo_new64_260001_270032/) · [64-state source/paired inference and integrity analysis](research/frozen_policy_transfer/review/PAIRED_AUTHORITY_FRONTIER_64.md).

**New stronger cross-robot public-proprioception falsifier (prospective 2026-10-09):** The earlier **Panda + xArm6** result with 32/32 correct position-target recoveries used the SAME t2 native arm-command amplitude as prior robot-specific public-motion calibration. That fixed-amplitude claim was deliberately stressed on **eight wholly new robot/reset seeds**, each with applied/held ACK truth and both 100% and **40%** of the announced native action (**32 physically distinct fault×scale conditions, 128 genuinely stepped controller worlds; only eight unique reset seeds**). At 40%, the unchanged fixed-scale observation classifier **abstained on 8/16** and restored 8/16, while a **prespecified zero-privileged-read command-conditioned class center** restored **16/16** by using the known action amplitude without recalibrating the prior response envelopes. Across both scales, **command-conditioned 32/32**, frozen scale-one baseline **24/32**, naive applied/held assumptions **16/32** each; no new false confident labels seen. This is **scripted native-command target XYZ reconstruction**, *not* heldout PPO task success, unseen robot zero-shot policy transfer, formal physics error bounds or hardware safety. [**Exact original 6/6-green genuine PhysX run**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909572930) · [**five permanent original JSONs + SHA256SUMS**](research/frozen_policy_transfer/evidence/cross_robot_native_command_amplitude_shift_new32_540001_550004/) · [**pre-implementation frozen scope and negative methods**](research/CROSS_ROBOT_ACK_AMPLITUDE_SHIFT_PREOUTCOME_V1.json) · [**source and actual physical controller code**](research/cross_robot_ack_amplitude_physx.py). This is a very small **affine command-conditioning hypothesis**, not a newly invented state estimator or certified robustness against arbitrary action changes.

**Negative and falsifying controls matter:** The 32-state timing intervention shows that fixed **t5 achieves one more success than adaptive**, though at over four times the target-read cost; adaptive is *not globally optimal* or uniquely superior at equal information. A separately preregistered achieved-motion nearest-target observer made **15/32 wrong confident historical ACK labels** despite some native task successes; the later more conservative model abstains when it cannot distinguish histories. [Permanent original failures and wrong-label ledger](research/frozen_policy_transfer/evidence/public_response_ack_probe_32_negative/). Another study refuted naive zero-read minimax belief midpoint superiority ([original evidence](research/frozen_policy_transfer/evidence/belief_minimax_prospective_64_96001_97016/)).

**Boundaries before scientific use:** native `physx_cpu` ManiSkill, one Panda controller family **for all frozen-PPO task recovery**, a separate mechanism-only xArm6 experiment, two *released external* [ActionShift frozen PPO baselines](https://github.com/Archerkattri/actionshift), simulated zero-delta arm target holds rather than real packet loss, target-**setpoint** error bounds only, not contacts/trajectories/actuator safety, no head-to-head with equal-information ActionShift active belief adapters, no independent external adoption. Trial states are **not** 64 independent pretrained policies. The earlier eight physically completed original jobs suffered an **artifact naming bug** and were technically rerun unchanged to produce the source-complete audited 32-state archive, not double-counted as new experiments.

**Independent reviewer:** [one-click genuine PhysX frozen seven-controller replication on your own fork](.github/workflows/external-selective-query-physx.yml) · [reproduction guide](research/frozen_policy_transfer/INDEPENDENT_REPLICATION_QUICKSTART.md) · [full source-linked research packet](research/frozen_policy_transfer/CERTIFY_OR_QUERY_FLAGSHIP_REVIEW.md) · [open public falsification challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67). We welcome original negative results and unmodeled controller implementations. Previous detailed fork evidence index is [archived without deletion](research/frozen_policy_transfer/ARCHIVED_CONTRIBUTOR_RESEARCH_FRONT_PAGE_20261009.md).

---

# ManiSkill 3


![teaser](figures/teaser.jpg)
<p style="text-align: center; font-size: 0.8rem; color: #999;margin-top: -1rem;">Sample of environments/robots rendered with ray-tracing. Scene datasets sourced from AI2THOR and ReplicaCAD</p>

[![Downloads](https://static.pepy.tech/badge/mani_skill)](https://pepy.tech/project/mani_skill)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mani-skill/ManiSkill/blob/main/examples/tutorials/1_quickstart.ipynb)
[![PyPI version](https://badge.fury.io/py/mani-skill.svg)](https://badge.fury.io/py/mani-skill)
[![Docs status](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://maniskill.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/996566046414753822?logo=discord)](https://discord.gg/x8yUZe5AdN)

ManiSkill is an open-source framework for robot simulation and training powered by [SAPIEN](https://sapien.ucsd.edu/), with a strong focus on manipulation skills. Among its features include:
- GPU parallelized visual data collection system. On the high end you can collect RGBD + Segmentation data at 30,000+ FPS on a 4090 GPU
- GPU parallelized simulation, enabling high throughput state-based synthetic data collection in simulation
- GPU parallelized heterogeneous simulation, where every parallel environment has a completely different scene/set of objects
- Example tasks cover a wide range of different robot embodiments (humanoids, mobile manipulators, single-arm robots) as well as a wide range of different tasks (table-top, drawing/cleaning, dexterous manipulation)
- Flexible and simple task building API that abstracts away much of the complex GPU memory management code via an object oriented design
- Real2sim environments for scalably evaluating real-world policies 100x faster via GPU simulation.
- Sim2real examples for deploying policies trained in simulation to the real world
- Many tuned robot learning baselines in Reinforcement Learning (e.g. PPO, SAC, [TD-MPC2](https://github.com/nicklashansen/tdmpc2)), Imitation Learning (e.g. Behavior Cloning, [Diffusion Policy](https://github.com/real-stanford/diffusion_policy)), and large Vision Language Action (VLA) models (e.g. [Octo](https://github.com/octo-models/octo), [RDT-1B](https://github.com/thu-ml/RoboticsDiffusionTransformer), [RT-x](https://robotics-transformer-x.github.io/))

For more details we encourage you to take a look at our [paper](https://arxiv.org/abs/2410.00425), published at [RSS 2025](https://roboticsconference.org/).

Please refer to our [documentation](https://maniskill.readthedocs.io/en/latest/user_guide) to learn more information from tutorials on building tasks to sim2real to running baselines. If you find any bugs or have any feature requests please post them to our [GitHub issues](https://github.com/mani-skill/ManiSkill/issues/) or discuss about them on [GitHub discussions](https://github.com/mani-skill/ManiSkill/discussions/). We also have a [Discord Server](https://discord.gg/x8yUZe5AdN) through which we make announcements and discuss about ManiSkill.

Users looking for the original ManiSkill2 can find the commit for that codebase at the [v0.5.3 tag](https://github.com/mani-skill/ManiSkill/tree/v0.5.3)

## Installation
Installation of ManiSkill is extremely simple, you only need to run a few pip installs and setup Vulkan for rendering.

```bash
# install the package
pip install --upgrade mani_skill
# install a version of torch that is compatible with your system
pip install torch
```

Finally you also need to set up Vulkan with [instructions here](https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html#vulkan)

For more details about installation (e.g. from source, or doing troubleshooting) see [the documentation](https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html
)

## Getting Started

To get started, check out the quick start documentation: https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/quickstart.html

We also have a quick start [colab notebook](https://colab.research.google.com/github/mani-skill/ManiSkill/blob/main/examples/tutorials/1_quickstart.ipynb) that lets you try out GPU parallelized simulation without needing your own hardware. Everything is runnable on Colab free tier.

For a full list of example scripts you can run, see [the docs](https://maniskill.readthedocs.io/en/latest/user_guide/demos/index.html).

## System Support

We currently best support Linux based systems. There is limited support for windows and MacOS at the moment. We are working on trying to support more features on other systems but this may take some time. Most constraints stem from what the [SAPIEN](https://github.com/haosulab/SAPIEN/) package is capable of supporting.

| System / GPU         | CPU Sim | GPU Sim | Rendering |
| -------------------- | ------- | ------- | --------- |
| Linux / NVIDIA GPU   | ✅      | ✅      | ✅        |
| Windows / NVIDIA GPU | ✅      | ❌      | ✅        |
| Windows / AMD GPU    | ✅      | ❌      | ✅        |
| WSL / Anything       | ✅      | ❌      | ❌        |
| MacOS / Anything     | ✅      | ❌      | ✅        |

## Citation


If you use ManiSkill3 (versions `mani_skill>=3.0.0`) in your work please cite our [ManiSkill3 paper](https://arxiv.org/abs/2410.00425) as so:

```
@article{taomaniskill3,
  title={ManiSkill3: GPU Parallelized Robotics Simulation and Rendering for Generalizable Embodied AI},
  author={Stone Tao and Fanbo Xiang and Arth Shukla and Yuzhe Qin and Xander Hinrichsen and Xiaodi Yuan and Chen Bao and Xinsong Lin and Yulin Liu and Tse-kai Chan and Yuan Gao and Xuanlin Li and Tongzhou Mu and Nan Xiao and Arnav Gurha and Viswesh Nagaswamy Rajesh and Yong Woo Choi and Yen-Ru Chen and Zhiao Huang and Roberto Calandra and Rui Chen and Shan Luo and Hao Su},
  journal = {Robotics: Science and Systems},
  year={2025},
} 
```

If you use ManiSkill2 (version `mani_skill==0.5.3` or lower) in your work please cite the ManiSkill2 paper as so:
```
@inproceedings{gu2023maniskill2,
  title={ManiSkill2: A Unified Benchmark for Generalizable Manipulation Skills},
  author={Gu, Jiayuan and Xiang, Fanbo and Li, Xuanlin and Ling, Zhan and Liu, Xiqiang and Mu, Tongzhou and Tang, Yihe and Tao, Stone and Wei, Xinyue and Yao, Yunchao and Yuan, Xiaodi and Xie, Pengwei and Huang, Zhiao and Chen, Rui and Su, Hao},
  booktitle={International Conference on Learning Representations},
  year={2023}
}
```

Note that some other assets, algorithms, etc. in ManiSkill are from other sources/research. We try our best to include the correct citation bibtex where possible when introducing the different components provided by ManiSkill.

## License

All rigid body environments in ManiSkill are licensed under fully permissive licenses (e.g., Apache-2.0).

The assets are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode).
