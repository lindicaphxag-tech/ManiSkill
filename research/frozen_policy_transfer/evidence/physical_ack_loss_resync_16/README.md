# Real PhysX frozen PPO unknown-ACK and single authoritative readback recovery
Source: GitHub Actions 37822693649, fixed head 46c16f56235c68a6823450ae9823ae44e32125b0.
Pre-outcome protocol: research/ACK_LOSS_PHYSX_RESYNC_PRECOMMIT_V1.json in original branch.
PullCube 85001–85008: source/live-memory/recovered-observer 8/8; matched memory-blind projection 5/8.
StackCube 95001–95008: source/live-memory/recovered-observer 8/8; matched memory-blind projection 0/8.
In all 16 states an action physically executed, its acknowledgement to the observer was made unknown,
the observer refused further action, and a SINGLE privileged native target-state readback resynchronized it.
This IS NOT physical actuator packet-loss recovery, autonomous sensing, independent external replication,
a robotics safety guarantee, or evidence that unknown delivery can be resolved without new information.
Source JSON bytes are copied unchanged; manifest hashes are recorded.
