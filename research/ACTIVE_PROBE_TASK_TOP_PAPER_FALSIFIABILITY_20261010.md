# Does active probing help, or does it corrupt the memory it is trying to identify?
**Study V7, 2026-10-10. Research-only. Preregistered task execution is in progress; DO NOT insert success numbers until audited.**

## Falsifiable research contribution
The controller implements a memoryful target command chart; the hidden state `h_t` is not merely the achieved public end-effector pose `x_t`. Following two truly injected native held/applied actions with ACKs unknown to the observer, a known-delivered native probe `u` is an intervention:
```
h_{t+1} = F_u(h_t)
y_{t+1} = G(h_{t+1}, x_t, controller_contact_dynamics)
```
The correct public belief update must therefore use the *post-action* target states, not `P(public y|pre-action h)` with the same old candidate labels. The runner physically steps native X and transports **all full-SE(3) controller target history hypotheses** before applying the original frozen public-response envelope. A fixed readback arm receives the exact same physical t4 X probe as both public-policy comparators. A ZERO arm receives the existing true neutral probe. No proof of repair safety or native active-probe optimum is implied.

### Structural null that must NOT be sold as innovation
For a controller that applies one common translation `u` to all candidate hidden target translations, `F_u(h_i)=h_i+u`. Before receiving any new observation:
```
F_u(h_i)-F_u(h_j)=h_i-h_j
```
and hence pairwise target-memory separations and discrete candidate entropy are unchanged by this bijective known intervention. The physically measured 15-mm hidden target shift alone says nothing about an information gain; any improvement must come from `G`, the noisy public response, and must be priced against the task perturbation. This elementary affine/isometric fact is established control theory and **is not a new top-paper theorem**. It need not hold under saturation, contact-dependent targets or nonbijective resets.

## Prospective native PhysX study
- Pre-registered first and source frozen before task outcomes, [full run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38014272258).
- **32 independent task reset clusters**, PullCube 4100001..4100016 and StackCube 4200001..4200016.
- Each reset has four ACTUALLY physically injected two-step held/applied ACK histories and two ACTUALLY physically stepped t4 native command variants: neutral all-zero vs normalized X=0.15.
- Hence **256 total task-mode/fault cells** = **128 matched ZERO-vs-X task pairs**, not 256 independent resets. Three individually task-evaluated matched controls A/B/C within each cell, and ten total physically stepped controller arms per cell. **2,560 actual PhysX controllers only if all 8 source-producing jobs finish**.
- A: original frozen complete-history position evidence gate or privileged target getter at t5.
- B: frozen posterior full-history gate using identical public xyz event budget / explicit readback when uncertain.
- C: strong actually-executed trusted target getter with same native t4 probe.
- X is a stress case for **a non-adapted response model trained on a different (neutral) probe**. The current study does not optimize active probes; a better conditional sensing planner (including ActionShift) remains an unexecuted comparator.
- Every arm uses exactly the same published third-party frozen PPO model checkpoint and seed; robot native goal target is AUDIT-ONLY when grading candidate correctness, except when the controller explicitly spends a counted privileged decision getter.
- Live success uses official native task success; diagnostic quantities include full-target authorization errors, refuses, completed actual native fault exposure, readbacks, sampled public xyz events and first successful step. Task contact force and electrical energy have NOT been independently measured or certified.

## Three possible scientifically valid outcomes
**X performs worse than ZERO**: direct evidence that information-seeking interventions impose nontrivial task cost under this controller, but NOT a universal no-probing theorem. Compare the actually executed readback C arm to distinguish action cost from wrong public authority.

**X ties ZERO**: physically confirms no measurable *sampled* task gain in this cohort; do NOT claim equivalence. If it changes readback counts, report task-stratified price ratio and exactly matched public sensor costs.

**X exceeds ZERO**: possible information value, but not superiority of a new algorithm; must compare with C and a truly model-matched strong ActionShift active-sensing policy on independently selected seeds.

For ALL outcomes, report failures, missing fault exposures, incomplete producer shards and partial data; never remove a failed seed or selectively resubmit modified methods as if it were the first-run dataset. First-run source SHA256 checks are separate from independent laboratory reruns.

## Publication comparison
- [TAMPURA (RSS 2024)](https://roboticsproceedings.org/rss20/p118.html): task-and-motion planning under action uncertainties, robot evidence.
- [Map Space Belief Prediction (RSS 2025)](https://roboticsproceedings.org/rss21/p039.html): learned calibrated manipulation belief with real-world transfer.
- [B-COD (CoRL 2025)](https://proceedings.mlr.press/v305/puthumanaillam25a.html): task-relevant just-enough sensing, real resource/energy costs.
- [ActionShift repository](https://github.com/Archerkattri/actionshift): strong relevant action contract and active belief adaptation baselines.
The current test is a **decisive mechanism falsifier**, not a main-track comparable top-system paper without a newly proposed optimized model-validity-aware policy, positive heldout task result under strong baselines, sensor/action costs, and external independent reproduction.

## Next formal gate after actual task audit
If physically complete, estimate test-only causal probe task effect clustered at original task/reset; no hyperparameter tuning or filtering. If omitted or failed, diagnose source and preserve original logs as a failure; fixes become visibly amended preregistration rather than a retroactive unmodified first experiment. The first main-track policy candidate is a validity-aware action-conditioned readback/probe selector that *provably falls back* when independent response-model shift evidence is insufficient. That model requires disjoint development/calibration/test resets and a genuinely new controller family before any claim of calibrated safety.
