# Compound unknown-ACK closed-loop PhysX experiment — source-frozen v1

**Pre-outcome contract, authored before the new multi-ACK PhysX jobs.**

Question: can a single unchanged third-party frozen ActionShift PPO run across the original achieved-pose-relative → stateful commanded-target-relative controller ABI when **two consecutive native arm-target command deliveries are unobservably held**?

## Frozen protocol
- Source: unmodified original two-history PhysX runner `research/frozen_ppo_ack_bounded_query.py`; preserved source blobs checked by CI. Extension: enumerate 1–16 possible controller target histories and compute ONE conservative, representable common native command with explicit worst-case positional/rotational setpoint residuals.
- Source: exact two-stage uncertainty through both step-2 and step-3 *simulated native arm target holds*; gripper is not dropped. Both acknowledgements in the adapter are `None`. This is NOT actual packet loss or real robot hardware.
- **Fresh seeds:** PullCube-v1 360001–360008 and StackCube-v1 370001–370008, 16 new reset states, 7 matched actual native PhysX controller arms per seed.
- Frozen published third-party PPO checkpoint SHA-256: Pull `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`; Stack `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`. Original source HF revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`.
- Controller action chart, official task success, action bound 0.05 m infinity norm / 0.05 rad geodesic, 50 time steps, no policy retraining.
- Seven same-seed worlds: fault-free reference; privileged controller oracle; optimistic unknown ACK; exact refusal; bounded common action with ZERO reads; bounded action or ONE evidence-triggered read; mandatory ONE real target read after both fault steps at t=4.
- Bounded method: translation has exact box Chebyshev center, SO(3) is conservative finite candidates incl pairwise geodesic midpoints; **authorization verifies every candidate target** using the executed representable Euler chart. If candidate search refuses, this is not a proof no valid command exists. Two-hypothesis route reuses original exact method.
- Record each case's actual official task-success outcomes, physical fault count/times, maximum belief width, privileged decision readbacks, exact no-query authorizations, refusal reasons, and postdispatch audit-only target residuals.
- **Hard gate:** zero false bound authorizations (or a specific logged counterexample, which invalidates the certificate), source SHA matched, complete 16-case denominator. No cherry-picking failures.
- Source task performance is *exploratory*; only 2 tasks / one Panda robot-controller family, no contact-force/collision safety, no independent researchers, no originality claim for known geodesic/Chebyshev geometry. Failure is recorded, not retrofitted.

## Interpretation
This is a useful original systems step beyond the earlier one-ACK two-state case even if task success falls. The model-level setpoint checker verifies conditional bounded *command targets*, not robot trajectory safety. No 16-state result is available when these seeds and parameters were frozen.
