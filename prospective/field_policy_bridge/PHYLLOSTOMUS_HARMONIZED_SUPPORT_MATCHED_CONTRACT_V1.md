# Harmonized support-matched 2022→2023 diagnostic v1

## Status

**POST-OUTCOME BOUNDARY DIAGNOSTIC. CANNOT RESCUE THE FROZEN FIELD GATE.**

Frozen after the 360-s measurement harmonization result showed:

- 2022 I360: H = +0.3580, 14/15 positive, p = 0.0001;
- 2023 I360: H = +0.05566, 3/6 positive, p = 0.2176;
- the original strongly negative 2023 carrier therefore became weakly positive after common-lag harmonization.

## Question

Is the remaining 2022→2023 difference in harmonized I360 plausibly explained by the much smaller 2023 repeated-individual support?

## Target support

Derive from the already-frozen 2023 harmonization-valid I360 rows:

- number of eligible individuals;
- the exact multiset of harmonization-valid session counts per eligible individual.

Do not use I360 values to define support.

Expected top-level support is:
- 6 individuals;
- 25 sessions total.

If this structural support differs, STOP.

## Donor pool

Use exactly the harmonization-valid 2022 rows produced by
`phyllostomus_measurement_harmonization_v1.py`.

Use only individuals with >=2 harmonization-valid sessions.

No donor is selected by H or I value.

## Pseudo-panel construction

For each accepted replicate:

1. choose 6 distinct 2022 donor individuals uniformly without replacement;
2. randomly permute the exact 2023 session-count multiset across those six donor identities;
3. reject the proposal if any donor has fewer available sessions than its assigned target count;
4. otherwise sample the assigned number of sessions uniformly without replacement within donor;
5. pool the sampled raw 4-feature I360 vectors;
6. recompute cohort mean/SD on the sampled pseudo-panel only;
7. define I360 exactly as the mean of the four z-scored features;
8. calculate the exact held-out self-history H statistic with equal-individual aggregation.

Thus each accepted pseudo-panel has exactly the same number of individuals and the same per-individual session-count multiset as harmonized 2023.

## Monte Carlo

Target:
- 9,999 accepted pseudo-panels.

Seed:
`202610051431`.

Attempt ceiling:
- 1,000,000 proposals.

If fewer than 9,500 accepted, STOP.

## Outputs

Report the 2022 support-matched distribution of:

- H;
- positive-individual fraction.

Compare against the observed harmonized 2023 values:

- H_2023 = +0.055658227354875606;
- positive fraction = 0.5.

Report:
- median and 2.5/97.5% quantiles of matched 2022 H;
- fraction H <= H_2023;
- fraction H <= 0;
- matched positive-fraction median and interval;
- fraction positive fraction <= 0.5.

## Interpretation

### 2023 lies comfortably inside matched 2022 distribution

The post-harmonization year difference is compatible with support limitation; the original strong negative reversal was primarily observation-process dependent.

### 2023 remains far below matched 2022

Even after common-lag harmonization and support matching, year/context dependence remains plausible.

## Ceiling

This is a post-outcome diagnostic.

It cannot:
- reclassify the frozen 2023 panel;
- reopen the 3-of-4 field carrier gate;
- prove that 2022 and 2023 ecology was identical.
