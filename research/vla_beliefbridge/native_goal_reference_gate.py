"""Fail-closed controller-semantic gate before applying target-history recovery to VLA.

A target-relative controller and an achieved-relative one are different
state transition systems. A missing acknowledgement does NOT imply the same
uncertain commanded-target recurrence in both. This is a provenance gate,
not an action generator or certified robotics safety proof.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class TransitionKind(str,Enum):
    UNKNOWN = "unknown_no_action_authorization"
    LAST_COMMANDED_TARGET = "last_commanded_target_relative"
    ACHIEVED_END_EFFECTOR = "achieved_end_effector_relative"

@dataclass(frozen=True)
class VerifiedNativeContract:
    transition: TransitionKind
    controller_class: str
    controller_source_sha256: str
    native_libero_abi: bool

class ContractRejected(ValueError): pass

def classify_native_controller_report(payload: dict) -> VerifiedNativeContract:
    if not isinstance(payload,dict) or payload.get("result")!="READ_ONLY_NATIVE_CONTROLLER_ABI_INSPECTION":
        raise ContractRejected("Actual native reset source report required")
    if payload.get("native_fixed_init_reset_completed") is not True:
        raise ContractRejected("Actual native LIBERO robot was not reset")
    nodes=payload.get("controllers")
    if not isinstance(nodes,list) or len(nodes)!=1:
        raise ContractRejected("Controller must be exactly one audited OSC for this gate")
    node=nodes[0]
    if node.get("class")!="robosuite.controllers.osc.OperationalSpaceController":
        raise ContractRejected("Native controller class unsupported")
    sha=node.get("file_sha256")
    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha):
        raise ContractRejected("Native controller source SHA256 missing")
    if node.get("has_set_goal") is not True or node.get("use_delta") is not True:
        raise ContractRejected("Native controller must have relative goal setter")
    ach=node.get("source_goal_relative_to_achieved_ee_pose")
    target=node.get("source_goal_relative_to_previous_desired_target")
    if type(ach) is not bool or type(target) is not bool or ach==target:
        raise ContractRejected("Native achieved/commanded reference not uniquely source-authenticated")
    if payload.get("source_ast_achieved_pose_relative") is not ach:
        raise ContractRejected("Top-level native provenance contradicts AST")
    if payload.get("source_ast_previous_target_relative") is not target:
        raise ContractRejected("Native reference contradiction")
    if node.get("source_semantics_verified") is not True:
        raise ContractRejected("Source AST witness not verified")
    if payload.get("same_target_memory_fault_as_maniskill_proven") is not False:
        raise ContractRejected("Cannot silently mark cross-engine controller semantics equivalent")
    return VerifiedNativeContract(
        TransitionKind.ACHIEVED_END_EFFECTOR if ach else TransitionKind.LAST_COMMANDED_TARGET,
        node["class"],sha,True)

def authorize_beliefbridge_target_history_adapter(contract:VerifiedNativeContract) -> dict:
    if not isinstance(contract,VerifiedNativeContract) or not contract.native_libero_abi:
        raise ContractRejected("Unverified native action provenance")
    if contract.transition != TransitionKind.LAST_COMMANDED_TARGET:
        return {
            "authorized":False,
            "reason":"DIFFERENT_ACHIEVED_RELATIVE_NATIVE_RECURRENCE_REQUIRES_NEW_FAULT_MODEL",
            "why":"Robosuite OSC computes the next target from achieved EE, not retained previous commanded target",
            "does_not_assert_vla_fault_recovery":True,
        }
    return {"authorized":True,
        "reason":"TARGET_RELATIVE_CHART_STILL_REQUIRES_PHYSICAL_ACK_INJECTION_VALIDATION",
        "does_not_assert_vla_fault_recovery":True}

def _test():
    sha="a"*64
    n={"class":"robosuite.controllers.osc.OperationalSpaceController","file_sha256":sha,
       "has_set_goal":True,"use_delta":True,
       "source_goal_relative_to_achieved_ee_pose":True,
       "source_goal_relative_to_previous_desired_target":False,
       "source_semantics_verified":True}
    p={"result":"READ_ONLY_NATIVE_CONTROLLER_ABI_INSPECTION",
       "native_fixed_init_reset_completed":True,
       "controllers":[n],
       "source_ast_achieved_pose_relative":True,
       "source_ast_previous_target_relative":False,
       "same_target_memory_fault_as_maniskill_proven":False}
    assert not authorize_beliefbridge_target_history_adapter(classify_native_controller_report(p))["authorized"]
    p["source_ast_achieved_pose_relative"]=False
    try: classify_native_controller_report(p)
    except ContractRejected:pass
    else:raise AssertionError("Contradictory provenance accepted")
    p["source_ast_achieved_pose_relative"]=True
    del n["source_semantics_verified"]
    try: classify_native_controller_report(p)
    except ContractRejected:pass
    else:raise AssertionError("Missing proof accepted")
    print("NATIVE_CONTROLLER_SEMANTIC_FAIL_CLOSED_TESTS_PASS")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:return _test()
    if a.input is None or a.output is None:p.error("--input / --output required")
    native=classify_native_controller_report(json.loads(a.input.read_text()))
    gate=authorize_beliefbridge_target_history_adapter(native)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(gate,indent=2,sort_keys=True)+"\n")
    print("NATIVE_TARGET_HISTORY_ACTION_AUTHORIZATION",json.dumps(gate,sort_keys=True))

if __name__=="__main__":main()
