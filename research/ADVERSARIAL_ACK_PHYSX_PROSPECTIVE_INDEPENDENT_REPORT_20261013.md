# Native PhysX execution acknowledgment corruption: bounded-risk selective confirmation

**Oct 13, 2026 • Prospective controlled simulator study, original 64 native worlds and independent numerical audit.**  
**Outcome:** predeclared engineering query-payload criterion **PASSED** on both native robot types, **but** the zero-error feasible-set rule, optimal reply-bit count and Bayes baseline are based on classical decision theory/information theory. This is NOT an original mathematical theorem, independent laboratory adoption, real sensor-noise calibration, or full robot-task success evidence.

## I. Real bug hypothesis & explicit model

A robot's control model uses a source sequence of actions, but delayed or bit-corrupted ACKs can cause the receiver to believe that actions actually executed when they did not. It may have an actual achieved EE pose from native physics, observed only through a finite-resolution bounded-error sensor chart. Trusting an unchecked receipt may choose an incorrect correction; always requesting the FULL ACK fixes the ambiguity but uses extra trusted reply payload.

**Assumed trusted sender knows actual execution h**, but an earlier two-bit untrusted received receipt r could differ from h in 0 or 1 bit. Each of the 4 histories occurs with prior 1/4. Corruption channel:
- r=h with probability **0.5**
- first bit flipped with probability **0.25**
- second bit flipped with probability **0.25**.

The receiver sees (r,z) with z in the registered quantized-support Y(h) of the true actual source-measured end-effector quaternion-log rotation. **No controller private target getter** is consulted by the decision policy. Synthetic sensor uncertainty bounds are explicit: 0.001 or 0.004 rad in each axis, quantization 0.005/0.015/0.04 rad.

## II. Mechanism and strongest matched baselines

Given an actual observation (r,z), construct the **entire information-consistent execution set**

    H(r,z) = {h: Hamming(h,r)<=1 AND z in Y(h)}.

Each h has a source-computable 6D correct native rotation command A(h) to the same all-ACK goal, previously validated in actual ManiSkill controller source; if two controls are numerically indistinguishable within 1e-6 in native control coordinates, they are the same corrective action.

- If every h∈H(r,z) requires the **same A(h)**, immediately issue it **without a trusted confirmation reply**.
- Otherwise ask the sender to distinguish one of K distinct needed action classes (not all hidden history identities); one trusted reply needs **ceil(log2 K)** bits. This assumes the receiver can send a query and the trusted sender knows both exact executed h and the query's action-class mapping; **request, authentication, network latency and query setup bytes are not priced**.
- For a zero-error protocol with the stated sender and observer side information, **ceil(log2 K)** is already the optimal information-theoretic reply length. No other equal-information exact zero-error protocol can improve the modeled per-cell fixed-length response payload. This is a standard classical result, not new math.
- Baseline **full trusted 2-bit ACK on every case**: exact zero error, **2 trusted reply bits**, same unpriced request assumptions.
- Baseline **no-extra-query Bayes MAP**: uses the same (r,z), exact fully specified error channel and uniform hidden-history prior; chooses the MAP corrective action. It is optimal in expected unverified classification risk **under the registered model** and NOT expected to have zero worst-case error without querying. The proposed selective protocol is therefore NOT falsely described as beating the Bayes oracle on identical cost and objective.
- Baseline **naïve trust the received 2-bit ACK**: immediately uses correction for r, without accounting for possible bit corruption.

## III. Frozen before outcomes and new true native PhysX execution

[Registered original trial protocol](SELECTIVE_CONFIRM_CORRUPT_ACK_PREREG_20261013.json), source Git blob `ac2af1cfdfcf1647e52b877014fef546ef5456df` frozen before new actual PhysX executions.

True physical-simulation test: two distinct ManiSkill-native PickCube-v1 CPU PhysX controller types, Panda and xArm6-robotiq, with `pd_ee_target_delta_pose` / root-aligned body delta-rotation chart. **New reset seed clusters** S=6800401..6800404 Panda and S=6900401..6900404 xArm6, not the earlier positive experiment's seeds. 4 seeds/robot ×2 native action variants ×4 actual hidden ACK histories = **32 original native PhysX worlds per robot, 64 total**.

Public achieved EE orientation and public reset quaternion of every original source world were recorded. Then every registered 3 sensor grid widths ×2 bounded-error radii ×2 action variants ×4 seeds per robot = **96 original dependent decision-parameter groups**. Under each true history the software exhaustively tests every possible registered delivered ACK (true + two one-bit flips) **and every possible quantized sensor reading** under the bounded noise model. These are not 96 independent robots or field trial episodes; only 8 independent simulated reset clusters.

- [Both full native PhySX jobs SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38376713806), 29/29 focused controlled unit/negative tests per robot.
- [Separate original-artifact independent audit SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38377254009), reconstructs ALL original public quaternion SO(3) relative-log features and independent expected receiver information sets, source-valid actions, Bayesian posteriors and query-length minima **without importing the policy module**. It verifies all 64 original native worlds, 96 parameter cells, zero unsafe command selection in stated model and the original result denominators. It is independently implemented numerical checking of original artifacts **not outside-laboratory replication**.
- The initial CI [38376280332](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38376280332) failed **BEFORE any PhysX execution** because a negative test toy accidentally shared the same mutable action dictionary across fake worlds, defeating the injected mismatch assertion. Fixed test fixture cloning without altering the preregistered source model or original new reset seeds; reran complete native PhysX study successful.

## IV. Registered outcomes and controls

| Robot type | Distinct native reset seeds | Original PhysX worlds | Original correlated sensor-condition groups | Mean trusted reply bits **saved** vs requesting full 2-bit ACK | Bayes MAP expected wrong correction rate if **no extra query** | Zero wrong corrections under fully registered bounded model |
|---|---:|---:|---:|---:|---:|---|
| Panda | 4 | 32 | 48 | **1.69140625** | **0.06640625** | Yes |
| xArm6-robotiq | 4 | 32 | 48 | **1.69140625** | **0.06640625** | Yes |
| Complete study | **8** | **64** | **96** | **1.69140625** | **0.06640625** | Yes |

**Interpretation:**
- Trusted reply budget is **2 - 1.69140625 = 0.30859375 bits on average**, not an actual variable-length stream length; it is the expectation of 0/1/2-bit *per-case fixed-length replies* over a **hypothetical specified probability model**. The real sender cannot always send a fractional bit. The costs of initial two-bit possibly corrupt ACK, requests, network RTT, authentication bytes, and any retransmission are **excluded**. Therefore NOT a measured total bandwidth or low-latency gain.
- The Bayes MAP wrong correction fraction of **6.640625%** comes from the same **assumed** 50% any-bit error channel, uniform histories and uniform feasible quantization bins, not natural observed packet corruption in a network or collisions.
- Full-ACK remains zero-error, as expected. Selective feasibility certification also returns zero incorrect corrective actions **by construction when its declared corruption/noise support is valid**. This does NOT guarantee safety if more than one ACK bit is wrong, the sensor-bound model fails, receipts are replayed without synchronization, or a trusted sender is absent.
- Original go/no-go: **both robot types** must save **at least 0.5 trusted reply bits on mean** over predeclared conditions, and no false-safe decision. Independently recomputed data: **BOTH PASS**. This is an original *engineering resource* gate, not scientific novelty superiority against known zero-error graph coding.

## V. What is still missing for PhD-grade original method and outside recognition

1. **New scientific mechanism beyond existing theory:** exact feasible-set queries/finite side-information coding are known; the new contribution is their physically grounded action-provenance application and original source-specific data structure, not a new theorem. Need a realistic online protocol for uncertain/late ACK, trust failures, true bus timestamps and calibrated observation uncertainties, with a falsifiable improvement vs the strongest already deployed robot runtime safety/filtering.
2. **Genuine task-level impact:** this study does not execute the correction to prove PickCube grasp task success or collision recovery, and no sensor measurement from a real camera or physically corrupted packet actually occurred.
3. **Outside validation:** no external robotics maintainer has merged this branch, no unaffiliated team reproduced the experiment, and no robotics conference or journal has accepted a paper.
4. **Strong action-chunk literature:** existing ICLR 2026 REMAC and October 2026 Consequence-Aware Adaptive Action Chunking (CA3C) already target action execution mismatch and replanning; they report endtask results. See https://proceedings.iclr.cc/paper_files/paper/2026/hash/c35834443b7881e782e52b3519fe27c7-Abstract-Conference.html and https://arxiv.org/abs/2610.07949 . No claim of beating these without implementing equal-cost production robot baselines.

**Current research classification:** preregistered two-robot system information-economy positive result with independent CODE evidence; incomplete original academic science and NO external scholarly acceptance. It is usable as an exploratory workshop *engineering measurement* lead, not an L9/L10 complete original-method flagship.
