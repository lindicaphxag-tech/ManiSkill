# Cross-policy repair transfer from Differential Execution Contracts

DEC has two distinct layers:

- the full canonical physical response operator J_phys, which is required for repair;
- the compact DEC signature, which is useful for comparison, clustering and diagnostics.

A signature alone is not sufficient to transfer a correction because it can discard the orientation of the support-to-command operator.

## Transfer question

Suppose frozen stack A has already paid the cost of identifying a high-quality physical repair sidecar. Can that sidecar be reused on frozen stack B without fully rebuilding it?

For a target disturbance delta_s:

true target response: Delta y_B = J_B delta_s + r_B

transferred repair: hat Delta y_A = hat J_A delta_s

with ||r_B|| <= 0.5 L_B ||delta_s||^2.

The executable certificate uses the conservative bound:

||Delta y_B - hat Delta y_A||
<= ( ||hat J_B-hat J_A||_2 + 2 eps_A + eps_B ) ||delta_s||
   + 0.5 L_B ||delta_s||^2.

This inequality is standard perturbation analysis and is not claimed as new mathematics. The research contribution is using an intervention-identified physical operator mismatch together with controller-authority gates to decide whether repair reuse is admissible.

## Fail-closed gates

Transfer is denied when:

- canonical physical operator dimensions differ;
- the target command is outside controller authority;
- the target loses a required local physical direction;
- the certified transfer-error bound exceeds a predeclared physical tolerance.

## Strong experiment

1. identify a high-quality source repair operator on policy A;
2. spend a small target probe budget on policy B;
3. freeze DEC/operator mismatch and target remainder/error budgets;
4. authorize or reject transfer before the held-out disturbance is executed;
5. compare transferred repair against B full re-query or B independently identified repair.

Baselines are unconditional repair reuse, support-set overlap, raw action-Jacobian distance, static controller metadata, and coarse DEC class.

Primary endpoints are false-authorization rate, certified-bound violation rate, target policy queries saved, and recovery outcome after authorized transfer.

## Kill criterion

If DEC-gated transfer cannot reduce false authorization or target probing cost against the strongest simple gate, DEC is descriptive rather than operationally useful and this line should be rejected.