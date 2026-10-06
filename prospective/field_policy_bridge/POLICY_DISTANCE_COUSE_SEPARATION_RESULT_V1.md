# Policy distance versus synchronous co-use separation result v1

## Status

**NO POSITIVE POLICY-DISTANCE / SPATIAL-SEPARATION ASSOCIATION IN EITHER YEAR.**

**Evidence provenance:** the H/V coordinates used here are post-outcome diagnostics. This downstream analysis is conditional on that exploratory representation and cannot establish the general wild carrier-to-space bridge. See `FIELD_EVIDENCE_PROVENANCE_GUARD_V1.md`.

Authoritative implementation:
`policy_distance_couse_separation_receipt_v2.py`

Authoritative workflow:
- run: **37296670608**
- job: **111719404182**
- head: `3c467b0d3a049fb2b7c133d5eed5781d620be8e9`
- conclusion: **success**
- 9,999/9,999 valid permutations per year

This receipt-only implementation reads the already frozen co-use dyad endpoint receipt and therefore does not reconstruct or alter encounter geometry.

A later dynamic reconstruction workflow displayed false-green status because a dependency was missing and `tee` masked the Python failure. It is not the evidentiary source for the values below.

## Question

Do biological dyads that differ more strongly in persistent two-dimensional H/V movement policy remain farther apart vertically when they actually co-use the same local space?

Primary predictor:

[
D^{policy}_{ij}=||\boldsymbol\theta_i-\boldsymbol\theta_j||_2.
]

Outcome:
the authoritative frozen dyad median of synchronous, session-centered, terrain-relative vertical separation.

The permutation null shuffles complete individual policy coordinates among biological identities within cohort while preserving:
- the frozen dyad network;
- observed dyad separations;
- policy-coordinate values;
- cohort membership.

## 2022

Frozen policy-matched dyads: **10**

Observed Spearman association:

[
\rho=+0.18788.
]

Permutation:
- null mean = **−0.00134**
- null central 95% = **[−0.5273, +0.5758]**
- one-sided p = **0.2743**

Verdict:
`NO_POSITIVE_POLICY_DISTANCE_SEPARATION`

## 2023

Frozen policy-matched dyads: **8**

Observed:

[
\rho=-0.19048.
]

Permutation:
- null mean = **+0.00329**
- null central 95% = **[−0.6905, +0.7143]**
- one-sided p = **0.6887**

Verdict:
`NO_POSITIVE_POLICY_DISTANCE_SEPARATION`

## Biological interpretation

Persistent policy differentiation and synchronous spatial separation are not monotonically coupled in either year.

This matters especially in 2023:
- the separate panel-level co-use analysis detected a positive synchronous vertical-separation excess;
- nevertheless, dyads farther apart in persistent H/V policy space are **not** the dyads that separate more strongly.

Therefore the data separate:

[
\boxed{
\text{persistent policy differentiation}
\neq
\text{pairwise spatial partitioning}
}
]

at the level of the same biological dyads.

## What this result does not prove

The test does not establish:
- exact zero association;
- absence of all resource partitioning;
- absence of competition;
- absence of nonlinear policy-to-space mappings;
- absence of coupling at a different spatial or temporal scale.

The dyad sample is small, especially in 2023.

For that reason a separately frozen leave-one-biological-individual max-statistic sensitivity tests whether one bat masks an otherwise positive relationship.

## Provenance

2022 authoritative co-use source artifact:
- artifact ID **11204898247**
- encounter set and artifact SHA are pinned in `COUSE_DYAD_ENDPOINT_RECEIPT_V1.json`.

2023 authoritative source artifact:
- artifact ID **11205525158**
- artifact SHA256 **4e0ecee59e8c4269b1b93fd062cddb0fe87a8b4d0b0c4b18edf186d75a4df80a**.

The receipt-only analysis does not alter:
- encounter definitions;
- synchronization windows;
- terrain correction;
- dyad medians;
- policy axes;
- policy-centroid construction.

## Claim ceiling

Allowed:

> **In two free-ranging P. hastatus panels, persistent pairwise movement-policy distance did not predict greater synchronous vertical separation.**

Stronger language such as equivalence, independence, or absence of ecological interaction is not supported.
