# Controller-State Handshake / Controlled Simulation Morphism

Static action conversion is insufficient when controllers have different
internal state: previous targets, integrators, filters, interpolation state, or
reference generators.

This prototype solves a stronger migration problem.

Source system:

```
s' = A_s s + B_s u
y  = C_s s
```

Target system:

```
t' = A_t t + B_t v
y  = C_t t
```

Compiler output:

```
t = H s
v = K_s s + K_u u
```

with proof obligations

```
C_t H = C_s
A_t H + B_t K_s = H A_s
B_t K_u = H B_s.
```

All three equations are linear in the unknown matrices H, K_s and K_u, so the
prototype solves them jointly and reports output, dynamics and action
residuals.  Exact certificates are verified by rollout tests.

Novelty boundary: controlled simulation / bisimulation relations are classical
control theory.  The intended research contribution is not that mathematics
itself; it is a controller-migration compiler for frozen robot policies that
extracts these obligations from real robot-learning controller interfaces,
synthesizes the handshake, refuses incompatible swaps, and links the
certificate to upstream action-conversion failures.
