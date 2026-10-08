# Clustered audit for the frozen 20-pair research bank

**Statistical caveat:** "20 pairs" consists of **10 restored states × 2
held-out A/B disturbances**. Within a state both A/B responses share the same
identified DEC/Jacobian distance. These pairs are NOT 20 independent states.

The original preregistered Spearman threshold and best-baseline margin remain
the **primary** decision. This optional checker is a **post-hoc exploratory
sensitivity audit**, never a substitute pass gate.

It reports:

1. the originally observed 20-pair Spearman correlations;
2. state-cluster bootstrap intervals (A/B sampled together, whole states
   with replacement);
3. ten leave-one-state-out correlations and baseline margins;
4. a state-block permutation right-tail *exploratory* p-value, permuting
   A/B target blocks together, not shuffling individual observations.

The permutation test additionally assumes the restored states are
exchangeable under its null. Only 10 state units are present. Bootstrap
percentile intervals with so few clusters are exploratory, not
confirmatory certainty statements.

## Input and CLI

Supply a JSON with the following shape (values illustrative, **not
research data**):

\`\`\`json
{
  "schema": "crg-paired-score-groups-v1",
  "groups": [
    {
      "state_id": 17,
      "pairs": [
        {
          "heldout_id": "A",
          "dec_distance": 0.2,
          "raw_distance": 0.3,
          "support_distance": 0.0,
          "static_metadata_distance": 0.0,
          "coarse_class_distance": 1.0,
          "heldout_response_distance": 0.5
        },
        {
          "heldout_id": "B",
          "dec_distance": 0.2,
          "raw_distance": 0.3,
          "support_distance": 0.0,
          "static_metadata_distance": 0.0,
          "coarse_class_distance": 1.0,
          "heldout_response_distance": 0.7
        }
      ]
    }
  ]
}
\`\`\`

At least three real state clusters are required, each with exactly A/B.
A full 20-pair bank uses ten state clusters. A/B within one state must
have exactly the same DEC distance (up to floating roundoff).

\`\`\`bash
python -m pytest -q tests/test_crg_clustered_evidence_audit.py
python -m research.crg_core.clustered_evidence_audit scores.json \
  --output exploratory_cluster_audit.json
\`\`\`

The main prospective 20-case PR uses a separately frozen primary gate.
Until that bank finishes, **no statistical claim is available**.
After v2 restoration amendment, reports must explicitly retain their
post-run-amended status. Do not retrospectively reinterpret this audit as
if its thresholds or permutation test were registered before data collection.
