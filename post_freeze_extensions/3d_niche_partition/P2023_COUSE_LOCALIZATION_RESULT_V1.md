# P. hastatus 2023 co-use localization diagnostic result v1

## Status

POST-OUTCOME ROBUSTNESS DIAGNOSTIC.

This diagnostic was opened only after the corrected 2023 primary co-use result was known. It cannot replace or upgrade the frozen primary result.

Authoritative workflow:
- run: `36954565174`
- head: `c9bdb11f88f1bc9964e62de986a217f2e93cdfb8`
- artifact: `11205431379`
- digest: `sha256:f76edfc16c8030f3e96397c50c76050144c8cc38d14d6cb01eab27e3316470b6`

## Primary reference

- observed separation: 26.57 m
- phase-null mean: 22.99 m
- excess: +3.57 m
- p = 0.0231

## Leave-one-dyad-out sensitivity

All eight frozen dyads were removed one at a time without reselecting support.

| removed dyad | excess | sensitivity p |
|---|---:|---:|
| 562–592 | +3.25 m | 0.0283 |
| 563–573 | +3.85 m | 0.0279 |
| 563–588 | +4.29 m | 0.0149 |
| 563–637 | +5.34 m | 0.0055 |
| 573–588 | +1.14 m | 0.2332 |
| 573–637 | +3.92 m | 0.0274 |
| 588–592 | +4.04 m | 0.0238 |
| 588–637 | +2.76 m | 0.0724 |

Six of eight leave-one-dyad-out variants retain p<0.05.

The signal is therefore **not a single-dyad artifact**, but it is not uniformly distributed across dyads. Removing dyad 573–588 weakens the excess substantially, and removing 588–637 also moves the sensitivity result above 0.05.

The dyad with by far the largest encounter count (563–573; 586 of 679 encounters) can be removed while the sensitivity result remains p=0.0279. Therefore the panel result is not driven by simple event-count dominance from that dyad.

## Endpoint-excluded descriptive sensitivity

The frozen endpoint-excluded 2023 universe contains only four usable individuals, below the predeclared five-individual inferential gate, so no PASS/FAIL is assigned.

Descriptively:
- 6 dyads
- 629 encounters
- observed separation 23.64 m
- phase-null mean 19.83 m
- excess +3.81 m
- empirical upper-tail location 0.011
- 95.31% of encounter endpoints belong to shiftable phase groups

Thus the positive direction does not disappear when endpoint-associated encounters are removed.

This argues against the signal being solely a departure/arrival or endpoint artifact, but the sensitivity remains non-inferential because biological replication falls below the frozen gate.

## Interpretation

The 2023 signal is best described as:

> **a context-dependent, dyad-heterogeneous co-presence separation signal.**

It is:
- broader than one high-count dyad;
- not obviously confined to endpoint-associated encounters;
- but sensitive to which dyads are represented.

This pattern is compatible with interaction-dependent heterogeneity, but does not uniquely identify competition.

## Claim ceiling

Do not claim:
- uniform vertical avoidance among individuals;
- population-wide competition-driven partitioning;
- independent replication from leave-one-out p-values;
- confirmatory endpoint-excluded support.

Allowed:
- the primary 2023 signal is not reducible to the single high-count dyad;
- interaction-dependent separation appears heterogeneous among dyads;
- the positive direction persists descriptively after endpoint exclusion.
