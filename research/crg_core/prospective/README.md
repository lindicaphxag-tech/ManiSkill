# Frozen fresh-state CRG conformal transfer pilot — 2026-10-08

The protocol JSON was committed as a **standalone first commit**:
`82e41074729d7651113f709d8e061eee480a9dd1`.
Its exact Git blob is pinned in the evaluator. A changed seed list or
response tolerance will fail the frozen-blob check.

**This is a new prospective pilot, not the 20-case negative-result dataset.**
The original ten inspected state IDs [17,29,43,59,71,89,101,131,151,181]
are excluded from *both* new calibration and new evaluation.

- Nine new calibration states: 211,223,227,229,233,239,241,251,257.
- Four untouched test states: 263,269,271,277.
- Official frozen LeRobot Diffusion/VQ-BeT checkpoints and exact
  historical probe-source commit `8207ac01...` remain pinned.
- Two predeclared A/B disturbances per state; all 13 states mandatory.
- State-block split conformal, alpha 0.10, k=9 with nine calibration
  state-blocks; frozen response-distance tolerance 1.0 absolute PushT
  action-coordinate units. The engineering threshold was fixed before this
  new pilot was run; it is not claimed to have clinical or hardware meaning.
- Predeclared validity gate: both policies must satisfy the old source's
  three-RNG DEC stability heuristic; both action/support charts must match
  the known PushT identity coordinates. This stability flag is a **proxy**,
  not an independently established locality or operator-norm guarantee.

**Prospective outcomes are not required to be positive.** The reported
denominator is always 4 test states and 8 dependent held-out responses.
If any state is missing, the result is INCOMPLETE, never a reduced-n pass.
If every test request is rejected, call it ZERO_UTILITY_ALL_ABSTAIN and
stop claiming practical advantages. If a test state fails the locality
heuristic, preserve it and report REJECT_INVALID_LOCAL_MODEL.

Always-abstain has zero false authorizations at zero coverage, so cannot
serve as evidence of utility. The naive Jacobian point reference may make
more authorizations; **do not compare conditional error rates as if coverage
were matched**. Full matched-coverage inference is deferred to a larger
separately preregistered study if this pilot shows nontrivial coverage.

No results from the historical 20 observations enter calibration, no
hyperparameters are tuned on the new test states, and no post-hoc case
exclusions are permitted. This is owner-run CPU simulation only, not
external independent replication or a proof of real-world safe actions.

The experiment may take substantial CPU time because all 13 independent
frozen-policy state probes use official fixed checkpoints. Its workflow
will upload every raw state artifact and a machine-readable negative or
positive pilot report; a green workflow only means execution succeeded.

## Verification

```bash
python -m pytest -q tests/test_crg_transfer_conformal_fresh_pilot.py
python -m research.crg_core.prospective.evaluate_fresh_pilot \
  --input-dir /path/to/13/state/artifacts \
  --output fresh_pilot_result.json
```

Any claim of superiority requires a later new, sufficiently powered
prospective comparison of false authorizations at matched action coverage
and query budget. Neither the original failed DEC bank nor this small
pilot alone can justify an L8/L9 performance claim.
