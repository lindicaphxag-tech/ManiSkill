"""Actual Hugging Face SmolVLA pretrained checkpoint forward pass on REAL LIBERO RGB frames.

Separate scientific gates:
1. Resolves and pins the real Hugging Face model revision and dataset revision.
2. Loads the released SmolVLA checkpoint + real LeRobot dataset observation.
3. Performs official preprocessor -> SmolVLA.select_action -> postprocessor.
4. Records actual model output shape, finite actions and source identities.
5. DEFINITIVELY DOES NOT convert generic LIBERO/SmolVLA actions into a
   ManiSkill `pd_ee_target_delta_pose` controller ABI. No action execution.

This is a checkpoint authenticity/inference probe, NOT robot task success.
CPU-friendly one-observation smoke; fail rather than silently substitute
random weights, synthetic model inputs or fabricated policy outputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import os
import platform
import time

import torch
import numpy as np
from huggingface_hub import HfApi

MODEL_ID="lerobot/smolvla_base"
DATASET_ID="lerobot/libero"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("real_smolvla_inference_probe.json"))
    p.add_argument("--model-revision",default=None)
    p.add_argument("--dataset-revision",default=None)
    p.add_argument("--max-episodes",type=int,default=1)
    args=p.parse_args()
    if args.max_episodes!=1:
        raise ValueError("This source-frozen checkpoint probe uses exactly one original episode")
    torch.set_num_threads(min(2,os.cpu_count() or 1))
    api=HfApi()
    model_info=api.model_info(MODEL_ID,revision=args.model_revision)
    ds_info=api.dataset_info(DATASET_ID,revision=args.dataset_revision)
    model_rev=model_info.sha
    ds_rev=ds_info.sha
    if not (isinstance(model_rev,str) and len(model_rev)==40 and
            isinstance(ds_rev,str) and len(ds_rev)==40):
        raise RuntimeError("Cannot pin actual Hugging Face upstream model/dataset revisions")

    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    from lerobot.policies.factory import make_pre_post_processors
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

    t0=time.monotonic()
    policy=SmolVLAPolicy.from_pretrained(MODEL_ID,revision=model_rev).to("cpu").eval()
    t1=time.monotonic()
    preprocess,postprocess=make_pre_post_processors(
        policy.config,MODEL_ID,
        preprocessor_overrides={"device_processor":{"device":"cpu"}},
    )
    # Must load REAL frames. The model card recommends "lerobot/libero".
    # Loading only episode 0 avoids the full 40-task dataset video download.
    dataset=LeRobotDataset(DATASET_ID,episodes=[0],revision=ds_rev)
    example=dict(dataset[0])
    image_keys=sorted(k for k in example if "image" in k or "camera" in k)
    if not image_keys:
        raise RuntimeError("Real LeRobot dataset observation has no camera tensor")
    t2=time.monotonic()
    with torch.inference_mode():
        policy.reset()
        prepared=preprocess(example)
        native_generated=policy.select_action(prepared)
        after_postprocessing=postprocess(native_generated)
    t3=time.monotonic()
    if not isinstance(after_postprocessing,torch.Tensor):
        raise RuntimeError("Unrecognized LeRobot postprocessed action type")
    arr=after_postprocessing.detach().cpu().numpy()
    if arr.size==0 or not np.isfinite(arr).all():
        raise RuntimeError("Real pretrained VLA inference produced invalid actions")
    record={
      "result":"REAL_PRETRAINED_SMOLVLA_CHECKPOINT_INFERENCE_COMPLETED",
      "model_id":MODEL_ID,"actual_model_revision":model_rev,
      "dataset_id":DATASET_ID,"actual_dataset_revision":ds_rev,
      "source":"LeRobot unmodified SmolVLAPolicy.from_pretrained + real dataset episode 0",
      "policy_state":"eval/no_grad and reset before inference",
      "normalization":"Official make_pre_post_processors; not a bespoke normalizer",
      "original_camera_keys":image_keys,
      "actual_preprocessed_observation_keys":sorted(prepared.keys()),
      "postprocessed_action_shape":list(arr.shape),
      "action_count":int(arr.size),
      "postprocessed_action_min":float(arr.min()),
      "postprocessed_action_max":float(arr.max()),
      "model_download_and_init_seconds":round(t1-t0,3),
      "real_dataset_load_seconds":round(t2-t1,3),
      "real_pretrained_forward_seconds":round(t3-t2,3),
      "source_torch_version":torch.__version__,
      "machine":platform.platform(),
      "source_robots_are_compatible_with_maniskill":False,
      "controller_action_abi_provenance_verified":False,
      "native_physx_actions_dispatched":0,
      "maniskill_task_success_tested":False,
      "full_world_action_model_predicted_future_states":False,
      "clinical_or_robot_safety_certified":False,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("REAL_PRETRAINED_SMOLVLA_FROZEN_INFERENCE",json.dumps(record,sort_keys=True))


if __name__=="__main__":
    main()
