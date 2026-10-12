# Hidden execution ACK and persistent controller memory: strict novelty and falsifiability register
**Frozen research positioning · 2026-10-13 · NO NEW POSITIVE OUTCOMES**

## Closest antecedents: clearly distinguish what IS NOT new

1. **Hu et al., "Real-World Reinforcement Learning of Active Perception Behaviors" (AAWR, NeurIPS 2025)** — learns active information-gathering actions using privileged teacher value information; reports 8 manipulation tasks on 3 robots. Real active perception is already an established competing capability. https://arxiv.org/abs/2512.01188
2. **"ActiveArena: Benchmarking and Understanding Active Perception in Robotic Manipulation" (September 23, 2026; preprint)** — active exploration, long-term memory, visual interaction, OOD protocols, 35 tasks. It is NOT an existing execution-ACK benchmark and cannot be cited as direct apples-to-apples superiority; it is a demanding adjacent generalization target. https://arxiv.org/abs/2609.24124
3. **Kobayashi, "When Identifiability Is Not Enough: Terminal Controllability in Task-Compatible Active Calibration" (June 2026, preprint)** — identifies an important orthogonal requirement: a probe can reveal hidden state yet leave the system in a poor task-recovery configuration. Task-compatible information seeking is prior art and must be explicitly controlled for. https://doi.org/10.64898/2026.06.11.731593
4. **ActionShift / DualABI** (https://github.com/Archerkattri/actionshift) already uses active probing and structured latent **action-interface** uncertainty. No claim of having invented information-gain actions, belief update, or general hidden action semantics.

## Actual candidate scientific question

**When a robot's last command may be unacknowledged, and its internal target-memory register is not directly exposed, when should a running manipulation policy (i) act using current public observations, (ii) spend task-compatible motion to obtain information, (iii) request an authoritative controller target read, or (iv) abstain?**

This differs from generic action-ABI inference only if the hidden *history of attempted command execution* and persistent commanded target memory are necessary to reproduce the phenomenon. Every competing action must be derivable from ONE admissible native controller action across all possible history states; made-up history-conditioned targets are forbidden.

The current `ack_native_probe_source_adapter`, `ack_robust_readback_value`, `ack_finite_sample_signal_calibration` and CPU tests are **conditional method prototypes**. Binomial intervals, binary minimax losses and constant-time four-rule decisions are established mathematical building blocks, NOT new independent theory claims.

## Original negative evidence that must remain visible

Original [48/48 Panda/xArm6 PhysX fixed-probe worlds, exact protocol and logs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276) span only EIGHT independent reset states: zero, fixed X and fixed Y probe under both physically applied and held t2-command branches. The previously frozen +5 mm observation-separation improvement gate FAILED for both robots: about +0.021 mm for X, much smaller than the threshold. This is NOT a positive result for an adaptive policy or a calibrated response-likelihood model. An earlier original 64-world study similarly found 32/32 correct history decisions from zero and nonzero probes, with NO decision-gain count.

## Mandatory **before** any originality/flagship performance claim

- **New independent reset cohorts:** freeze training/calibration/validation/test seed ranges and robot control configurations BEFORE observing held-out outcomes. Count unique resets, never correlated truth×probe worlds as iid subjects; estimate matched uncertainty at reset-cluster level.
- **Admissible actions:** every proposed probe is a single native 6D command, replayed through the actual target-controller recurrence for all hidden histories; no true target getter, simulated hidden ACK labels or oracle future outcomes may enter decisions.
- **Calibration:** pre-specify binary public signal thresholds and likelihood family; derive familywise finite-sample simultaneous bounds on a DISJOINT calibration population. Honest abstention/readback if the bounds are too wide. If prior prevalence shifts, test a held-out prior interval, not an after-the-fact optimum.
- **Task-compatible probing:** charge actual actions, time, sensor reads and **measured** motor/contact budgets if claiming robot costs. Do not use arbitrary declared proxy costs as physical energy. Probe-induced collision, terminal loss of control, or loss of downstream grasping ability are primary failures even if ACK was inferred correctly.
- **Mandatory baselines in the same environment:** never probe; fixed X/Y probe (original negative controls); mandatory authoritative target read; random equal-budget source-valid probe; equal-budget information-seeking baseline that does not use the novel hidden-history model; oracle privileged diagnostic UPPER BOUND only.
- **Primary outcomes:** task completion/recovery success, wrong-confident action-authority rate, number of paid authoritative reads, wall-clock delay and measured action effort **together** (Pareto tradeoff), plus fully reported abstention and failed reset rates. Pure across-world XYZ separation is ONLY a mechanistic auxiliary metric.
- **No novelty shortcut:** AAWR/ActiveArena results are NOT direct matched experiments for the current problem. A fair experimental adaptation is required before comparative superiority. Explicitly report if an outside baseline cannot represent hidden target memory.
- **Prospective negative-stop criterion:** if equal-cost active actions do not improve properly calibrated task-level risk/cost over mandatory readback or zero probe on unseen resets, write a negative result. Do not retune the threshold, exclude difficult cases, or call conditional toy math a robotics advance.

## Evidence level ledger

- [x] Established, merged EEG model engineering (Braindecode #1200/#1319): external upstream evidence, separate from THIS research.
- [x] PhysX initial mechanistic test: authentic and complete, **negative** for fixed nonzero probe gain.
- [x] Conditional exact decision algorithms and independently tested confidence-interval arithmetic: CPU/software evidence.
- [ ] Fresh, independently calibrated binary observations from original PhysX resets.
- [ ] Native active-probe-vs-readback cost-controlled policy comparison with actual task outcomes.
- [ ] Strong method baselines and statistically defensible independent test cohorts.
- [ ] External-lab reproduction or peer-reviewed method/phenomenon paper.
- [ ] Formal upstream ManiSkill integration/acceptance (current #167 is OWN-FORK Draft).

**Current rigorous label:** promising source-constrained algorithmic research program, NOT yet a validated original state-of-the-art active robot policy, formal safety certificate, peer-reviewed result, or L9/L10 acceptance.
