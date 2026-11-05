# Seasonal spatial-sharing topology across public GPS source cohorts

**2026-10-20 — exploratory, POST-INSPECTION; not preregistered.**
This is a secondary audit of the archived, checksum-pinned Movebank V2
aggregates. It does not freshly reprocess original GPS tracks, nor does it
infer social affiliation, direct encounters, habitat/resource sharing or
causal effects.

## Observable pattern: average overlap hides pair membership

For each source year, use exactly the same eligible pairs in both seasons.
Winter is December, January and February **within the same calendar year**
(these are not a chronologically contiguous interval); summer is June–August.
Each pair needs at least two supported months in each season. The primary
display uses 5-km grid cells, origin (0,0), and annual-centroid distance ≤25 km,
a post-inspection geometric sensitivity, NOT verified group membership.

| Source-year | Matched pairs | Winter-only positive X | Summer-only positive X | Positive in both | Active-edge Jaccard |
|---|---:|---:|---:|---:|---:|
| Wild turkey 2019 | 112 | 8 | 0 | 68 | 0.895 |
| Wild turkey 2020 | 21 | 11 | 0 | 10 | 0.476 |
| Black bear 2020 | 104 | 1 | 10 | 7 | 0.389 |
| White-tailed deer 2019 | 55 | 8 | 8 | 14 | 0.467 |
| White-tailed deer 2020 | 205 | 15 | 2 | 34 | 0.667 |

Positive X means that *sampled geographic occupancy distributions* overlap
at the specified grid resolution. It is NOT an observed encounter.

**Distinct configurations emerge in the archive:**

- Wild turkeys: every summer-positive dyad is also winter-positive at the
  5-km reference grid. Yet 2019 retains 68/76 winter-positive pairs,
  while 2020 retains only 10/21. The dominant driver of mean X differs
  even between years of the same species.
- Black bears: summer has more positive-overlap dyads (17 versus 8),
  but the conditional strength of positive overlap is lower. Seven of
  eight winter-positive edges persist, ten summer-positive edges are new.
  This is *diffusion of observed geographic sharing*, not proof of new
  social partners.
- White-tailed deer: 2019 has eight winter-only and eight summer-only
  positive edges despite equal edge incidence in the two seasons;
  2020 loses fifteen winter-positive edges and gains two summer-positive
  edges. Different changes in edge sets can occur with small and
  scale-sensitive changes in mean overlap.

The active-edge Jaccard is both/(both + winter_only + summer_only), i.e.
one minus the fraction of distinct positive edges that appear in one
season only. It must be null if neither season has positive edges.
The associated phi binary indicator correlations for rows in table
order are 0.856, undefined, 0.555, 0.394, 0.763. Turkey 2020's
phi is undefined because all 21 eligible dyads are winter-positive.
Neither Jaccard nor phi is a biological p-value.

A synthetic counterexample demonstrates this independent dimension.
Winter X values (0.5,0.5,0,0) and summer values either (0.5,0.5,0,0)
or (0,0,0.5,0.5) share identical seasonal mean X, incidence, and
conditional positive strength, yet Jaccard equals 1 versus 0.
The test is included in the reproducible verifier.

## Exactly additive mean-overlap decomposition

Define p = fraction of eligible dyads with X > 0, and
m = mean X among positive dyads; overall mean X = p × m.
The symmetric two-component difference between winter and summer is:

Delta X = (p_w - p_s) (m_w + m_s)/2
        + (m_w - m_s) (p_w + p_s)/2.

This is a *descriptive algebraic decomposition*, not a causal explanation.

| Source-year | Winter–summer X | Incidence component | Conditional-strength component | Sign over 16 grids: X / incidence / strength |
|---|---:|---:|---:|---|
| Turkey 2019 | +0.141367 | +0.045614 | +0.095753 | X 15+/1−; p 14+/1−/1=; m 15+/1− |
| Turkey 2020 | +0.378657 | +0.328888 | +0.049769 | X 16+; p 16+; m 6+/9−/1= |
| Black bear 2020 | +0.000592 | −0.028954 | +0.029547 | X 9+/7−; p 16−; m 13+/3− |
| White-tailed deer 2019 | +0.003579 | 0 | +0.003579 | X 5+/11−; p 4+/8−/4=; m 8+/8− |
| White-tailed deer 2020 | +0.006382 | +0.029540 | −0.023158 | X 3+/13−; p 16+; m 16− |

All 16 settings are the 4 grid sizes (1, 2, 5, 10 km) × 4
grid origins. They are **dependent sensitivity settings, not biological
replications**. Bear 2020 has opposed incidence and strength terms,
almost exactly offsetting the mean. Deer 2020 has an opposite
incidence/strength contrast across *all* 16 settings, while the
total X direction reverses. Consequently neither cohort supports a
scale-independent conclusion about the direction of *mean* overlap.

Jaccard varies by cell size/origin, too: ranges across all 16 settings
are turkey 2019 0.697–1.000, turkey 2020 0.286–0.714,
bear 2020 0.250–0.721, deer 2019 0.467–0.704,
deer 2020 0.667–0.949. There is no proposed universal numerical
turnover threshold.

## Reproducibility and boundaries

- Pinned aggregate input:
  [V2 full aggregate ZIP](CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip),
  Git blob SHA1 0da5fe5f429e08194525c59b70d0840735d958ac.
- [Machine-readable focal ledger](EDGE_TOPOLOGY_REFERENCE_2026_10_20.json).
- [Executable independent validator](validate_edge_topology_v1.py), and
  [synthetic/pinned-source tests](tests/test_edge_topology_v1.py).
- The validator checks all **80** source-year/window/risk-set strata,
  **1,280** scenarios (16 per stratum), positive-edge partitions,
  every non-null p × m, the exact mean-difference decomposition,
  frozen risk set support, and reconciliation with original V2 reference
  summaries. A fifth source (Bighorn Mountain moose) remains
  **SOURCE CLOCK STOP**, not a null effect.

Run: PYTHONPATH=prospective/multitaxon_individuality python -m
unittest discover -s prospective/multitaxon_individuality/tests
-p 'test_edge_topology_v1.py' -v, then python
prospective/multitaxon_individuality/validate_edge_topology_v1.py.

Original Movebank DOIs: [turkeys](https://doi.org/10.5441/001/1.671),
[bears](https://doi.org/10.5441/001/1.706),
[white-tailed deer](https://doi.org/10.5441/001/1.718).
The original-file MD5/source SHA256 receipts were checked in the
previous V2 study; this is an audit of **existing aggregates only**.

**Limits:** Dyads and configurations are dependent; source study,
individual populations and annual cohorts are not independent
species replicates. GPS fix/detection effort is not standardized
between seasons, and any positive-X edge may vary under changing
grid or missing locations. Annual-centroid proximity is not social
association or a resource-overlap measurement. Individual movement
repeatability R, co-presence T and independently measured resource
exposure E remain unknown for these cohorts. No population p-values,
intervals or causal mechanisms are inferred.

This does **not** claim discovery of overlap-network methods:
seasonally weighted space-use networks were previously studied in
[panthers (2023)](https://www.nature.com/articles/s41598-023-44815-y)
and overlap number/strength in
[wild pigs (2022)](https://www.nature.com/articles/s41598-022-07297-y).
The present addition is an auditable **cross-dataset comparison of
mean, incidence, strength and edge retention**, with STOP rules.

**Next validation gate:** source-specific population metadata and
balanced seasonal GPS detection, followed by an independent
taxon/population with adequate observation support.
