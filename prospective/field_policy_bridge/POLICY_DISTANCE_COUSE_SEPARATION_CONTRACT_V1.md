# Pairwise policy distance versus synchronous vertical separation contract v1

## Status

**POST-OUTCOME MECHANISM DIAGNOSTIC.**

Frozen after:
- P. hastatus 2022 and 2023 showed persistent fixed-bin 2-D (H,V) policy carriers;
- synchronous co-use vertical separation had already been analysed under its frozen encounter architecture;
- 2022 showed no additional synchronous vertical separation;
- 2023 showed one context-dependent positive separation signal.

No pairwise policy-distance/separation association has yet been calculated.

## Question

Do dyads that differ more strongly in their persistent movement policy also remain farther apart vertically when they occupy the same 500-m cell at the same time?

This directly tests whether **policy differentiation is expressed as spatial partitioning**.

## Panels

Analyse separately:
- P. hastatus 2022;
- P. hastatus 2023.

Do not pool years.

## Persistent policy coordinate

Use exactly the fixed-bin 360-s bivariate policy carrier:

[
oldsymbol	heta_i=(H_i,V_i)
]

where H and V are the frozen standardized horizontal- and vertical-intensity components.

For each individual:
- average session H,V equally over all policy-valid sessions in that year/cohort;
- no co-use outcome enters (oldsymbol	heta_i).

For dyad (i,j):

[
D^{policy}_{ij}=||oldsymbol	heta_i-oldsymbol	heta_j||_2.
]

Also report the transparent allocation-axis distance

[
D^{alloc}_{ij}=|A_i-A_j|,quad A=(H-V)/sqrt2
]

as a descriptive secondary.

## Co-use separation endpoint

Reuse the **authoritative frozen dyad medians** from
`COUSE_VERTICAL_SEPARATION_RESULT_V1.md` / its corrected workflow.

For each structurally usable dyad:
- outcome = observed median absolute session-centered terrain-relative vertical separation in metres;
- no new encounter definition, synchronization window or support threshold is introduced.

Only dyads for which both individuals have eligible policy coordinates are retained.

## P1 — rank association

Within each panel, compute Spearman correlation across eligible dyads between:
- primary: D_policy and observed dyad vertical separation;
- secondary: D_alloc and observed dyad vertical separation.

The biological prediction under policy-as-partition is positive.

## P2 — excess-separation association

Where authoritative dyad-level phase-shift null summaries are recoverable, define:

[
E_{ij}=S^{obs}_{ij}-E_0[S_{ij}]
]

using the dyad's null mean under the already-frozen synchrony-destruction null.

Then correlate D_policy with E_ij.

If dyad-level null means are not recoverable without redefining the null, STOP P2 and report only P1.

## Permutation calibration

Primary P1 null:
- within each cohort, permute complete individual policy coordinates among biological individual labels;
- retain the fixed observed co-use dyads and observed dyad separations;
- recompute policy distances and Spearman rho.

9,999 permutations.

Seeds:
- 2022: `202610051531`
- 2023: `202610051532`.

One-sided p for positive rho.

Require at least 5 eligible dyads and >=9,500 valid permutations.

## Interpretation

### Positive policy-distance/separation association

Persistent personal policies are partly expressed as pairwise spatial separation during co-use.

### No positive association

> policy differentiation does not map monotonically onto pairwise vertical partitioning.

This is a direct dyad-level version of:

[
	ext{individual policy differentiation}
eq	ext{spatial partitioning}.
]

A 2023 panel-level excess separation may still exist without being organized by persistent policy distance.

## Ceiling

This diagnostic cannot identify competition and cannot turn post-outcome association into causal mediation.
