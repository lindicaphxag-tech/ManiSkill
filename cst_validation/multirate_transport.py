from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .closed_loop_transport import (
    ClosedLoopTransportCertificate,
    LinearClosedLoopModel,
    synthesize_closed_loop_transport,
)


@dataclass(frozen=True)
class LiftedClosedLoopModel:
    micro_model: LinearClosedLoopModel
    hold_steps: int
    macro_model: LinearClosedLoopModel


@dataclass(frozen=True)
class MultiRateTransportCertificate:
    source_lift: LiftedClosedLoopModel
    target_lift: LiftedClosedLoopModel
    transport: ClosedLoopTransportCertificate
    same_macro_horizon: bool
    source_macro_seconds: float
    target_macro_seconds: float
    reason: str


def lift_zero_order_hold(
    model: LinearClosedLoopModel,
    hold_steps: int,
) -> LiftedClosedLoopModel:
    """Lift x+=Ax+Bu over hold_steps with one action held constant."""
    if hold_steps < 1:
        raise ValueError("hold_steps must be >= 1")
    A=np.asarray(model.A,dtype=float)
    B=np.asarray(model.B,dtype=float)
    if A.ndim!=2 or A.shape[0]!=A.shape[1]:
        raise ValueError("A must be square")
    if B.ndim!=2 or B.shape[0]!=A.shape[0]:
        raise ValueError("B must have the same state dimension as A")

    n=A.shape[0]
    A_power=np.eye(n)
    B_lift=np.zeros_like(B,dtype=float)
    # x_h=A^h x_0 + sum_{i=0}^{h-1} A^i B u
    for _ in range(hold_steps):
        B_lift += A_power @ B
        A_power = A @ A_power

    return LiftedClosedLoopModel(
        micro_model=model,
        hold_steps=hold_steps,
        macro_model=LinearClosedLoopModel(A=A_power,B=B_lift),
    )


def synthesize_multirate_transport(
    source: LinearClosedLoopModel,
    target: LinearClosedLoopModel,
    *,
    source_control_period: float,
    target_control_period: float,
    source_hold_steps: int,
    target_hold_steps: int,
    horizon_atol: float = 1e-12,
    atol: float = 1e-10,
    rtol: float = 1e-10,
) -> MultiRateTransportCertificate:
    """Match controllers only after lifting them to one physical time horizon.

    Refuses to call different wall-clock horizons equivalent. This prevents a
    numerically convenient but physically invalid comparison of, e.g., one
    20 Hz source step against one 100 Hz target step.
    """
    for name,value in (
        ("source_control_period",source_control_period),
        ("target_control_period",target_control_period),
    ):
        if value<=0 or not np.isfinite(value):
            raise ValueError(f"{name} must be finite and positive")

    source_lift=lift_zero_order_hold(source,source_hold_steps)
    target_lift=lift_zero_order_hold(target,target_hold_steps)
    source_seconds=float(source_control_period*source_hold_steps)
    target_seconds=float(target_control_period*target_hold_steps)
    same=bool(abs(source_seconds-target_seconds)<=horizon_atol)

    if not same:
        # Return no misleading transport.  The caller must select a common
        # physical horizon before comparing controller semantics.
        raise ValueError(
            "source and target lifted steps cover different physical horizons: "
            f"{source_seconds} vs {target_seconds} seconds"
        )

    cert=synthesize_closed_loop_transport(
        source_lift.macro_model,target_lift.macro_model,atol=atol,rtol=rtol
    )
    return MultiRateTransportCertificate(
        source_lift=source_lift,
        target_lift=target_lift,
        transport=cert,
        same_macro_horizon=True,
        source_macro_seconds=source_seconds,
        target_macro_seconds=target_seconds,
        reason=(
            "source and target are compared after zero-order-hold lifting to "
            "the same wall-clock control horizon"
        ),
    )
