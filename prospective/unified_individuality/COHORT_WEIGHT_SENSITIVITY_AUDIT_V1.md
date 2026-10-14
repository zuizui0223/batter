# Cohort-imbalance audit of descriptive one-dimensional vertical-profile overlap

**Date:** 2026-10-14  
**Status:** *Post-outcome descriptive sensitivity*, calculated after the original JAE shape results, Figure 5B individual profiles and pooled 684-dyad Figure S1 statistics had already been inspected. Not a registered or independent test.

## Why a source-panel median is not a species-level ecological parameter

The source-derived Figure S1 summarizes all distinct unordered animal pairs **within each original panel and exact collection site/colony/year**; it never compares animals from different cohorts. However, its one number per panel is the *median of these dependent pairs pooled across the within-panel cohorts*. A cohort with n animals contributes n(n−1)/2 pairs, so the larger cohorts can dominate the pooled median.

There are 103 panel-indexed profile records but only 101 distinct literal source ID strings; two recur between P. hastatus 2016 and 2022. The two repeated labels do **not** establish actual cross-year recapture. No current overlap pair is a same-identifier self-pair or a cross-year pair, but the 103 records must not be described as 103 independently verified living bats across all panels.

## Pair weighting and cohort sensitivity

| Original panel | Original within-cohort pairs (not independent) | Pooled dyad median O | Median of eligible cohort medians | Largest cohort's fraction of dyads | Remaining-dyad median after largest cohort omitted |
|---|---:|---:|---:|---:|---:|
| *Eidolon helvum* | 41 | 0.817 | 0.855 | 28/41 = **68.3%** | **0.887** (13 pairs) |
| *Hypsignathus monstrosus* | 276 | 0.801 | 0.801 | 276/276 = 100% | Not defined: one cohort |
| *Phyllostomus hastatus* 2022 | 262 | 0.919 | 0.917 | 171/262 = **65.3%** | 0.912 (91 pairs) |
| *P. hastatus* 2023 | 60 | 0.899 | 0.865 | 45/60 = **75.0%** | **0.831** (15 pairs) |
| *P. hastatus* 2016 | 45 | 0.802 | 0.802 | 45/45 = 100% | Not defined: one cohort |

The *median of cohort medians* gives every pair-eligible collection cohort equal weight. This is an **alternative descriptive aggregation**, not a population or cohort-level effect estimate and not a confidence interval. In *Eidolon*, three of the five pair-eligible cohorts have only **two** individual profile records and thus **one** observed pair apiece; equal weighting therefore gives very small cohorts disproportionate influence. One additional *Eidolon* cohort has only one individual and contributes **zero pairs**; that stratum is not assigned an invented overlap.

A leave-largest-cohort-out summary is **not** an inferential leave-one-cluster-out standard error and should not be interpreted as a generalization test. With only two eligible source cohorts in P. hastatus 2022 or 2023, it simply leaves the other original cohort; in one-cohort panels it is undefined.

## Full site/colony/year table — the preferred biological description

| Original panel | Source collection cohort | Source panel profiles | Nonindependent pairs | Descriptive median O |
|---|---|---:|---:|---:|
| *E. helvum* | Burkina Faso, Ouagadougou::2013 | 2 | 1 | 0.855 |
| *E. helvum* | Burkina Faso, Ouagadougou::2014 | 5 | 10 | 0.902 |
| *E. helvum* | Ghana, Accra::2009 | 1 | 0 | — |
| *E. helvum* | Ghana, Accra::2011 | 2 | 1 | 0.902 |
| *E. helvum* | Ghana, Kibi (Old Tafo)::2013 | 2 | 1 | 0.817 |
| *E. helvum* | Zambia, Kasanka::2014 | 8 | 28 | 0.728 |
| *H. monstrosus* | Lek Njoukou::2020 | 24 | 276 | 0.801 |
| *P. hastatus* 2022 | Aj-cave (Colony 2)::2022 | 14 | 91 | 0.912 |
| *P. hastatus* 2022 | La Gruta (Colony 1)::2022 | 19 | 171 | 0.922 |
| *P. hastatus* 2023 | Aj-cave (Colony 2)::2023 | 10 | 45 | 0.900 |
| *P. hastatus* 2023 | La Gruta (Colony 1)::2023 | 6 | 15 | 0.831 |
| *P. hastatus* 2016 | La Gruta::2016 | 10 | 45 | 0.802 |

The colony/year strata have no guarantee of exactly simultaneous biological interaction, identical horizontal support, or identical measurement precision. These O values describe **one-dimensional session-median-centered altitude-shape self-predictors**, not actual 3D habitat use or competitor avoidance.

## What this adds and what it does not

- The within-panel pooled medians are real descriptive values from the original protected data, but the **numerical summaries can change substantially depending on which cohort contributes the pair mass** (notably *Eidolon* and *P. hastatus* 2023). The per-cohort medians are therefore the transparent biological display; avoid species-level or universal overlap statements.
- A close median shape overlap is not evidence for shared resources or space if the underlying individual predictors use different self-derived 5-km horizontal weighting sets, and it is not a non-inferiority/equivalence proof.
- The original original-data source results remain authoritative: centered whole-distribution identity supported in five comparative panels, the focal *Tadarida* centered profile FAIL, post-outcome V_rel 4/4 supported, positive S_rel 0/4 supported and co-use 1/4 heterogeneous exception.
- There are only **five study panels across three positive comparative taxa** represented in Figure S1 (three *Phyllostomus* study-year panels). Treating the 12 source cohorts or 684 pairs as separate phylogenetic or independently replicated tests would be invalid.
- The original source archives are unchanged. A reproducible numerical read-out and an independent CSV-based verification are stored in `figures/COHORT_WEIGHT_SENSITIVITY_V1.json` and `validate_cohort_weight_sensitivity_v1.py`, respectively. The latter validates 103 panel-indexed records and two repeated source identifiers without deciding actual individual recapture.

**Decision for manuscript:** Keep Figure S1 as *Supplementary descriptive illustration* and put the cohort-stratified counts/medians and imbalance warning in SI Table S9 and Methods S14. In the main text emphasize that panel-level O values are dependent dyad descriptions and not a source-null-tested ecological law. There is no new source permutation, effect test, registered hypothesis, fixed behavioral mechanism or formal across-species pooling.
