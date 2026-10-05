# Policy-distance/co-use leave-one-individual robustness contract v1

## Status

**POST-OUTCOME ROBUSTNESS DIAGNOSTIC — frozen before leave-one-individual correlations are calculated.**

Parent:
`POLICY_DISTANCE_COUSE_SEPARATION_CONTRACT_V1.md`

The full-sample dyadic association has already been defined. This robustness cannot redefine the primary and cannot turn an unsupported primary into a confirmatory result.

## Question

Could one biological individual with several unusual dyads mask an otherwise strong positive relationship between persistent policy distance and synchronous vertical separation?

Because dyads share individuals, arbitrary dyad deletion is not allowed.

The only sensitivity is biological-node deletion.

## Data

Analyse separately:
- *P. hastatus* 2022;
- *P. hastatus* 2023.

Use exactly:
- the same persistent H/V individual policy centroids;
- the same frozen co-use dyads;
- the same observed dyad median vertical-separation endpoint;
- the same cohort mapping.

No dyad, encounter, policy axis or synchronization rule is changed.

## Leave-one-individual set

For every biological individual that occurs in at least one eligible co-use dyad:

1. remove that individual;
2. remove every dyad incident to it;
3. retain all remaining eligible dyads;
4. require at least 5 dyads;
5. recompute Spearman rho between policy distance and observed vertical separation.

Report every admissible deletion.

## R1 — maximum deletion-rescued coupling

Define:

[
T_{max}
=
\max_i \rho_{(-i)}.
]

This is deliberately the most favorable one-individual deletion for the positive-coupling hypothesis.

## Selection-corrected null

Within each frozen cohort:
- permute complete individual H/V policy centroids among biological individual labels;
- keep the co-use network and separation outcomes fixed;
- for each permutation, repeat the **entire** leave-one-individual scan;
- record the maximum admissible (ho_{(-i)}).

Use:
- 9,999 permutations;
- 2022 seed `202610052201`;
- 2023 seed `202610052202`.

One-sided max-statistic p:

[
p_{max}
=
P(T_{max,null}\ge T_{max,obs}).
]

Require >=9,500 valid max statistics.

## R2 — full deletion profile

Descriptively report:
- n admissible individual deletions;
- minimum rho;
- median rho;
- maximum rho;
- fraction > 0;
- fraction >= 0.3;
- identity of the deletion yielding the maximum.

These are robustness descriptors, not separate significance tests.

## Interpretation

### Selection-corrected max p <= 0.05

A positive policy-distance/separation association is hidden by at most one biological individual.

This remains post-outcome robustness and does not replace the full-sample primary.

### Selection-corrected max p > 0.05

No one-individual deletion yields positive coupling stronger than expected when the most favorable deletion is selected under the exchangeability null.

Allowed wording:

> **The absence of a positive full-sample policy–space relationship is not rescued by deleting any single biological individual.**

Do not call this equivalence to zero.

## No rescue

Do not:
- drop two or more individuals;
- delete dyads based on separation;
- use a different policy axis;
- choose a colony/year subset after seeing R1;
- report the uncorrected p-value for the most favorable deletion.
