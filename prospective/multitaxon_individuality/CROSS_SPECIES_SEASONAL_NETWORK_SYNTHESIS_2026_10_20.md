# Spatial sharing can be reorganized without a change in mean overlap

**Source-hash-verified exploratory synthesis · 20 October 2026.** This is a scoped result for **two calendar years of wild turkey from one source and black bear in 2020 from another source**; the moose cohorts have different or inadequate timing support. No independent cross-clade causal law, social encounter T or measured resource partitioning E is established.

## Main question

Which aspect of space sharing changes between seasons: (1) *how many dyads overlap* or (2) *how strongly overlapping dyads share space*? Can the mean conceal compensatory changes? These are arithmetic descriptions of geographic 2D occupancy, not measured interactions between animals.

Use the same **opportunity-qualified pair-risk set** for both seasons. Pair-specific occupancy overlap X in [0,1] is balanced by source-day and monthly effort. For each season define p as fraction of eligible dyads with X>0, and m as conditional mean X among positive dyads. For p>0 in both seasons:

```text
X_bar = p × m
X_bar_w − X_bar_s
 = (p_w − p_s)(m_w + m_s)/2   [incidence component]
 + (m_w − m_s)(p_w + p_s)/2   [positive-strength component]
```

This symmetric decomposition is exact, but the terms are not causal effects. Count the actual same-pair state transitions 00, winter-only, summer-only, 11; marginal counts cannot identify transitions.

## Verified 5-km reference grid: December/January/February vs June/July/August

| Source | Year | Animals | Eligible dyads | Winter mean X | Summer mean X | Δ mean | Incidence component | Strength component |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Wild turkey | 2019 | 19 | 171 | 0.316919 | 0.224328 | **+0.092591** | +0.029876 | +0.062715 |
| Wild turkey | 2020 | 8 | 28 | 0.496194 | 0.212201 | **+0.283993** | +0.246666 | +0.037327 |
| Black bear | 2020 | 17 | 118 | 0.031017 | 0.030495 | **+0.000522** | −0.025519 | +0.026041 |

**Contrast A: same sign, different internal contributions.** Turkey 2019 winter-high overlap is mostly driven by stronger sharing *within positive dyads*; in turkey 2020, winter-high overlap is mostly explained by *more positive dyads*. The two annual cohorts come from the **same published source** and have different sample sizes, so this is not evidence of independently evolved mechanisms.

**Contrast B: near-cancellation.** Black bear winter and summer means differ by only +0.000522. The winter-positive fraction is 8/118 (0.067797), summer-positive fraction 17/118 (0.144068), while conditional strength is 0.457497 in winter versus 0.211670 in summer. Incidence decreases by −0.025519 and strength increases by +0.026041, almost cancelling. The matched dyad transitions are **100 neither, 1 winter-only, 10 summer-only, 7 both**, not inferred from marginals. This is a genuine geometric shift in *measured pair occupancy* under the declared grid, **not direct association, social encounter or competition**.

| Source-year | 00 neither | 10 winter-only | 01 summer-only | 11 both |
|---|---:|---:|---:|---:|
| Turkey 2019 | 95 | 8 | 0 | 68 |
| Turkey 2020 | 7 | 11 | 0 | 10 |
| Black bear 2020 | 100 | 1 | 10 | 7 |

## Grid sensitivity and STOP results

Every comparison was repeated at 1, 2, 5, 10 km with four grid origins. **Turkey 2019 winter-high holds in 15/16 settings** (one reversed), and turkey 2020 in **16/16**. Bear 2020 is **9/16 positive and 7/16 negative**: do **not** assert a robust sign for the tiny mean difference, even though the 5-km decomposition is exact.

One original Bighorn Mountain moose package (DOI 10.5441/001/1.714) was checksum-verified but **52,648 GPS rows failed the declared ISO timestamp decoder**, so it is explicitly STOP/format-unresolved, not proof the animals lacked GPS or were absent during the period. No biological seasonal statistic may be derived from this run. The alternative Snowy Range moose package (DOI 10.5441/001/1.700; CC BY-NC) has 123,399 valid positions but no qualifying December–February versus June–August matched dyad cohort. It does allow the **different** January–February versus March–April comparison:

| Snowy Range year | Matched animals | Dyads | Jan–Feb X | Mar–Apr X | Early − late | 16 grid sensitivity signs |
|---|---:|---:|---:|---:|---:|---|
| 2019 | 22 | 231 | 0.029134 | 0.023696 | +0.005438 | 12 positive / 4 negative |
| 2020 | 16 | 120 | 0.015043 | 0.017871 | −0.002828 | 4 positive / 12 negative |

**Do not call that moose result a winter–summer reversal.** Different calendar contrasts are not directly pooled. The original previous-session anecdotal moose summer-high result remains unverified, and the former bear 6 vs 14 positive-pair marginal numbers are not reproduced by this fixed same-risk-set analysis.

## Inference boundary

Original package GPS and reference files were fetched from the Movebank DSpace ORIGINAL bundles and matched to publisher MD5. Source-specific event filtering is complete to the declared parser and years. Source clocks may be UTC or GPS time; source sites, biological population membership, environmental covariates and simultaneous encounters are **not harmonized**. Even 118 observed dyads are highly dependent through 17 animals and one source, and year × grid scenarios are sensitivity choices rather than biological replication. There are no population confidence intervals or randomization-based biological p-values.

The consistent **descriptive methodological finding** is that mean geographic overlap does not uniquely specify the organization of shared use. The **empirical finding within this sample** is the verified partition into incidence and positive-strength components and 00/10/01/11 dyad states, with contrasting examples in turkey and bear. Neither shows whether resource competition, migration, seasonally shared habitat, sampling effort or social behavior is responsible.

Next substantive validation is to estimate site/population membership from original metadata, control sampling frequency and animal survival, and test whether incidence/strength arrangements recur in **independent** populations; separately add true resource E and encounter T where observable. R (behavioral identity) from new taxa is not available on the current X-only comparison and **must not be claimed**.

## Machine-readable evidence

- [All source checksums, STOP flags, per-scale outcomes, individual/dyad denominators, and seasonal pair-state counts](CROSS_SOURCE_SEASONAL_X_EXPLORATORY_ACTION.json)
- [Main source-verified comparison table](CROSS_SOURCE_SEASONAL_X_EXPLORATORY_ACTION.md)
- [Entire original-source reproduction and validation script](cross_source_seasonal_overlap_v1.py)
- [Source and synthetic tests](tests/test_cross_source_seasonal_overlap_v1.py)
- [Earlier mule-deer original-source 2018–2020 study](DEER_SEASONAL_RX_RESULT_2026_10_20.md)
