# Frozen cross-policy adjudication

The Diffusion PushT and VQ-BeT PushT probes intentionally use the same physical
support chart, state restoration protocol, reset seed, perturbation magnitudes,
held-out disturbance, and physical support metric.

The adjudicator refuses comparison if any frozen field differs.

When both reports are complete it emits:

- DEC signature distance at the first action step;
- relative distance between fresh held-out action responses;
- whether robust CRG decisions agree;
- whether both policy families pass the repeated-probe DEC stability gate.

This two-policy artifact is **descriptive evidence only**. It does not replace
the preregistered 20-pair prospective gate in `cross_policy_dec_gate.py`.

The purpose is to prevent a common failure mode in cross-model papers: silently
comparing two policies that were probed under different state, metric, support,
or held-out intervention definitions.
