# One-command CPU reproduction — LeRobot semantic self-consistency blind spot

From the root of this validation branch:

```bash
bash validation/crossstack/reproduce_lerobot_cpu.sh
```

The script:

1. fetches only the pinned upstream source file from `huggingface/lerobot@8c920c4270460851cedd2737657584586d3dc66f`;
2. AST-checks that the forward and inverse helpers still use the audited positional-prefix contract;
3. runs the explicit non-prefix state/action witness;
4. runs the deterministic 32-case sweep;
5. writes `lerobot_mapping_compensation.json`.

No GPU, simulator, LeRobot installation, or model checkpoint is required.

Expected frozen result is **not** an acceptance criterion. A useful independent reproduction may disagree.

Please report:

- OS / Python version;
- exact script revision;
- raw JSON;
- any network/source deviation;
- agreement / disagreement / null result.

Current independent third-party reproduction count: **0**.
