# IER-Funnel: Intervention-Effect Reachability for Hidden Native Controller Memory
**Research challenge specification, 2026-10-10. Method hypothesis, not a demonstrated superior method or paper acceptance.**

## Research question after 2026 Aug/Sept/Oct prior work
FACT (arXiv:2608.10232, 10 Aug) already learns failure-aware action-conditioned future/predictive progress. CoRe (2608.14822, 14 Aug) already performs training-free imagined VLA trajectory realignment. FARE/Causal-History Recovery (2609.18016, 16 Sep) already tests full/prefix/reset WAM causal histories. Magic-W0 (2609.39870, 30 Sep; v2 3 Oct) already jointly represents 3D state, transitions and future semantics. FAVOR (2610.06280, Oct 5) already verifies future state anchors. LIBERO-RECOVER (2609.05178, Sep) already covers 1000+ graded recovery scenarios.

**A simple fault detector + predictor + posterior + threshold + POMDP is not novel against these works.** Our potentially distinct scientific object is *native controller commanded-target memory, its typed command semantics, irreversible or noninjective authority changes, and whether a particular recovery can actually make a failing frozen robot task succeed*.

## Current evidence (do not alter)
Prior author-operated native ManiSkill: 2,560 physically stepped CPU PhysX controller worlds, 32 independent reset clusters repeated under four ACK truths each. Under the original complete-history A, ZERO 109/128 task successes, X 99/128; under B/C, ZERO 109/128 vs X 102/128. Four wrong confident complete native SE3 authorizations appeared under X with 26.734–91.674 mm position errors. X changes hidden native target by ~15 mm; that is *not* information gain. Original all-source archive audited by independent SHA-only CI 38015149933; not independent outside-operator replication.

The old ZERO/X action *hindsight oracle* is 112/128 at best on the same A cells (only three X-only successes); 16/128 fail under BOTH ZERO and X. This is an observed two-action portfolio ceiling only, not a generalization limit. Thus better ZERO/X routing alone cannot produce a large task success breakthrough on that observed cohort.

## Semantic theorem: shared relative-action non-contraction

For the actual checked `PDEEPoseController`:
- root translation: `p_i^+ = p_i + d(a)`
- root-left rotation: `R_i^+ = R(a) R_i`.
For every shared command `a`, pairwise position difference and SO3 geodesic distance are invariant:
`p_i^+ - p_j^+ = p_i-p_j`; `d(R_i^+,R_j^+) = d(R_i,R_j)`.
This extends to finite open-loop common action sequences as long as every candidate receives the same applied action and the same verified controller ABI. It does NOT prohibit informative observations, history-contingent control, stochastic contact effects, privileged readback, or a truly noninjective native target rewrite. This is standard group-action geometry: a *necessary impossibility lemma*, not by itself new ML theory.

Let `g` be a desired root-frame setpoint and `d_j in [l_j,u_j]` the native delta box. A tight minimax translational certificate is
`L_p = max_j max(|min_i p_ij + d_j^* - g_j|, |max_i p_ij + d_j^* - g_j|)`,
where `d_j^* = clip(g_j - (min_i p_ij + max_i p_ij)/2, l_j,u_j)`.
For SO3, `L_R >= 0.5 max_{ij} angle(R_i^-1 R_j)`, from the triangle inequality. If either exceeds the declared task budget, no identical relative native command can achieve the target for every candidate. `research/native_memory_funnel_certificate.py` implements only this negative feasibility screen; if it passes, actual motion remains UNPROVEN and requires the existing geometry/IK/controller verification.

## Causal recovery action types and their authority
1. `ZERO / PASSIVE`: time passes; may permit servo settling, but not costless and does not erase native memory.
2. `COMMON_RELATIVE`: public command with target-state isometry, no hidden-memory collapse; physically changes geometry/contact and may improve or harm task.
3. `PROBE`: may give informative public evidence but also changes physical and hidden states; condition on actual action and context, not ZERO-trained likelihood.
4. `READ`: a trusted complete controller-target getter, counted as one privileged READ, only if target getter is available.
5. `REANCHOR`: simulator-internal `arm.set_state(target_pose=actual achieved EE pose)` writes native target memory from publicly achieved geometry, counted as one privileged WRITE. A genuine noninjective memory reset. It is **NOT a normal robot actuation interface nor proof of hardware deployability**. Use it only as an upper/diagnostic privileged-action comparator until an actual hardware/ABI equivalent is verified.
6. `ROBUST TASK RECOVERY`: real regrasp, reposition, reroute or retrial actions must be added later; only they can address the 16/128 baseline common failures that would otherwise remain unresolved.

## Intended algorithm (not yet implemented as integrated on-task learned planner)

Belief `b_t(h,x,c)` is over native commanded-target memory `h`, achieved physical state `x` and contact regime `c`. A learned action/ABI-conditioned response model must predict the **joint** `p_theta(h',x',o'|h,x,c,a)` from genuinely stepped training resets, with uncertainty support checked per action/controller chart. ICERE presently learns a candidate ranking, NOT this full model.

For each action `a`, first apply deterministic structural feasibility tests, then optimize model-family-worst-case expected task utility over future recovery plans:
```
utility = completed_task_without_false_full_SE3_authority
          - lambda_read * paid_internal_getters
          - lambda_write * paid_internal_setters
          - lambda_step * extra_native_actions
          - lambda_damage * measured_contacts_and_failures
```
Only select a learned recovery over a strong ZERO/query baseline when a *future-disjoint, reset-cluster-based* lower confidence bound on paired improvement is positive and the authorization risk and sensor/action budgets meet predeclared criteria. Otherwise abstain. These planning and calibration primitives are mostly standard; novelty must be demonstrated by native-memory reachability + true closed-loop recovery over harder tasks, across policies, controllers and observation shifts.

## Current actual implementation
- `research/conditional_residual_energy.py` in ICERE: candidate-permutation-equivariant action-conditioned residual energy, supervised training on original source 16 independent development reset clusters and a disjoint 16-reset calibration split; 4 model variants and CI. The symmetric pairwise KL regularizer can incorrectly suppress genuine posterior differences under interventions; its impact MUST be determined by out-of-sample ablation.
- `research/cira_intervention_gate.py`: conservative matched-task-utility lower confidence bound and original-reset wrong-authority upper bound, with fallback to ZERO/QUERY. Test-based reference, not fitted PhysX recovery planner.
- `research/native_memory_funnel_certificate.py`: exact per-axis translation minimax and rotation impossibility lower bound; checks typed ABI and privileged-write cost.
- `research/frozen_ppo_native_reanchor_dev_physx.py`, `research/run_native_reanchor_dev_physx.py`: a **development, physically executable** native target-write comparator. Same frozen PPO, same ACK truth and pre-t4 public pose/physical actions, 8 fresh original reset clusters total (4 per task), 32 paired ACK conditions, planned 672 actual CPU PhysX control worlds. This is not evidence until full original source/shard audit completes. In a distinct formal confirmatory study, these seeds must NOT be reused.

## Formal empirical go / no-go gates

**Gate A (diagnostic setter pilot)**: The matched original simulator-internal reanchor action must be physically executed and audited; evaluate if it causes positive **rescue of ZERO failure**, not merely reduces hidden-target error. If it does not help, stop treating reanchor as the core avenue.

**Gate B (deployable action contract)**: Build and test a legitimate public/robot controller capability for recovery with identical interface and costs for all methods. A bare `set_state` simulation write cannot be the headline contribution. A strong always-trusted getter must be a comparator, not an inconvenient baseline to omit.

**Gate C (learned response/decision)**: Fit action-conditioned joint effects on disjoint development resets; independently calibrate and freeze action-specific OOD/model-validity gates. Current 8-reset per-stratum ICERE calibration cannot support a nontrivial 90% cluster conformal threshold; avoid inflating 8x4 ACK truths as 32 independent resets.

**Gate D (prospective validation)**: New disjoint reset clusters, real full task success, wrong confident full SE3 target authorization, privileged reads/writes, timing, public samples, measured contact/collision/energy if available. Compare against ZERO, trusted getter, original A/B, identical-budget strong ActionShift and a correctly action-conditioned constrained POMDP.

**Gate E (generalization and outlet)**: Add harder non-ceiling manipulation tasks, two native controller/robot families, multiple frozen policies, adverse sensor/contact shifts and an outside-operator audit. Without fresh positive task-level recovery, do not submit an apparent successful-method paper. RAS is a plausible target if strong task evidence exists; RSS/CoRL/RA-L are stretch options conditional on substantially more results. Publication is never guaranteed.

## Scientifically meaningful ablations
- Model-free semantics vs learned action-conditioned public likelihood.
- Without typed controller-memory tracking.
- Without reachability infeasibility screen.
- Without sensing-induced physical cost.
- Without privileged read/write accounting.
- Without model family validity / abstention.
- Without contact/task-progress-aware recovery.
- With vs without symmetric cross-action posterior KL (may harm).
- Reset history only vs reanchor controller target only vs both.
- Exact same-information ActionShift / constrained-belief planner.

Do NOT rewrite currently negative PhysX results as outcomes of the new model. All 2026 citations above are preprints unless externally verified peer-reviewed.
