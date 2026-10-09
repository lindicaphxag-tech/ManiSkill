# Observable-ACK: before-outcome public-probe identifiability contract (v0.1)

Date: 2026-10-09. **Method specification and executable synthetic tests, not a completed PhysX experiment, a preregistered positive finding, or a formal safety certification.**

## Motivation and decisive falsifier

The original source-audited 64-state compound-ACK PhysX result is NEGATIVE for the previous reactive-query claim: 45/64 success with 44 target reads versus fixed-t4 55/64 with 64 reads. A retrospective task-ID composition yields 55/64 with 55 reads, **but that hybrid was never physically executed**. See PR #110 and permanent source-archive PR #111. Any new claim must prospectively beat a task-aware scheduled baseline, not merely a weak zero-query opponent.

## Mechanism

Let the complete, known finite controller target hypotheses be M_h (XYZ only), public achieved pose x, and a common known-delivered physical native target translation d. Under an independently attested **one-step** response envelope

    y = x + alpha_h (M_h + d - x) + e,
    alpha_h in [alpha_min, alpha_max] subset [0,1], ||e||_2 <= epsilon,

each history's public-output set is a 3-D line segment thickened by a noise ball. For each d, calculate exact 3-D segment-to-segment distances. A public probe has a conditional unique-history certificate only if the **minimum across every pair** exceeds 2 * (epsilon + guard). With overlapping possible responses, the controller MUST query or refuse. After physical dispatch, identify a branch only if precisely one candidate segment is compatible with the real public achieved XYZ; reject if zero matches (model falsified), and abstain if multiple.

Only attempt this mechanism when:
1. all possible hidden target histories are enumerated, with provenance from a known action interface;
2. the native chart is independently checked, the common command is actually delivered, and the measured public before/after motion is correctly time aligned;
3. gain/noise envelopes are calibrated on genuinely **disjoint** source trajectories for the same controller, fault regime, load/contact phase and sensor;
4. the candidate d is legal as a native translation and **every** hypothetical post-command setpoint is within a declared per-axis error cap relative to the source intended target. No rotation command is generated.

Even then the guarantee is ONLY history discrimination conditional on a correct response model. It is not task success, probe optimality, force/torque/collision safety, network packet-loss fidelity or a calibrated distribution-free coverage guarantee. A *model-independent* guarantee is impossible from code alone.

## Prospective PhysX experiment gate (not yet performed)

Precommit and source-freeze BEFORE observing any NEW outcomes:
- 64 new reset seeds, e.g. PullCube 620001..620032 / StackCube 630001..630032; must first verify they are disjoint from all prior calibration and test seeds and lock original PPO weights and source controller code hashes.
- Same two unknown-ACK target-hold faults, same genuine native simulator family, same downstream action admissibility and setpoint accuracy bounds, same stopping rules across competing controller arms.
- Calibrate alpha interval and public-observation/model error on a **separate dataset** (independent initial states, independent motion phase). Freeze calibration *before* test state runs; refuse any phase outside validated coverage. Compare calibration misses explicitly, including contact-induced model falsification.
- Compare: (A) fixed immediate t4 query; (B) frozen old reactive scheme; (C) task-aware policy chosen on OLD cohorts only; (D) proposed public-probe-when-certified, otherwise query/refuse; (E) always no-query. Include explicit probe cost, decision-query cost, extra physical steps, irreversible task harm, failure-to-reach-both-faults and early refusal on all seeds.
- Fair information comparison: cap **each adaptive and task-aware comparator** at 48 actual privileged target reads across 64 states, in deterministic 8-state shards with allocation frozen before result; report also unconstrained fixed-t4 as a separate 64-read upper-information comparator. Do not call these equal-budget if actual consumed reads differ; report the exact success-query Pareto pairs. Never let probes use hidden target getters, outcomes or task reward.
- Primary success endpoint: original external frozen PPO task completion over ALL 64 original registered resets; preregister task-specific results and paired discordance; secondary: **correct public-history identification and abstention coverage with audit-only hidden truth**, correct setpoint command error on actually delivered actions, data-model falsification rate, total added steps and readback tokens.
- Go/no-go for the new idea: if conditional public-motion model calibration fails or *actual* certified probe coverage is near zero, report a **negative** mechanism result without optimizing thresholds using test outcomes; if success fails to exceed the strongest task-aware information-matched competitor, do not claim an adaptive-query advantage.
- Outcome-independent, fail-closed integrity audit must confirm all seeded physical runs, exact model/calibration provenance, both faults attempted with every early refuse retained, original run hashes, nonexecuted masked commands kept separate from executed setpoint audits, and every private getter categorized as decision-read or audit-only.

## The immediate deliverable

`research/public_probe_observability_contract.py` and pure-stdlib falsification tests encode the observation-set intersection and refusal logic. They do not execute ManiSkill or claim runtime integration. **No new PhysX study, cross-platform validation or third-party adoption is asserted by this branch.**
