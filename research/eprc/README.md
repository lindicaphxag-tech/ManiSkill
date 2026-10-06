# EPRC public executable capsule

This fork-only capsule exposes the smallest runnable form of **EPRC — Embodied
Policy Runtime Compiler**.

It is intentionally not an upstream ManiSkill proposal and does **not** count as
external adoption.

## What is executable

`runtime.py` implements a fail-closed execution decision:

```text
PASS
TRANSPORT
REPAIR
REJECT
```

from an explicit evidence bundle containing:

- action-semantics resolution;
- runtime provenance validity;
- controller representability margin;
- canonical physical-command error;
- exact-transport availability;
- intervention-identified support stability;
- held-out intervention residual;
- transverse perturbation magnitude;
- certified repair radius;
- local physical contract class.

The emitted certificate is independently re-derived by `verify_certificate`
and is bound to runtime provenance through a SHA-256 digest.

## 5-minute reproduction

```bash
python -m pytest -q tests/test_eprc_runtime.py
python research/eprc/reproduce.py research/eprc/evidence/replication_example.json --expect REPAIR
```

The second command compiles an evidence bundle, emits a provenance-bound certificate, and independently re-verifies it. No simulator or GPU is required for this contract-level capsule.

## What would count as meaningful external evidence

Issues are disabled on this fork, so third-party results are accepted through **ordinary pull requests** adding one digest-bound JSON record under `research/eprc/evidence/replications/`. A result should provide:

1. policy family and checkpoint;
2. controller representation;
3. exact provenance tuple;
4. physical support intervention protocol;
5. support stability;
6. held-out directional residual;
7. representability margin;
8. emitted decision;
9. whether the decision matched actual execution outcome.

A positive result is **not required**. A clean rejection or negative result is equally useful if the evidence is complete.

Replication records can be sealed with:

```bash
python research/eprc/seal_replication.py path/to/record.json
```

and are validated in CI. Self-authored records are rejected as independent evidence.

## L8 / L9 gates

This repository owner does not count self-authored forks, stars, or workflow
runs as external adoption.

- **L8 trigger:** one third-party result-bearing reproduction, or one maintained
  robotics project adopts the runtime contract primitive.
- **L9 trigger:** independent implementations compare or build upon EPRC and the
  contract becomes part of an external runtime / paper / toolkit.

## Nearest-neighbor discipline

EPRC is not presented as the first runtime safety layer, counterfactual planner,
latency compensator, controller converter, Jacobian method, or VLA recovery
system.

The narrower research question is whether a frozen policy's **executable
physical contract** can be recovered strongly enough to choose between exact
transport, bounded local repair, and rejection across policy/controller changes.
