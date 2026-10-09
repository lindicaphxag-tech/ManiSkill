# V11 research upgrade — When Did the Command Execute?
## Controller-History Observability, Belief-Consistent Compilation, and the Success–Information Frontier

**Status:** Evidence-constrained working manuscript plan (9 October 2026). This is **not** a completed V11 experimental result or a submission-ready new PDF. Every prospective result is withheld until the registered native-PhysX auditor passes. Anonymous submission needs separate removal of public repository/author provenance.

### Abstract — currently defensible (based on the already completed original 64-reset four-truth cohort)

Robotic action interfaces can silently lose command acknowledgments while leaving the execution state uncertain: a controller may have applied or held each command, resulting in different latent commanded targets despite a documented action coordinate convention. We examine whether achieved end-effector motion can identify complete execution histories sufficiently to avoid privileged controller-target reads, and whether a truthful read is useful without synchronizing subsequent action compilation. Under frozen third-party policies for two ManiSkill manipulation tasks, we physically vary the application of two consecutive native commands, yielding four actual execution-truth patterns in a source-audited 64-reset PhysX cohort. Public-motion history selection attains 55/64 task successes with 50 privileged reads, compared with 56/64 and 59 reads for a task-aware comparator and 57/64 and 64 reads for fixed readback. Fourteen public histories are selected without a private read and none is wrong in this cohort; this observation does not constitute a zero-error guarantee. The results expose a trade-off between authoritative information cost and task completion, not task-success superiority. We also isolate a cache-consistency failure in which an accurate read can still lead to an incorrect compiled action. A prospectively registered same-reset four-condition factorial is designed to separate execution-truth effects from reset-state heterogeneity, without claiming those results before completion.

**Do not insert numeric claims from the new prospective factorial before the all-shard full audit.**

### 1. Scientific questions and novelty boundary

- RQ1 (observability): Which finite combinations of native command execution can be distinguished from **already available public achieved motion**, without a privileged commanded-target getter?
- RQ2 (control): If multiple complete target histories survive, when does a common bounded native action preserve the desired action target under every surviving history?
- RQ3 (systems integrity): What synchronization is necessary after a private read so that the next action is compiled from the updated target memory, not a stale branch?
- RQ4 (cost–success): What **Pareto frontier** emerges once public sensing samples, probe actuator time, state reads and real task completion are disclosed separately?

We do **not** claim a general solution to unknown robot action wiring or learned interface adaptation. ActionShift considers hidden compositional action-contract changes and task-regret-aware probing; ActionABI identifies equivalence classes of action contracts from logged trajectories. Here the documented action chart is fixed; the hidden variable is actual recent physical execution truth and consequent native commanded-target memory.

### 2. Set-valued execution-history formulation

For two unknown execution acknowledgments, let the finite history hypothesis space be
`H = {HH, AH, HA, AA}`, where the first/second letters denote whether the corresponding native command was physically **Held** or **Applied**. Each hypothesis `h` induces a complete native controller target `q_h in SE(3)` after applying the known action chart. Crucially, all components of `q_h` (including rotation) come from the *same full execution history*, not coordinate-wise mixing.

Let public achieved motion before and after the common zero-target-displacement probe be `w = (x_pre, x_post)`. For each candidate target history, a preregistered empirical motion envelope predicts a set `E_h` of possible public responses. The admissible set is `H_w = {h in H : w is compatible with E_h}`. The public observer may adopt a unique history only when exactly one candidate survives and its residual margin exceeds the fixed threshold. Because the envelope is calibrated on prior experiments, this is an empirical **selection rule**; it does not certify physical safety or probabilistic confidence under distribution shift.

If `|H_w| > 1`, the system must either make a common bounded action, collect new public evidence, issue a counted authoritative target read, or refuse. It must never silently assume the command was applied.

### 3. Exact robust-action feasibility boundary

Define the native command feasible set `U`. For a task-desired target `g`, a bounded tolerance `(eps_pos,eps_rot)`, and hypothesized target `q_h`, define

`A_h(g) = {u in U : ||pos(F(q_h,u))-pos(g)||_inf <= eps_pos and geodesic(rot(F(q_h,u)),rot(g)) <= eps_rot}`,

where `F` is the verified native target-update function under the controller chart.

**Proposition (finite robust-action feasibility).** A common one-step native command satisfies the stated target tolerances for all surviving execution histories if and only if `intersection_{h in H_w} A_h(g)` is nonempty.

*Proof.* A command is robust precisely when it lies in the feasible-action set of every surviving history. By elementary set intersection, such a command exists exactly when the intersection is nonempty. QED.

**Scientific boundary:** this is a necessary/sufficient statement for the verified target-update model and chosen tolerances, **not** a novel physical hardware safety certificate, a solution to closed-loop contact dynamics, or a proof that one query always suffices. If the intersection is empty, any one-step zero-information action violates the target specification for at least one surviving hypothesis; a read, additional probe, altered target/tolerance, or refusal is required.

### 4. Readback-integrity invariant

A trusted target read yielding `q_read` must atomically perform: (i) invalidate all cached history-specific action decisions; (ii) set the unique current native target belief to `{q_read}`; (iii) recompute and validate the native action from this new state; and (iv) log which branch and controller-state version produced the dispatched action. Reading true state followed by executing a previously compiled action is not an authorized correction.

**Tests required before any strong claim:** incorrect cached branch fails closed; delayed read cannot reuse prior compiled command; all public-only decisions make zero private decision-time reads; audit-only private getters never influence the runtime policy.

### 5. Completed four-truth evidence (original 64 reset IDs, not the prospective matched factorial)

| Frozen arm / method | PhysX task successes | Counted decision-time private target reads | Extra public achieved-XYZ samples |
|---|---:|---:|---:|
| Public complete-history selection | **55/64** | **50** | **128** |
| Task-aware robust/selective strong | **56/64** | **59** | Not incrementally charged in original comparator |
| Fixed readback at t5 | **57/64** | **64** | Not incrementally charged in original comparator |
| Always assume both HELD | **35/64** | **0** | No additional public witness |

Results refer to the genuine 2×2 physically varied-ACK cohort preserved in the parent research branch and author-operated PR #138; not to the earlier t3-always-HELD 58/64 comparison. The 64 reset IDs are split across the 4 truth patterns (8 Pull and 8 Stack per pattern); truth patterns **do not** share reset identities in this completed study. The public-vs-task-aware paired outcomes are 54 both succeed, 7 neither, 1 public-only success, and 2 task-aware-only successes. An unadjusted exact discordance test yields no demonstrated difference; it cannot establish noninferiority. Fourteen public complete-history selections had zero observed wrong selections, but no zero-failure guarantee follows.

**Information costs:** 9 fewer target reads versus task-aware come with one fewer task success and 128 extra public XYZ sample events. The 9/128 threshold (0.0703125 private-read equivalents per public sample) is only a read-budget arithmetic boundary before motion, time, energy, and sensing infrastructure costs. Do not say it is an energy or latency break-even.

### 6. Prospective same-reset factorial (registered, not completed)

Pre-outcome frozen seed groups: PullCube 1310001–1310016; StackCube 1320001–1320016. For each `(task, seed)`, run the SAME nine comparator worlds under **all four** physically applied/held t2/t3 truth combinations. Planned denominator: 32 distinct reset identities × 4 conditions = 128 source experiment cells × 9 independent PhysX worlds = 1,152 worlds. Exactly 16 shard original files plus their 16 independent shard audits are required, followed by a strict complete-population independent auditor.

- Each seed must have four condition-specific records and identical initial source physical observation hashes across conditions. Missing or mismatching observation hashes **invalidate**, not merely reduce, the dataset.
- Keep early pre-fault failures and early-stop refusal in every denominator, and explicitly separate intervention exposure from enrollment.
- Primary table: task × true HH/AH/HA/AA, task success, private reads, public admission/false admission, paired method discordances.
- Statistical unit is the **source reset identity**, with four condition cells clustered together (N=32, not N=128 independent). Exact cluster sign-swap is a sensitivity calculation requiring exchangeability; seed-cluster bootstrap intervals are descriptive, not proof of randomization or noninferiority.
- Report independently the 16-shard source hashes, world count, immutable frozen checkpoint identity and full-audit pass. Workflow creation alone does not produce a physical result.

**Result table for this subsection stays BLANK until all original physical jobs pass.**

### 7. Figure architecture suitable for high-quality review

**Figure 1 — Mechanistic identifiability.** Four complete native commanded-target history branches (HH/AH/HA/AA) derived from two ambiguous ACKs. Show two public achieved-XYZ pose samples and candidate-motion residual intervals. Separate the empirical unique-survivor decision and counted private getter; after read, show the compiler-cache invalidation required for belief consistency. No invented measured trajectories: render actual branch/observations only from native source logs.

**Figure 2 — Evidence rather than decoration.** A 2×4 matrix of Pull/Stack by HH/AH/HA/AA from the prospective *matched* cohort, with physically achieved trace overlays for the same source seed; mask any not-yet-executed cells. Adjacent plot: paired seed-cluster difference in success vs read budget, with confidence interval and public XYZ cost shown separately.

**Table 1 — Completed old cohort.** Current 55/64, 56/64, 57/64, 35/64 and actual read/sensing counts, with subgroup failures and early-stop exposure rates.

**Table 2 — Prospective same-seed factorial.** Do not publish until all runs pass, and do not pool 128 correlated cells as 128 independent seeds.

### 8. Reviewer-disarming limitations

The current study relies on Panda-family controllers, two simple manipulation tasks, frozen PPO rather than general-purpose VLA policies, a fixed known native action chart, a simulator-specific empirical response envelope, a neutral probe with nonzero time/actuation, and original execution performed by the authors. True xArm frozen learned-policy task success is absent; ActionShift-style active sensing is not faithfully implemented at equal full-information cost; independent third-party original results are not available. The observed lack of wrong confident selections is a finite-sample fact only. All negative outcomes and source failures remain in the primary reports.

### 9. Promotion gates for an honestly high-level representative work

1. **Matched physical factorial complete:** all 16 source shards and the independent all-population audit green; actual task-level factorial findings retained even if negative.
2. **Method improvement beyond selection:** an explicitly preregistered task-regret/robust-action-based *active* sensing branch that beats or defines a useful Pareto point against task-aware and fixed controls under the same public measurement, probe and privileged read budget. Don't import the ActionShift name as a label without reproducing its adapter/variables faithfully.
3. **Genuine cross-embodiment learned-policy transfer:** a checkpoint trained for the other robot/controller's own action/observation contract, frozen before all evaluation; compare within matching pairs and preserve failures. Simply replaying Panda weights on xArm is not valid.
4. **Independent run with outsider-selected seed list:** outside researcher independently executes and releases raw outputs and environment details. An author-owned fork or self-CI pass does not count.

This draft upgrades the research question, exact feasibility model, causal design, statistical unit, and honesty of the quantitative claims. It does not claim a manuscript score, main-conference acceptance or new success advantage without evidence.
