# Intervention-Valid Conditional Energy for Controller-State Recovery
### Algorithmic candidate and journal-fit research gate — 2026-10-10

> **Research-only Draft. No new heldout positive native task success is yet observed.**
> Earlier actual 2,560 ManiSkill CPU PhysX trajectories are the DEVELOPMENT evidence for this new algorithm, not independent evidence for its gain.

## A. Hypothesis, method and falsifiability

Native robots often keep an internal **commanded target memory** distinct from the publicly achieved end-effector pose. Missing delivery acknowledgements (ACKs) yield multiple complete-position-and-orientation target histories. Our prior source-pinned 2,560-world task study shows that a deliberately known-delivered X probe alters the internal target by 15 mm and degrades StackCube success even with trusted readback. With the ZERO response model reused under X, the geometric authority gate also confidently chooses **four wrong SE(3) targets** with **26.7–91.7 mm** coordinate errors.

**Do not claim these are hardware collision events, nor that all active sensing must be harmful.** The zero and X response likelihoods differ; the old model was intentionally misspecified.

The proposed mechanism is a *learning-and-decision pipeline*, not a renamed textbook POMDP:

1. **Action-conditioned forward latent transition**: Each known native probe (a) transports candidate target states by an action-specific controller memory transform (h'_i=F_a(h_i)). Four physically injected ACK histories remain explicit and no audit-only native target getter informs public online decisions.
2. **Permutation-equivariant, nonlinear public-response energy:** Candidate features use **public** normalized geometric residual (r_i/\varepsilon), candidate-to-best and center differences, residual quadratic transforms, public achieved-XYZ motion, rotation spread, task and native-action identity. Shared multilayer embeddings and a candidate-average context yield four logits (s_\theta(h'_i,a,y)). Permuting candidate indices must identically permute logits; no positional candidate index leaks labels. See `research/conditional_residual_energy.py`.
3. **Distributionally robust group risk:** Actual retrospective TRAIN resets are partitioned into four task×probe strata; optimize
   \\[\mathcal L_{\mathrm{DRO}}(\theta)=\tau\log\sum_{g\in\mathcal G}\exp\{\mathcal L_g(\theta)/\tau\},\quad \tau=0.2.\\]
   This is **standard log-sum-exp distributional reweighting**, not a new theorem.
4. **Causal contrast across physically paired interventions:** Known delivered X changes native target (F_X(h)) but not which past ACK hypothesis is correct. Fit
   \\[\mathcal L_{\mathrm{pair}}=0.09\;\mathbb E_{(y^0,y^X)}\left[\tfrac12\{D_{KL}(q^0\|q^X)+D_{KL}(q^X\|q^0)\}\right].\\]
   **Critical possible failure:** physically distinct public responses legitimately change posterior confidence, so this *regularizer may over-constrain* inference. Its ablation is mandatory; its weight is fixed BEFORE new test.
5. **Cluster-aware conformal hypothesis set and query fallback:** For each independent calibration reset and each action, compute worst nonconformity (S_j=\max_{t\in \{0,1,2,3\}}(1-q_\theta(h^*_{j,t}\mid y_{j,t},a))\). For (n) iid/exchangeable task reset groups, take the \\(\lceil(n+1)(1-\alpha)\rceil\\)-th order score (∞ if this rank exceeds (n)); form
   \\[\Gamma_\alpha(y,a)=\{i:1-q_\theta(i\mid y,a)\le S_{(k)}\}.\\]
   **Authorize only if this set is a singleton; otherwise a paid privileged getter.** This offers a standard **marginal joint-ACK true-set containment** under exchangeable resets and frozen fitting. It is **NOT** a bound on error *conditional on authorizing*, collision safety, model shift, or hardware reliability. See `research/cluster_conformal_authority.py`.

The existing 8 independent calibration resets per task are INSUFFICIENT for a finite 90% conformal threshold (ceil((8+1)·0.9)=9, no 9th observed reset), so the strict conformal gate necessarily queries. At alpha=0.05, **at least 19 independent calibration resets per task/probe** are required even to obtain a finite order statistic; nontrivial singleton-coverage typically requires more. We explicitly refuse to treat 8 resets × 4 ACK truths × 2 probes as 64 iid calibration samples.

### Formal observation on interventions
For a deterministic one-to-one memory transform (F_a) over candidate states, (H(F_a(H))=H(H)). Thus a known target translation alone cannot reduce discrete latent uncertainty. The information gain can only come from **the action-conditioned public observation** (Y\mid F_a(H),a), and must be traded against task perturbation. This is a standard entropy invariance fact, not an independently novel theorem. The observed 15-mm intervention is therefore not itself an information-gain claim.

## B. What has truly been executed vs still pending

**REAL, source-shard SHA audited** (old 2026-10-10 pre-intervention learning corpus): 32 independent resets, 2 tasks × 16 independent reset clusters, four held/applied ACK combinations and two actual X/zero physical probes, 256 task-fault/probe cells, 10 actual controller branches each = **2,560 genuine PhysX CPU rollouts**. Strict archive hash review [38015149933](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38015149933) passed 72/72 JSON digest checks. This is author-operated SIMULATION only.

**SOURCE DATA EXPORTED NOW:** `research/first_source_256_public_residual_training_records.json` includes exact 256 public residual/XYZ/probe context and one audit-only true hypothesis label, with source run and provenance. **Train resets** task-seeded 1–8; **calibration resets** 9–16; physical truth/probe cells remain repeated observations. This split was implemented after inspecting previous source results and is **development selection**, not untouched confirmation. True target labels may be used offline for fitting and calibration only, never the online target predictor.

**CODE COMMITTED NOW:** differentiable nonlinear equivariant model, deterministic group-DRO and paired intervention trainer, 4 predeclared ablations, source/seed integrity checks, 8 online-inference tests; a separate conformal-hypothesis-set reference with 9 adversarial tests. Do not claim trained-checkpoint performance until the actual ML workflow passes.

**NOT YET EXECUTED:** new, never-seen frozen PPO task rollouts with `ICERE` in the loop, calibration across at least 19 new independent resets per task-probe, task-level surpassing original zero method, or any outside-lab or hardware validation.

## C. Negative real task evidence must remain in the paper

| TRUE task, 16 independent resets / 64 correlated ACK fault truths | A geometry ZERO | A geometry X | B posterior ZERO | B posterior X | C privileged ZERO | C privileged X |
|---|---:|---:|---:|---:|---:|---:|
| PullCube successes | 62/64 | 61/64 | 62/64 | 62/64 | 62/64 | 62/64 |
| StackCube successes | 47/64 | 38/64 | 47/64 | 40/64 | 47/64 | 40/64 |
| **Pooled** | **109/128** | **99/128** | **109/128** | **102/128** | **109/128** | **102/128** |

ZERO geometry A uses 90 privileged getters over 128 fault contexts, compared with matched-public B 125 getters while both have 109/128 task success. X mode A wrongly self-authorizes four full hidden SE(3) targets; ZERO has zero *observed* wrong self-authorizations, but no population-level <10% risk guarantee from this cohort. New models must beat **ZERO and same-information B**, not cherry-pick the weak active X baseline.

## D. Exact journal fit and comparison with previous accepted work

**Primary if heldout task gain + cross-context robustness succeeds: _Robotics and Autonomous Systems_ (Elsevier, ISSN 0921-8890).** Official scope explicitly covers symbolic/sensory robot control and learning and theoretical/computational/experimental autonomous systems. The journal is the best topic match for hidden controller state recovery, intentional probe effects, active sensor action cost and full-task manipulation. Importantly, RAS 2026 articles include **“A context-adaptive policy framework for robust and reactive robotic manipulation via uncertainty-aware imitation learning”** and **SPARS (structure-informed progress-aware fabric learning)**: the latter reports **69% vs 41%** fold success and transfer to physical UR5. Our current study does not match these positive effects or physical transfer.

**Conditional high-innovation alternate: _Engineering Applications of Artificial Intelligence_ (EAAI).** Its publisher scope explicitly lists intelligent fault detection, automation and robotics, but also specifically calls for genuine **real-world engineering AI applications and public datasets**. Public ManiSkill only and two toy tasks may be rejected as insufficient engineering validation. EAAI abstract must explicitly distinguish AI contribution vs engineering application; single-column submission and no undefined title/abstract acronym.

**Backup topic-compatible: _Journal of Intelligent & Robotic Systems_**, with published works on simulation-based robotics systems and control, if the final algorithm is sound but the gains are smaller. This is not guaranteed easy.

**Do not submit to _Neurocomputing_ until the contribution truly centers on transferable new neural learning theory/architecture**, not just adding a small DeepSets network to a robotics integration story. Although robotics appears in its broad applications scope, the publisher emphasizes neural computation contributions. **Do not promise any JCR/CAS/CCF 2026 tier or acceptance probability without current official classification verification.**

**A top-tier robotics journal is especially challenging without hardware.** The no-hardware plan can compensate partially with 4+ diverse manipulation tasks, at least two different native controller families, 3+ frozen policy architectures, two distinct physics assumptions/controllers, full unit-time/sensor/actuation accounting and third-party cloud reruns; it cannot create a real physical robot result.

## E. Hard stop/go publication gates

- **G0 source correctness:** no privileged online label leakage; exact train/cal/test disjoint by *reset cluster*; byte-hashed original data; all protocol/code amendments disclosed.
- **G1 learnability:** pretrained/fixed trained model beats min-residual and frozen posterior on *independent calibration*, including subgroup worst-case wrong-ranking, and robust regularization contributes beyond ablations; if not, stop and redesign instead of tuning test.
- **G2 independent conformal calibration:** allocate >=19 (prefer 32–64) independent unseen calibration resets *per task/probe* to support a finite 95% per-context joint-ACK rank threshold; evaluate singleton authorization coverage without misreporting conditional error.
- **G3 fresh frozen policy tasks:** only after model and thresholds are committed, run **new independent** PullCube/StackCube reset groups and compare ICERE, ZERO geometry, X geometry, matched-public Bayesian B, paid privileged C, plus a published proper active method if its source can run. Co-primary: official full task success and wrong confidently authorized full SE(3) controller state; secondary: getters, public samples, extra native actions, task contact and wall time if measured. Cluster by reset, preserve all negative groups.
- **G4 transfer:** new controller/robot, policy, fault frequency/timing and response-shift tests, with external independent source rerun. If these cannot be completed, target a narrower simulation methodology claim or redirect venue.

**Timeline:** an October 2026 model-development gate and November–December **submission preparation** are conceivable only if the new tests actually finish. Acceptance in November/December cannot be promised; editorial assessment and peer review are outside our control.

## Paper working title

*When the Probe Changes the Controller: Intervention-Conditioned Belief Recovery with Reset-Calibrated Abstention for Robotic Manipulation*

Do not present this as a completed experimentally superior method before G1–G3; currently the novel empirical result is a **falsification** of a zero-probe response model under active X.
