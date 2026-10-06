# Prospective multi-state response-jet gate

## Frozen before execution

Policy:
`lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`

Runtime:
`LeRobot 3c0a209f9fac4d2a57617e686a7f2a2309144ba2`

Disjoint PushT reset seeds:

```text
101, 211, 307, 401, 503
```

The physical support chart, coarse/fine/finer radii, held-out disturbance,
paired-randomness seeds, controller authority, and CRG tolerances are inherited
unchanged from the frozen PushT protocol.

## Model-order test

For each state:

1. coarse and fine centered-derivative maps fit
   `D(h)=J0+C h^2`;
2. the finer map is not used in fitting;
3. a model-order upgrade passes only if:
   - jet / first-order held-out prediction error <= 0.5; and
   - relative jet prediction error <= 0.25.

This diagnostic does not itself authorize a repair.

## Frozen promotion rule

Only states where the first-order locality test fails but the held-out jet test
passes count as **jet rescues**.

Across the five frozen states:

- 0 rescues -> `DROP_JET_FROM_FLAGSHIP`;
- 1-2 rescues -> `KEEP_AS_SECONDARY_MECHANISM`;
- >=3 rescues -> `PROMOTE_TO_BROADER_PROSPECTIVE_TEST`.

This is a research-triage rule, not a population-confidence statement.

Negative outcomes remain public.
