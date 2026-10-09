# BeliefBridge: FULL 16-state, seven-arm, TWO unknown-ACK genuine PhysX results

**2026-10-09, v3 pre-outcome source-frozen experiment — complete denominator, mixed/negative algorithmic outcome.** This is an original *contributor-executed* closed-loop systems experiment, **not** robot hardware, actual network packet loss, clinical or collision safety, peer-reviewed publication, or independent external replication.

## Immutable original execution
- **Native full run [#37898781176](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37898781176): all three jobs SUCCESS**, including geometry contracts and genuine native simulator worlds for both PullCube and StackCube.
- [Original PullCube 8-state raw JSON, logs, source blobs and checksum archive (artifact #11601523455)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37898781176/artifacts/11601523455).
- [Original StackCube 8-state raw JSON, logs, source blobs and checksum archive (artifact #11600918940)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37898781176/artifacts/11600918940).
- Exact source under test: `b7670dd17037bbb94d208a40a1e068ce972b5484`; conservative multi-history bounded-action certifier source Git blob `36707a177549104ba5b4bd9bcebc76518f0d2840`; native runner source Git blob `99836af14205fe3e95e52a2e0d68237c7c8a9045`.
- **Prospective v3 protocol** frozen before these results: [COMPOUND_ACK_MULTI_HYPOTHESIS_PRECOMMIT_V3.md](../COMPOUND_ACK_MULTI_HYPOTHESIS_PRECOMMIT_V3.md). Source-file Git blob `99e904c21a2c4c0b8e3ca15ee9da4ddd44d0caa4`.
- The **v1** experiment failed due to counting physically masked commands as executed; the **v2** experiment failed because the mandatory readback arm used an unsynchronized single-state observer during its prequery wait. Both failure records are explicitly retained in the v3 protocol, and v3 uses NEW 400001/410001 reset-state ranges instead of reusing those partially inspected development cohorts.

## Original REAL simulator evaluation conditions
- Two released, SHA-frozen third-party ActionShift PPOs, no retraining; PullCube-v1 400001–400008 and StackCube-v1 410001–410008.
- **16 original reset states × 7 independently stepped matched controller worlds = 112 native task episodes**. Different controller variants are not 112 independently sampled reset states.
- Both interventions are native commanded-arm **target holds at steps 2 and 3** with unknown delivery acknowledgements. Gripper actions are not dropped. This is NOT actual packets lost in robot middleware.
- Readback is privileged controller-target memory, counted only when used for an action decision. Private per-step oracle access is a separate informational upper comparator, **not zero-cost**.
- The bounded controller has up to **4 live distinct hidden target histories** in every tested seed of the selective, no-read and post-fault fixed-read arms. At most 16 are supported by the code, but this study only physically exercised up to 4.
- One native command is authorized when every held-controller-target hypothesis meets 0.05m position infinity-norm and 0.05rad rotational-geodesic setpoint error limits. The SO(3) search is conservative; refusal does NOT prove no legal command exists.

## Complete actual task success and privileged information costs

| Original controller world | Pull successes /8 | Stack successes /8 | Total /16 | Decision target reads |
|---|---:|---:|---:|---:|
| Original source pretrained PPO, no fault (context) | 8 | 8 | 16 | 0 |
| Continuously privileged actual target oracle under double hold | 8 | 6 | 14 | Continuous, **not counted as 0** |
| Optimistic guess ACK succeeded, no privileged read | 1 | 1 | 2 | 0 |
| Strict exact-common-action or refuse | 0 | 0 | 0 | 0 |
| Conservative bounded common action, never read | 1 | 1 | 2 | 0 |
| **Conservative bounded action or ONE evidence-triggered target read** | **8** | **3** | **11** | **7 + 4 = 11** |
| **Conservative bounded action until ONE fixed t=4 trusted read** | **8** | **5** | **13** | **8 + 8 = 16** |

**Mixed conclusion, not a win claim:** Active selective uses **5 fewer** privileged decision reads than fixed-t=4 (11 vs 16, 31.25% fewer), but succeeds on **2 fewer tasks** (11 vs 13). In StackCube alone, the fixed read succeeds **5/8 vs 3/8**, so the current active strategy **does not dominate** on the query-cost versus task-success frontier; different query timing/trajectory decisions can hurt.

**Exact paired outcome table** (same 16 reset states): 10 both succeed, 1 selective-only success, **3 fixed-read-only success**, 2 both fail. No statistical significance or population superiority is claimed from this tiny two-task experiment.

Against the **zero-read** conservative controller, selective success is **11/16 vs 2/16**, but that comparator has **less privileged information**, so the gain cannot establish equal-budget method superiority.

### Every v3 source task-state — original outcomes, NO exclusions

| Task | Seed | Selective | Fixed t=4 | Never read | Selective reads | Fixed reads |
|---|---:|---:|---:|---:|---:|---:|
| Pull | 400001 | 1 | 1 | 1 | 0 | 1 |
| Pull | 400002 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400003 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400004 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400005 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400006 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400007 | 1 | 1 | 0 | 1 | 1 |
| Pull | 400008 | 1 | 1 | 0 | 1 | 1 |
| Stack | 410001 | 0 | 0 | 0 | 1 | 1 |
| Stack | 410002 | 0 | 1 | 0 | 0 | 1 |
| Stack | 410003 | 0 | 0 | 0 | 1 | 1 |
| Stack | 410004 | 1 | 0 | 0 | 1 | 1 |
| Stack | 410005 | 0 | 1 | 0 | 0 | 1 |
| Stack | 410006 | 1 | 1 | 1 | 0 | 1 |
| Stack | 410007 | 0 | 1 | 0 | 0 | 1 |
| Stack | 410008 | 1 | 1 | 0 | 1 | 1 |

## Actual post-dispatch certificate/actuator audit

Original artifacts have two distinct ledgers:
1. **48 certified command attempts physically masked by the deliberately injected hold faults.** These are labeled *NOT DISPATCHED*, and no claim that the physical target met the counterfactual command is made.
2. **384 original after-dispatch simulated-controller target checks** for truly emitted authorized commands, with the actual target memory read *after* the native simulator step as **audit-only** input. All 384 measured commanded-setpoint position and rotation errors fit within the recorded per-action certificate limits plus the declared `1e-4` numerical audit guard.

This is a **conditional simulated-controller setpoint check**, not certified robot trajectory tracking, contact/force safety, obstacle avoidance, or a proof that the user-supplied set of hypotheses is complete in an actual deployed system.

Every artifact file was independently checked against the original `SHA256SUMS` and immutable original SHA-256:
- Pull original SHA256 manifest: `2e0d0ef11bbb559a5ed25941213f51f2ea444403e56ce3dca0922bc7e4f77095`.
- Stack original SHA256 manifest: `62353524018a049c20ac596946a707c7f70490e22404498087db33fe0199709c`.

**No paper or external endorsement has accepted the new Multi-ACK result.** Previously approved and merged Braindecode contributions are separate, independent upstream engineering accomplishments.

## Re-run the evidence audit without GPU or simulator

Source: [audit_compound_ack16.py](review/audit_compound_ack16.py). Download/extract the two **actual** published GitHub Action artifacts into directories `original16/pull_cube` and `original16/stack_cube` respectively:

```bash
python -m research.frozen_policy_transfer.review.audit_compound_ack16 \
  --pull original16/pull_cube --stack original16/stack_cube \
  --output original_compound_ack16_audited.json --self-test
```

The auditor pins the exact CI commit, both source blobs and protocol blob, both complete original JSON hashes, all original episode seeds, all seven official success flags, every real-versus-masked native certificate record, all controller decision read counts and the negative paired comparison. The `--self-test` mode also changes the original result file and checksum manifest on purpose and requires both corruptions to be rejected. **A green author-operated replay of this audit is not independent reproduction of native physics**.

## Next hard scientific go/no-go
A flagship *original paper* would require an equal-information-budget, strong query-timing baseline (not only the fixed-t=4 policy), genuinely new fault patterns, extra robot/controller family or simulator, and at least one outside investigator running native PhysX independently. Especially important: explain **Stack seeds 410002/410005/410007**, where the fixed-t=4 method succeeds but the current active strategy fails, without tuning to the already-observed v3 test seeds. If the improvement fails on the next untouched cohort, publish the negative result and do not claim L8/L9 significance.
