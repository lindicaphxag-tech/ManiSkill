# Evidence-Gated Action Authority for Frozen Manipulation Policy Transport
**Research manuscript seed · v0.1 · 2026-10-09**

**Status:** preprint **not submitted**, not peer reviewed; original owner-run
native ManiSkill PhysX studies only. This document presents an experimentally
supported question and honest current boundaries, not proof of high-tier acceptance.

## Abstract (research-draft English, 207 words)

Frozen manipulation policies can change behavior when an achieved-relative
control interface is replaced by an accumulated-target interface: the same
action vector may encode different commanded setpoints depending on hidden
controller history. Missing execution acknowledgments exacerbate this
ambiguity, because the controller's previous target cannot be assumed from
the submitted command alone. We study an **evidence-gated authority** adapter
that propagates possible commanded-target histories, uses a common public
achieved-motion probe to test candidate responses under a fixed historical
model envelope, and accesses the controller's privileged target state only
when the public evidence is ambiguous or inconsistent. On two unchanged
third-party PPO policies in native ManiSkill PhysX, a prospectively specified
32-condition task-by-execution-truth study yielded **identical paired task
outcomes** for conditional versus mandatory target readback (27 successes,
five failures for both), while reducing privileged reads from **32 to 11**.
Among 21 public-only unique history decisions, no false confident decision
was observed in this cohort. Important falsification controls reveal why
unconditional inference is insufficient: an uncalibrated public-motion
nearest-target heuristic assigned 15 of 32 histories incorrectly, and the
empirically calibrated response envelope excluded the true history in one
separate held-out condition. These results establish a reproducible
information-cost/task-outcome trade-off under controlled simulator conditions,
**not** a general physical-state certification, task-safety guarantee,
statistically proven equivalence, or demonstrated hardware deployment.

## What the central *mechanism* actually adds

**Do not claim first-ever action-space adaptation, active probing,
set-membership inference or belief-space safe control.** All of those have
precedents. The focal integration is more precise: a frozen pretrained policy
migrates across two known native controller *target memory semantics*, with
uncertainty over **which physical command was actually executed** after an
unacknowledged step. Public achieved pose may sometimes justify a unique
history, but an empirical dynamics error envelope can be wrong; therefore
authorization explicitly distinguishes **one plausible history**, **multiple
plausible histories** and **no history consistent with the model**.

Formally, given current achieved robot position `x`, observed post-probe
position `y`, histories `h ∈ {held, applied}` and history-specific commanded
targets `M_h`, the pilot model computes

`r_h = min_{alpha in [0,1]} ||y - x - alpha(M_h - x)||_2`.

With each task's *historically learned, non-certified* tolerance `eps_task`,
if exactly one history has `r_h <= eps_task`, continue with that
history. If zero or two histories satisfy the condition, perform **one**
privileged controller target read and resynchronize before proceeding.
This simple geometric test is not a new mathematical theorem.

## Currently reproducible evidence

| Frozen owner-run actual PhysX experiment | Exact observations | Claim boundary |
|---|---|---|
| Basic uncalibrated one-probe public nearest-target | 15/32 **wrong confident** hidden histories, task success 19/32 | Task success does not certify state inference |
| Historical-error-envelope, separate prospective 32-state study | 24/32 unique public decisions, zero observed wrong; **one model-invalid true history**; task success 22/32 | Model envelope is not physically certified |
| **Evidence-gated unique-public-or-query new 32-state study** | **27/32** hybrid and **27/32** compulsory query (exactly paired success/failure); **11 versus 32** privileged reads; **21** unique public-only decisions, zero observed wrong | Specific simulated tasks/controllers, not a population equivalence theorem |

All distinct experiment sources have different reset-seed cohorts, but each
task reset seed is deliberately reused across *two* actual execution truths
to produce paired contrasts. Do not count those as different independently
trained policies. The experiments use only two separately published frozen
PPO task policies on **one Panda target-controller family**.

Primary original [eight genuine PhysX shards and failed auditor](
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833095443),
followed by [GREEN corrected source-only original-denominator auditor](
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833936506)
and [permanent untouched JSON evidence](./evidence/observability_gated_query_fresh32/).
The former audit's Python shadowed-variable bug was corrected in the
separate auditor; physics source/results/controller/thresholds were not modified.
The original negative and response-envelope falsifier sources are in
[public-response-negative](./evidence/public_response_ack_probe_32_negative/)
and [empirical-response-32](./evidence/empirical_public_response_new32/).

## Related work and differentiation to review carefully

- [ActionShift](https://github.com/Archerkattri/actionshift) already studies
  belief/probe/learned adaptation of *hidden action-interface contracts*,
  including target semantics and actuation lag, with frozen pretrained
  ManiSkill backbones. We need **direct same-conditions empirical comparison**
  before claiming our controller-specific authority procedure is better.
- [SPACE (2026)](https://arxiv.org/abs/2606.24049) uses Cartesian state
  delta and an action adapter for cross-robot representation/dynamics transfer.
  Our unresolved issue is *commanded-target memory provenance under ACK
  ambiguity*, which is narrower than general embodiment transfer.
- [TempoWAM (2026)](https://arxiv.org/abs/2608.09492) studies adaptive
  replanning based on estimated progress. Our observed cost is instead
  *privileged controller-memory queries*, not WAM forward passes.

### Non-negotiable additional experiments before a strong journal/conference claim

1. Real physical or at least materially different robot/controller families,
   with independently attested sensor/frame and response model bounds.
2. Equal-information-budget comparators (fixed/random 11-read allocations,
   learned public-state observer, external original ActionShift adaptation).
3. Contact-stage failure localization, varied gains/control frequencies,
   domain-shift uncertainty, delayed/reordered/physically dropped packets.
4. Independently authored reproduction and statistical confidence intervals
   at **seed-block/task level** (not treating matched fault truths as independent).
5. A publicly available task-independent library API with well-defined
   refuse/authorize/query contracts and independent implementation tests.

**We do not yet have this evidence, and we will not represent this v0.1 as
an accepted ICRA paper, a formal safety certificate or a third-party merge.**
