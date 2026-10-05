# CoRL 2026 workshop paper scaffold (anonymized)

Target workshop: Everything Beneath the Policy — How Controllers, Hardware, Data Infrastructure Shape Robot Learning.

Working title:

**Actions Are Not Tensors: Auditing and Transporting Controller Semantics in Robot Learning Infrastructure**

Backup conservative title:

**Beneath the Action Tensor: Controller-Semantic Transport for Robot Learning Infrastructure**

Status: scaffold only. Do not submit until at least one production-controller result and one public trajectory result are frozen.

## Abstract — evidence slots

1. Problem: identical-looking action vectors can denote different physical goals because controller semantics depend on normalization, current/target state, frames, rotation charts, IK and interpolation.
2. Empirical anchor: public robot-learning stacks contain acknowledged failures consistent with this abstraction gap.
3. Method: CST semantic type system + exact normal-form compiler; CT-CST counterfactual trace compiler for non-isomorphic controller families.
4. Evidence: deterministic chart witnesses, production controller preservation, public trajectory conversion, rotation-chart factorial.
5. Conclusion: action-space reporting should include controller semantic type and transport authority rather than only tensor shape/control-mode name.

Do not fill numerical slots from synthetic tests when a production/public-stack result is required.

## 1. Why action tensors are underspecified

Motivating examples:
- normalized delta-q versus physical absolute q;
- delta-current versus delta-target hidden state;
- axis-angle versus XYZ Euler;
- world versus body/root frame;
- endpoint target equality versus interpolation / actuator-trace equality.

Key thesis:

    software type compatibility + tensor shape compatibility
        != control-semantic compatibility

## 2. Controller-Semantic Transport

### 2.1 Semantic type

Type fields:
- physical goal space;
- update semantics;
- coordinate frame;
- parameterization;
- hidden controller state;
- interpolation;
- actuator semantics.

### 2.2 Exact compiler

    T_A->B(u; z_A, z_B) = encode_B(decode_A(u, z_A), z_B)

Exact authority only when both interfaces share a physical normal form and the target image contains the goal.

### 2.3 Counterfactual Trace Transport

For non-isomorphic controller families:

    Psi_C(s,z,u) = short physical trace

    u_B* = argmin_u d(Psi_B(s,z_B,u), Psi_A(s,z_A,u_A))

Authority requires residual, identifiability/conditioning and saturation gates.

## 3. Controlled evidence

### E1 — exact-family semantic preservation

Table rows: robot/controller pair.
Columns: coverage, median residual, p99 residual, false accepts, naive-copy residual.

Required before submission: real production ManiSkill controller result.

### E2 — public trajectory conversion

Compare:
- upstream converter;
- minimal semantic bug fix;
- CST exact compiler;
- naive tensor copy.

Report every episode; no silent retry filtering.

### E3 — rotation representation × controller sign factorial

2x2 design:
- historical converter / historical sign;
- fixed converter / historical sign;
- historical converter / fixed sign;
- fixed converter / fixed sign.

Use PegInsertionSide Diffusion Policy if feasible because upstream maintainer explicitly requested it.

### E4 — CT-CST cross-family authority

At minimum one accepted and one refused public controller pair.
Plot certificate residual/conditioning against held-out rollout divergence.

## 4. What existing infrastructure hides

Report the semantic fields that common control-mode strings omit.

Candidate table:
- control mode name;
- native action shape;
- physical goal;
- hidden state;
- frame/chart;
- exact transport class;
- known failure anchor.

## 5. Limitations

- simulator/controller semantics may not transfer exactly to hardware;
- CT-CST is query-expensive in v0;
- local trace matching is not global task equivalence;
- IK branch changes and contacts can make the target map discontinuous;
- external adoption is not claimed until an upstream maintainer retains code/tests.

## 6. Reproducibility / artifact statement

Release:
- frozen commit hash;
- exact CI run IDs;
- public validation protocol;
- per-episode JSON/CSV evidence;
- scripts for every figure/table;
- upstream issue/PR links separated from author-owned evidence.

## Workshop-specific fit

The contribution is not framed as a new policy architecture. It exposes and controls hidden controller/infrastructure choices beneath policy training, with factorial ablations, negative cases and a reusable reporting/transport abstraction.

## Submission go/no-go

GO only if:
- production ManiSkill gate is green;
- at least one public trajectory conversion is frozen;
- no claim relies only on author-owned synthetic evidence;
- double-blind PDF removes account/user identifiers.

STRONG GO if additionally:
- #429 patch is under upstream review or merged;
- PegInsertionSide factorial has at least multiple seeds;
- second-stack robomimic/robosuite evidence exists.
