# Main-track CoRL/RSS/ICRA reality check — action execution-history authority

**Internal hostile-review audit · 9 Oct 2026 · NOT a paper acceptance or acceptance prediction.** This is an evidence decision sheet for optimizing the next actual research work, not another presentation of accumulated self-fork PRs.

## Target-level assessment

The [CoRL 2026 regular-paper review criteria](https://www.corl.org/contributions/old_instruction-for-reviewers) stress **robot-learning relevance, original scientific/technological significance, and objectively established claims**. A manually designed controller with no substantive learning question may be considered out of scope. Simulation-only results can be accepted, but trained-policy relevance, realism and credible sim-to-real evidence must be convincing. The [author instructions](https://www.corl.org/contributions/instruction-for-authors) require an eight-page initial main manuscript, double-blind anonymity, and an explicit Limitations section. The 2026 submission cycle deadline has already passed; do not assume a later cycle's dates or reuse a public identity-revealing GitHub link in an anonymized manuscript.

## 10 potential hostile reviewer objections; current evidence; concrete decisive gate

| Main-reviewer objection | Objective present status | Nonnegotiable improvement before claiming strong main-track contribution |
|---|---|---|
| **1. Incremental method, not robot learning** | Exact binomial risk gate, SE(3) midpoint, conditional query and task-ID decision are known algorithmic concepts. Two frozen PPO models are used but gate itself has no new learned representation. | Introduce a **learned public-response model-validity or task-regret predictor** trained on truly separate robot rollouts, with task-conditioned calibration and an explicit **learned-vs-static** ablation. Make controller-state uncertainty relevant to policy decisions, not only offline scoring. |
| **2. Official strongest prior art missing** | ActionShift DualABI already actively probes unknown action ABI using task regret. A normalized-residual 0.95 heuristic is not equivalent to DualABI. | Port the actual DualABI method class with matched exposure/observation privileges and physical probe budget, plus exact belief, fixed, entropy and no-information ablations. Attribute distinct hidden mapping vs unknown execution state. |
| **3. Success conceals wrong hidden-state inference** | The actual first-run 640-world cohort includes wrong confident full target history at seed 1760020 although official task succeeded. 1/16 accepted wrong => 26.4% 95%-upper only under IID. | Primary endpoint **wrong complete target pose among authorized**, conditional selective calibration, minimum nontrivial coverage, and failures after actual physical actuation; not binary success alone. |
| **4. Data overlap inflates sample independence** | Cross-branch audit revealed 160 source cohort rows but only 128 unique task/reset identifiers; 32 were reused and 16 same-fault truth. | Immutable global registry of task reset IDs, task models and fault patterns; separate training, calibration, model selection, testing, and outside investigator samples. |
| **5. Small, task-correlated evidence** | 64 actual reset IDs, up to 10 same-seed comparator worlds (not 640 independent robots); many eight-cell task×truth groups of size 8. | State-level paired uncertainty, 4 actual ACK truth strata per task, much larger independently seeded test, report failed/fault-not-reached rows, and a **predeclared error+coverage statistical gate**. |
| **6. Query price is unfair** | Original A saved 16 private target reads vs fixed but spent 128 public XYZ sampling events and identical neutral probe time; no latency/energy measurement. | Same-public-data algorithm competition; release wallclock and actual private getter/probe latency, probe magnitude/time, public sensing/read permissions, and a prespecified price-weighted Pareto frontier. |
| **7. Simulation isn't actual packet loss** | CPU ManiSkill native target-held events simulate executed/held history truth, but not real middleware TCP/ROS ACK delay/drop or physical collision/force. | A true command-execution middleware impairment (dropped/delayed ACK with real motor-commit ground truth), measured action execution and at least one physical robot or convincing policy transfer across control families. |
| **8. Cross-embodiment headline misleading** | Panda+xArm6 source physics scripted correction exists; no confirmed learned target-policy recovery across both robots. SmolVLA LIBERO demos do not automatically prove this ManiSkill contract. | Two separately task-competent frozen **learned** policies on different controller/robot families, same unknown-ACK fault contract, real closed-loop task outcomes. |
| **9. Risk guarantee relies on unverified stochastic assumptions** | Clopper-Pearson plus finite-grid union is mathematically sound only under independent/exchangeable, stable per-task source state distribution and correct audited labels. | Explicit source-validity test, predeclared shift failure/abstention criteria, task+fault model mismatch stratification and a heldout confidence calibration trace. No hardware guarantee language. |
| **10. No external scientific adoption** | Upstream question to ActionShift remains open; author-owned PR merges and own CI are not independent replication, adoption or peer review. | Invite a third-party collaborator to choose fresh unseen states and run official released checkpoints from their independently controlled repo, post complete raw originals; pursue opt-in maintainer scope response rather than repeated nudges. |

## What can be claimed *today*

The reliable statement is a **real, source-audited simulator falsifier**: a frozen pretrained robot policy can finish a task while a public-motion observer confidently authorizes the wrong latent commanded-target memory. The original public method traded off 16 private controller-target reads against 128 public XYZ events at matched task success in one source-frozen cohort. Standard finite-sample statistical control is now implemented as an executable **future method admission gate**, with a hard coverage requirement and exact multiplicity correction. **None** of those facts alone demonstrate a novel deep learned robot algorithm, physical deployment safety, external investigator reproduction, or exceptional main-track acceptance probability.

## Recommended high-value main-track project scope — ONE flagship rather than multiple self-fork papers

Provisional manuscript title: **When Did My Command Execute? Learning When to Trust Hidden Controller State in Robot Policies**.

**Central hypothesis (not established):** A lightweight, externally calibrated learned response-validity and task-impact estimator can choose a reliable hidden target-history or an authoritative read, reducing actual private information cost **at nontrivial coverage and controlled wrong-history risk**, under matched physical sensing/control resources, compared with *the strongest fixed and active belief baselines*. Learned target-memory risk must be causally relevant to contact-rich frozen policy task success.

Core method research additions: (i) full target-history set and native chart representability, (ii) learned sensor-response validity or task-regret estimator from independently collected PhysX/possibly hardware interaction, (iii) exact source-truth-authorized reliability certificate with coverage requirement, (iv) budgeted active read vs probe arbitration with task utility, (v) end-to-end frozen policy rollout under ambiguous command commit, (vi) explicit abstention on shift and unknown task. **No new mathematical novelty** claimed for standard geometric or binomial tools.

### A disciplined eight-page main paper skeleton

| Page | Scientific content and expected grounded evidence |
|---:|---|
| 1 | Physical motivation: two same numeric policy actions but different internal target-memory semantics; original confident wrong-history success counterexample with real XYZ and target pose frames; concise verified claims. |
| 2 | Formal partially observed controller transition model with applied/held ACK, task intervention loss and trusted/private observation contract; distinguish hidden ABI grammar prior art. |
| 3 | Proposed learned reliability/observability feature model and certified authority-query-probe decision policy; native controller chart/float32 exact representation. |
| 4 | Calibration/training/test splitting, finite-grid conditional risk-and-coverage theorem with exact assumptions and sample budget, failure/abstain mode. |
| 5 | Benchmarks: actual ACK truths, source policies, task competence, distinct robot families, matched physical step and public sensing/privileged read budgets. |
| 6 | Main table: task success AND wrong latent history, read/observation/probe costs, paired intervals and matched-info official DualABI comparison. |
| 7 | True ablations: no learned validator, no target-history set, wrong native chart, no risk gate, all-read, no public sensor, calibration/contact shift, latency stress. |
| 8 | Physical episode qualitative failure/success frames, external investigator reproduction, explicit limitations and source data integrity. |

**Never insert a simulated top-conference table entry with no real raw outcomes.** The correct next work is one genuinely novel, task-competent, independently auditable learning contribution and its matched-budget evaluation—not cosmetic manuscript multiplication.
