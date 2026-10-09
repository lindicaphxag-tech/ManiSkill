# Cost-sensitive interpretation of original strong060 prospective PhysX — reviewer evidence note
Date 2026-10-10. Source branch research/strong060-resource-pareto-audit-20261010; parent FIRST ORIGINAL executed PhysX program and source archives unchanged.

## Source validity
The original 32-reset-cluster, 128 matched physical fault-condition, 1,280-controller-world archive was already frozen and independently source-recomputed in `research/frozen_policy_transfer/evidence/strong060_prospective_original128_first_3110001_3120016/`.
This follow-up is an **offline inference from existing source**, not new simulator execution. Novel audit:
- script `research/review_strong060_original_cost_frontier.py`;
- successful GitHub Actions job https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37973273352;
- original recomputation SHA256(JSON) `57485114f58101a24c20d2f1155ac96482a7754693878e940a2197215cf142e8`;
- independently archived audit ZIP artifact 11636528247.

## Matched FULL original outcomes

| Source PPO control | True PhysX official task successes | Privileged target reads | Public XYZ samples | Wrong confident full-target authorizations |
|---|---:|---:|---:|---:|
| A: public complete-history membership or authoritative read | 109/128 | 94 | 256 | 0 |
| B: same-public 0.60 residual posterior or authoritative read | 109/128 | 98 | 256 | 0 |
| C: mandatory target read | 110/128 | 128 | 0 | n/a |

**Exactly matched per-cell A/B successes on these 128 cells** (0 A-only, 0 B-only), which means A weakly reduces read cost *on this fixed tested cohort and these endpoints*. It is not proof of stochastic policy superiority in unobserved robot scenarios. A/C discordance: A-only **0**, C-only **1**; bootstrap paired 32 source reset clusters, Δsuccess/physical truth = −0.0078125, descriptive 95% interval [−0.0234375,0]. This is **not evidence of noninferiority**.

Each of 32 reset clusters is exposed to four actual applied/held truth conditions, so standard errors must respect this clustering; 128 conditions and 1,280 worlds are NOT independent n. Zero wrong approvals from 34 authorizations is not a safety guarantee or a validated low error-rate bound when multiple approvals share original state clusters.

## Pareto tradeoff and new exact reviewer decision

Let λr be the *task-success-equivalent opportunity cost of one privileged controller target read* and λs the cost of one extra public XYZ sample (both nonnegative). On the 128 tested physical conditions, the sum of utility differences is exactly

\[
U(A)-U(C)=\underbrace{109-110}_{-1}
-\lambda_r(94-128)-\lambda_s(256-0)
=-1+34\lambda_r-256\lambda_s .
\]

The complete-history selective read wins **only when** \(\lambda_r>(1+256\lambda_s)/34\). E.g. if public XYZ sampling were free (unverified), the break-even private read cost is 0.0294118 *task successes per read*; at public cost 0.001, it is 0.03694. Different, measured sensor/latency/energy prices can reverse the method ranking. No physical price calibration exists yet, so one cannot claim A universally more efficient than C.

At the exact archive-level endpoints A has identical per-condition task outcomes and identical public sample count as B while making four fewer private reads; **A aggregates better on these three observed axes**. That does not imply superior inference calibration beyond this small cohort or fairness versus official ActionShift DualABI (not executed).

## Implications for BeliefBridge VLA manuscript
1. Preserve the original matched source evidence, task/read/sensor Pareto and negative comparison. Treat it as **PPO controller-history mechanism provenance**, not actual SmolVLA task recovery.
2. Do not reuse exact 311/312 reset IDs as a fresh VLA independent test. They are exposed.
3. Physically measured command-commit uncertainty matters only for a verified **stateful target-relative VLA/controller ABI**; neither SmolVLA generic action shape nor true LIBERO checkpoint forward demonstrates that.
4. For RA-L/T-RL/T-RO flagship, choose truly task-competent frozen VLA plus matched active baseline, measured private read and public acquisition cost, actual task-level recovery, distinct controller family, and outside-authored replication.
5. Evidence is author-operated CPU PhysX, not actual ROS missing acknowledgements, real robot contact safety, or peer-reviewed acceptance.

**Scientific disposition:** reliable historical source re-analysis + falsifier, NOT submission-ready BeliefBridge-VLA.
