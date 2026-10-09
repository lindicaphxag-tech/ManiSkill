# Frozen BEFORE implementation / outcomes: public PRECONTACT authority query against strong task-ID prior

Recorded 2026-10-09. Original signed baseline source experiment completed before this protocol:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486
64 reset states and 448 true real-PhysX target-worlds, 2 released PPO checkpoints.
Original source blob: `99836af14205fe3e95e52a2e0d68237c7c8a9045`.
Original bounded multi-history solver blob: `36707a177549104ba5b4bd9bcebc76518f0d2840`.

## Exact NEW physics registers
PullCube-v1 **470001–470008** and StackCube-v1 **480001–480008**.
No seed from the original 420001–420032 / 430001–430032 cohort is reused.
Two genuine consecutive native arm ZERO/HOLD physical faults at t=2 and t=3 with BOTH controller delivery ACKs unknown to the observer; unchanged task gripper.

Seven original independent actual native control worlds plus TWO additional actual simulated worlds at each reset state:
1. Precontact-authority method: after t=3, if history belief is ambiguous, calculate 3D center distance to the manipulated object's center using the simulator's *FULL-STATE observation field already visible to the source PPO* (Stack cubeA pose; Pull obj pose); compute both the achieved tool pose distance and the requested physical source-policy target distance to that object. If min distance <= **0.10 metres**, spend ONE authoritative controller-target read before dispatch; otherwise retain the existing original robust setpoint bounded-or-one-query gate. No more than ONE trusted read per original episode, ever.
2. Strong trivial task-ID baseline: on StackCube, fixed target read at t=4; on PullCube, preserve original geometry-triggered one read. A method that cannot beat this simple predictor cannot claim novel query-timing superiority.

Three original strongest comparators that MUST be displayed and fully run: geometry-triggered selective read, one mandatory fixed t4 read, zero-query bounded geometry. Also retain remaining four original physically stepped controller arms, and preserve all failures.

Checkpoint SHA256 frozen and identical to original source:
- Pull: `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`
- Stack: `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`
- HF released revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`.
- Panda native target controller `pd_ee_target_delta_pose`; source achieved-delta `pd_ee_delta_pose`.
- Original action-mapping geometry: 0.05 metre coordinate-infinity commanded-setpoint bound and 0.05 radian geodesic; target native action remains normalized.
- 50 simulator steps per episode; report official native task success independently of geometry certificate.

**Decision-input restriction:** The precontact trigger gets simulator full-state TCP and object pose **available in the source-policy state observation**. It may NOT access the controller's private target state, actual held-v-applied truth, official task success or reward. Such full-state task observation is **not** an RGB/camera-only capability and does not establish real-robot sensing.

**Scientific integrity:** 16 original seeds, 9 actual independently stepped controller worlds, 2 real native hold faults for every operational arm, exact refusal arm early halt clearly recorded. All paired task outcomes, trusted-read steps/counts, early refusals, task-success steps, near-contact public distances and original source/checkpoint identity must be published. Reject false positives and source omissions. We do not expect a guarantee of improved outcomes. We WILL preserve failures. Any post-hoc tweak of threshold, release prior or cohort cannot be represented as this precommitted method.

The 0.10 metre proximity is an *a priori heuristic* corresponding to 2.5 times 4cm cube width. It is NOT fitted to this new cohort nor is it a formal contact-safety threshold. This is author-operated official ManiSkill PhysX, not independent lab validation, network-level packet loss, third-party acceptance, cross-robot frozen-policy execution or robotic contact safety.
