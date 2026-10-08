# Frozen-PPO bounded-or-query: two *actual* controller execution truths
Original 4-job real PhysX run (not an outside independent lab):
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828787703
Exact running code head: 3d61c625fcc8ca88a22817276562d0fdc4447067.
The prospectively frozen condition/seed/budget contract and its outcomes are unchanged.
Actual applied arm command vs actual neutral native arm command are separately simulated
with unknown ACK, four matched groups x eight original seeds, two fixed external PPOs.
Summary: selective bounded-or-query 28/32 official task success vs mandatory one-read 29/32;
one READ is used in 10/32 compared with 32/32 always-query (68.75 percent reduction).
Per-pair discordance selective-only 1, mandatory-only 2. Do not claim equal success.
Source conditions: Pull applied 8/8 vs always 8/8, Pull held 8/8 vs always 8/8;
Stack applied 6/8 vs always 7/8; Stack held 6/8 vs always 6/8.
The neutral-held task/seeds 142001-142008 and 152001-152008 overlap the separate
64-state validation source on these same reset seeds (Actions 37828426195).
NEVER combine these overlapping episodes as independent extra holdout observations.
This is conditional native-controller COMMAND TARGET error, not robot task-safety,
hardware network packet-loss handling or independently reproduced scientific adoption.
Study's most important failure: StackCube applied seed 152001 authorized 47
robust common commands (no readback), failed the task; mandatory query succeeded.
Geometric tolerance is NOT task-success sufficiency, especially near contact.
