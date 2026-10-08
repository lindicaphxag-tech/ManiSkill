# Repairability Bottleneck Decomposition

CRG should not collapse every rejected repair into one generic failure. A frozen policy can fail for fundamentally different reasons.

Let C map action coordinates to canonical physical command space and J be the intervention-identified action-support Jacobian. Then the policy-consistent physical response is G=CJ.

For requested physical correction d, compare two structural residuals:

    r_controller = dist(d, Im(C))
    r_policy     = dist(d, Im(CJ)).

Because Im(CJ) is a subset of Im(C):

    r_policy >= r_controller.

The non-negative difference

    Delta_policy = r_policy - r_controller

is the local **policy restriction gap**: physical correction capability that exists in the controller but is not exposed by the frozen policy's current counterfactual response.

## Failure taxonomy

- ROBOT_LIMITED: d is outside Im(C). Changing only the policy-side repair cannot solve it.
- POLICY_LIMITED: d lies in Im(C) but outside Im(CJ). The robot/controller can express the correction, but not through the current frozen-policy response image.
- AUTHORITY_LIMITED: d lies in Im(CJ), but current linear action constraints make the required support-space correction too large.
- MODEL_LIMITED: d lies in Im(CJ) and controller authority is sufficient, but the correction exceeds the frozen local trust region.
- AUTHORITY_AND_MODEL_LIMITED: both radii are insufficient.
- CERTIFIED: structural and magnitude gates all pass.

## Runtime consequence

This decomposition makes rejection actionable:

- ROBOT_LIMITED -> change controller/embodiment/physical plan;
- POLICY_LIMITED -> replan, switch policy, or retrain;
- AUTHORITY_LIMITED -> change controller mode or reduce demanded correction;
- MODEL_LIMITED -> re-probe or replan rather than extrapolate;
- CERTIFIED -> execute the policy-consistent repair.

## Novelty discipline

Subspace projection and pseudoinverse residuals are standard linear algebra. The research contribution under test is the use of intervention-identified frozen-policy response to separate policy limitation from controller limitation at runtime, then connect that diagnosis to a certified repairability radius.

## Empirical falsifier

The taxonomy is useful only if these predicted bottlenecks correspond to distinct observed failure modes. A decisive study should inject matched disturbances that selectively cross the controller-image, policy-image, authority, and trust boundaries. If the resulting runtime failures do not separate accordingly, the decomposition should not be promoted as a core claim.