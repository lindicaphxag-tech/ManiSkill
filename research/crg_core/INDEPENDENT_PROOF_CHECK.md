# Independent CRG impossibility proof check

This small script is a **standalone arithmetic auditor** for the robust
counterfactual repairability (CRG) impossibility inequality. It depends only on
NumPy and avoids importing the policy runtime, simulator, optimizer, or large
EPRC research branch.

For a unit vector \`n\`, support radius \`r\`, map estimate \`G_hat\`, target
\`d\`, assumed operator-norm error bound \`epsilon\`, and **trusted externally
supplied** residual tolerance \`tau\`, check:

    n^T d - r (||G_hat^T n||_2 + epsilon) > tau

With numerical slack >1e-9, this verifies the claimed separation inequality
and implies that no admissible **local linear** map in the assumed uncertainty
ball can repair the target within tau.

Run:

\`\`\`bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_independent_proof_checker.py
python -m research.crg_core.verify_impossibility \
  --claim trusted-claim.json --witness normal-only-witness.json
\`\`\`

Claim JSON:

\`\`\`json
{
  "physical_map": [[1.0]],
  "target": [0.8],
  "certified_radius": 0.5,
  "operator_error_bound": 0.1,
  "residual_tolerance": 0.1
}
\`\`\`

Witness JSON:

\`\`\`json
{"normal": [1.0]}
\`\`\`

The witness file cannot override the external claim's tolerance, radius, or
operator uncertainty. Cases with NaN/Inf, non-unit normal, or invalid shapes
fail closed.

**Important boundary:** \`arithmetic_witness_valid=true\` does not establish
that a real frozen policy produced the measurements, that the assumed
operator-norm envelope actually contains the true local policy map, that the
local model is valid, or that an independent research group replicated the
experiment. \`external_experiment_verified\` is **always false** in this
arithmetic-only CLI. Real-world certification depends on separately verified
experimental assumptions. The separation inequality itself is established
convex analysis, not a newly invented theorem.
