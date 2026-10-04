# Early-experience history-carrier metadata preflight contract v1

## Status

**OUTCOME-BLIND PREFLIGHT.**

No route geometry, trajectory similarity, self-history advantage, treatment effect on route reuse, or experience slope may be calculated until this gate is passed and the exact estimator is frozen.

## Dataset

Mendeley Data v1:
`10.17632/wh7c636y3t.1`

Dataset id:
`wh7c636y3t`

## Required structural objects

The public archive must reproducibly expose enough information to link:

1. individual bat identity;
2. environmental treatment: enriched / impoverished;
3. season;
4. source colony/origin if available;
5. sex and age if available;
6. baseline behavioural measures or source-defined baseline PC/traits if available;
7. release chronology or batch/date;
8. repeated outdoor GPS movement by individual;
9. chronological night/day identity;
10. x-y or lon-lat plus time for the outdoor movement records.

## First-pass file opening rule

First pass is **metadata only**:
- dataset snapshot metadata;
- folder names;
- file names;
- file sizes;
- file hashes;
- content types.

Do not download movement files during the metadata inventory.

## Structural support floor

The history-carrier experiment opens only if:

- at least **5 enriched** and **5 impoverished** bats have outdoor movement series;
- at least **5 bats per treatment** have at least 10 usable chronological outdoor nights at the later coordinate-support gate;
- treatment identity is linkable to movement identity without inference from movement behaviour.

If either treatment has fewer than five structurally eligible bats:
**STOP**.

No treatment pooling or threshold relaxation.

## Randomization provenance

Before outcome opening, document from the peer-reviewed source that treatment assignment occurred after baseline measurement and was randomized.

If public metadata permit recovery of the exact randomization blocks (e.g. season × source colony), freeze them before outcome opening.

If exact blocks are unavailable, do not invent them; use the source-supported randomization structure that can be reproduced.

## Baseline-predisposition role

Baseline behavioural measures are optional for the randomized-treatment primary but desirable for a mechanistic secondary.

If baseline data cannot be linked to GPS identities:
- the treatment primary may still proceed;
- the predisposition-vs-experience secondary remains closed.

## No-outcome list

The preflight must not calculate:
- day-to-day spatial distance;
- self-versus-other history distance;
- route overlap;
- corridor width;
- route entropy;
- treatment difference in any new movement-history metric;
- post-release exploration effect already studied by the source paper.

## Next gate

If metadata support is adequate:

1. freeze exact file-content structural allowlist;
2. count usable individuals/nights without route comparison;
3. freeze the route-history estimator and randomization calibration;
4. only then open the new movement-history outcome.
