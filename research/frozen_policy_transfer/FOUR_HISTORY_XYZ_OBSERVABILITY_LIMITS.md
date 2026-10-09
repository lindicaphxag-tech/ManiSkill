# The missing information in a four-history robot controller

*Source-first methodological note · 2026-10-09 · elementary identifiability argument, not a new theorem or physical safety certificate.*

## Observation-set test

A controller that accumulates previously **commanded** native target `M_t` may have a finite set of plausible target histories `H_t` after missed ACKs. Consider a known-delivered native **zero target-delta** probe that yields only before/after public achieved **XYZ** `(x,y)`. Suppose a separately calibrated (but NOT certified in our studies) one-step response model has
`y=x+α(M_h^{XYZ}-x)+e`, `α∈[α_min,α_max]`, `||e||₂≤ε`.

The reachable public observation set for each hypothesis `h` is the closed line segment from `x+α_min(M_h^{XYZ}-x)` to `x+α_max(M_h^{XYZ}-x)`, dilated by an `ε` Euclidean ball. For one observation to identify *any* member of the hypothesis set correctly without a private read **for every physically permitted response**, all these sets must be pairwise disjoint. This is the standard set-membership identifiability condition, not new geometry.

If two such sets intersect, the common public observation can arise under two distinct histories. A deterministic classifier that confidently selects one under that observation necessarily selects the wrong one in at least one consistent physical world. No tuning of the classification threshold can turn that identical observation into physical execution truth.

## Important rotational blind spot

If `h_i != h_j` as six-degree-of-freedom commanded targets but `M_i^{XYZ}=M_j^{XYZ}` while the target **orientations differ**, the model above predicts the **same XYZ observation set** for both. The public XYZ-only measurement cannot distinguish their target rotational memory, independent of measurement precision. More generally, even if position sets differ, lack of an externally validated model relating **target rotation** to achieved XYZ makes unique orientation identification an assumption, not a certificate.

Our 2026-10-09 [pre-outcome four-history PPO study](PPO_PUBLIC_FOURHISTORY_NEW32_PREOUTCOME_V1.json) therefore deliberately refuses public-only belief collapse if hypotheses' target rotations do not agree to within the prespecified `1e-5rad` guard. The guard is **conservative**, and may eliminate virtually all public-only decisions. That result, if observed, is a meaningful negative test of *this* XYZ-only certificate, **not** a proof that public full SE(3) pose, force, joint history or active probing could never help.

## What an improved follow-up MUST measure

Use truly independent calibration and unseen physical tests to bound positional AND rotational response on each robot and task phase. Candidate observables include public achieved EE quaternion, joint encoders and force/torque where present, with honest extra sensing and actuation budgets. Any claimed native-target full-pose inference must be evaluated against **true post-step hidden commanded state strictly for audit**, and with *genuinely executed* policy task success; do not silently use simulator-private controller memory as an input.

Active experiments are only worth dispatching where a pre-action **information-separation benefit** exceeds their physical movement and time cost. When all physically admissible probes leave overlapping response sets, the only source-justified action is to query an authoritative target state or abstain; there is no novelty in calling such a reject rule `certified safety`.

## Primary reviewer comparisons

- **Strong task-gated rule** (PullCube selective geometric query, StackCube fixed t4) that was physically run prospectively on 64 old seeds and matched a fixed-query task-success vector with 56 rather than 64 private reads. Reuse its selection RULE but do not reuse outcomes on new seeds.
- **Same-time forced t4 target query** with known authoritative information rather than a zero-information guessing strawman.
- **Full source actual native-double-fault reach**, including early-stop refusals and two injections physically masked. No task-success advantage is valid if the same fault regime was not encountered.
- **Exact private decision-state reads, public XYZ sample count, additional env.step cost, wrong-confident latent history** and paired actual task completion. Distinguish information access from actuation/recovery efficiency.

A valid negative result informs the next architectural direction: observe full SE(3) (under calibrated response assumptions) or pay for explicit state evidence rather than treating every geometrically valid native command as permission to continue the policy.
