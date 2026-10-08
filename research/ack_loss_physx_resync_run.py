"""Precommitted frozen PPO lost-ack and single trusted-readback resync intervention.

Runs the unchanged six-arm original simulator trial. The observer is given an
UNKNOWN acknowledgement after one *physically delivered* command, refuses its
next decision, and can resume only after an explicit authoritative target read.
This isolates communication ACK loss, NOT physical actuator packet loss.
"""
from pathlib import Path
import json
import os
import sys
import numpy as np
import torch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import frozen_ppo_action_history_observer as baseline
from action_abi_history_observer import ActionHistoryObserver, TargetPose

COHORTS={"pull_cube":85001,"stack_cube":95001}
task=os.environ.get("ABI_TASK")
if task not in COHORTS:
    raise RuntimeError("Unexpected, unregistered task")
first=COHORTS[task]
baseline.FIRST_SEED=first
baseline.SEEDS=tuple(range(first,first+8))
baseline.ALL_SEEDS=baseline.SEEDS
baseline.OUTPUT_NAME=f"ack_loss_physx_resync_{task}_8.json"
context={"worlds":[],"seed":None,"events":[],"injected":False}
original_env=baseline.env
original_trial=baseline.trial
original_ack=ActionHistoryObserver.acknowledge


def observed_env(mode):
    world=original_env(mode)
    if context["seed"] is not None:
        context["worlds"].append(world)
    return world


def ack_with_loss(self,ticket,*,applied):
    # The method's original acknowledgement logic remains unchanged except
    # for one deliberately missing receipt in an otherwise normal rollout.
    if (context["seed"] is None or context["injected"]
            or self.sequence != 3):
        return original_ack(self,ticket,applied=applied)
    if applied is not True:
        raise RuntimeError("Unexpected native action acknowledgement input")
    if len(context["worlds"])!=6:
        raise RuntimeError("Observer arm identity ambiguous: refuse intervention")
    context["injected"]=True
    original_ack(self,ticket,applied=None)
    refused=False
    try:
        _=self.pose
    except RuntimeError:
        refused=True
    if not refused:
        raise RuntimeError("Safety-critical falsifier: missing ACK did not invalidate action authority")
    arm=context["worlds"][3].unwrapped.agent.controller.controllers["arm"]
    exact=arm.get_state().get("target_pose")
    if exact is None:
        raise RuntimeError("Trusted controller-command-target readback unavailable")
    values=np.asarray(torch.as_tensor(exact).detach().cpu(),dtype=float).reshape(-1,7)[0]
    if not np.all(np.isfinite(values)):
        raise RuntimeError("Nonfinite authoritative target resynchronization")
    target=TargetPose.from_arrays(values[:3],values[[4,5,6,3]])
    self.reset(target)
    predicted=self.pose
    poserr=float(np.max(np.abs(np.asarray(predicted.position)-values[:3])))
    context["events"].append({
        "seed":context["seed"],"action_index":2,
        "physical_env_step_completed":True,
        "receipt":"UNKNOWN_NOT_DELIVERED_TO_OBSERVER",
        "further_action_was_refused":refused,
        "authoritative_target_reads_for_recovery":1,
        "resync_target_position_abs_error_m":poserr,
        "private_readback_not_used_for_normal_actions":True,
        "note":"readback is necessary privileged recovery, not a sensor-free result"
    })


def intervention_trial(policy,seed):
    context["seed"]=seed
    context["worlds"]=[]
    context["events"]=[]
    context["injected"]=False
    try:
        out=original_trial(policy,seed)
        events=list(context["events"])
        if len(events)>1:
            raise RuntimeError("Unregistered multiple fault injections")
        out["ack_loss_fault"]=(events[0] if events else
            {"seed":seed,"triggered":False,"reason":"observer_arm_never_reached_third_action"})
        if events:
            out["ack_loss_fault"]["triggered"]=True
        return out
    finally:
        context["seed"]=None
        context["worlds"]=[]
        context["events"]=[]


baseline.env=observed_env
baseline.trial=intervention_trial
ActionHistoryObserver.acknowledge=ack_with_loss
baseline.main()
result_file=Path(baseline.OUTPUT_NAME)
data=json.loads(result_file.read_text())
seeds=list(baseline.SEEDS)
if data.get("seed_list")!=seeds or len(data.get("episodes",[]))!=8:
    raise RuntimeError("Lost-ack prespecified source cohort incomplete")
if sum(e.get("ack_loss_fault",{}).get("triggered",False) for e in data["episodes"])==0:
    raise RuntimeError("No actual fault intervention: invalid prospective study")
data["external_fault_protocol"]="research/ACK_LOSS_PHYSX_RESYNC_PRECOMMIT_V1.json"
data["original_observer_commit"]="0865e6d50ec30d6a069e2d7dfee1f9be834c2c21"
data["intervention_kind"]="delivered_action_unknown_ack_then_single_privileged_target_resync"
data["fault_triggered_episodes"]=sum(e["ack_loss_fault"].get("triggered",False) for e in data["episodes"])
data["per_action_privileged_target_reads_for_normal_observer"]=0
data["privileged_reads_for_recovery"]=data["fault_triggered_episodes"]
result_file.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
print("ACK_LOSS_PHYSX_RESYNC_SUMMARY",json.dumps({
    "task":task,"success":data["success_count"],"episodes":len(seeds),
    "faults":data["fault_triggered_episodes"],"privileged_recovery_reads":data["privileged_reads_for_recovery"],
    "paired_live_vs_recovered":{
        "live_only":sum(e["success_once"].get("projected",False) and not e["success_once"].get("observer",False) for e in data["episodes"]),
        "recovered_only":sum(e["success_once"].get("observer",False) and not e["success_once"].get("projected",False) for e in data["episodes"])}
},sort_keys=True))
