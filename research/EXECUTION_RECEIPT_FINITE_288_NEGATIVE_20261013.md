# Execution-history receipt coding with noisy quantized state: preregistered NEGATIVE research gate

**Date:** 2026-10-13. Public original source and three independent operating-system executions. Neither native ManiSkill/PhysX control task nor real-world robot execution is claimed by this finite mathematical study.

## Discovered systems question and theory priority

Earlier real ManiSkill CPU PhysX tests falsified our source-chart SO(3) superiority hypothesis against a command-variant-aware reset reference. New separate question: when ACK execution history is hidden from the future controller but a trusted sender can provide a short execution receipt, how many bits are **necessary and sufficient to determine a safe exact next correction** given bounded and quantized public end-effector state observation?

The answer for **the registered finite, bounded-noise model** is the chromatic number of the zero-error functional computation confusability graph. For histories h, k, put an edge if their possible sensor observations share a value but their required corrective anchor differs. A correct fixed-length acknowledgment code is a proper coloring. Thus, minimum bits = ceil(log2 χ(G)). The mathematical graph-coding principle is **existing prior art**, not a first-original information-theory theorem. See [Orlitsky–Roche functional compression and later graph-coloring study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11049120/).

This is an **application-specific computational prototype only**. The encoder must reliably know actual executed ACK history, and the bounded sensor-noise support must be correct. Neither holds automatically on real hardware.

## Exact precommitted protocol

- [Original frozen protocol with Git blob b0acaad...](EXECUTION_RECEIPT_FINITE_PREREG_20261013.json), authored before first execution.
- 2 illustrative manipulator charts, Panda-like / xArm6-like (NOT their physically simulated articulation); ACK history lengths H=3 and H=4, 12 independent seeded finite controller action templates, three fixed observation quantizations, and two finite sensor noise supports = **288 registered conditions**. 3/4-step histories give 8/16 distinct latent source statuses per condition.
- An exact DSATUR chromatic minimizer gives minimum fixed-length receipt bits. Strong baselines: full 3/4-bit trusted ACK receipt (guaranteed safe), the **optimal posterior MAP action** from public quantized sensor value alone (uses the exact public generative model), bitcount receipt with identical observation side information, and a greedy proper graph-coloring baseline. Exhaustively verify every actually feasible history/observation pair, not just a random rollout.
- Original preregistered success gate: at least **144/288** cases save >=25% of full trusted ACK bits; all permitted observations must decode without any unsafe alias. NO modification to seed/resolution/noise/history definitions after results.
- No actual PhysX episode success, contact safety, collision recovery, RoboTwin, PACE, full robot middleware bandwidth gain, model-free VLA or physical ACK network test was conducted in this finite prototype.

## Three operating systems and independently reconstructed exact source

- [Full original 3-OS source CI: SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38362714720), 296 original test cases **per OS**, including independent enumeration of all H=3 8-state graph partitions, explicit confusion cases, Bayes-vs-count control and all 288 recorded observations.
- An earlier run [38362569064](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38362569064) failed **after** passing 296/296 focused tests, because the result executor read a registered nested key from the JSON root. Fixed the code to use the **unchanged original frozen plan**. No registered condition or outcome was changed.
- [Independent all-288 exact chromatic source audit: SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363149395). Separate auditor does not import main coding or graph construction: reconstructs each of the 288 graphs and Bayes no-receipt optimal decision from the saved original model and source steps, independently proves none admits a smaller number of colors, and checks all three OS original JSON artifacts agree after canonical JSON normalization. One first audit failed solely by comparing Windows CRLF bytes against Unix LF; corrected auditor **canonicalizes parsed JSON** while retaining all recorded original data and precommitted success condition.

## Fully audited NEGATIVE outcome

| Registered model group | Cases | Cases >=25% bit savings | Mean actual bits saved vs full ACK |
|---|---:|---:|---:|
| Panda-like finite controller | 144 | **41** | 0.30556 bits |
| xArm6-like finite controller | 144 | **70** | 0.64583 bits |
| **All finite conditions** | **288** | **111** | **0.47569 bits** |

- **111/288 = 38.54%**, below the **144/288 = 50%** study goal.
- The exact minimum-receipt tag plus available sensor observation had **0 alias errors across all registered true histories and supported observations**. This is an exact finite coding result, not a real-hardware reliability bound.
- Pure **no-receipt MAP** benchmark has mean correct-anchor accuracy ~0.27344 in the Panda-like group and ~0.33268 in the xArm6-like group, under the **registered uniform hidden-state and observation-bin model**. These are deliberately idealized source/observation distributions, not observed robot failure rates.
- The receipt codec was mathematically bit-optimal **under the specified graph and fixed-length coding problem**; hence higher savings cannot be achieved within this registered specification without changing the observation model or permitting errors. This is the important *information boundary*, but the underlying theorem is known information theory.

**Decision:** the precommitted positive research gate **FAILED**, so this is not a demonstrated breakthrough robotics communication method. Report its null finding. Its exact lower bound is useful for deciding when additional execution telemetry is genuinely indispensable; the next significant step is measuring actual robot internal control state, quantized sensing, ACK receipt cost and task-level recovery in **new native PhysX/other robot tasks** with prior strong Bayesian planning/control comparators. This finite toy should not be sold as two different hardware morphologies tested.

## Originality, strongest competitors and third-party recognition

- Zero-error functional source coding, characteristic graphs, exact coloring and Bayesian MAP with receiver side information were already known. No mathematically novel theorem is claimed; the compiled model is an engineering application.
- [PACE 2026](https://arxiv.org/abs/2606.00537) adapts action-chunk execution horizon and reports actual bimanual/single-arm robot success. Any future physical execution policy must compare with such validated alternatives and consider observation cost.
- An important physical state counterexample or actual native PhysX task-level win has NOT yet been produced by this receipt proposal.
- No external robotics maintainer approved or merged this new research branch. Three-OS success and separate author-written audit are not independent outside laboratory scientific acceptance.

**Conclusion:** a correct, fully reproduced **negative** finite information-cost study. Under the research ethics gate, preserve evidence, withdraw precommitted superiority and only restart after a distinct, experimentally justified, prospectively frozen native-robot challenge.
