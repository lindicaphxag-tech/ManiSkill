# Authority-aware minimax probe synthesis: strict research gate (v1)

**Status (10 October 2026): working algorithmic prototype and proof-carrying FINITE-MODEL tests. No new PhysX outcomes, independent adoption, or main-conference claim.** This is a research branch, not an upstream ManiSkill feature.

## Problem decision rather than history classification

The goal is **not** to infer the exact hidden controller history in every case. A public-observation belief set B may contain many controller histories. An intervention can be authorized if **every history still compatible with the observations requires the same repair action**. This task-relevant equivalence quotient can be coarser than exact state/history identification.

When repair labels differ, the policy may either:

- pay for a **privileged authoritative read** that reveals the true controller history;
- issue a **known-delivered repair-preserving probe**, observe a possibly adversarial public response and update the set B; then continue or read.

The optimizer selects the complete finite-horizon decision tree minimizing **worst-case sum of abstract positive integer costs**. It does not optimize measured task reward, actual work or force. A separate enumerating verifier checks all modeled hidden-history / possible-observation traces, correct action authorization, branches, model provenance and worst-case node costs. An unknown runtime observation forces a **read** and explicitly invalidates the original model cost bound.

## Exact finite-model formulation and reproducibility

Let H be a finite set of hidden histories and r(h) the required repair for h. A probe p has abstract cost c(p)>0 and a nonempty *complete* possible response support O_p(h) for every h; these supports can overlap, reflecting sensor noise or ambiguous responses. After observing o, the belief is B'={h in B : o belongs to O_p(h)}. Model probes must preserve required repairs r(h) and hidden history indices: this is a **modeling assumption to verify physically**, never a claim inferred from a user-provided flag alone.

For remaining probe depth d and unit getter cost R:

    V(B,d)=0                                      when all r(h) in B are equal
    V(B,0)=R                                     otherwise
    V(B,d)=min{R, min_p [c(p)+max_o V(B'_p(o),d-1)]} otherwise

A probe is chosen only if its worst-case cost is **strictly lower** than reading; ties prefer the getter. Dynamic programming stores full decision trees; a separate non-memoized exhaustive oracle checks the optimum on 70 fixed-seed randomized worlds. Certify() walks **every modeled response branch**, rejects missing branches, fabricated posteriors, wrong repairs and altered cost bounds, without calling the optimizer. Runtime next_request() returns probe / authorized repair / read, with an unconditional read fallback on any previously unmodeled observation.

Run from repository root (no GPU, no ManiSkill import):

    python -m unittest discover -s tests -p test_authority_probe_minimax.py -v
    python -m research.authority_probe_minimax

Source: [authority_probe_minimax.py](authority_probe_minimax.py); [adversarial tests](../tests/test_authority_probe_minimax.py). Cross-platform CI is in .github/workflows/authority-aware-minimax.yml.

## Three deliberately SYNTHETIC diagnostic cases

| Case | Exact-result behavior | What it proves in the finite model | What it does NOT prove |
|---|---|---|---|
| Four distinct histories with identical repair | Authorize immediately, cost 0 rather than getter cost 5 | Exact hidden-state identity is not necessary to select a repair | That any real controller has this verified action equivalence |
| Four repairs, cheap two-way probe cost 1, complete probe cost 3, getter cost 5 | Pick complete probe, worst-case cost 3 | Local cheapest-first probing can cost more than global minimax | Adaptive probing beats a physical baseline in ManiSkill |
| Two histories, indistinguishable under a nonzero probe cost 2, getter cost 5 | Getter, cost 5 | Do not pay for an uninformative action in worst-case control | Physical non-identifiability for all possible probes |

All three are **constructed input models**, not simulator tests or novel-POMDP benchmark wins. Finite-horizon belief-space dynamic programming is classical; novelty would need to arise from an empirically validated controller interface/repair contract, usable uncertainty model and genuine downstream value.

## Why previous PhysX evidence motivated this choice

Existing author-operated source-frozen ManiSkill work gives two hard constraints:

1. The 32-reset / 128-cell / 1280-world prospective strong-score physical comparison: A/B0.60 task success exactly 109/128 each; 94 vs 98 private controller reads, exploratory whole-reset sign-flip p=0.289. **Do not claim meaningful method dominance.** [source and paired audit](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/reviewer-audit-strong060-20261010/research/frozen_policy_transfer/PROSPECTIVE_STRONG060_FLAGSHIP_RESULTS_20261010.md).
2. The 192-world Panda/xArm6 low-SNR known-delivered zero/X/Y probe experiment: all three probe types identified 32/32 heldout ACK outcomes; no observed benefit of nonzero action and no physical safety assurance. [permanent source and negative report](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/LOW_SIGNAL_ACTIVE_PROBE_FALSIFICATION_FIRST192_20261010.md).

This prototype **does not overwrite or re-label** either experiment. Its synthetic improvements must not be merged into their tables or presented as actual new PhysX advantages.

## Critical falsifiers BEFORE a physical policy claim

1. **Response support validity:** real sensors can produce an observation not contained in O_p(h). Need a separately fitted and frozen conservative model with independently tested coverage, including a reject-on-unknown mechanism. If the real true state falls outside B, no certificate remains valid.
2. **Probe changes the hidden state:** a physical probe can shift commanded targets, cause contact or damage, or change which repair is safe. The static repair-preserving model is then invalid. Need explicit intervention-state transition semantics and achieved/target SE(3) records, not an asserted boolean.
3. **Calibrated regret / cost:** integer unit probes and getter calls are synthetic. Need measured time, energy, contacts, collisions, public XYZ acquisition, privileged getter counts and complete task outcomes under *the same* state/action prefix.
4. **Baseline fairness:** compare against zero probe, fixed norm-matched probe, tuned passive scorer B0.60, mandatory getter, and separately implemented active-adaptation competitor under matched sensing/actuation budgets.
5. **Generalization:** freeze on a new development cohort, validate on a disjoint calibration set, then run new heldout seeds and a different robot/controller/learned policy. Preserve all failed prefixes, weird observations, negative results and adversarial counterexamples.
6. **Independent adoption:** a reviewer or external team must actually run the package and publish the resulting issue, downstream use or official upstream merge. GitHub Actions on author-controlled repositories are software validation, not third-party research adoption.

## Against independently verifiable ecosystem-ownership exemplars

There is **no official L8/L9 grading standard**; the labels are informal career-planning shorthand. Compare *visible outcomes*, not PR counts:

- **Braindecode official NeuroRVQ continued maintenance:** an independent maintainer authored and merged [#1254](https://github.com/braindecode/braindecode/pull/1254), including multisignal presets and seven hosted checkpoints. The user's 15 Braindecode merges provide stronger external engineering acceptance, but long-run subsystem ownership of a method they themselves invented is not established.
- **ManiSkill core project:** its official benchmark couples released simulation infrastructure and the [RSS 2025 paper](https://github.com/mani-skill/ManiSkill). The user's original PhysX research exists, but no official robotics-method upstream merge or downstream external adoption has yet been evidenced.
- **FlashAttention official line:** [paper + original code + recorded external users](https://github.com/Dao-AILab/flash-attention). That ecosystem-wide original-method adoption is a useful *L9-style outcome comparator*, not proof that some individual has a formally assigned L9 grade.

### External-recognition acceptance gates (do not manufacture)

- **Next engineering win:** a reputable subsystem maintainer accepts one of the already reviewed JAX or ManiSkill PRs. Count it only when merged upstream.
- **Next research win:** a new method defeats strong matched-information/matched-action baselines *on new physical simulations*, with error, cost and uncertainty reported; a promising but insignificant result is not enough.
- **Next ownership win:** at least one non-author user integrates the independently released method or performs an independently chosen new-source reproduction; the full record must be public or reviewable.
- **High impact:** multiple independent groups adopt the idea, and an original accepted paper/software release is sustained across versions. It cannot be achieved by writing a README or synthetic tests alone.
