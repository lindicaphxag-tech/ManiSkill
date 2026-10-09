# L7 → L8/L9 outcome-driven research & external-adoption dossier (10 October 2026)

**This is an evidence map, not an official ranking of people.** "L7–L9" are private shorthand and have no standardized academic meaning. Do not convert GitHub merged PR counts or CI pass rates into a paper acceptance probability.

## Attributed facts versus not-yet-confirmed recognition

- **27 genuinely merged external upstream pull requests** across [Braindecode](https://github.com/braindecode/braindecode) (15), [MOABB](https://github.com/NeuroTechX/moabb) (9), [JAX](https://github.com/jax-ml/jax) (2), and [Ray](https://github.com/ray-project/ray) (1), verified from user-authored upstream status on 2026-10-10. Prior/current pending upstream #41227 / #41228 remain **open**, not merged.
- BCI official upstream model work is accepted engineering contribution. A later [Braindecode maintainer #1254](https://github.com/braindecode/braindecode/pull/1254) independently extends NeuroRVQ ecosystem support, but it does **not** establish that this user originally invented NeuroRVQ or serves as that subsystem's project maintainer.
- Our **original** 1,280-world prospective ManiSkill physical arm comparison showed **A/B success 109/128 each, 94 versus 98 getter calls**, paired whole-reset exact sign-flip p≈0.289. Weak advantage; do not claim established superiority.
- Our **original** 192-world Panda/xArm6 known-delivered probe experiment showed **zero/X/Y each 32/32 ACK recognition cases** and no incremental nonzero-probe benefit. Only 16 independent new reset seeds, not 96.
- The new finite dynamic and effect-aware planner/checker [source](effect_aware_authority_certificate.py) is a **model-only artifact**: correctness under supplied finite transition supports, repair outcomes, assumed getter observation sets, fresh atomic reads and abstract costs; 6/6 OS/Python CI. Synthetic optimality is checked per concrete contract by an independent Bellman oracle with a bounded resource gate.
- [New anchored full-SE3 Panda/xArm6 experiment](PHYSX_ANCHOR_REPAIR_FIRST128_PREOUTCOME_V1.json) is *prospectively preregistered*. Its run cannot be counted before the **entire** original four-shard PhysX and post-hoc source audit complete. Comparison controls actual known ACK history to isolate intervention-conditioned repair semantics; it is **not an online belief adaptation or task-success experiment**.
- No confirmed independent downstream use of this original repair-authority engine, official ManiSkill feature merge, real robot safety proof, or accepted top-conference method paper.

## Established external comparators and our precise scientific delta

| Established original work (specific verifiable public claim) | What it already proves/delivers | Why current author work does NOT match it yet |
|---|---|---|
| [Safe Reinforcement Learning via Shielding (AAAI 2018)](https://ojs.aaai.org/index.php/AAAI/article/view/11797) | Reactive shields enforce specified temporal logic safety requirements under formal assumptions, backed by published demonstrations | Our model-only repair postcondition checks are not novel safety shielding; no verified physical controller transition completeness or temporal specification |
| [Safe Reinforcement Learning via Formal Methods (AAAI 2018)](https://ojs.aaai.org/index.php/AAAI/article/view/12107) | Explores runtime monitors and the importance of reality matching verified models | Our model mismatch handling is an implementation prototype without new real system invariants or robustness guarantee |
| [Safe Policy Improvement for POMDPs via Finite-State Controllers (AAAI 2023)](https://ojs.aaai.org/index.php/AAAI/article/view/26763) | Existing research on partially observed finite-state policies and reliable improvement | Our finite belief-state Bellman recursion must not be claimed as novel general POMDP planning |
| [ManiSkill3 official software and RSS 2025 paper](https://github.com/mani-skill/ManiSkill) | Real cross-robot platform, benchmark tasks, reproducible interfaces, trained policies and a paper other teams can build upon | We have validated scripted Panda/xArm6 controller behaviors; no integrated and externally adopted submodule or learned-policy task-level generalization |
| [PyTorch accelerated scaled-dot-product attention integrations](https://pytorch.org/blog/out-of-the-box-acceleration/) | Official PyTorch documentation acknowledges leveraging FlashAttention-style fused kernels in a widely deployed API | Our proposed intervention-aware recovery engine has no independent upstream embedding or broad downstream usage of this kind |

### Impact tiers (not nominal scores assigned to researchers)

- **L7-style evidence:** repeated successful complex upstream integration, maintainer-acknowledged corrections, exact source testing, reviewer-readable original research packages.
- **L8-style evidence:** one *original, clearly differentiated* method accepted after independent quantitative counterfactuals plus at least one unaffiliated independently executed downstream integration/reproduction; continued maintenance through a release cycle.
- **L9-style evidence:** a paradigm-level technical idea, major independent academic review and repeated ecosystem-wide adoption across projects, with sustained ownership. An author-side CI or synthetic benchmark cannot satisfy this.

## What changed on this branch (the non-cosmetic part)

The earlier transition-aware prototype correctly models the probe-induced state change, but its independent **policy soundness checker alone did not prove global optimality**, and it assumed a private getter was a perfect full-state oracle. In [effect_aware_authority_certificate.py](effect_aware_authority_certificate.py):

1. Repairs are **real modeled actions with nondeterministic successor sets**: permission requires every possible successor from every feasible state to lie in the modeled goal set, not merely the same text repair label.
2. A privileged read returns a possibly **aliased observation**, not assumed full state identity. Read newness/atomicity is an explicit modeled precondition; runtime fresh-epoch evidence is required before authorization based on its response.
3. Safe-stop is explicit. The optimizer may choose to **halt** instead of inventing authority when no warranted information or repair exists.
4. Proof is decomposed into a fully enumerated **soundness checker** and a separate finite-state **global Bellman optimality checker**, rejecting a deliberately *sound but strictly suboptimal* malicious certificate. Neither verifier trusts the synthesizer's optimization assertion.
5. Adversarial tests include incomplete read observations, stale getter provenance, missing repair postconditions, hidden forbidden states, and 80 deterministic randomized small contract comparisons. [CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37992750950) passed on Linux/Windows/macOS with Python 3.11 and 3.13 (6/6).

No guarantee extends beyond the supplied physical state/response/repair model; the caller-supplied freshness boolean is NOT intrinsically authenticated by Python code, and unknown events still may already have caused irreversible physical harm. We do not call this a certified robot safety shield.

## Three nonnegotiable external-impact gates

**Gate A — decisive real-robotics scientific effect.** A prospective new-world trial on genuinely ambiguous or repair-changing controller conditions. Include passive scorer B0.60, zero action, fixed norm-matched probe, intervention-aware repair with correct budget, and authoritative getter. Same source initial state/prefix, complete hidden-truth factorial, explicit task success, correct repair, unsafe contact, elapsed time and action/sensing/read cost. Preserve negative results, unavailable contracts and injection failures.

**Gate B — independent reproduction.** Release a small standalone package with exact original source hash, input dataset manifest and a script that reruns from new reviewer-selected seeds. Ask another person/team to choose their own initial conditions, execute their own physics, and document discrepancies (including failure). Author-controlled six-platform CI does not count.

**Gate C — official and sustained technical adoption.** Take one genuinely generalizable correctness mechanism into appropriate upstream, respond to maintainer review and obtain an upstream **merged** record. Continue to maintain that same subsystem. Do not open unrelated tiny PRs just to raise a total.

## High-risk contradiction checklist for all future papers

- No "proved safe real robot": the model transition/getter envelopes are not independently complete.
- No "proof-carrying optimal" without independent global comparison: local path/cost consistency is weaker.
- No "no private access": the anchored PhysX trial inspects private target states post-step for **audit**, but they are not fed into either repair strategy; its oracle-supplied ACK truth means this is not belief inference.
- No "128 independent tasks": one registered initial robot/seed contributes eight correlated conditions. The independent reset unit is 16.
- No "probabilistically certified error <5%" from the eight-reset per-robot calibration; fail-closed calibration sample-size checks in earlier research require ≥39 additional independent residual groups for a finite two-history 95% Bonferroni conformal threshold *after freezing the selector*.
- No "original POMDP method", "FlashAttention-level ecosystem adoption", "official ManiSkill merge", or "paper accepted" without public primary-source proof.

**Honest state:** materially stronger system contract prototype + genuine author-operated source evidence, still **L7**, not yet independently adopted L8/L9.
