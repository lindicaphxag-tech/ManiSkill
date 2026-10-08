"""Causal probe-factor experiment. Source code from the original 32-seed holdout."""
import hashlib,json,os,pathlib,re,subprocess,sys
source=pathlib.Path("research/frozen_ppo_ee_swap.py").read_text()
assert source.count("SEEDS=tuple(range(10001,10033))")==1
assert source.count("            if all(completed.values()):")==1
modes={
 "untouched":None,
 "obs_only":'for z in ("source","compiled"): observations[z].detach().cpu().numpy().copy()',
 "qpos_only":'for z in ("source","compiled"): envs[z].unwrapped.agent.robot.get_qpos().detach().cpu().numpy().copy()',
 "tcp_only":'for z in ("source","compiled"): envs[z].unwrapped.agent.tcp.pose.p.detach().cpu().numpy().copy()',
 "qpos_and_tcp":'for z in ("source","compiled"): (envs[z].unwrapped.agent.robot.get_qpos().detach().cpu().numpy().copy(), envs[z].unwrapped.agent.tcp.pose.p.detach().cpu().numpy().copy())',
}
out=pathlib.Path("probe_results");out.mkdir(exist_ok=True)
records=[]
for name,probe in modes.items():
 for repetition in range(3):
  code=source.replace("SEEDS=tuple(range(10001,10033))","SEEDS=(10014,)")
  if probe:
   instrument="            "+probe+"\n"
   code=code.replace("            if all(completed.values()):",instrument+"            if all(completed.values()):")
  temp=out/f"{name}_{repetition}.py";temp.write_text(code)
  env=os.environ.copy();env["PYTHONUNBUFFERED"]="1";env["PYTHONHASHSEED"]="0"
  cmd=[sys.executable,str(temp)]
  # In the original script, 'frozen_ppo_pickcube_gate' is imported
  # from the research/ directory containing the original source.
  env["PYTHONPATH"]=str(pathlib.Path("research").resolve())
  proc=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=300)
  raw=proc.stdout+"\n"+proc.stderr
  (out/f"{name}_{repetition}.log").write_text(raw)
  matched=re.findall(r"FROZEN_PPO_SWAP_EPISODE\s+(\{[^\n]+\})",raw)
  result=json.loads(matched[-1]) if matched else None
  row={"mode":name,"rep":repetition,"exit":proc.returncode,
       "code_sha256":hashlib.sha256(code.encode()).hexdigest(),
       "success":result.get("success_once") if result else None,
       "steps":result.get("episode_steps") if result else None,
       "initial_obs":result.get("initial_obs_maxdiff") if result else None}
  records.append(row)
  print("CST_PROBE_INTERVENTION",json.dumps(row,sort_keys=True),flush=True)
  (out/"probe_summary.json").write_text(json.dumps(records,indent=2))
  if proc.returncode or not result or result.get("seed")!=10014:
   raise RuntimeError(f"Probe arm {name}/{repetition} did not finish")
print("CST_PROBE_COMPARISON",json.dumps({
 n:{"n":len([r for r in records if r["mode"]==n]),
    "compiled_success_count":sum(r["success"].get("compiled",False) for r in records if r["mode"]==n),
    "source_step_values":sorted(set(r["steps"]["source"] for r in records if r["mode"]==n))}
 for n in modes
},sort_keys=True))
