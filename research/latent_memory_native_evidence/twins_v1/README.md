# Native controller hidden previous target-state counterexample
Source run 37820410085, head 4d8ed412a39f4f7add6dfac0532982f3b7067c21.
Protocol frozen before implementation at 91b0166334521e660ebd7acdd11e22344608707b.
Original JSON+log copied without modification after SHA-256 checking against fixed fingerprints in archive-native-memory-twins.yml.
A/B/C worlds start with equal physical achieved pose and joint state; native controller state replay changes B/C previous targets by +0.02 m x.
A and B invert actual previous targets and agree on commanded desired target (~6.8e-9 m error).
C blindly copies A's action with B's latent target and misses desired commanded target by ~0.02 m.
This is a controlled API-legal state replay, not naturally sampled independent episodes; full observation DOES disclose target state unless source-policy projection hides it.
No robot safety, task completion improvement, random human intervention prevalence, or third-party replication is claimed.
