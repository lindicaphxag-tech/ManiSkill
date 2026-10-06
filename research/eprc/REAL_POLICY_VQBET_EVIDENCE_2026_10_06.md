# Frozen real-policy evidence — VQ-BeT / PushT — 2026-10-06

This record freezes the first successful end-to-end public frozen-policy probe
for the DEC / CRG / AMRC line. It is **not** external adoption and **not** an
L8 event.

## Provenance

Current training-runtime run:

- workflow: `37456801175`;
- artifact: `11410675017`;
- artifact ZIP SHA-256:
  `56c367a0c7564a11f6347bd0eebe996555d62d7a8f7d9fded1e6aa6f13c182de`;
- frozen policy: `lerobot/vqbet_pusht`;
- model revision:
  `390e5e4c079c880b22e873dad53ecfac706bc78a`;
- LeRobot commit:
  `3c0a209f9fac4d2a57617e686a7f2a2309144ba2`;
- exact research branch head:
  `49f7bae973f50f8f166076430017f7857d3f778e`.

Historical-native confirmation:

- workflow: `37456801100`;
- artifact: `11410085345`;
- artifact ZIP SHA-256:
  `745e21a4e6e75556b19c93922f34b1914b4a08ea009ad2abd9c3727bb9d02a60`;
- historical LeRobot commit:
  `2cb0bf5d4154c8fefe03d1dca394fc5e1d778a97`;
- historical model revision: `bff7190`.

Only packaging/runtime compatibility surfaces were changed:
`pyav -> av` distribution naming, an explicit `packaging.version` import,
and Pymunk 6.11.1 for the checkpoint-era PushT collision API. Policy weights
and policy math were unchanged.

## Result

The important result is **not** a successful repair.

Repeatability is exceptionally stable:

- paired policy replay max error: **0.0**;
- preprocessing repeat error: **0.0**;
- five RNG-seed DEC q95 radius: **0.0**;
- empirical stochastic local-map radius: **0.0**.

But the local linear response is not scale-stable:

- fine-vs-coarse operator drift: **3.0126126299**;
- max relative scale curvature: **0.9645005488**;
- max symmetry residual: **12.0019283295**.

For the frozen held-out physical disturbance
`[10 px, -6 px, 0.35 rad]`:

- robust certified support radius: **0.5**;
- residual tolerance: **4.0**;
- nominal residual: **4.4226541813**;
- robust residual interval:
  **[2.9163478663, 5.9289604963]**;
- robust CRG decision: **INCONCLUSIVE**.

The information-only AMRC planner then allocated its complete frozen budget:

- 6 additional symmetric probe directions;
- 12 planned policy evaluations;
- final planned decision: **INCONCLUSIVE**.

Those probes were planning-only and are not counted as executed evidence.

## Interpretation

This is a useful negative result.

The obstacle is not RNG repeatability or missing repeated observations. The
dominant observed uncertainty is finite-difference **scale drift / locality
mismatch**. Therefore blindly collecting more same-scale samples is not a
justified response to this certificate failure.

The next prospective comparison is frozen before outcomes:

1. additional same-scale probing;
2. smaller-scale probing with a correspondingly smaller trust region;
3. a validated higher-order local response model.

At matched policy-query budget, the method must show that routing by uncertainty
source resolves certificates better without increasing false accepts. If it
does not, the evidence-action routing extension is rejected.
