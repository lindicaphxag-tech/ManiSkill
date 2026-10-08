# Certificate identifiability

AMRC asks for the next probe that resolves one runtime repair request. This file
sharpens that into an experiment-design problem.

Let V be the support-space information matrix and xi the current candidate
repair direction. Its uncertainty term is proportional to:

    xi^T V^{-1} xi.

After one physical probe z, information becomes V + z z^T. Sherman-Morrison
gives the exact one-step reduction.

Under ||z|| <= m, the continuous probe that maximizes this reduction has
direction:

    z* proportional to (V + m^2 I)^{-1} xi.

For unit probes:

    z* proportional to (V + I)^{-1} xi.

This is standard generalized-Rayleigh / rank-one-update mathematics; the
formula itself is not claimed as a new theorem. The research contribution under
test is using **certificate-directed identifiability**, rather than full system
identification, as the query objective for frozen robot-policy repair.

## Fixed-direction budget

If the same probe z is repeated k times:

    V_k = V + k z z^T.

The directional uncertainty can therefore be evaluated in closed form. The
capsule reports the smallest repeated-probe count that would shrink uncertainty
below the current repair-certificate slack, while holding the nominal map fixed.

This number is explicitly an **information-only planning estimate**. New probe
observations can change the estimated physical map and must be incorporated
before a runtime certificate is accepted.

## Falsifiable claim

On real frozen policies, compare:

- dense coordinate identification;
- coded CASJ;
- finite candidate AMRC;
- continuous certificate-optimal probing.

At matched false-accept rate, the certificate-optimal strategy must reduce
black-box policy evaluations to first terminal certificate. If it does not, this
component is removed from the flagship claim.
