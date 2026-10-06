# Manual submission commands

The connected GitHub integration cannot create forks in external repositories.
Once the public handoff CI is green, the remaining steps are mechanical.

```bash
git clone https://github.com/huggingface/lerobot.git
cd lerobot
git checkout d40e8709cffb93644db66e30604ef50fdec003cb
git switch -c feat/act-relative-actions

git apply /path/to/lerobot_act_relative_actions.patch
git diff --check

python -m pip install -e .
python -m pip install pytest
python -m pytest -q tests/processor/test_act_processor.py --tb=short

git add src/lerobot/policies/act/configuration_act.py \
        src/lerobot/policies/act/processor_act.py \
        tests/processor/test_act_processor.py

git commit -s -m "feat(act): support relative actions through shared processor pipeline"
```

Then push the branch to your LeRobot fork and open a PR against
`huggingface/lerobot:main` using
`LEROBOT_ACT_RELATIVE_ACTIONS_PR_BODY.md`.

Do not claim merge/adoption before the upstream PR is retained by maintainers.
