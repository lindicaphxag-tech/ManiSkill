# Proof-carrying CRG impossibility certificate

For the centered certified repairability set

    K = { G xi : ||xi||_2 <= r },

the support function in physical direction n is

    h_K(n) = r ||G^T n||_2.

Therefore any nonzero direction n satisfying

    n^T d > h_K(n)

proves that target correction d is outside K.

The public capsule now carries this as an independently verifiable dual witness.

## Why this matters

The verifier does not call the repair optimizer and does not need to trust how
the nearest point was computed. It only needs:

- the frozen physical repair map G;
- certified radius r;
- requested physical correction d;
- normalized separation normal n;
- claimed support / margin values.

It recomputes the support inequality from scratch.

This turns one important CRG outcome from:

    "our optimizer could not find a repair"

into:

    "here is a compact witness proving that no repair inside the certified
     local policy-consistent set can satisfy this target."

## Claim boundary

This is standard convex separation/support-function mathematics. The novelty
claim is not the theorem. The research contribution under test is that an
intervention-identified frozen-policy repair set is useful enough that such
certificates predict real closed-loop recoverability and expose actionable
policy/controller bottlenecks.

## Real-policy requirement

For every VQ-BeT / second-policy held-out request classified as certified
impossible, export the witness and independently verify it before using the
label in any result table.
