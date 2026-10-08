"""Re-run unchanged frozen PPO holdout code on seed 10014 in isolated processes."""
import json, os, pathlib, re, subprocess, sys
out=pathlib.Path("repeatability_artifacts"); out.mkdir(exist_ok=True)
code="""
import random, numpy as np, torch, os, sys
sys.path.insert(0,'research')
if os.environ['SEED_ALL_RNG']=='1':
 random.seed(10014); np.random.seed(10014); torch.manual_seed(10014)
import frozen_ppo_ee_swap as m
m.SEEDS=(10014,)
m.main()
"""
rows=[]
for mode in (0,1):
 for rep in range(6):
  env=os.environ.copy(); env["SEED_ALL_RNG"]=str(mode); env["PYTHONUNBUFFERED"]="1"
  result=subprocess.run([sys.executable,"-c",code],env=env,
                        capture_output=True,text=True,timeout=300)
  output=result.stdout+"\n"+result.stderr
  (out/f"mode{mode}_rep{rep}.log").write_text(output)
  matches=re.findall(r"FROZEN_PPO_SWAP_EPISODE\s+(\{[^\n]+\})",output)
  record=json.loads(matches[-1]) if matches else None
  row=dict(mode=mode,rep=rep,exitcode=result.returncode,record=record)
  rows.append(row)
  (out/"repeatability.json").write_text(json.dumps(rows,indent=2))
  print("REPEATED_10014",json.dumps(row,sort_keys=True),flush=True)
  if result.returncode or not record or record["seed"]!=10014:
   raise RuntimeError("Repeated-run missing or failed")
print("REPEATABILITY_SUMMARY",json.dumps({
 "n":len(rows),
 "compiled_successes":sum(r["record"]["success_once"].get("compiled",False) for r in rows),
 "source_steps":sorted(set(r["record"]["episode_steps"]["source"] for r in rows)),
 "compiled_steps":sorted(set(r["record"]["episode_steps"]["compiled"] for r in rows))
}))
