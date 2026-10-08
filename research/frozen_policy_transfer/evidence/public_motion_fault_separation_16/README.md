# Original, owner-operated frozen-PPO PhysX two-world public-motion evidence
Source actual PhysX run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826808073
Exact head: 4b0128e37b04332464d79d320f23a12697ea9932
Pre-outcome protocol: research/PUBLIC_MOTION_FAULT_IDENTIFIABILITY_PRECOMMIT_V1.json
Both original full-denominator source JSONs are copied unchanged, SHA256 manifest included.
PullCube: 8 untouched states, minimum maximum-joint-qpos separation at fault 0.025806 rad; after four identical commands >=0.065704 rad.
StackCube: 8 untouched states, minimum maximum-joint-qpos separation at fault 0.021964 rad; after four identical commands >=0.062899 rad.
Important: identical simulator initial conditions, known controller model, and counterfactual paired worlds.
The publicly permitted qpos and qvel differ; the hidden commanded-target field was excluded from measurements.
These results demonstrate DESCRIPTIVE physical-state distinguishability between executed and neutral-held paths.
They DO NOT demonstrate a valid causal online fault classifier from one noisy real trajectory, an adaptive probe policy,
a learned correction, reliable ROS packet timing, hardware safety, or independent third-party execution.
