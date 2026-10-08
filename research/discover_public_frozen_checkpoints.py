"""Provenance-only, no model training: discover authentic public PPO backbones."""
import json
from huggingface_hub import HfApi
api=HfApi()
info=api.model_info("kattri15/actionshift-baselines",files_metadata=True)
rows=[]
for sibling in info.siblings:
 name=sibling.rfilename
 if name.endswith((".pt",".pth",".safetensors",".ckpt")):
  lfs=getattr(sibling,"lfs",None)
  rows.append({"file":name,"size":getattr(sibling,"size",None),
               "sha256":lfs.get("sha256") if isinstance(lfs,dict) else None})
print("FROZEN_SECOND_TASK_FILES",json.dumps({
 "repo":"kattri15/actionshift-baselines",
 "repo_commit":info.sha,
 "files":rows},indent=2,sort_keys=True))
assert rows,"No checkpoint binaries in public release"
