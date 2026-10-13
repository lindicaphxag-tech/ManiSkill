# Independent replication and adversarial refutation checklist: native execution-receipt study

**Purpose:** let an unaffiliated robotics researcher *challenge, reproduce or reject* a narrowly stated study claim before any submission. Reproducing a saved author-run artifact is NOT the same as external laboratory validation. We explicitly invite direct competing implementations and negative results.

## Falsifiable statement — AND WHAT WE DO NOT CLAIM

Under **four** acknowledged histories `00/01/10/11`, a corrupted already-received two-bit ACK at Hamming distance <=1 of actual executed ACK, a public true achieved EE quaternion from native Panda or xArm6 CPU PhysX, and an explicitly declared synthetic SO(3) log-coordinate bounded quantization model, a receiver can avoid extra trusted confirmation precisely when all information-consistent histories require an identical source-valid 6D native target-restoration command. Otherwise a trusted ACK-aware sender replies with the index of the required corrective action. This can reduce the expected **additional trusted REPLY bit** cost relative to always asking for the full 2-bit ACK when a possibly corrupted ACK has **already** been delivered.

**This is standard zero-error functional source coding/feedback—not a new information-theory theorem.** No evidence of physical task completion, real packet security or practical network RTT improvement is claimed. The best *zero-error* oracle with the same model should TIE the source method; improvement over that optimum is mathematically impossible. The Bayes MAP comparator can have an expected wrong correction because it sends 0 new trusted bits and optimizes a different objective.

## Pre-outcome register / exact evidence (immutable IDs)

- [Original prospective JSON](SELECTIVE_CONFIRM_CORRUPT_ACK_PREREG_20261013.json) Git blob `ac2af1cfdfcf1647e52b877014fef546ef5456df`.
- [Primary native PhysX implementation](adversarial_ack_selective_confirmation_physx.py) and [adversarial model/test controls](test_adversarial_ack_selective_confirmation_physx.py).
- [Primary original CPU PhysX dataset/experiment Actions run 38376713806](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38376713806), both native controller shards succeeded; includes full original measured 64 true PhysX EE quaternions and 96 parameter-cell records as Actions artifacts, not fabricated numbers.
- [Independent full original artifact verifier](audit_adversarial_ack_selective_confirmation_physx.py), [audit workflow 38377254009](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38377254009) SUCCESS; no imported original policy/Bayes/feasible-set algorithm into audit.
- [Detailed results and counterclaims](ADVERSARIAL_ACK_PHYSX_PROSPECTIVE_INDEPENDENT_REPORT_20261013.md): 1.69140625 mean saved **additional** verified reply bits (both morphologies), 0 invalid chosen corrections under defined finite support; Bayes MAP has 0.06640625 expected correction error *under assumed distribution*.

## Reproduction commands in an appropriate CPU PhysX host

Clone the original branch and checkout the recorded exact commit; install dependencies compatible with the original successful Actions workflow:

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
git checkout research/adversarial-ack-selective-confirm-20261013
python -m pip install -e . pytest
python -m pytest -q research/test_adversarial_ack_selective_confirmation_physx.py
python -m research.adversarial_ack_selective_confirmation_physx --robot panda
python -m research.adversarial_ack_selective_confirmation_physx --robot xarm6_robotiq
```

Linux CPU runners need native Vulkan/Mesa shared libraries (see exact original `.github/workflows/adversarial-ack-selective-confirm-physx.yml`). Original run used Python 3.11, CPU PhysX and deterministic explicitly registered 8 new reset seeds. To replay source audit, download both original named artifacts into subdirectories `unseen-native-corrupt-ACK-panda/` and `unseen-native-corrupt-ACK-xarm6_robotiq/` and execute `python -m research.audit_adversarial_ack_selective_confirmation_physx --source <dir> --out independent.json`.

## Peer-review tests that could DISPROVE or sharply limit the claim

1. **Public observation stability:** repeat with genuinely heldout reset seeds **and different initial task objects**, unexpected collision impulses, mass/friction variations, and publicly measured sensor calibration rather than Gaussian/box assumptions. Fail if a true executed ACK/history lies outside the declared observation envelope.
2. **Source authority:** eliminate trusted sender; demonstrate honest runtime knowledge of actual consumed controller actions under asynchronous queueing. If not possible, state that receipt construction is circular and no runtime system exists.
3. **Total network cost:** count the initial 2-bit possibly-corrupted receipt, the query request, timestamp/nonce/authentication bytes, actual transport byte padding, p50/p95 round-trip time. A **single reliable 2-bit authenticated ACK** is a vital challenger. If it is available at the same cost, this method may be worse, despite having an apparent 1.691-bit conditional savings in *additional reply payload*. Do NOT claim a net bandwidth gain without this comparison.
4. **Strong control prior art:** compare with model-predictive state estimation, active Bayesian system ID, REMAC (ICLR 2026), PACE and CA3C (October 2026) on actual task outcomes under equal observation, latency and intervention budgets. Do not compare only to naïvely trusting corrupt ACK.
5. **Independent artifact validation:** compute achieved EE quaternions from original PhysX pose fields, recompute graph/correction labels and Bayes MAP, keep all seeds (8 independent reset clusters; the 96 sensor conditions are repeated observations). Any nonfinite pose, changed target source, dropped history or false-safe source action must FAIL.
6. **Science novelty:** source coding and zero-error feedback were published years ago. Identify a new causal system behavior or different proof/algorithm and cite prior art; don't ascribe the coding theorem to this work.
7. **Outside review:** submit exact source, raw SHA/provenance, all failing cases and comparable systems to maintainers or independent academic lab. *Only actual independent reviewer action/adoption constitutes Gate 4.*

## Unresolved doctoral flagship gates

- G1 original executor observability problem: a bounded, source-specific **systems hypothesis**, but no measured real packet corruption or task failure.
- G2 original core algorithm: currently **NO priority theorem**; existing coding and exact query objective.
- G3 independent computed evidence: **YES** for original PhysX states and model-defined guarantees, **NO** for external dataset/task-level advantage or actual trusted-transport cost.
- G4 external academic recognition: **NO**. An author-written independent verifier and self-hosted issue/README are not external acceptance.

**This dossier deliberately makes the method easier to reject under a stronger experiment rather than pre-judging acceptance.**
