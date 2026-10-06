# Prospective multi-state response-jet result — 2026-10-06

The five-state gate in `PROSPECTIVE_MULTISTATE_JET_GATE.md` was frozen before
execution. Its promotion rule was:

- 0 jet rescues -> `DROP_JET_FROM_FLAGSHIP`;
- 1-2 rescues -> `KEEP_AS_SECONDARY_MECHANISM`;
- >=3 rescues -> `PROMOTE_TO_BROADER_PROSPECTIVE_TEST`.

## Frozen outcomes

| PushT reset seed | First-order locality route | Held-out jet improvement ratio | Jet upgrade |
| ---: | --- | ---: | --- |
| 101 | REFINED_FIRST_ORDER_CERTIFICATE | 0.9206756 | false |
| 211 | REFINED_FIRST_ORDER_CERTIFICATE | 1.1416062 | false |
| 307 | REFINED_FIRST_ORDER_CERTIFICATE | 0.7602857 | false |
| 401 | REJECT_FIRST_ORDER_LOCAL_MODEL | 0.9380329 | false |
| 503 | REJECT_FIRST_ORDER_LOCAL_MODEL | 1.0313905 | false |

Frozen jet acceptance required improvement ratio <= 0.5 plus the relative-error
gate. No state passed.

Aggregate adjudication:

- first-order contracting states: **3/5**;
- first-order rejected states: **2/5**;
- jet upgrades: **0/5**;
- jet rescues: **0/5**;
- final promotion decision: **DROP_JET_FROM_FLAGSHIP**.

The adjudicator workflow completed successfully. The result is retained as a
negative prospective result rather than tuned away.

## Interpretation

A two-scale centered-response jet did not justify higher model order on this
frozen state bank. More model complexity therefore does not become part of the
flagship method.

The surviving flagship question is stronger and simpler:

> can the runtime identify whether its current local physical model is
> sufficiently supported to certify repair, and fail closed when locality does
> not hold?

The negative jet result increases confidence in keeping model-order escalation
optional rather than turning it into a mandatory part of CRG.

## Evidence boundary

This is self-authored prospective evidence, not external validation. It does not
satisfy the independent replication gate and contributes zero external-adoption
credit.
