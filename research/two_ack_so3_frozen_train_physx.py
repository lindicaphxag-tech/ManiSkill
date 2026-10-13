"""Original training-only frozen native SO3 action-fault observations.

This script records public EE/reset quaternions for registered variants and
histories, NOT a learned VLA, robot safety study or new-seed test data.
"""
import argparse
import json
from pathlib import Path

from research.two_ack_so3_native_protocol import (
    HISTORY_ORDER, reset_so3_feature, setup_public_two_ack_world,
    verify_registered_plan,
)


def train_robot(robot):
    spec = verify_registered_plan()
    if robot not in spec["robots"]:
        raise ValueError("Unknown registered robot")
    rows = []
    for seed in spec["training_seeds"][robot]:
        for variant in spec["action_variants"]:
            for truth in HISTORY_ORDER:
                env = None
                try:
                    env, ctrl, arm, reset, observed, predicted = (
                        setup_public_two_ack_world(
                            spec, robot, seed, variant, truth
                        )
                    )
                    record = {
                        "robot":robot, "seed":seed, "variant":variant,
                        "true_history_training_only":truth,
                        "public_reset_quat_xyzw":list(reset.quaternion_xyzw),
                        "public_pre_decision_quat_xyzw":list(observed.quaternion_xyzw),
                        "relative_public_so3_quat_xyzw":reset_so3_feature(
                            observed.quaternion_xyzw, reset.quaternion_xyzw
                        ),
                        "public_ee_position":list(observed.position),
                        "source_hypothesis_quat_xyzw":{
                            h:list(predicted[h].quaternion_xyzw) for h in HISTORY_ORDER
                        },
                        "sim_backend":"real_physx_cpu",
                        "private_controller_target_reads":0,
                    }
                    print("TWO_ACK_SO3_TRAIN_WORLD",
                          json.dumps(record,sort_keys=True),flush=True)
                    rows.append(record)
                finally:
                    if env is not None: env.close()
    expected = {(seed,variant,h)
                for seed in spec["training_seeds"][robot]
                for variant in spec["action_variants"]
                for h in HISTORY_ORDER}
    observed={(r["seed"],r["variant"],r["true_history_training_only"])
              for r in rows}
    if observed!=expected or len(rows)!=32:
        raise RuntimeError("Missing/duplicate or mislabelled training world")
    out={
        "schema":spec["schema"], "robot":robot,
        "registered_training_only":True,
        "unique_training_reset_clusters":4,
        "actual_source_native_physx_training_worlds":32,
        "preregister_blob":"44f770ecabe87e894eb7a3fa94dde3e94a730734",
        "rows":rows
    }
    name=f"two_ack_so3_original_train_{robot}.json"
    Path(name).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("TWO_ACK_SO3_TRAIN_COMPLETE",json.dumps({
        "robot":robot,"worlds":len(rows),"original_training_only":True
    },sort_keys=True),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--robot",choices=("panda","xarm6_robotiq"),
                        required=True)
    train_robot(parser.parse_args().robot)
