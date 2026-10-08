# History as the interface: an evidence-gated research program for frozen robot policy transport

**Research/technical-review packet · 9 October 2026 · contributor-operated evidence**

**Do not cite this repository as a peer-reviewed paper or upstream ManiSkill endorsement.** The repository is a public research fork, and every simulator trial, proof and audit in this packet has been carried out by the contributor or their automated CI—not an independent robotics lab. The rigorous result is **conditional**: access to the relevant previous commanded target is sufficient for a known controller chart, while *private getter access is not intrinsically necessary* when the same state is reconstructible from an acknowledged command stream.

## Abstract (research statement, not accepted-paper abstract)

A frozen robot policy can emit numerically valid end-effector actions yet fail after changing from achieved-pose-relative to accumulated target-relative control, because the same command is interpreted against a different historical reference. We investigate which information is actually required to preserve this action semantics. Four released, independently pretrained PPO checkpoints provide paired genuine-PhysX task outcomes under an unmodified source policy, naive action transfer, exact-or-refuse conversion, bounded live-target conversion, and a matched history-blind control. A separately preregistered 64-state two-task falsification asks whether direct private controller-memory reads can be replaced by a recursively reconstructed target from reset and the previously submitted actions. The shadow estimate and privileged approach yield identical binary task outcomes on all 64 original paired states. A further prospective 16-state experiment replaces controller-owned target-update functions with a separately implemented acknowledgement-gated observer that does not read private target state while choosing actions and matches the privileged outcomes on all 16 states. Finally, controlled native-PhysX twins and a separate joint-target controller test distinguish information-theoretic target ambiguity from implementation-specific action-chart errors. These results support the conditional sufficiency of command-history reconstruction and explicit refusal when state provenance is lost. They do **not** establish novel controller identification, real-hardware safety, independent external adoption, or state-of-the-art learning performance.

## Scientific object: target-state observability, not a generic action adapter

Let the actual achieved end-effector pose be \(X_t\), previous **commanded** target state \(M_t\), and frozen source policy action \(a_t=\pi(o_t)\). A source controller interprets the action against \(X_t\); an accumulated-target destination interprets an action against \(M_t\). A converter first constructs the source's intended physical target \(D_t\) and then solves the destination's chart inverse **conditioned on the correct \(M_t\)**.

For a documented deterministic destination update with known reset target and **verified applied** native commands,

\[
\hat M_0=M_0,\qquad\hat M_{t+1}=F(\hat M_t,u_t).
\]

If the actual controller obeys the same recurrence, induction gives \(\hat M_t=M_t\). Hence a private live getter is **sufficient but unnecessary** in this restricted regime. This is an elementary state-observer fact, not a new theorem. It depends on a correct reset reference, known action framing/scaling and complete acknowledgements. It does not apply blindly to undocumented controllers, delayed/dropped commands, external state resets or hidden actuator transitions.

A controller with target memory can be **not observable from achieved pose alone**: two histories may have the same \(X_t\) and source policy observation yet distinct previous targets \(M_t^A\ne M_t^B\). For an additive position chart, if both histories must receive the same command \(u\) to reach desired \(D\), the triangle inequality gives the worst-case commanded-setpoint error lower bound
\[
\inf_u\,\max\{\|M_t^A+u-D\|_\infty,\|M_t^B+u-D\|_\infty\}
\ \ge\ \tfrac12\|M_t^A-M_t^B\|_\infty.
\]
**This is about commanded setpoints, not physical tracking, contact, collision or full SE(3) pose.** A complete official target-memory observation can distinguish the histories; indistinguishability refers to the achieved-state/source-policy information used by the blind action adapter.

## Evidence ladder: never pool these as interchangeable validations

| Evidence layer | Original study and fixed population | Observed result | What it can support |
|---|---|---|---|
| Four-task frozen-policy source experiment | [Four-task first-screen packet](STATEFUL_ACTION_ABI_FLAGSHIP.md); original Pick/Push and newly preregistered Pull/Stack task cohorts | Task-level failures and recovery under real closed-loop target-memory conversion; non-exact projections reported | Same Panda controller-family failure mode and fixed-policy transfer, **not cross-robot** |
| **New, separate 64-state mechanistic falsifier** | [Pre-outcome protocol ed97913](https://github.com/lindicaphxag-tech/ManiSkill/commit/ed979138bed2cd4ac6b3e5c4137799ce7c73711a); PullCube **71001–71032**, StackCube **81001–81032**; [original genuine PhysX Actions 37818985343](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37818985343) | **All 64/64** binary live-memory versus recursively reconstructed-shadow outcomes agree; see exact values below | Runtime-memory read is not necessary when the existing controller recurrence and valid command stream are available |
| **Fully separately implemented action-history observer, 16 new states** | [Pre-outcome protocol 8084b681](https://github.com/lindicaphxag-tech/ManiSkill/commit/8084b681e9eca69046894d1e831746a44741cc35); PullCube **62001–62008**, StackCube **72001–72008**; [original full 5-job success run 37819111802](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802) | Privileged converter **6/8, 7/8**; independently coded observer **6/8, 7/8**; matched all 16 binary outcomes; max final reference error **2.385e-8 m / 6.501e-7 rad** | Action-only target reconstruction without **private state getter during decision making**, under reliable acknowledgement and documented Panda frame |
| Native controlled hidden-memory twins | [Exact native-PhysX counterfactual 37820410085](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37820410085), four tasks; controlled two prior targets separated by **2 cm** | Correct state-conditioned inverse in each world reaches same commanded target to numerical tolerance; blind action copy shifts target by about **2 cm** | Structural controller-memory non-identifiability in a **constructed replay**, not naturally occurring task failure rates |
| Distinct controller implementation sanity test | [Joint-target controller PR #65 (merged)](https://github.com/lindicaphxag-tech/ManiSkill/pull/65), four official PhysX tasks, seven joint target accumulators | Source-pinned additive interval-certificate check with fail-closed controls | Formula/contract portability to **joint-target** control on the **same Panda**, not a second robot or policy transfer success |
| Bounded-error authority theorem & executable checker | [Minimax certificate PR #62 (merged)](https://github.com/lindicaphxag-tech/ManiSkill/pull/62) | Exact boxed additive setpoint minimax; adversarial endpoint witness; stale/untrusted/unsupported contracts refuse | **Mathematical command-target guarantee under explicitly supplied assumptions only** |

### Exact new 64-state outcome table: not 64 independent policies

| Original paired destination trial arm | PullCube 71001–71032 | StackCube 81001–81032 |
|---|---:|---:|
| Frozen source policy / native chart | 32/32 | 29/32 |
| Naive copy to accumulated-target chart | 12/32 | 1/32 |
| Strict exact conversion or refuse | 13/32 | 14/32 |
| Live prior-target, bounded projected conversion | **32/32** | **29/32** |
| Achieved-pose-substituting blind conversion (same projection) | 12/32 | 1/32 |
| Action-history **shadow** prior-target reconstruction | **32/32** | **29/32** |
| Live-only vs shadow-only paired successes | **0 vs 0** | **0 vs 0** |

**Raw data are permanently copied byte-for-byte from the original successful CI** to [the public default-branch nine-JSON + SHA256SUMS archive](evidence/shadow_observer_64_71001_81032). This archive was verified by [trusted-main Actions 37822124303](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37822124303). Recompute the actual full 64-row aggregate, not these markdown totals:

```bash
cd research/frozen_policy_transfer/evidence/shadow_observer_64_71001_81032
sha256sum -c SHA256SUMS
cd ../../../..
python -m research.frozen_policy_transfer.verify_shadow_source \
  --input-dir research/frozen_policy_transfer/evidence/shadow_observer_64_71001_81032
python -m unittest discover -s tests -p test_action_abi_shadow_observer_auditor.py -v
```

**Important negative nuance:** the 64-state *shadow* implementation reuses the destination controller's `compute_target_pose` to predict the next target and verifies the observation-state memory slice. Its zero recorded prediction error is therefore a controller-internal recurrence test; **do not describe the 64 states as validation of a fully independent black-box observer**. The **separate** 16-state action-history observer uses a coded recurrence without private getter during decision making and checks the private target **only at the end** for audit. It still depends on documented controller semantics and truthful command acknowledgement.

## From exact observability to uncertainty-authorized action

When acknowledgement becomes unknown, the controller may or may not have applied a command: the next target is a *set* of possible histories. Continuing with one guessed prior target and reporting an exact repair is unjustified. A two-phase command acknowledgement observer already [fails closed on unknown delivery or stale acknowledgements](../action_abi_history_observer.py) via API-level tests; no genuine dropped-command PhysX policy-recovery success is claimed.

For a **separately attested**, axis-aligned box of possible additive prior *position setpoints* \(M_i\in[L_i,H_i]\), legal additive command \(u_i\in[a_i,b_i]\), desired setpoint \(D_i\), the well-known robust minimax command is

\[
u_i^\star=\operatorname{clip}\bigl(D_i-\tfrac12(L_i+H_i),[a_i,b_i]\bigr),
\]
\[
E_\infty^\star=\max_i\Bigl[\tfrac12(H_i-L_i)+
\operatorname{dist}\bigl(D_i-\tfrac12(L_i+H_i),[a_i,b_i]\bigr)\Bigr].
\]

The [implemented certificate](../latent_target_memory_cert.py) authorizes only if the independent box provenance is trusted, fresh, additive chart/bounds verified, and \(E_\infty^\star\) is strictly within the requested commanded-target error budget after a numeric margin. It otherwise refuses. **The formula is standard minimax robust optimization**, and its certificate is *not* valid for joint-trajectory safety, SE(3) rotations, actuator saturation not captured by the model, force/contacts, or collision.

A [separate draft set-valued ambiguous-ACK experiment](https://github.com/lindicaphxag-tech/ManiSkill/pull/66) tracks finitely many *realized* target histories and asks for a **common exact** inverse. It remains draft/CPU contract testing and is **not** a successfully validated native PhysX loss-recovery method. An exact feasible intersection is a stronger condition than bounded-error minimax; do not conflate these authorizations.

## Distinguish what is proved, what is experimentally supported and what is still open

**Proved algebraically under a declared model:** deterministic recurrence reconstructibility from acknowledged commands; two-history additive-setpoint error lower bound; known interval-box minimax bound. These are elementary/known results, not broad new robot-control theorems.

**Observed in original PhysX:** frozen-policy binary success on four tasks for one Panda chart mismatch; 64-seed shadow comparison; 16-seed separately implemented history observer; synthetic-target-twin interventions on four native tasks; joint-target additive controller check. Trial count is **not** the count of independently trained policies, robots or external teams.

**Still unproved and arguably required for a strong CoRL/RSS/ICRA method:** controller-implementation-independent diagnosis beyond published Panda charts; real dropped/delayed commands with online resynchronization and a fair learned/history-observer comparator; motion/actuator/force/contact safety metrics; predeclared fresh states beyond the current cohorts; independent researcher execution and documented upstream adoption. Early success cannot be presented as a general VLA controller repair.

## Nearest-neighbor originality veto for information-authorized action

The proposed **bounded common action versus selective privileged query**
is **not** the first controller adaptation method, belief-set planning method,
or principled selective-sensing method. Specific prior art that must be
handled in any publication-quality related work:

- [SPACE (2026)](https://arxiv.org/abs/2606.24049) already
  learns robot-specific command adapters from desired Cartesian state
  deltas with online adaptation across embodiments and shifting dynamics.
  Our narrower target-memory condition should not be compared to
  direct-action-copy alone when claiming superior adapter performance.
- [Hibbard, Tanaka and Topcu, *Automatica* 2023]
  (https://doi.org/10.1016/j.automatica.2023.111140) already studies
  simultaneous perception/action decisions using invariant finite belief
  sets. 'Query only when the belief is insufficient' is not a new idea.
- [Jaulin, *Automatica* 2009]
  (https://doi.org/10.1016/j.automatica.2008.06.013) establishes
  robust set-membership estimation; interval posterior propagation and
  min-max geometry alone do not establish a new estimation principle.
- [Garrett et al., 2019](https://arxiv.org/abs/1911.04577) study
  belief-space re-planning and information-seeking manipulation
  actions under partial observability.

- [Banerjee et al., HRI 2026, *A Human-in-the-Loop Confidence-Aware
  Failure Recovery Framework for Modular Robot Policies*]
  (https://emprise.cs.cornell.edu/modularhil/) already determines
  when costly human information requests improve recovery in modular
  manipulation. Reducing query count under uncertainty in itself
  is NOT original to this project; our current simulation instead
  targets a very specific missing low-level **commanded-target ACK**
  state variable and uses a privileged controller-state readback.
- [MAGMA-GEN, CoRL 2026]
  (https://magma-rob.github.io/magma-gen) develops recovery supervision
  from counterfactual execution after ambiguous manipulation failures.
  It reinforces why our native target-hold outcomes must NOT be
  described as the first counterfactual robotic fault recovery.
**Surviving focused hypothesis, not a verified novelty claim:**
make the *robot action ABI's hidden previous commanded target* the
explicit authority-bearing information state, with an exact native
root-control representation gate, ACK provenance, two-history bounded
SO(3)/position setpoint error, and a budgeted privileged readback.
Validate the joint effect with an equal-information/equal-readback
budget source policy trial rather than presenting classical sensing
or interval-control concepts as discoveries. Actual trajectory
deviations, controller variants and outside replication remain required.
## External reproducibility request

[Public replication/falsification issue](https://github.com/lindicaphxag-tech/kaggle/issues/67) asks independent researchers for exact source SHA, policy checkpoint SHA-256, runtime versions, fresh preregistered task seeds, **complete failures** and native controller state evidence. External replies and outside-run source traces—not additional author-owned PR merges—are the decisive next recognition event.
