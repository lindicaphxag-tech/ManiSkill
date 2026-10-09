# Epoch-fenced repair authority: exact source, synthetic attack table and external review gates

**Research engineering result, 10 Oct 2026. Not a new general distributed-systems fencing theorem, not robot hardware safety, not physically tested read freshness, not a manuscript accepted by a journal.**

## What changed

[Source](epoch_fenced_repair_authority.py) composes the [finite effect-aware repair decision certificate](effect_aware_authority_certificate.py) with a **single in-flight, command-epoch-fenced action/read adapter**. The legacy convenience API trusted a caller-supplied fresh=True boolean: without an independent version check, a stale correct-looking read can authorize a repair. The new adapter binds a read to a single local session/ticket/command-epoch and requires the return's observed epoch to agree; a stale/replayed/late read halts instead of reauthorizing. Known-delivered probes advance the epoch, unknown ACKs halt, and outside-the-model public observations halt.

These rules protect against accidental misuse ONLY WHEN the adapter owns every command and a trusted controller boundary provides the command epoch and actual delivery status. Ticket numbers and booleans are not cryptographic attestations; bypassing the adapter or having a malicious lower-level component voids the claimed conditional guarantee.

## Source-only tests actually executed

[First feature suite CI #37995548607](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37995548607): six OS/Python combinations, each 11 targeted stale ACK/read tests plus 10 inherited model effect/optimality tests; all successful.

[Fixed 512-case synthetic attack suite CI #37995714107](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37995714107): six OS/Python combinations, exact deterministic seed 20261010, source-only (no installed physics or GPU), all successful:

| Construction | Legacy convenience API with unverified fresh=True | Version-fenced adapter |
|---|---:|---:|
| 256 constructed stale read returns | 256/256 incorrectly accepted as fresh | **256/256 halt** |
| 256 actually current read returns | 256/256 correctly routed | **256/256 correctly routed** |
| 256 known probe commands with ACK not confirmed | baseline not evaluated in this suite | **256/256 halt** |

**These are constructed synthetic fixtures, not measured stochastic rates or manipulation-task successes.** The unfenced convenience API intentionally lacks any epoch check; a fair competitive alternative is a correct hand-written epoch-fenced adapter, ROS2 controller state versioning, or controller-provided authenticated sequence counter. Those strong controls have NOT been run. The 512 trials are not IID user or robot tasks and the 6 CI platforms do not make this an external replication.

## Mathematical and systems boundary

Conditional claim: given finite complete probe/read response and repair successor supports, verified model digest, and an honest session-local single-dispatch adapter, an authorization can only follow an observation sequence that matches the certified decision path and, for reads, matches the current command epoch. The underlying finite model assumes atomic/fresh read semantics. It cannot guarantee anything about undetected external hardware commands or forged controller reports. A bona fide independently validated robot protocol requires provenance and monotonicity across the real execution boundary, not a Python bool supplied by the caller.

## Prior art and peer-review positioning

- [Kim et al., Realizable Continuous-Space Shields for Safe Reinforcement Learning (L4DC 2025)](https://proceedings.mlr.press/v283/kim25c.html): safety-realizability in continuous state/action domains, stronger than our finite supported-model guarantee.
- [Recovery-based Shielding with GP Dynamics (AAMAS 2026)](https://doi.org/10.65109/EAHU8566): continuous nonlinear unknown dynamics/uncertainty and empirical safety/performance, which this source-only study does not reproduce.
- [RA-L author guidelines](https://www.ieee-ras.org/publications/ra-l/ra-l-information-for-authors/): open submissions, six months to final accept/reject, rigorous original robotics novelty, and a short 6-page format.
- [Robotics and Autonomous Systems official journal](https://www.sciencedirect.com/journal/robotics-and-autonomous-systems): module-level robotics experiments can fit, but source-only protocol tests are insufficient evidence of robot control utility.
- [Journal of Intelligent & Robotic Systems](https://link.springer.com/journal/10846): relevant robotics engineering scope, but a reported median **12 days to first decision** is NOT a 12-day acceptance promise and the journal is fully OA.

## New target for an L8-style method rather than 'more green CI'

1. Externally specified and valid lower-layer read epoch proof — e.g. verifiable controller command counter included in readback, detected out-of-band robot commands, stale/replayed packets injected under physical action. Audit complete pre/post target quaternion and achieved pose, not only an approximate controller error.
2. Fair **nontrivial** baselines: correct analytic epoch-fenced repair (not legacy intentionally insecure bool API); correct action-aware inverse; authoritative read; task-competent learned policy; same public sensing, actuation, and synchronization cost.
3. Prospective physical task studies with genuinely independent robot/reset groups, multiple controller families, task success, false authorization, wrong repair, recovery latency, getter counts, probe costs, unsafe contacts and confidence bounds. Publish negative results.
4. Open a genuine maintainable upstream feature / request for independent use only after feature/API design fits the maintainer's scope; an author fork's merged PR or CI is not external adoption.

**Current distinction:** Stronger verifiable software artifact; zero new externally confirmed merges and zero independent adoption resulting from this branch. A publisher's editorial acceptance cannot be inferred from synthetic test success.
