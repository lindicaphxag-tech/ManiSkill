# Prospective query timing placebo: 64 NEW native PhysX task states, eight real controller arms

**Completed, NO post-hoc tuning, negative cases retained.** [Eight actually successful original CPU PhysX CI jobs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629). Source method/third-party PPO models and the **16-of-64 periodic query allocation** were frozen before ANY outcomes in [commit ee209f6](https://github.com/lindicaphxag-tech/ManiSkill/commit/ee209f6bc80e2bb280f9b00e6a9bafc330bdc799); immutable protocol Git blob `fc6c52c227f68c351b4f5637069672eae62a2e62`.

## What this tests (stronger than mandatory-read vs selective-read comparison)

The flagship bounded-or-query policy queries the real privileged target **when the same predeclared 0.05m/0.05rad two-history command authorization fails**. Prior trials compared it to mandatory every-episode readback and to zero-query refusal. Those contrasts do NOT isolate whether reading intelligently beats just allocating approximately the same number of queries without looking at evidence.

Here an otherwise identical new eighth PhysX world **precommits before trials** to a mechanically simple state-independent query schedule: after the actual unknown ACK at t=2 and before the first post-fault decision at t=3, read real target **iff seed % 4 == 0** (8/32 Pull seeds, 8/32 Stack seeds, **exactly 16/64 reads**). On all other states it runs the same original two-target robust bounded command and refuses if outside the bounds, without EVER querying. No adaptive tuning or new PPO.

The adaptive comparator, copied from the original full seven-arm method, was **not budget-matched post hoc**; its actual queries are reported verbatim. The periodic schedule is fixed and reproducible, **not a genuinely stochastic random-query method**, a learned query policy, or an optimal-information baseline.

## True PhysX, complete original denominator

| Arm/condition | Native tasks succeeded /64 | Privileged target **decision** reads |
|---|---:|---:|
| Source trained PPO/no injected target hold (context only) | 61 | 0 |
| Privileged live controller target oracle under fault | 59 | Repeated privileged access (not measured as 0) |
| Optimistic missing ACK guessed delivered | 40 | 0 |
| Strict exact common action or fail closed | 0 | 0 |
| Zero-query two-target bounded command | 41 | 0 |
| **Evidence-triggered bounded then ONE read only if required** | **58** | **17** |
| **PRECOMMITTED periodic 1-in-4 episode readback** | **47** | **16** |
| Every episode mandatory one readback | 60 | 64 |

**Primary matched-info-cost outcome:** selective/adaptive **58/64 using 17 reads**, periodic precommitted **47/64 using 16 reads**; query calls differ by **one**. Native same-seed binary task success discordance is **12 adaptive-only wins versus 1 periodic-only wins**; remaining paired cells both successful 46, neither 5. Exploratory, **unadjusted** conditional two-sided exact McNemar p ≈ **0.00341796875**. This tests task-state paired binary outcomes on the registered two tasks, NOT a universal population improvement, robotic collision safety or policy optimality. No multiple-comparison/robot-family generalization claim.

**Independent reset-state denominator:** PullCube 260001–260032, StackCube 270001–270032, **64 unique source states**, each with eight matched physical worlds; do not double-count distinct controller-world runs as independent reset states. Two original third-party ActionShift PPOs kept frozen, native controller `pd_ee_delta_pose` source to `pd_ee_target_delta_pose` target for **one Panda robot family**. The actual native gripper keeps policy action and the arm target is intentionally replaced by a **zero/held command at step index 2**, with unknown acknowledgment in the decision logic. This is NOT network packet loss, contact/torque safety, privileged-free operation or physically deployed robotics.

## Per-task and fixed chunks

| Task | Distinct states | Selective success | Periodic success | Selective reads | Periodic reads |
|---|---:|---:|---:|---:|---:|
| PullCube | 32 | **32** | 30 | 3 | 8 |
| StackCube | 32 | **26** | 17 | 14 | 8 |

| Task | Original shard | Selective succeeds | Periodic succeeds | No-query bounded succeeds | Every-episode target read succeeds | Selective private reads | Periodic private reads |
|---|---:|---:|---:|---:|---:|---:|---:|
| pull_cube | 0 | 8 | 7 | 6 | 8 | 2 | 2 |
| pull_cube | 1 | 8 | 8 | 8 | 8 | 0 | 2 |
| pull_cube | 2 | 8 | 8 | 8 | 8 | 0 | 2 |
| pull_cube | 3 | 8 | 7 | 7 | 8 | 1 | 2 |
| stack_cube | 0 | 8 | 4 | 3 | 7 | 5 | 2 |
| stack_cube | 1 | 6 | 5 | 3 | 7 | 3 | 2 |
| stack_cube | 2 | 6 | 3 | 1 | 8 | 5 | 2 |
| stack_cube | 3 | 6 | 5 | 5 | 6 | 1 | 2 |

### All 64 predeclared original task×seed outcomes (including failures)

| Task | Seed | No-fault source | Optimistic | Bounded no read | Selective | Periodic query | Mandatory read | Selective private reads | Periodic private reads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pull | 260001 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260002 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260003 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Pull | 260004 | 0 | 0 | 0 | **1** | 1 | 1 | 1 | 1 |
| Pull | 260005 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260006 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260007 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260008 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260009 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260010 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260011 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260012 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260013 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260014 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260015 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260016 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260017 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260018 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260019 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260020 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260021 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260022 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260023 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260024 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260025 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260026 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Pull | 260027 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260028 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Pull | 260029 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260030 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260031 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Pull | 260032 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 1 |
| Stack | 270001 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270002 | 1 | 0 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270003 | 1 | 0 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270004 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 1 |
| Stack | 270005 | 1 | 0 | 0 | **1** | 0 | 0 | 1 | 0 |
| Stack | 270006 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270007 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270008 | 1 | 0 | 0 | **1** | 1 | 1 | 1 | 1 |
| Stack | 270009 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270010 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270011 | 0 | 0 | 0 | **0** | 0 | 0 | 0 | 0 |
| Stack | 270012 | 1 | 1 | 0 | **1** | 1 | 1 | 1 | 1 |
| Stack | 270013 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270014 | 1 | 0 | 0 | **0** | 0 | 1 | 0 | 0 |
| Stack | 270015 | 1 | 0 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270016 | 1 | 1 | 0 | **1** | 1 | 1 | 1 | 1 |
| Stack | 270017 | 1 | 0 | 0 | **0** | 0 | 1 | 0 | 0 |
| Stack | 270018 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270019 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270020 | 1 | 0 | 0 | **0** | 1 | 1 | 0 | 1 |
| Stack | 270021 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270022 | 1 | 1 | 0 | **1** | 0 | 1 | 1 | 0 |
| Stack | 270023 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270024 | 1 | 0 | 0 | **1** | 1 | 1 | 1 | 1 |
| Stack | 270025 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270026 | 1 | 0 | 0 | **0** | 0 | 1 | 0 | 0 |
| Stack | 270027 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270028 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 1 |
| Stack | 270029 | 1 | 1 | 1 | **1** | 1 | 1 | 0 | 0 |
| Stack | 270030 | 0 | 0 | 0 | **1** | 0 | 0 | 1 | 0 |
| Stack | 270031 | 1 | 0 | 0 | **0** | 0 | 0 | 0 | 0 |
| Stack | 270032 | 1 | 0 | 1 | **1** | 1 | 1 | 0 | 1 |

## Reviewer source verification

Original source run 37833053629, original source evaluator tested commit `e23909a43b8d9aeb4dba5b46e8f9c9845993cb57`, original prior method Git blob `1dc653cdc44e422c8340475ad00f828b3a41eb4f`, robust certifier `bb5fd155b7291fb127f94138fca321201c8271c3`. Rejected out-of-bound actions, exact/nonexact projections and all original per-state native task success flags are contained in the original JSON. Eight original CI artifacts include complete stdout and `pip freeze`:

- pull_cube chunk 0: [source PhysX job 113503039123](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039123) · [original ZIP artifact 11574044288](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11574044288)
- pull_cube chunk 1: [source PhysX job 113503039148](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039148) · [original ZIP artifact 11573929639](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11573929639)
- pull_cube chunk 2: [source PhysX job 113503039562](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039562) · [original ZIP artifact 11574755657](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11574755657)
- pull_cube chunk 3: [source PhysX job 113503039419](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039419) · [original ZIP artifact 11574457033](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11574457033)
- stack_cube chunk 0: [source PhysX job 113503038670](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503038670) · [original ZIP artifact 11574103909](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11574103909)
- stack_cube chunk 1: [source PhysX job 113503039179](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039179) · [original ZIP artifact 11574307686](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11574307686)
- stack_cube chunk 2: [source PhysX job 113503039084](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039084) · [original ZIP artifact 11573944792](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11573944792)
- stack_cube chunk 3: [source PhysX job 113503039122](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/job/113503039122) · [original ZIP artifact 11575005123](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629/artifacts/11575005123)

A complete new stdlib verifier `research/audit_certify_query_periodic_placebo64.py` requires all eight original source files, 64 IDs, frozen checkpoint identities, true physics faults, each arm's privileged query ledger, exact scheduled seed quota, measured vs theoretical commanded-target audit error, and honest native task results. Its conditional McNemar calculation is **exploratory and unadjusted**, not a statistical power statement about unseen robot embodiments.

**Not claimed:** third-party lab reproduction, acceptance by official ManiSkill or ActionShift, VLA training, cross-robot embodiment transfer, physically measured TCP/ROS ACK loss, motor torques, force/collision guarantee, or a newly invented event-triggered sensing theory.

**Next hard evidence gate:** a separately maintained second controller and unknown delay/drop/reorder protocol, task-level trajectory/contact risk, random/learned budget-matched query policies, independent outside-lab execution, and calibrating observation reliability against false confident target-history authorizations.
