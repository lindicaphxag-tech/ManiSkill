# From static ACK belief to transition-aware repair authority

**10 October 2026 · research-first, model-only dynamic algorithm plus a linked independent source *audit of author-operated prior PhysX*. No fresh physics on this branch, independent researcher verification, third-party adoption or official robotics upstream merge.**

## 1. Scientific contrast: what the older model cannot justify

Previously [authority_probe_minimax.py](authority_probe_minimax.py) optimized repair decisions over a static hidden-history set B, treating a probe as preserving repair semantics. It is correct under its explicit assumptions, but real native controllers update internal command targets when a probe is delivered. Merely using the original action history to decide a post-probe repair can be **wrong**.

This branch introduces [dynamic_authority_shield.py](dynamic_authority_shield.py), with finite latent states, state-dependent repairs, and explicit action-conditioned nondeterministic transitions (observation, successor state). It refuses to probe whenever *any currently possible* transition enters a modeled forbidden state, updates the belief using **post-action states**, and authorizes a repair only when every surviving successor state has the same prescribed repair. Unknown observations trigger authoritative read and a declaration that the original model-bound guarantee is no longer applicable.

The new [adversarial test file](../tests/test_dynamic_authority_shield.py) includes a **constructed counterexample** where a state formerly requiring CONTINUE transitions on probe delivery into a new state requiring REINITIALIZE. A naive repair-preserving static rule would authorize CONTINUE based on its old state; the dynamic engine correctly authorizes REINITIALIZE after the response. This proves only a model-assumption failure, **not that such a changed repair occurred in the archived physics**.

### Finite model / minimax contract

- State set S, initial nonempty B0 subset S, forbidden modeled states F disjoint from B0.
- For each state s, a required action r(s); not necessarily the exact state identity.
- Probe p costs positive abstract c(p) and has **complete** possible pairs (public observation o, next state s') for each s. Without validated completeness the certificate is not a physical claim.
- Probe inadmissible whenever one possible s' is in F. Otherwise, B'=union of next states consistent with the observed symbol.
- Authorize r only if {r(s):s in B} has one element. Else either atomic authoritative read with cost R or a feasible probe that minimizes worst-case total cost up to frozen depth d.

All integer abstract costs have no measured relation to latency, force, contact, energy or controller getter overhead.

The synthesizer computes the optimal finite-horizon policy under these assumptions by memoized minimax; the independent verifier checks every modeled branch, repair decision, provenance hash and worst-case cost without calling the synthesizer. A separate uncached exhaustive oracle verifies the root optimum in **160 adversarial randomized small worlds**, so model soundness and optimality are distinct checks. There is no claim of better-than-classical belief-state dynamic programming.

**Model-only, 6/6 original CI:** [run #37989526570](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37989526570), Linux/macOS/Windows and Python 3.11/3.13, 10 test functions including the 160 independently enumerated worlds.

### Three synthetic counterexample categories

| Case | Dynamic model first decision | Exact modeled abstract cost | Proper inference |
|---|---|---:|---|
| Repair changes under a probe | Probe, then post-action repair | 1 (getter baseline 5) | Static state-to-repair persistence can authorize a wrong action |
| Apparently useful probe may enter forbidden contact state | **Read**, not probe | 5 | Worst-case unsafe-state reachability veto |
| Nonzero actuator motion reveals no hidden state | **Read** | 5 | More motor actuation does not imply information value |

These synthetic costs are **by construction**. No empirical speedup or hardware safety claim.

## 2. Genuine original Panda/xArm6 physics — what it does and does not say

To prevent mistaking a constructed dynamic counterexample for an observed real controller failure, [audit_dynamic_probe_archive_link.py](audit_dynamic_probe_archive_link.py) independently reads the original 24-file SHA256-authenticated source archive from [2026-10-10 first 192-world experiment](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/evidence/low_signal_first192_20261010). It validates the complete 96 never-seen physical source rows across Panda and xArm6, 16 independent robot/reset seeds, both true ACK histories, and all zero/X/Y physically stepped probes.

The exact per-truth grouped comparison finds:
- **32** robot/reset/ACK-truth groups, each with zero/X/Y matched original source;
- **64/64** nonzero X/Y probe worlds showed >0.5 mm public achieved-EE displacement relative to the paired zero action;
- **32/32** groups had **the same final corrective native six-dimensional command** across zero, X, and Y; zero observed "repair-changing probe" in this restricted archived data.
- No measured full action-conditioned hidden **SE(3)** support completeness, no probe safety certificate, and no learned PPO/VLA task success in these rows.

The 32 groups are *not 32 independent reset seeds*: there were **16 reset seeds**, each repeated under two correlated ACK truths. Zero corrections changed in these grouped records does not prove repair invariance on future states or different controllers. It only documents a narrow physically observed negative result. A physical nonzero probe moved the achieved state, but no different corrective native vector was needed in the paired source.

**Real-source validation gate:** [workflow #37989796685](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37989796685), which checks byte-authenticated first-run JSONs on multiple operating systems; only count as passed when the GitHub Actions workflow has actually completed successfully. This is again **author-operated source replay**.

## 3. Strongest established comparator families

The goal is *not* to present finite-state belief dynamic programming as new. Relevant prior art includes:

| Independent established work | What it already covers | Remaining research work before novelty claim |
|---|---|---|
| [Safe RL via Shielding, AAAI 2018](https://ojs.aaai.org/index.php/AAAI/article/view/11797) | Temporal-logic safety shields and runtime blocking of unsafe actions | Actual robot/controller-state contract validation and physical task utility |
| [Safe RL via Formal Methods, AAAI 2018](https://ojs.aaai.org/index.php/AAAI/article/view/12107) | Verified monitors and model-mismatch-aware fallbacks | Source-proven real ACK/target transitions, calibrated uncertainty and matched read costs |
| [Probabilistic Shielding, AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/33767) | Probabilistic shielding guarantees under known MDP safety dynamics | Empirically justified, independently calibrated controller response transition supports |
| [ManiSkill3, RSS 2025](https://github.com/mani-skill/ManiSkill) | Reusable embodied simulation, baselines, cross-robot tasks | External users, real official upstream ownership, transfer beyond scripted controller probes |
| [FlashAttention](https://github.com/Dao-AILab/flash-attention) | Original method/papers + documented external adoption and continuing software evolution | A demonstrated method performance advantage and independent ecosystem adoption |

**There is no official L8/L9 rating for people.** These are comparable *outcomes*, not labels assigned to researchers. This project's accepted EEG integration work is strong open-source engineering but is not evidence of an original robotics algorithm being adopted by another lab.

## 4. Hard gates for an authentic L8/L9-style research outcome

1. Collect actual action-conditioned controller target **and achieved** SE(3) state transitions under intervention, not only reconstructed public XYZ and posthoc corrective native vectors; do not assume probe preserves repairs.
2. Demonstrate a **nontrivial collision** in which passive public response leads to different correct repairs, and show that a safe, nonzero probe can disambiguate it without task regret. Freeze development seeds, probe selection, independent calibration seeds, then heldout seeds. If no such scenario exists, report a negative result.
3. Include tuned same-information passive scoring, fixed norm-matched probe, robust optimal finite-model shield, always authoritative getter, and a comparable active adaptation baseline. Execute all candidates under matched original physical prefix and count **all** failures and costs.
4. For requested statistical risk, calibration must use independent reset groups and a predictor/selector frozen on a separate population. Existing 8 old resets per robot cannot yield the claimed 95% marginal two-hypothesis certificate: the previously published fail-closed module requires **at least 39 independent residual groups**, plus the independence assumptions.
5. Refuse a robot safety claim until forbidden events and action costs are verified with realistic contacts; even a perfect synthetic model proof is not physical verification.
6. Invite actual independent operators to select new states and publish their own output. A GitHub Actions CI, author README, or self-merged fork PR is **not** external adoption. External GitHub merge requires the original upstream owner to merge the submitted PR.

### Assessment

The correct classification is still **engineering L7 with a growing original methods research prototype**. A scientifically defensible L8 outcome would require independent original-method use and cross-controller policy-level benefits. L9-style impact requires sustained cross-project adoption, an accepted original research contribution and independent extensions; software unit tests alone cannot substitute.
