# Fixed prospective 32-condition empirical response experiment
Public official original PhysX run: 37832214332, source sha a68f5d8ae73ebf6ef59bd94fa949cc3fd7f8f018.
Protocol and empirical response-error thresholds: research/EMPIRICAL_RESPONSE_NEW32_FROZEN_BEFORE_RUN_V1.json, frozen BEFORE new runner.
16 PullCube and 16 StackCube task-truth combinations (8 new reset seeds each x applied/held actual execution), all original 8 JSONs + 8 raw logs + aggregate source.
Confident public-motion label 24/32, observed false confident labels 0/24, eight abstentions (including one false empirical-model envelope), task success 22/32 vs one private target read 30/32, optimistic no-read 24/32, pessimistic no-read 25/32.
**No strong safety conclusion:** controller-response enclosure is estimated from only 4 historical training seeds per task; 0 observed errors does NOT certify future action delivery. The zero-privileged-read method FAILED to match oracle task success. One new original condition falsified the empirical response envelope itself.
Original JSON and log bytes retain exact SHA-256 as pinned by trusted-main CI; no repeated same-seed model tuning or cherry-picking.
