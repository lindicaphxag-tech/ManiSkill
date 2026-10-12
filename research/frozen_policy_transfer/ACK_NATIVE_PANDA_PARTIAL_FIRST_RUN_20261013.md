# Frozen ACK-response native PhysX pilot — PARTIAL first-run record

**First execution: 2026-10-13 local China time, completed Panda only.**
This memo preserves genuine original native PhysX **negative** evidence before
any xArm6 infrastructure retry or later outcome inspection.

- Freeze (pre-outcome blob `6f97dccaa4740039019db0726e21ea0a970a1fa3`):
  `research/ACK_ACTIVE_NATIVE_PROBE_PILOT_PREREG_20261013.json`.
- [First execution job, Panda 24/24 genuine native worlds](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294457476/job/114962085897)
  · [unaltered original log + JSON artifact #11767651229](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294457476/artifacts/11767651229).
- XArm6 in the same first run **failed before the first physical world**:
  the absent optional xArm6 Robotiq URDF caused an interactive asset-download
  prompt, which raised EOFError in GitHub Actions.
  [Exact failed job](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38294457476/job/114962085793).
  The subsequent infrastructure-only change enabled ManiSkill's documented
  `MS_SKIP_ASSET_DOWNLOAD_PROMPT=1` for optional robot asset provisioning,
  without changing the registered seeds, actions, source recurrence or gate.
  Repeated Panda worlds in any infrastructure retry are **not new independent
  reset states or a fresh blind cohort**.

## Entire completed Panda original denominator

Four reset clusters `5601001–5601004` × applied/held ACK truth × three
physically executed zero/X/Y native probes = **24** actually stepped worlds.
Each row logs public pre/post XYZ, native six-dimensional action, actual
`PDEEPoseController` mapping, zero decision-time privileged target reads,
and a post-actuation-only hidden target audit. Per-world recurrence discrepancy
was below the registered `1e-4m` refusal threshold.

| Seed | Zero gap (mm) | Nonzero X gap (mm) | Nonzero Y gap (mm) |
|---|---:|---:|---:|
| 5601001 | 1.913099 | 1.932422 | 1.911406 |
| 5601002 | 1.944705 | 1.968072 | 1.941433 |
| 5601003 | 1.919392 | 1.940358 | 1.917494 |
| 5601004 | 1.934748 | 1.954850 | 1.932261 |
| **Mean, four reset clusters** | **1.927986** | **1.948926** | **1.925648** |

- Original nonzero X minus zero mean: **+0.020940 mm** (about 21 µm).
- Original nonzero Y minus zero mean: **−0.002337 mm**.
- The frozen exploratory *5 mm* public-response separation-benefit gate is
  **not met on Panda for either fixed probe**. That already prevents a
  two-robot success claim for this frozen experiment. Full xArm6 denominator
  is not yet complete as of this record.

### Essential interpretation

This is **not** 24 independent initial reset states (there are four), and
the outcome measured here is **public positional response separation**,
not correctness of a calibrated history predictor or policy task success.
The three probes do not have equal motor displacement/energy/contact cost.
There is **no** independent response-envelope calibration, validated
active policy selection, VLA, downstream manipulation success, or deployment
safety assurance. The observation is consistent with the previously published
Panda/xArm6 negative active-vs-zero probing control; no novel advantage can
be claimed from the tiny original X response gap.

The study remains fail-open to a negative result: the preregistered source,
seed list, action magnitudes and 5 mm gate were NOT retuned after seeing
these Panda outcomes.
