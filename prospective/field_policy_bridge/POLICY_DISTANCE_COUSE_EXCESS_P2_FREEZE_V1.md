# Policy distance versus dyad excess separation — P2 recovery implementation freeze v1

## Status

**IMPLEMENTATION FREEZE FOR THE ALREADY-PREDECLARED P2 ENDPOINT.**

Parent:
`POLICY_DISTANCE_COUSE_SEPARATION_CONTRACT_V1.md`

The parent contract already specified:

[
E_{ij}=S^{obs}_{ij}-E_0[S_{ij}]
]

and a positive rank association between persistent policy distance and dyad-specific excess synchronous separation, conditional on recoverability of authoritative dyad-level phase-shift null means.

The receipt-only primary could not evaluate P2 because the archived co-use artifact exposed observed dyad medians but not dyad-level phase-shift null means.

This implementation freeze defines how to recover those means **without changing the frozen co-use design**.

## Panels

Analyse separately:
- `phyllostomus_2022`;
- `phyllostomus_2023`.

No pooling.

## Co-use reconstruction

Reuse exactly the authoritative implementation in:

`post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py`

including:
- frozen x-y-time encounter receipt;
- 500-m cells;
- panel-specific synchronization tolerance;
- primary endpoint/all-space scope;
- terrain-relative, session-centered vertical endpoint;
- frozen phase groups;
- frozen circular-shift null;
- frozen B and seed.

Before opening/reusing vertical endpoints, require:
- encounter SHA equals the frozen receipt;
- encounter count equals the frozen receipt;
- dyad count equals the frozen receipt.

No encounter may be added or removed.

## Dyad-specific null mean

For every frozen permutation b:

1. draw the exact same group-level circular shifts as the co-use primary;
2. compute shifted endpoint values;
3. compute the median absolute vertical separation separately for every frozen dyad.

For dyad d:

[
ar S_{0,d}
=
rac1B sum_b S^{(b)}_d.
]

Then:

[
E_d=S^{obs}_d-ar S_{0,d}.
]

The panel-level mean of (ar S_{0,d}) must reproduce the authoritative primary panel null mean to numerical precision.

The equal-dyad mean of (E_d) must reproduce the authoritative panel calibrated excess.

If either cross-check fails:
`STOP_DYAD_NULL_RECONSTRUCTION_DRIFT`.

## Policy distance

Use exactly the already-frozen bivariate H/V policy centroid:

[
D^{policy}_{ij}=||\boldsymbol\theta_i-\boldsymbol\theta_j||_2.
]

No alternate axis or distance is selected.

## P2 statistic

Within each year:

[
\rho_E
=
Spearman(D^{policy}_{ij},E_{ij}).
]

Require >=5 policy-matched frozen dyads.

## Policy-label null

Reuse the parent-contract policy permutation:

- within each cohort, permute complete individual H/V policy coordinates among biological individual labels;
- keep the frozen dyad network, observed separations, and dyad null means fixed;
- recompute policy distances and (ho_E).

Permutations:
**9,999**.

Seeds:
- 2022: `202610052301`
- 2023: `202610052302`

Require >=9,500 valid statistics.

One-sided p for positive policy-distance/excess-separation coupling.

## Interpretation

### Positive supported P2

Persistent movement-policy differentiation partly predicts **additional** synchronous spatial separation above each dyad's phase-shift baseline.

### Unsupported P2

> **Policy differentiation does not monotonically identify which dyads exhibit extra co-presence-dependent vertical separation above their own frozen phase-shift baseline.**

This is stronger than the raw-separation primary because dyad-specific baseline separation has been removed.

## Claim ceiling

Even an unsupported P2 does not establish:
- exact zero coupling;
- absence of nonlinear coupling;
- absence of competition;
- absence of resource partitioning;
- independence at other scales.

## No rescue

Do not:
- change circular-shift rules;
- change synchronization windows;
- use mean rather than frozen dyad median;
- select a subset of dyads;
- change the H/V policy representation;
- switch to a two-sided test after output.
