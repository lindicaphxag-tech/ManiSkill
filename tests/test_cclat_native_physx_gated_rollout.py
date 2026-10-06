import itertools

import numpy as np

from cst_validation.closed_loop_transport import synthesize_closed_loop_transport
from cst_validation.dominance_gate import (
    calibrate_quadratic_remainder,
    certify_calibrated_dominance,
)
from cst_validation.native_physx_two_joint import NativeTwoJointPlant, frozen_policy, linearize


def _calibration_shell(plant, *, seed):
    state_limit=np.array([0.08,0.08,0.15,0.15],dtype=float)
    action_limit=np.array([0.15,0.15],dtype=float)
    states=[]
    actions=[]

    # Include all box corners so the declared calibration domain is fixed,
    # rather than determined by lucky random extrema.
    for signs in itertools.product([-1.0,1.0],repeat=6):
        signs=np.asarray(signs)
        states.append(signs[:4]*state_limit)
        actions.append(signs[4:]*action_limit)

    rng=np.random.default_rng(seed)
    for _ in range(96):
        states.append(rng.uniform(-state_limit,state_limit))
        actions.append(rng.uniform(-action_limit,action_limit))

    states=np.asarray(states)
    actions=np.asarray(actions)
    observed=np.stack([plant.transition(x,u) for x,u in zip(states,actions)])
    return states,actions,observed


def test_calibrated_gate_repairs_transient_without_overcorrecting_near_equilibrium():
    source_model_plant=NativeTwoJointPlant(
        stiffness=[100.0,80.0],damping=[10.0,8.0]
    )
    target_model_plant=NativeTwoJointPlant(
        stiffness=[60.0,120.0],damping=[6.0,12.0]
    )
    source_model=linearize(source_model_plant)
    target_model=linearize(target_model_plant)
    transport=synthesize_closed_loop_transport(source_model,target_model)

    src_states,src_actions,src_next=_calibration_shell(
        NativeTwoJointPlant(stiffness=[100.0,80.0],damping=[10.0,8.0]),
        seed=202610061,
    )
    tgt_states,tgt_actions,tgt_next=_calibration_shell(
        NativeTwoJointPlant(stiffness=[60.0,120.0],damping=[6.0,12.0]),
        seed=202610062,
    )
    source_env=calibrate_quadratic_remainder(
        source_model,src_states,src_actions,src_next
    )
    target_env=calibrate_quadratic_remainder(
        target_model,tgt_states,tgt_actions,tgt_next
    )

    initial=np.array([0.06,-0.05,0.10,-0.08],dtype=float)
    ref=NativeTwoJointPlant(stiffness=[100.0,80.0],damping=[10.0,8.0])
    naive=NativeTwoJointPlant(stiffness=[60.0,120.0],damping=[6.0,12.0])
    gated=NativeTwoJointPlant(stiffness=[60.0,120.0],damping=[6.0,12.0])
    for p in (ref,naive,gated):
        p.reset_state(initial)

    ref_trace=[ref.state()]
    naive_trace=[naive.state()]
    gated_trace=[gated.state()]
    interventions=0
    refusals=0
    margins=[]

    for _ in range(30):
        x_ref=ref.state()
        x_naive=naive.state()
        x_gated=gated.state()

        u_ref=frozen_policy(x_ref)
        u_naive=frozen_policy(x_naive)
        u_gated_policy=frozen_policy(x_gated)

        gate=certify_calibrated_dominance(
            source_model,target_model,transport,
            state=x_gated,source_action=u_gated_policy,
            source_envelope=source_env,target_envelope=target_env,
        )
        if gate.use_transport:
            u_gated=gate.target_action
            interventions+=1
        else:
            u_gated=gate.fallback_action
            refusals+=1
        margins.append(gate.certified_margin)

        ref_trace.append(ref.step(u_ref))
        naive_trace.append(naive.step(u_naive))
        gated_trace.append(gated.step(u_gated))

    ref_trace=np.asarray(ref_trace)
    naive_trace=np.asarray(naive_trace)
    gated_trace=np.asarray(gated_trace)
    naive_err=np.linalg.norm(naive_trace-ref_trace,axis=1)
    gated_err=np.linalg.norm(gated_trace-ref_trace,axis=1)

    metrics={
        "mean_naive_error":float(np.mean(naive_err[1:])),
        "mean_gated_error":float(np.mean(gated_err[1:])),
        "mean_error_ratio":float(np.mean(gated_err[1:])/np.mean(naive_err[1:])),
        "terminal_naive_error":float(naive_err[-1]),
        "terminal_gated_error":float(gated_err[-1]),
        "max_naive_error":float(np.max(naive_err)),
        "max_gated_error":float(np.max(gated_err)),
        "max_error_ratio":float(np.max(gated_err)/np.max(naive_err)),
        "interventions":interventions,
        "refusals":refusals,
        "source_remainder_coefficient":float(source_env.coefficient),
        "target_remainder_coefficient":float(target_env.coefficient),
        "min_margin":float(np.min(margins)),
        "max_margin":float(np.max(margins)),
    }
    print("CCLAT_GATED_POLICY_METRICS",metrics)

    # Frozen before seeing the run.
    assert interventions >= 1
    assert metrics["mean_error_ratio"] < 0.8
    assert metrics["max_error_ratio"] < 0.95
    assert metrics["terminal_gated_error"] < 1e-6
