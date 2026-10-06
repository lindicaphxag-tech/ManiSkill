# Bilateral coordinate invariance of Differential Execution Contracts

Cross-policy comparison has two coordinate problems, not one.

- Action coordinates can differ: absolute joints, relative joints, normalized actions, EE pose charts.
- Support coordinates can differ: object-frame pose, world-frame pose, normalized support variables, or another locally invertible parameterization of the same physical perturbation.

Let xi be a support chart, a an action chart, s the canonical physical support coordinate, and y the canonical physical command. The raw black-box derivative is:

  J_raw = da / dxi.

The canonical DEC is:

  J_phys = (dy/da) J_raw (dxi/ds).

Now change both charts locally:

  a' = h(a),   xi' = g(xi).

Then:

  J_raw' = Dh J_raw Dg^{-1},

while the semantic lifts become:

  dy/da' = (dy/da) Dh^{-1},
  dxi'/ds = Dg (dxi/ds).

Therefore all chart terms cancel and J_phys is unchanged.

## Boundary

This is only an equivalence when both coordinate maps are locally invertible and reasonably conditioned. Occlusion, lossy projection, clipping, discretization, aliasing, saturation, or a rank-deficient support representation are not harmless reparameterizations; they destroy information or authority and must invalidate the equivalence claim.

## Why this matters for CASJ / DEC

CASJ may be probed through different support parameterizations across environments or policies. Without bilateral lifting, a raw Jacobian difference can be caused by either the action chart or the support chart. DEC comparison should occur only after both sides are mapped into common physical units.

Physical gain is preserved after canonicalization. Once both sides are in the same physical units, a larger J_phys is a real behavioral difference.