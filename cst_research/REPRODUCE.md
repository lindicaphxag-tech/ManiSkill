# Reproducing CST Evidence

## Research core

Checkout `research/closed-loop-semantic-transport-v1`, then:

    python -m pip install numpy pytest
    cd cst_research
    python -m pytest -q test_*.py

Latest public result at the time of this document: 46 passed.

## Focused upstream regression

The PR-ready source branch is `fix/joint-delta-to-joint-pos-pr`.

Run:

    python -m pip install -e '.[dev]'
    python -m pytest -q tests/test_pd_joint_delta_to_pos_regression.py

The public comparison workflow also checks out baseline `main`, copies the identical regression into it, and requires baseline failure plus patch pass:

https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37459621516

## Evidence hygiene

- Fork CI success is labeled public validation, not upstream adoption.
- Simulator infrastructure failures are retained rather than deleted.
- Negative method results are retained if controller execution is reached.
- No task-level success claim is made until an actual replay / simulator assay measures it.
## Bounded JIT validation

Pinned LeRobot source -> CST step-time CURRENT_STATE adapter:
- run `37464317553`: SUCCESS;
- 2,000 trajectories / 18,000 actions;
- bounded relative offsets +/-0.2;
- JIT max goal error `7.45e-9`;
- naive-copy median/p95/max per-trajectory goal error `0.555 / 0.852 / 1.152`.

Full CST research suite after JIT runtime: `46 passed`.