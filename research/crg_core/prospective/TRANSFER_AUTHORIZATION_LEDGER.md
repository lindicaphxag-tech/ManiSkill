# Transfer authorization versus distinct-response detection

**Identified before the new frozen 13-state experiment finished.**

The completed old cross-policy study already falsified global DEC-distance
superiority. The subsequent [fresh-state conformal pilot PR #46]
(https://github.com/lindicaphxag-tech/ManiSkill/pull/46) freezes nine
new calibration states and four new test states, but its initial
aggregate contains a *reporting-label* bug:

- STATISTICALLY_SIMILAR means an actual action transfer may be authorized;
- STATISTICALLY_DISTINCT means the responses differ: do NOT transfer;
- ABSTAIN_UNCERTAIN means no authorization;
- REJECT_INVALID_LOCAL_MODEL means no authorization.

The original aggregate currently calls the sum of SIMILAR + DISTINCT
`authorized_requests`, which is **actually decisive classifications**,
not robot transfer authorizations. Its `false_authorizations` mixes
false-positive transfer approvals with false *nontransfer* rejections.
This can make an algorithm that only rejects transfers look useful.

The read-only ledger in this directory consumes the unmodified pilot
aggregate after the frozen-policy data are generated, reclassifying all
eight A/B observations from the original test seeds 263,269,271,277.

It reports separately:

- transfer_authorized_count = SIMILAR only;
- correct_distinct_nontransfer_count = DISTINCT with actual gap > tau;
- false_transfer_authorization_count = SIMILAR with actual gap > tau;
- false_distinct_rejection_count = DISTINCT with actual gap <= tau;
- abstentions and invalid model rejections;
- *distinct screening coverage* versus **actual transfer authorization coverage**.

A pilot with eight correct DISTINCT decisions has 100% informative
decisions, but **0% actual transfer authorization and ZERO_UTILITY_NO_TRANSFER**.
The full frozen test denominator remains four state clusters, eight paired
observations. No outcomes are omitted.

The fixed tau=1.0 and frozen test seed set are enforced independently.
This ledger does not change the calibration, produce policy calls, look
at new data to tune thresholds, or create an independent external
replication. It measures average responses over three policy RNG seeds,
**not** single-action collision safety or randomized tail risk.

```bash
python -m pytest -q tests/test_crg_transfer_authorization_ledger.py
python -m research.crg_core.prospective.transfer_authorization_ledger \
    /path/to/prospective_pilot_result.json \
    --output corrected_transfer_accounting.json
```

Important: No claim of superior risk-coverage tradeoff may be made
by comparing models at *unequal* transfer authorization coverage and
different policy-query costs. The proposed correction is an
outcome-accounting integrity fix, **not a method improvement**.
