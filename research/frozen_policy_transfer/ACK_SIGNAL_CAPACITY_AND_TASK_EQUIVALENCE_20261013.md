# Signal-budget / task-equivalence certificate for missing robot acknowledgements

**Status (2026-10-13): exact finite mathematical bound + independent numerical oracles; NOT new real PhysX evidence, a safety proof, or a previously unknown information-theoretic result.**

## Question

Two missed execution acknowledgements (ACKs) can yield four plausible persistent commanded-target histories:

`{HELD/HELD, HELD/APPLIED, APPLIED/HELD, APPLIED/APPLIED}`.

A proposed probe returns one frozen **binary** public signal `Z∈{0,1}`. A deterministic policy that uses only Z has at most two possible recovery decisions. It cannot, solely through that signal, identify four distinguishable histories. More calibration resets do not add an observation outcome.

However, **history identification is not necessarily the task objective**. Different histories may admit the *same* safe/effective recovery decision. Their decision-level equivalence must be established via a source-grounded, action-specific task-loss matrix; it cannot be assumed from similarity of current XYZ observations.

## Conditional exact optimization

Let histories `H={h1,...,hn}`, frozen recovery outputs `D=H` (each output is a candidate history-associated recovery action), arbitrary nonnegative losses `L(h,d)`, and an independently justified bounded prior set

`P={p: sum_h p_h=1, lower_h<=p_h<=upper_h}`.

For an observation alphabet with at most `M` distinct outcomes, any deterministic decoder has at most M distinct recovery outputs `S⊆D`. Even with hypothetically perfect intervention-dependent signals, the decision loss cannot be smaller than

`R_floor(M) = min_{S⊆D, |S|<=M} max_{p∈P} sum_h p_h min_{d∈S} L(h,d)`.

**Proof.** For any decoder, its selected output for history h is in its image S. Its loss is at least the best loss among S; multiply by any fixed p, sum, and take max over admissible p, then minimize over candidate images. This establishes a lower bound for every physical signal law. A hypothetical noiseless oracle that sends the best output index in S to the decoder can attain the expression, showing it is *optimistically tight* for the stated abstract observation/cost model, not necessarily achievable by a real controller. Under a rectangular prior set, maximize the fixed nonnegative loss vector by filling admissible upper-prior mass in descending loss order; exhaustive decision-set enumeration solves the finite bound exactly.

In the special case of four independent equally likely and truly different histories, zero-one history loss gives:

| Distinct observation outcomes M | Optimistic minimum worst-case error |
|---:|---:|
| 1 | 0.75 |
| 2 (one-bit sensor) | **0.50** |
| 3 | 0.25 |
| 4 (two bits worth of output labels) | 0 |

Thus a **5% history-misclassification guarantee is mathematically impossible with one binary observation in this four-truth, symmetric zero-one loss example**, regardless of the calibration sample count.

This is **not a universal two-bit sensor requirement for four histories**. If `HELD/HELD` and `HELD/APPLIED` admit the same zero-loss correction, and the remaining pair admits another, a two-outcome signal has `R_floor(2)=0`. Distinguish **recovery-action equivalence** from hidden-history equality. Likewise, asymmetric losses, prior bounds and additional available readback decisions change the answer.

## How this changes prospective robot experiments

1. Freeze the actual missing-ACK truth set and physically valid recovery candidates. Compute or independently estimate a task-level loss matrix for each history–recovery pairing on distinct training/calibration resets, not on the held-out decision cohort.
2. Before allocating physical probing budget, evaluate `R_floor(2)` for a frozen binary response. If it exceeds the desired risk cap, that **entire one-bit probe-based decision class** is excluded; use additional genuinely distinct information, authoritative target readback or abstention rather than collecting more identical Z samples.
3. If the risk floor allows admission, still require source-valid common native actions, fresh action-conditional signal likelihoods, simultaneous familywise calibration, complete cost accounting, and strong fixed-probe/zero-probe/privileged-readback baselines. An optimistic floor below the cap is **necessary, not sufficient**.
4. Report exact task success and wrong-confident authority alongside abstentions, actual robot motion/contact costs, query counts and independent reset clusters. Do not relabel reused worlds as independent calibration samples.

## Implemented artifact

- `research/ack_multihistory_minimax.py::optimistic_signal_capacity_floor`: exact task-loss-aware finite-observation lower bound, arbitrary nonnegative recovery matrix and bounded prior.
- `research/ack_multihistory_minimax.py::minimum_signal_outcomes_for_risk_cap`: minimum *not-yet-ruled-out* alphabet size for a specified loss budget; not a controller certification.
- `tests/test_ack_multihistory_minimax.py`: independent HiGHS LP validation across random 2–5 history models, plus four-truth exact counts, a task-equivalence counterexample, malformed evidence and infeasible decision classes.

**Novelty boundary:** the pigeonhole/information-capacity reasoning is elementary and already known in decision theory. Its value here is diagnosing a concrete mismatch between the frozen ACK sensing interface, the controller-history hypothesis set and the actual task-equivalent recovery actions. Neither paper priority nor a positive physical performance claim is established by this mathematical guard. The prior negative 48-world native PhysX pilot remains unchanged.
