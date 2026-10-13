# Native PhysX execution-receipt generalization: in-hindsight compression disappears under heldout codebooks

**2026-10-13 • prospective matched, original 256-world CPU PhysX result.**
**This is an observed systems finding + explicit negative go/no-go, not a first-new zero-error information theorem, robot hardware safety certificate, or accepted scholarly publication.** Author-independent artifact-audit workflow: [#38389862807](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38389862807). Do NOT describe that audit as passed until its exact job succeeds.

## Causal question

Previous information-theoretic study [#38363869998](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363869998) reported **64 of 96** actual native Panda/xArm6 quantized public EE orientation sensor cases could be resolved with <2 source ACK bits while preserving unique corrective control. But those per-reset receipt graphs were built from **all four original simulated ACK alternatives on the SAME test reset**. While valid as *retrospective conditional information minima*, this is an optimistic `oracle-case-informed codebook`. It is **not proof** a deployed receiver can infer that graph for a previously unseen world.

Our new question was more causally valid:

> Freeze receipt codebooks using only an earlier, independent robot-reset training cohort. On newly heldout true native controllers, do compact receipts still outperform a fully trusted two-bit ACK when a fraction of receipts become stale?

## Frozen source boundaries

- Original full source hypothesis/protocol: [prospectively frozen test design](TRANSACTIONAL_NATIVE_RECEIPT_PREREG_20261013.json), unchanged Git blob `3b79f160de1f30ec22419169956588853f6eb667`.
- Training: four older original native CPU PhysX seeds per robot from [#38363869998](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363869998). The codec must be fixed from these **training-only** public quaternion-log bounded-noise support unions for each robot and action variant. No test seed's unobserved hypothetical alternative can fit the graph or Bayes prior.
- Test: **four fully new reset clusters per robot** (Panda S6000501–04, xArm6 S6100501–04), 2 announced actual native delta action variants (A/B), 4 hidden execution ACK histories, and 4 prospectively fixed policies = **128 actual independently reset PhysX worlds per robot, 256 policy worlds total**, but only **8 independent reset clusters**.
- Observation: current 3D log of actual public achieved EE rotation relative to public reset, quantized at fixed 0.04 rad per component with fixed synthetic ±0.004 rad per-component bounded observation model. This is NOT actual calibrated camera noise or hardware.
- Policies, same histories/reset/seeds: `EPOCH_FULL_ACK` (fresh full 2-bit ACK plus 1-bit epoch = 3 paid bits), `EPOCH_BLIND_COMPRESSED` (uses the previous epoch's payload in 50% of registered histories and does not reject stale), `EPOCH_GUARDED_COMPRESSED` (rejects stale or out-of-training-support packets, obtains a new charged 2-bit true receipt), and `SENSOR_ONLY_OPTIMAL_BAYES` (zero ACK bits, true training-support posterior MAP).
- The current sender KNOWS actually executed ACK truth, but that sender's secure transport trust is ASSUMED in simulation rather than demonstrated. Sequence numbers are established networking, not original novelty.

## Original physical-CPU outcomes, full denominator

[Original full 2/2 native simulator jobs SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38388979357). Each robot's 128-world original source results are in that Actions run's artifact.

| Original outcome | Panda | xArm6 |
|---|---:|---:|
| Actual native PhysX policy worlds | 128 | 128 |
| Independent fresh reset clusters | 4 | 4 |
| Native controller action variants | 2 | 2 |
| Frozen complete hidden ACK histories | 4 | 4 |
| Frozen policies repeated per history | 4 | 4 |
| New TRAIN-ONLY codebook's minimal bits | **2** | **2** |
| Transaction guard wrong native corrective commands | **0** | **0** |
| Epoch-blind stale packet wrong native corrective commands | **8** | **8** |
| Original reset clusters with strictly improved corrected orientation by >=0.001 rad vs blind packet | **4/4** | **4/4** |
| Average charged guard payload + epoch + requery bits | **4.0** | **4.0** |
| Fully trusted current ACK comparison (2 bits + epoch) | **3.0 bits** | **3.0 bits** |

The prior per-reset hindsight `χ(G)` may permit 1-bit/0-bit codes for many conditions; the TRAIN union graph contained three needed label colors per robot×variant (color assignment `[0,1,1,2]`), hence fixed-length **ceil(log2 3)=2 bits** for unseen resets. Our guard then spends an extra one-bit epoch plus the charged reliable requery for any stale/out-of-support packet. Even with exactly 0 wrong control actions and measurable recovery benefit compared with a weaker epoch-blind packet, the full ACK has the SAME no-error action outcome using *fewer paid bits*. Therefore **the preregistered multi-objective gate is FALSE**.

**Key counterfactual conclusion:** The expected communication savings depended on a codebook tailored to each test reset's full counterfactual ACK outcomes; once this hindsight is disallowed and external fresh payloads are faithfully priced, it is **not** an additional operationally useful compact control protocol. This is evidence of *codebook generalization and information budget*, not an information-theoretic new impossibility theorem.

## Prior art and expert bar

- [RACE (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fab80bb9d97e9b9ff5c19f91f72838c6-Abstract-Conference.html) and [REMAC (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c35834443b7881e782e52b3519fe27c7-Abstract-Conference.html) study action-execution and policy-latency consistency with actual task performance.
- PACE/FutureRTC and the main LeRobot RTC `reset_epoch` are already relevant execution-consistency methods. Rolling sequence/nonce and receiver discard-on-stale semantics do not qualify as new theory or first-invention.
- A valid new mechanism must remove the trusted sender assumption without unearned hidden information, or prove a concrete robust continuation envelope with explicit observation calibration and realistic task-level risk, versus these matched prior strategies; it cannot be achieved merely by renaming sequence numbers or retuning quantization after inspection.
- An independently implemented auditor of same original 256 worlds remains **software verification**, not outside-lab academic recognition. No accepted manuscript, new official upstream PR or external research-group adoption from this experiment is claimed.

**Decision:** the new training/test generalization and paid-communication comparison invalidates the earlier favorable practical-compression interpretation for deployment. Preserve original results and this negative result together, without hiding either. The correct next action is to stop marketing graph-code compression as a new original doctoral-level algorithm; future work would need physical-controller execution provenance integrated into a real chunk policy and performance on completed robot tasks.
