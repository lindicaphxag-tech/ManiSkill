# Independent investigator replication request — source-frozen PickCube target-memory recovery

**Prepared 2026-10-14. Evidence request only; NOT an external lab endorsement or peer-reviewed acceptance.**

## Public, separately auditable experiment

- Original **before-outcome frozen PickCube task**: `research/PICKCUBE_UNSEEN_TASK_FROZEN_BEFORE_RESULTS_20261014.json` committed at `2ecc0dfa2c6a78efda0ba702f2c27c024956dea1`.
- Original method: `research/reachable_native_so3_robust.py` (frozen after negative Pull/Stack development evidence).
- Native PhysX actual 5-world runner: `research/frozen_ppo_reachable_so3_external_pickcube.py` on **32 new reset seeds**, independent of previous Pull/Stack task seeds.
- Registered policy checkpoint: `kattri15/actionshift-baselines`, `ppo/pick_cube_final_ckpt.pt`, SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`, revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`.
- Expected 32 distinct reset clusters, with 5 physically stepped controller runs each. Artificial fault is a **zero arm target command** at t=2,3, not actual network ACK loss.
- Competing privileges: unrestricted live private-target oracle (not free), correct scheduled target read, original source-history finite-set read-on-refusal, new SO3 reachable read-on-refusal, and no-fault PPO competence. The first four controller arms each execute genuine separate simulations, not retrospective counterfactual splicing.
- Primary: official task success, number of counted *decision-time* private reads, complete fault exposure and matched within-state discordances. Commanded-target after-step getters for audits must not enter decisions.
- Scientific claim must FAIL unless new method maintains corrected fixed-read success and saves ≥4 target reads, while also maintaining original selective-read success and saving ≥2 reads. Do not cherry-pick a different cost tradeoff after outcome.

## Specific third-party review requests

1. **Verify the frozen protocol commit predates first actual PickCube task results.** Detect overlap of task/reset IDs with earlier research; this is a new TASK but still Panda robot and an available task-trained PPO, not a novel embodiment.
2. Independently install official ManiSkill and retrieve the exact external frozen checkpoint SHA; select **new reset IDs yourself**, prior to running the method, rather than reusing our test seeds. Publish all states including early termination, no eligible fault, invalid action charts and failures.
3. Repeat the corrected fixed-read comparator with actual target-memory singleton reset; contrast the unrestricted oracle separately, not as a zero-read method.
4. Audit that the proposed action is one admissible 6D command shared across *all* controller-memory hypotheses, with no hidden true-ACK label, privileged `target_pose` read, or test outcome informing the candidate search.
5. Compare against task-aware value/recovery baselines, including learning-based action residual methods and task-compatible information-gathering methods, under identical observation and paid-read budgets.
6. Report matched seed-level outcomes, empirical confidence intervals, private readback cost and physical effort/latency; **do not count multiple interventions on one reset as independent subjects**.
7. Independently execute both positive cases and failure counterexamples; contact/collision/IK validity is not established by the current commanded-target certificate.

## External recognition status

- 2026-10-14: **NO outside scientist replication, manuscript review, editorial acceptance or upstream ManiSkill maintainer merge established**.
- Braindecode EEGCLIP DDP PR #1320 is genuinely externally upstream merged, and counts as engineering recognition ONLY.
- A third-party fork/issue comment/independent written verification must be recorded with concrete URL, timestamp, and scope before upgrading the external-evidence claim.

## Exact replication command

Use GitHub Actions on this source branch as a reference for OS requirements and checkpoint provisioning. The owner GitHub Action is **not** the independent outside-lab test. If a researcher runs an independent fork, require fresh investigator-chosen seeds, a frozen fork commit, full logs, and model SHA. Do not edit the initial protocol after seeing outcomes.
