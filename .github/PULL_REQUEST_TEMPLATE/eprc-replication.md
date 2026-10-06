# EPRC / DEC independent replication

Thank you for testing the public capsule. Positive, negative, and null results are all welcome.

## Required identity

- Policy family:
- Immutable checkpoint / commit:
- Controller representation:
- Task / environment:
- Reproduction repository / commit:

## Intervention protocol

Describe the physical support perturbations, magnitudes, seeds, and whether privileged simulator state was used.

## Evidence

Add one sealed JSON record under:

`research/eprc/evidence/replications/`

Generate its digest with:

```bash
python research/eprc/seal_replication.py path/to/record.json
```

Report:

- support stability:
- held-out residual:
- representability / support-restricted authority residual:
- DEC distance or contract class:
- emitted PASS / TRANSPORT / REPAIR / REJECT:
- actual execution outcome:
- false accept / false reject, if any:

## Independence checklist

- [ ] I am not the owner of this repository.
- [ ] The result was produced independently from the author's self-validation runs.
- [ ] I retained failed, null, and negative outcomes.
- [ ] The checkpoint and source revisions are immutable.
- [ ] The evidence record passes the repository validation workflow.

Self-authored reruns, stars, forks, or workflow runs do not count as external replication.
