# Controller-Memory Recoverability: operator contract and upstream readiness gate
**2026-10-10 | research-only software contract; no claim of improved task success.**

## Why this belongs in a robotics API rather than a classifier notebook

A source policy running `pd_ee_target_delta_pose` issues relative commands against the *stored native target*, not necessarily the publicly achieved EE pose. After unknown ACKs, one public physical state can correspond to multiple hidden native target histories. A controller API therefore needs to distinguish **four different kinds of intervention**:

| Operation | Hidden native target changes? | Epistemic support changes? | Authority required |
| --- | --- | --- | --- |
| Known-delivered native relative command | yes; same group transform of every supported history | no contraction from action alone | verified chart and delivery |
| Public EE pose observation | no controller-memory write | only with a calibrated action-conditional likelihood | public observation provenance |
| Trusted native target read | no | collapses after actual source getter | explicit privileged getter |
| Privileged target write from achieved pose | yes, *non-injective* setter | collapses only after setter success | separate privileged setter and audit |

**The write path is a simulator-internal ability, NOT a zero-cost or standard physical robot command.** A target-position write does not establish IK feasibility, contact safety, or task success.

## Controller-memory non-contraction result

For the verified root translation and root-left SO(3) action chart, the *same known-delivered* relative command transports each candidate native target as
`(p_i,R_i) -> (p_i + d, R_delta R_i)`.
Therefore its translation L-infinity diameter and SO(3) geodesic diameter are invariant. A finite sequence of common relative actions cannot reduce the latent memory spread; **a probe can reduce uncertainty only via its action-specific observation likelihood, not via commanded-target transport itself**. This elementary group-action fact is a required negative feasibility certificate, NOT a new theorem.

The existing `research/native_memory_funnel_certificate.py` adds an exact bounded-translation minimax goal-error lower bound, plus a universal half-rotation-diameter lower bound. `research/native_memory_recoverability.py` makes the distinct privileges/capabilities executable as fail-closed typed effects. They serve different purposes: feasibility vs epistemic/physical semantics.

## Actual development experiment versus scientific claims

The separately frozen 8-reset, 32 correlated ACK-condition development pilot uses the new `fault_reanchor_public_achieved_target` operator in actual CPU PhysX. Before the t4 known-delivered ZERO motion, it writes the **public achieved** EE pose to simulator-native `set_state({"target_pose": ...})`; it audits after the real physics API call and charges one privileged native target write. Original/source ZERO and trusted-getter arms are paired on the same reset and ACK truth. This is **a privileged-write oracle/control primitive**, not a deployable free repair.

- Independent before-fault source PPO, reset, fault and action prefixes must match; a hidden target read cannot control the new intervention.
- Every task result and privileged read/write must be counted, even if the reanchor harms success.
- Baseline original X-vs-ZERO 2,560-controller-world study is never relabeled as fresh success.
- Original pilot source and full SHA manifest audit are in `research/audit_native_reanchor_dev_physx.py` and `.github/workflows/native-reanchor-dev-physx.yml`. **Check their actual GitHub run conclusions before claiming a single physical pilot result.**

## Gates to a genuinely transferable top-paper + upstream feature

**A. Correctness/portability:** expose a typed/native memory interface independent of training policy. Test frame, normalization, relative action delivery, read vs write, reset, stale ACKs, SO(3), and simulator version changes. A maintained upstream PR must not silently re-purpose `set_state` as an online hardware-safe action.

**B. Prospective original task recovery:** after development, freeze source and choose completely new reset clusters. Require improvement on *both-fail* original action conditions, rather than profiting from a ZERO/X hindsight selection. Compare against ZERO, getter, original A/B/C, proper active methods and constrained belief planning under identical sensing plus explicit privilege accounting. Report full task success, false complete native SE(3) authority, extra actions, getter/write costs and contacts where instrumented. Use reset-cluster inference.

**C. External adoption:** maintainer review, independent non-author rerun, documented public API, regression tests in source repository, and at least one downstream use (e.g. LeRobot action conversion or another controller). Number of PRs and author's own CI jobs do not measure adoption.

**D. Novelty:** the mathematical invariant, exact finite POMDP, split-conformal and DeepSets are established mechanisms. Novelty (if achieved) must lie in **learned intervention validity + controller-native memory recovery as an executable decision across unknown ACKs and tasks**, producing task gains that survive strong comparators and shift.

## Open-source tier evidence

Braindecode upstream **NeuroRVQ #1218 (merged 2026-10-06)** includes maintainer-run NeuralBench replication and formal review; standalone **NeuroRVQTokenizer #1223 (merged 2026-10-08)** contains independent implementation/parity and upstream merge. Retired superseded #1222 was closed without merging. Treat those as *verified adoption* and this ManiSkill branch as *research development*, not an accepted robotics PR.

The next meaningful contribution is one independently replayable controller ABI test suite adopted in upstream — not another large pile of unrelated draft PRs.
