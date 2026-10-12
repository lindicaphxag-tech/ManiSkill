# Completed original native PhysX ACK-probe pilot: 48/48 physical worlds

**2026-10-13 — Frozen NEGATIVE original result, NOT policy success or safety proof.**

**Pre-outcome protocol:** `research/ACK_ACTIVE_NATIVE_PROBE_PILOT_PREREG_20261013.json`; immutable Git blob `6f97dccaa4740039019db0726e21ea0a970a1fa3`. Two robot bodies (Panda and xArm6 Robotiq), each with four original reset seeds, two real applied/held ACK interventions and three physically stepped fixed native zero/X/Y probes = **8 independent reset clusters × 6 conditions = 48 native PhysX worlds**. Source target recurrence checked after each true step without leaking privileged target to a decision.

**[Complete original physics + source-audit run #38294905276](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276)**: both [Panda](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/job/114963533901) and [xArm6](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/job/114963534044) executed all 24 registered physical worlds; the [independent complete 48-world JSON auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/job/114964707313) passed. **All three jobs green.** [Combined raw 48-world JSONs, native logs and full audit artifact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/artifacts/11768196287). Robot originals: [Panda](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/artifacts/11768910515) and [xArm6](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294905276/artifacts/11767771704).

First run [#38294457476](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294457476) completed Panda 24, but xArm6 failed BEFORE PHYSICS due an interactive URDF asset-download prompt. Infrastructure-only `MS_SKIP_ASSET_DOWNLOAD_PROMPT=1` fixed the second run; **replayed Panda seeds are NOT counted as new independent states**. The protocol, probe amplitudes and evaluation threshold did not change. [Original partial first-run evidence](ACK_NATIVE_PANDA_PARTIAL_FIRST_RUN_20261013.md).

## All paired raw-response outcomes (four reset clusters per robot)

Each gap is the Euclidean public post-probe XYZ difference between separately, actually executed applied/held worlds on the same original seed and same fixed probe; units **mm**.

| Robot | Zero gap | Native +0.15 X | Native +0.15 Y | X minus zero | Y minus zero |
|---|---:|---:|---:|---:|---:|
| Panda | 1.927986 | 1.948926 | 1.925648 | +0.020940 | −0.002337 |
| xArm6 Robotiq | 2.098340 | 2.117779 | 2.107098 | +0.019439 | +0.008758 |

The original freeze demanded **≥5 mm** of response-gap improvement on **≥3/4 reset states on BOTH robots** for a SINGLE fixed probe to justify an independently calibrated follow-up. Independent auditor records **0/4 for every robot/probe**. The gate **FAILED**; no material active-probing superiority is supported.

### Limitations that cannot be omitted

The 48 correlated worlds constitute only eight independent reset clusters; no statistical null-effect population theorem follows. The label-aware across-truth response gap is an **offline physical diagnostic, not online classification accuracy**. This study executes **fixed zero/X/Y probes**, not the proposed adaptive probe policy. It does NOT independently attest an action-specific noise/gain envelope, compare equal motor energy/contact costs, test task completion, deploy VLA, prove safety, or constitute third-party reproduction. One post-action true-target getter per world was used for AUDIT ONLY, never for a method decision. The source-faithful common root-translation action does not change pairwise commanded-target differences; under fixed common response gain, no artificial information gain should be claimed.

**Decision:** Keep research method PR #167 Draft. This is a reproducible mechanism-level falsifier and negative first physical test, not L10 performance.
