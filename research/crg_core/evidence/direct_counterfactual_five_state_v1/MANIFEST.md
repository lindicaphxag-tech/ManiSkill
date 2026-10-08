# Frozen PushT full-request response: five-state evidence manifest

**Data owner:** lindicaphxag-tech. **Original run:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37808323459  
**Protocol frozen before runner:** 5333216603586adfc6e4831df3c17ead48581a48  
**Runtime and source:** https://github.com/lindicaphxag-tech/ManiSkill/pull/53  
**Evidence export (all six original files):** Actions artifact `crg-direct-counterfactual-5state-original-evidence` on the original successful run.

## Scope and prior commitment

5 complete restored PushT states, 10 paired A/B physical requests, two
precommitted groups of three stochastic policy seeds per request,
240 actual official Diffusion/VQ-BeT first-action model evaluations.

The intervention is a simulator state oracle, not a robot repair trial.
The protocol explicitly lacks a proven hard action-output bound.
Therefore **certified transfer authorizations are zero**, full closed-loop
task outcomes were not measured, and this is not independent replication.

## Byte-level SHA-256 provenance

| File | SHA-256 |
|---|---|
| direct_counterfactual_result.json | `57ccb088e82a1bee48b132bf3a8ffe97dcae818e02cf2f133dbd2dd8eddae22e` |
| state-311.json | `928a57807960a49e10968d6ca65dc1d991cef3b3ad1538c977d734922460421d` |
| state-313.json | `54df98e940fe1718e8b2ff3c3135dbb485b87a18060d23753d73f014c99a1b0b` |
| state-317.json | `f7cdeb18271a38ea9df0d41c636eb655fa909fd9832b527763380d0f036c06e2` |
| state-331.json | `346956381c80eda455a65f275c26ead26c9cdc4a5dfc1af05439a4002c0931a5` |
| state-337.json | `fad347bf46a0f2da5bf7010c460c1155377b1fa0f43896e98922f3903f69d047` |

Aggregate frozen protocol SHA-256:
`bb7ef7a67d25bc9c8f3587517113d8f226161c6369cccdb27ea03d00d32248ec`.

## Independently reconstructed exploratory diagnostic

| State | Request | Three-seed screening mean gap | Separate three-seed audit mean gap |
|---|---|---:|---:|
| 311 | A | 2.502443 | 2.447847 |
| 311 | B | 7.044805 | 6.907834 |
| 313 | A | 1.766567 | 1.744145 |
| 313 | B | 1.388546 | 1.278448 |
| 317 | A | 1.970020 | 2.037607 |
| 317 | B | 2.297122 | 2.562353 |
| 331 | A | 0.816440 | 0.634146 |
| 331 | B | 3.672509 | 3.527052 |
| 337 | A | 0.681136 | 1.008056 |
| 337 | B | 1.065039 | 1.096800 |

At the frozen response tolerance 1.0, the *untrusted* screening
means would authorize 2/10 requests. One of those 2 (337/A) is
not below tolerance in the independently seeded audit mean. This is
**one exploratory sample-mean threshold discordance, not a measured
false authorization against a known true mean**. With only three
stochastic seeds in each group, the audit is not ground truth.
A third-party observer should not reinterpret the discordance as
collision risk, field safety, or estimated real deployment utility.

The exact archives, not rounded summary values, are the official evidence.
The archive workflow replays original JSON and checks static SHA-256
before attempting a permanent Git commit. Commit persistence is not
claimed until that downstream write job actually succeeds.
