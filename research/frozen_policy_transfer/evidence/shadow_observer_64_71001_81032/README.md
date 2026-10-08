# Original complete 64-state shadow target-memory observer evidence
This is an author-run genuine ManiSkill PhysX frozen-policy test, NOT an independent third-party simulation or real robot safety proof.
Frozen source protocol: ed979138bed2cd4ac6b3e5c4137799ce7c73711a, Git blob 285a7457e4aa05240b970e5550bcf06942535ceb.
Successful ORIGINAL exact-head CI: 37818985343, commit f2bee90ef7ff2550351f579056688bd441044857.
Original 9-JSON archive artifact: GitHub Actions artifact 11568143703, ZIP digest sha256:f5164ebe8e2ddf0db0acb0cefa5f11f90ac02ad39743959a19fda06829fb3420.
All nine JSON files are COPIED byte-for-byte from that artifact, not recreated from narrative reports. SHA256SUMS pins their content.
PullCube seeds 71001–71032: source 32, naive 12, state-blind 12, exact-only/refuse 13, live bounded 32, history-reconstructed shadow bounded 32.
StackCube seeds 81001–81032: source 29, naive 1, state-blind 1, exact-only/refuse 14, live bounded 29, shadow bounded 29.
Every original binary paired shadow/live success agrees, with zero discordants in both tasks. Native target-state reconstruction error in the simulator is zero at recorded precision, but this 'shadow' runner STILL uses source controller target transformation code and checks the observation memory slice; it is NOT a fully private-state-blind implementation.
See the separate stronger, acknowledged-action-only observer in ManiSkill research/action_abi_history_observer.py and its distinct 16-state prospective study.
Bounded projected action is NOT_EXACT. All performance results are limited to the same Panda controller-family semantic mismatch.
