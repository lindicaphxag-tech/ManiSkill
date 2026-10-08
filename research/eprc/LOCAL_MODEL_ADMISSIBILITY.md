# Two-axis local-model admissibility

The prospective five-state VQ-BeT experiment falsified a tempting shortcut:
**repeatability and locality are not interchangeable notions of uncertainty.**

The two gates answer different questions:

1. **DEC stability** — do repeated black-box probes identify the same local map?
2. **scale locality** — does the estimated first-order map converge as the
   physical intervention radius shrinks?

The frozen state set produced all four combinations:

| seed | q95 DEC radius | DEC stable | contraction ratio | locality contracts | admissibility |
|---:|---:|:---:|---:|:---:|---|
| 101 | 1.43245 | no | 0.35086 | yes | INFORMATION_LIMITED |
| 211 | 0.00000 | yes | 0.65506 | yes | ADMISSIBLE_FIRST_ORDER |
| 307 | 0.18009 | no | 0.66487 | yes | INFORMATION_LIMITED |
| 401 | 0.00000 | yes | 0.90908 | no | LOCALITY_LIMITED |
| 503 | 0.46941 | no | 2.77197 | no | REJECT_LOCAL_MODEL |

Frozen thresholds were unchanged:

- DEC q95 stability threshold: 0.15;
- locality contraction threshold: 0.75.

## Runtime consequence

A single scalar "uncertainty" cannot choose the right next action.

```text
                     locality contracts
                    yes               no
DEC stable   yes   FIRST-ORDER       LOCALITY-
                   ADMISSIBLE        LIMITED

             no    INFORMATION-      REJECT
                   LIMITED           LOCAL MODEL
```

Only the upper-left quadrant may authorize a first-order repair certificate.

- **INFORMATION_LIMITED:** more/reoriented repeated evidence can still be useful.
- **LOCALITY_LIMITED:** additional same-scale repeats are wasteful; the model
  class or intervention scale must change.
- **REJECT_LOCAL_MODEL:** neither path is justified.
- **ADMISSIBLE_FIRST_ORDER:** proceed to the CRG repairability certificate,
  which may still return REPAIR / IMPOSSIBLE / INCONCLUSIVE.

## Prospective jet result

The separately frozen response-jet experiment produced **0 jet rescues out of
5 states**, so its preregistered adjudicator returned:

`DROP_JET_FROM_FLAGSHIP`.

That negative result is retained. The project therefore does not use a
higher-order local model to rescue failed first-order cases.

## Claim discipline

The four-way table is currently a result on five frozen VQ-BeT PushT states,
not a universal taxonomy theorem.

The publishable hypothesis is narrower:

> separating repeated-probe identifiability from scale-locality produces better
> evidence routing than collapsing both into one uncertainty score.

A future comparison must test whether this two-axis router reduces wasted
policy queries and false repair authorization versus scalar uncertainty
baselines on disjoint states and a second policy family.
