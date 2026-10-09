> **Independent contributor's RESEARCH FORK, not the official ManiSkill 3 project.** All controller-repair experiments here are contributor-operated; no ManiSkill maintainer adoption, external lab replication, real hardware or certified collision safety is implied.

## Representative research · When to read a hidden robot controller target?

**Question.** A frozen manipulation policy controls a stateful action interface, but an arm command may be executed without a trustworthy acknowledgement. The prior commanded target becomes uncertain. Should the adapter keep issuing conservative actions, stop, or pay for one authoritative target-state read? Can it select the *time* of that read based on explicit commanded-target error evidence?

**What we implemented:** a two-history SE(3) commanded-**setpoint** authority checker with a known Panda target/achieved controller chart; a bounded common native command is issued only when all possible prior targets stay within predeclared setpoint-error limits, otherwise the adapter spends one **privileged** target read and resumes the original pretrained PPO. **No new PPO/VLA is trained.** These are known robust-control ingredients; the research contribution being tested is their event-triggered protocol and measured resource–task outcome tradeoff, not a newly invented minimax theorem.

| Original preregistered real-PhysX population | Bounded, no state reads | Evidence-triggered one-read *if needed* | Fixed comparator |
|---|---:|---:|---:|
| **64 new task resets** · PullCube/StackCube, independent cohort | 41/64 | **58/64 · 17 reads** | Predeclared every-fourth-seed t3: 47/64 · 16 reads |
| **32 different NEW task resets** · *actually step-controlled query-time intervention* | 24/32 | **31/32 · 7 reads** | Fixed t3: 31/32 · 32 reads; **fixed t5: 32/32 · 32 reads**; fixed t6: 27/32 · 28 reads |

**Read the original, not the narrative:** [32-state eight-controller complete original JSONs + SHA256SUMS](research/frozen_policy_transfer/evidence/query_timing_causal_new32_280001_290016/) · [newest 10-job audited original native PhysX](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896219598) · [before-outcome protocol](research/QUERY_TIME_CAUSAL_FRESH32_PREOUTCOME_V1.json) · [previous 64-state exact pinned source](research/frozen_policy_transfer/evidence/periodic_query_placebo_new64_260001_270032/) · [64-state source/paired inference and integrity analysis](research/frozen_policy_transfer/review/PAIRED_AUTHORITY_FRONTIER_64.md).

**Negative and falsifying controls matter:** The 32-state timing intervention shows that fixed **t5 achieves one more success than adaptive**, though at over four times the target-read cost; adaptive is *not globally optimal* or uniquely superior at equal information. A separately preregistered achieved-motion nearest-target observer made **15/32 wrong confident historical ACK labels** despite some native task successes; the later more conservative model abstains when it cannot distinguish histories. [Permanent original failures and wrong-label ledger](research/frozen_policy_transfer/evidence/public_response_ack_probe_32_negative/). Another study refuted naive zero-read minimax belief midpoint superiority ([original evidence](research/frozen_policy_transfer/evidence/belief_minimax_prospective_64_96001_97016/)).

**Boundaries before scientific use:** native `physx_cpu` ManiSkill, one Panda controller family, two *released external* [ActionShift frozen PPO baselines](https://github.com/Archerkattri/actionshift), simulated zero-delta arm target holds rather than real packet loss, target-**setpoint** error bounds only, not contacts/trajectories/actuator safety, no head-to-head with equal-information ActionShift active belief adapters, no independent external adoption. Trial states are **not** 64 independent pretrained policies. The earlier eight physically completed original jobs suffered an **artifact naming bug** and were technically rerun unchanged to produce the source-complete audited 32-state archive, not double-counted as new experiments.

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
