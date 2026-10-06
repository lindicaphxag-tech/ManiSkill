# Oracle-free runtime prediction certificate

## Hole closed

Fresh-policy responses are valid evaluation labels, but they cannot be runtime inputs to a method whose purpose is to avoid an unsafe or expensive fresh re-query.

The runtime certificate therefore uses only:

- an identified local physical response map G_hat;
- an operator-norm uncertainty bound epsilon_G;
- a known normalized support disturbance xi;
- a certified locality/controller-authority radius;
- a frozen response-error tolerance.

## Certificate

Assume ||G_true - G_hat||_2 <= epsilon_G and predict d_hat = G_hat xi.

Then ||G_true xi - d_hat||_2 <= epsilon_G ||xi||_2.

If ||xi|| is inside the certified radius and epsilon_G ||xi|| is below tolerance, the correction prediction is certified without querying the fresh policy.

Otherwise the runtime returns INCONCLUSIVE or REFUSE_OUTSIDE_CERTIFIED_REGION.

## Evidence boundary

This certifies local policy-response prediction fidelity under the stated uncertainty model. It does not by itself certify task success, collision safety, long-horizon stability, or correctness of the uncertainty bound.

## Prospective evaluation

Freeze a disturbance bank, issue the oracle-free certificate first, then obtain the fresh policy response only as an evaluation oracle. Certified cases must remain inside the frozen response-error tolerance. Coverage and false certification should be compared with fixed-radius and perturbation-magnitude baselines.

The claim is rejected if useful coverage collapses or certified cases violate the frozen tolerance.