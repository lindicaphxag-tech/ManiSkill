# When Robot Actions Leave No Trace
## Structural limits of identifying hidden controller state from matched public motion

**Main-track research working paper, v0.8 · 9 October 2026**
**Evidence level:** author-operated genuine ManiSkill CPU PhysX with original frozen third-party PPOs, pre-outcome frozen protocol and source-hash verification. Not peer reviewed, not independently replayed by another laboratory and not tested on real robotic hardware. The observational impossibility statement has a narrowly specified information set, not universal sensory impossibility.

### Abstract

A frozen robot policy may command a target-accumulating controller with a documented Cartesian action interface while failing to observe whether two previous commands were executed. Four target-memory hypotheses can then be consistent with its local action history, and the actual hidden commanded-target pose may differ even when observable robot motion appears normal. We ask when public end-effector motion identifies that hidden memory, when only a privileged target-state read can distinguish it, and whether avoiding reads affects task outcomes. Two separate source-frozen genuine ManiSkill PhysX studies provide complementary evidence. In the first, four physically realized unknown-ACK execution truths applied to the same source reset produced three exact pairs of identical pre/post public XYZ observations with different actual full SE(3) hidden target memories. These are constructive limits on deterministic inference from the stated observation alone, not a guarantee about all sensors or possible actions. In a second prospective study, 32 distinct task/reset clusters were each replayed under four actual ACK patterns and ten physically stepped controller treatments, yielding 128 condition cells and 1,280 real simulator-controller trajectories. Full-history public evidence, the same-input normalized-residual 0.95 heuristic and fixed authoritative reading achieved exactly the same 104/128 official successes on the identical conditions. They consumed 102, 122 and 127 privileged target reads, respectively. The public method accepted 26 histories without observed errors, but these admissions arose from only 20 independent reset clusters; its one-sided 95% confidence upper bound on at least one error per authorizing reset is approximately 13.9% under strong cluster-level IID assumptions. Thus the evidence supports a conditional information-cost reduction, not task-success improvement, latent-state safety or a verified 10% risk bound. The findings motivate an action-conditioned active probe/read strategy whose response-model reliability must be established on genuinely separate physical data.

### 1. Scientific question: latent *execution*, not hidden ABI syntax

Let the internal commanded target be \(M_t\in SE(3)\), the received native policy action \(u_t\), and hidden execution truth \(z_t\in\{0,1\}\). Even with a completely known target update \(F\), the controller may satisfy

\[M_{t+1}=\begin{cases}F(M_t,u_t),&z_t=1\\M_t,&z_t=0.\end{cases}\]

A policy without trusted execution ACK knows \(u_t\) but not \(z_t\). For two unknown independent execution events at steps 2 and 3, its full target-history set is \(\mathcal H_t=\{M_t^{00},M_t^{01},M_t^{10},M_t^{11}\}\), subject to any exact equivalences. Importantly, an action compliant with the *syntax* of a controller API need not have the right physical semantics if another commanded target was previously accumulated.

This differs from online **action ABI identification** (where the controller grammar itself is unknown). It does not establish priority over task-regret active adaptation; ActionShift DualABI, UP-OSI and RMA are relevant prior work. Our actual robot evidence here covers one Panda controller family and two separately pretrained frozen PPO manipulation tasks, not a policy learned within this manuscript.

### 2. Constructive physical observation-equivalence witness

**Source-frozen separate PhysX study**: 32 task/reset clusters, four physically stepped execution patterns per reset; original first-run [source-audited observational-collision workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37939434976). The auditor reads 34 immutable first-run files and verifies original source/reset truth and actual physically dispatched known-delivered zero native six-dimensional neutral probe at step 4. Within its explicitly limited sensor contract, an observation is

\[o=(\mathrm{task},\mathrm{initial\ public\ state},x_{\mathrm{EE},\mathrm{before}}^{XYZ},x_{\mathrm{EE},\mathrm{after}}^{XYZ},u_{\mathrm{probe}}).\]

For original PullCube reset seeds **2110003, 2110004 and 2110012**, different physical ACK truths yield **identical six numeric XYZ observation values and the same initial-public-state hash**, yet original audit-only controller target histories have distinct full SE(3) identities. The source enforces separation in BOTH commanded target position and orientation (at least several centimeters and a non-negligible angle) and both physical faults and common neutral probe actually occur.

**Conditional identifiability lemma.** For two factual physical worlds \(W_0,W_1\) with equal observable \(o\) but distinct true hidden memories \(M_0\ne M_1\), every deterministic forced classifier \(\hat M=g(o)\) produces the same output in both worlds and is wrong on at least one. If the pair occurs with exactly equal prior mass and errors have equal cost, any forced classifier has average correctness at most 1/2. A method can abstain, query a trusted target, or perform a *different* potentially separating probe. This is the familiar observation-equivalence argument instantiated by actual controller data, **not a newly proven general impossibility theorem**. The equality is limited to the specified task/initial public state and achieved XYZ under that particular neutral probe; vision, force, a nonzero discriminating probe or other information may resolve it.

[Source auditor and three immutable physical witnesses](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/observability-collision-audit-20261009/research/audit_counterfactual_execution_observability.py) · [Existing conditional probe-or-read interface and negative model-trust tests](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/observability-collision-audit-20261009/research/conditional_probe_or_read.py). The latter is a safe-abstaining software interface, **not** a real-trained response predictor or tested task-level recovery algorithm.

### 3. Physically isolated four-truth factorial experiment

A second **independently frozen** protocol, from original code Git commit `a85a256378c817c6ca65f3ea458928540e519924`, tested previously unused PullCube task/reset IDs `3010001–3010016` and StackCube `3020001–3020016`. Each of the **32 unique task/reset IDs** was physically stepped at all four joint ACK execution truths—held/held, applied/held, held/applied and applied/applied—rather than allocating distinct seeds to the four faults. In each true task/reset/fault cell the script executed ten actual native controller worlds (1,280 factual native trajectories in total).

The three principal comparison arms A/B/C shared the same task initial public hash, verified actually dispatched source actions at both faults, achieved and native commanded-target full SE(3) trajectories before the decision, and the same physically delivered neutral step-4 probe. At step 5:

**A — complete-history set-membership / read:** compare two actually observed public XYZ samples against the original fixed training-derived residual envelope; when exactly one entire full-target-history candidate is admissible and alternatives clear a fixed margin, authorize it, else pay for the actual privileged target getter.

**B — identical-public residual-weight heuristic / read:** see precisely the same public XYZ and physical probe; normalize the frozen residual score across hypotheses and authorize only when precommitted 0.95 threshold is met. This score is NOT a calibrated Bayesian posterior and NOT ActionShift's actual DualABI.

**C — fixed true target read:** on the same actual physical predecision prefix, request authoritative hidden target. C does not receive the two decision-visible public XYZ measurements, so any cross-sensor cost comparison must price those events explicitly.

All original 16 eight-state source shards and four same-reset initial-hash ledgers passed the [first-run full 128 source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37944800521). The permanent byte-level physical archives, full terminal logs, environment and SHA-256s are [stored on this research branch](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/isolated-query-factorial-128-20261009/research/frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016).

### 4. What the prospective 128-cell result actually shows

| Actually stepped native physical treatment | Task successes | Actual privileged target reads | Decision-visible public XYZ events | Accepted full target histories | Observed wrong accepted histories |
|---|---:|---:|---:|---:|---:|
| **A. Complete-history evidence or true target read** | **104/128** | **102** | **256** | **26** | **0** |
| B. Same-public fixed 0.95 residual weights | 104/128 | 122 | 256 | 6 | 0 |
| C. Fixed true target memory | 104/128 | 127 | 0 | 0 | N/A |

All three treatments succeeded on the **same 104 individual task/fault cells and failed the same 24**. Their sampled causal contrast in task-success indicators is literally zero and does not establish noninferiority in a larger population. The 127 rather than 128 C reads are measured actual getter calls: one source arm terminated before a planned getter. A saved **25** target getter calls relative to C, **20** relative to B, while consuming 256 public XYZ events. In read-equivalent units alone, A's advantage over C disappears if the additional public XYZ acquisition is priced above `25/256=0.09765625` target-read units per event; no measured network latency, energy, contact force, real hardware sensor cost or probe-risk parameter supports a universal operating-cost claim. A/B have the same public sensing and probing budgets; C differs in decision-visible public observations.

#### Eight source-frozen task × physical truth strata, each has 16 truth conditions

| Task | Held→held: successes / A reads | Applied→held: successes / A reads | Held→applied: successes / A reads | Applied→applied: successes / A reads |
|---|---|---|---|---|
| PullCube | 16 / 16 | 16 / 10 | 16 / 13 | 15 / 12 |
| StackCube | 6 / 13 | 12 / 13 | 9 / 16 | 14 / 9 |

The public method authorizes zero full-history candidates on PullCube held→held and StackCube held→applied, yet authorizes seven on StackCube applied→applied. This illustrates **task- and fault-conditioned observability**, not a fixed universally useful query probability. Each arm's per-cell success equals the two baselines in the first experiment. Subgroup comparison here is descriptive and must account for the same reset state appearing in four fault conditions.

### 5. Cluster-correct credibility of the apparent 'zero-error' result

The 26 accepted and correctly identified histories arise from only **20 independent task/reset IDs** (10 PullCube and 10 StackCube); some reset IDs contribute multiple correlated truth conditions. Counting all 26 confident decisions as IID observations would manufacture excessive precision.

| Error-risk counting unit | Accepted units with zero observed wrong histories | One-sided 95% exact binomial upper, if counting units IID |
|---|---:|---:|
| Events (naive IID, **unjustified**) | 26 | ~10.9% |
| Independent reset clusters with at least one admission | **20** | **~13.9%** |
| Separate PullCube accepted reset clusters | 10 | ~25.9% |
| Separate StackCube accepted reset clusters | 10 | ~25.9% |

The cluster estimand is the probability of **at least one wrong accepted history among four potential fault trials of a new reset, conditional on some admission for that reset**. It is not the per-event conditional wrong-authority probability. The exact interval assumes exchangeability of the selected *resets* within tasks and no source/domain shift. Neither measure demonstrates 10%-or-better real deployment risk. We also cannot treat 1,280 controller worlds as independent statistical units.

For information cost rather than task success, the [source-locked 32-reset clustered reviewer audit](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/isolated-query-factorial-128-20261009/research/review_original_factorial128_cluster_risk.py) resamples the original 16 Pull and 16 Stack **whole four-truth clusters**, not individual events, to provide exploratory 95% bootstrap sensitivity intervals on total private getter saving. Such resampling is exploratory, not a new prospective confirmatory test. All negative task and error cases remain included.

### 6. The falsifiable method direction, without pretending it is verified

The observation-equivalence witness motivates **action-conditioned observability planning**, distinct from simply increasing confidence on the same uninformative neutral probe. Given a complete trusted history set \(\mathcal H\), each admissible proposed native probe \(a\) must have a validated public response set \(\mathcal Y(h,a)\) for every candidate \(h\), including independently calibrated response-model errors and physical sensor tolerance. If the predicted sets overlap for any pair, a single observation may leave them indistinguishable. A one-step discriminating probe is only *conditionally* eligible when **all** response sets are pairwise separated, command chart and maximum target error are represented in the true float32/controller domain, conservative task regret is below a preset cap, and its actual sensing/time cost beats a trusted private target read. Otherwise the correct action is to query or abstain. This is an established experiment-design/set-separation principle applied to ACK-induced controller-memory uncertainty; the model validation and task benefit remain to be demonstrated.

**Missing core main-conference scientific gate:** a real *learned*, transfer-validated response-prediction model and task regret estimator fit on independent calibration rollout data; a preregistered action-conditioned nonzero probe study with actual task success, probe costs and post-inference error; a same-public and same-probe-budget implementation of official ActionShift/DualABI and simple read/heuristic controls; a second task-competent learned robot/controller family; contact and sensor OOD testing; and an unaffiliated external investigator's fresh-source reexecution. The current code for conditional probe eligibility is a tested **interface only**. It must not be cited as evidence of new active-probe task gains.

### 7. Ethics, limitations, and quantitative honesty

All studies here are robot simulator studies under author-controlled CI, not real lost ROS/TCP ACK, surgical robot safety, collision/force control, or independent software/hardware deployment. Panda is the sole genuine learned policy controller family in the main paired experiment, with two task-frozen PPOs. Equal observed task success does not mean equal effects in unobserved populations, and zero observed latent errors under correlated test conditions does not certify safe autonomy. The claim of restricted observation non-identifiability only concerns a stated achieved-XYZ+known-neutral-probe information set; richer vision, force feedback, different probing or privileged target-state access may resolve it. All raw physical source, frozen protocol, reproducibility commands and actual negative outcomes should accompany any scientific submission.

### Direct review checklist

- Original physical protocol Git blobs and first-run SHA256 remain unchanged, and all 16 distinct factual physical source shards present.
- 32 unique reset clusters × four physical fault truths are counted, not misrepresented as 128 independent resets.
- Under C, 127 physically charged readbacks are used instead of an invented 128; 256 public XYZ sample events and common physical neutral step are priced explicitly.
- No claim of ActionShift DualABI superiority or more than 104 task successes; source mismatch and missing fault mean an invalid whole-cohort gate.
- Sample-level wrong-authority risk, independent-cluster conditional risk, and per-task upper bounds use their correct *different estimands*.
- Experimental novelty is currently an empirical physical observation-equivalence counterexample plus a careful bounded information-cost benchmark, **not** a new learning method or top-conference acceptance.
