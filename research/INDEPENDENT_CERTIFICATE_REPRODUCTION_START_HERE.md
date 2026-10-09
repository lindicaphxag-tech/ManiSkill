# Independent challenge quickstart: effect-aware controller repair authority

**Research prototype; no GPU, physics engine or third-party accounts required.**

This package is hosted inside the public [ManiSkill fork](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/repair-effect-observability-certificate-20261010), but the following **certificate verification is Python-standard-library only**. A successful check means the decision is correct under the *supplied finite state/response/repair model*, **not** that a real controller is safe or the model is complete.

## Three reproducible commands

Clone the **specific research branch**, not the upstream default:

```bash
git clone --single-branch --branch research/repair-effect-observability-certificate-20261010 \
  https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill

python -m unittest discover -s tests -p 'test_effect_aware_authority_certificate.py' -v
python -m unittest discover -s tests -p 'test_repair_authority_cli.py' -v
```

Generate and independently check one certificate:

```bash
python -m research.repair_authority_cli --mode synthesize \
 --contract research/fixtures/authority_cheap_discriminating_probe.json \
 --output generated_certificate.json

python -m research.repair_authority_cli --mode verify \
 --contract research/fixtures/authority_cheap_discriminating_probe.json \
 --certificate generated_certificate.json
```

Additional fixtures:

| Fixture | Valid model-only first action | Reason |
|---|---|---|
| [Aliased private read](fixtures/authority_aliased_getter.json) | HALT | Getter returns the SAME public symbol for states requiring opposite repair effects |
| [Fresh discriminating read](fixtures/authority_fresh_complete_getter.json) | READ | An assumed atomic, fresh getter can distinguish and justify safe repair actions |
| [Cheap distinguishing probe](fixtures/authority_cheap_discriminating_probe.json) | PROBE | A complete, nonforbidden modeled probe permits goal-certified post-action repair at lower abstract cost |

All six combinations of Ubuntu/macOS/Windows and Python 3.11/3.13 passed in [the exact source-only JSON CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37993610557). An earlier initial CI failed on Windows due an invalid hard-coded Unix /tmp path; it remains visible and is **not** counted as a passing run.

## Call for truly independent counterexamples

You are encouraged to construct your own finite JSON model and a policy whose **true worst-case abstract cost** is below the generated tree, or produce a certificate incorrectly accepted despite an unsafe possible repair effect. Include exact commit SHA, altered JSON fixture, command output and expected versus actual behavior.

A high-value *physical* counterexample instead invalidates the assumptions:

- the true controller state falls outside the modeled belief;
- a probe has a transition absent from its declared support;
- the privileged getter reports a stale controller epoch;
- a repair action nominally labeled safe can reach an unmodeled unsafe state;
- actual actuation and sensing cost defeat the abstract integer ranking.

**The solver cannot authenticate a caller-provided fresh-epoch boolean.** A hardware/system adapter must validate the getter epoch outside this Python code; do not use synthetic tests as a machine safety certification.

The fork's GitHub Issues are currently disabled, so reproducibility feedback can be shared by a pull request against the experimental branch if GitHub permits it, or through an existing independent research contact. Do not classify a comment, author's invitation, or CI rerun as proof of outside-lab adoption. A true adoption claim needs a separately authored, verifiable execution or integration.

## Relevance of true robot physics

There are two earlier author-operated PhysX datasets:

- [1,280-world frozen PPO A/B/C strong-score comparator](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/reviewer-audit-strong060-20261010/research/frozen_policy_transfer/PROSPECTIVE_STRONG060_FLAGSHIP_RESULTS_20261010.md): A/B both 109/128 task successes, four getter saves with exact whole-reset p=0.289. No significant method dominance.
- [192-world Panda/xArm6 low-signal zero/X/Y](https://github.com/lindicaphxag-tech/ManiSkill/blob/evidence/low-signal-first192-permanent-20261010/research/frozen_policy_transfer/LOW_SIGNAL_ACTIVE_PROBE_FALSIFICATION_FIRST192_20261010.md): all three probes get 32/32 correct ACK histories; no benefit of additional nonzero actuation.

[New prospective 128-world fixed-anchor SE3 transition protocol](PHYSX_ANCHOR_REPAIR_FIRST128_PREOUTCOME_V1.json) uses separate new seeds, explicitly **oracle known ACK histories**, and examines whether a known-delivered native rotational probe changes the full-SE3 repair needed to restore a fixed preprobe target. This is a *narrow repair-semantics falsifier*, not an online ACK detector. The first four physics shards are complete; the first run's summary job failed due missing gymnasium in the auditor. A separately sourced first-run recovery/archive is necessary before any finalized numerical report.

## Prior art and why this is not a claim of original POMDP algorithm

- [Alshiekh et al., AAAI 2018, Safe Reinforcement Learning via Shielding](https://ojs.aaai.org/index.php/AAAI/article/view/11797).
- [Fulton & Platzer, AAAI 2018, Safe RL via Formal Methods](https://ojs.aaai.org/index.php/AAAI/article/view/12107).
- [Simão et al., AAAI 2023, Safe Policy Improvement for POMDPs via Finite-State Controllers](https://ojs.aaai.org/index.php/AAAI/article/view/26763).

Finite belief-space dynamic programming and runtime shielding are known. A publishable method contribution would need verified controller transition/getter semantics, a substantively different theorem or genuinely strong prospective task-level results, and comparison with the strongest existing shielding/active-adaptation implementations.

This document is a **reproducibility invitation**, not proof of external adoption.
