# First genuinely executed 128 full-SE3 anchored repair PhysX worlds
Genuine first-run source: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37993147659
Source SHA: da75e908038f6315785ffd840a0938053d3b8ab8, run attempt 1.
All four physical execution shards passed. Original aggregate audit failed because the
otherwise unused source-only aggregation job lacked the gymnasium import dependency.
No physics was rerun to conceal that failure. An independent CI recovery installs the
missing dependency and checks the four ORIGINAL run's full raw data and matched prefix.
Each of 16 independent robot/reset seeds is repeated in eight correlated
ACK truth x probe x repair arm conditions = 128 physically executed worlds.
Both repair methods receive the same oracle ACK truth; this tests a fixed t1
commanded-target full-SE3 repair semantic, NOT online recognition, policy
task success, safe robot certification, external replication or upstream merge.
Original source, log and environment files are byte-preserved; original
JSONs plus regenerated review are accompanied by exact SHA256 checksums.
