# Horizontal overlap is not a null test of added vertical segregation — claim audit v1

**Scope:** Manuscript-level interpretation and algebraic check of the original, already-computed 500-m source results. **No new GPS/DEM extraction, inferential tests, permutations, confidence intervals, parameter fits, or preregistration are claimed.**

## Why the title and ecological conclusion were narrowed (15 October 2026)

The previous wording, "Persistent individuality need not entail spatial partitioning in bats", was too broad for the observed estimands. **Horizontal space use was not demonstrated to be unpartitioned.** The original paired session summaries show systematically higher descriptive horizontal overlap for repeated sessions from the *same* animal than for comparisons with another animal. This may reflect within-individual site fidelity or horizontal differentiation, but these marginal summary means are **not** a calibrated causal or population-level test of horizontal niche segregation. The paper can test the narrower proposition: individual-specific vertical organization does not consistently coincide with *added terrain-relative vertical segregation* at the source spatial and temporal resolution.

Revised working title: **Persistent individuality without consistent additional vertical segregation in bats**.

## Direct original source comparisons (rounded from preserved source blob)

| Panel (two species total) | Eligible animal n | Same O_XY | Other O_XY | Same O_XYZ | Other O_XYZ | S_native | S_rel |
|---|---:|---:|---:|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | 8 | 0.619 | 0.322 | 0.523 | 0.240 | +0.103 | −0.0158 |
| *Phyllostomus hastatus* 2022 | 5 | 0.549 | 0.334 | 0.507 | 0.309 | −0.017 | −0.0090 |
| *P. hastatus* 2023 | 6 | 0.547 | 0.202 | 0.508 | 0.190 | −0.004 | +0.0163 |
| *P. hastatus* 2016 | 9 | 0.511 | 0.208 | 0.425 | 0.181 | +0.130 | +0.0289 |

Here O_XY denotes the probability-mass intersection of the two-dimensional horizontal grid, O_XYZ the intersection of the joint two-dimensional horizontal-by-native-centered-altitude grid, averaged under the original session/animal weighting. **Neither is contemporaneous animal co-use, shared prey, or a lifetime home-range overlap parameter.** Figures S1 and S2 do *not* estimate the same overlap variable or use identical source animal subsets.

## A useful exact mathematical fact (not an animal-data test)

For any two normalized nonnegative *joint* probability distributions P(c,z) and Q(c,z) on an identical eligible session-pair grid, let P(c) = SUM_z P(c,z), and similarly Q(c). Then for every horizontal cell c,

`SUM_z min(P(c,z), Q(c,z)) <= min(P(c), Q(c))`.

Summing across cells proves **O_XYZ <= O_XY**. Adding a dimension may reveal more geometric detail, but a lower 3D overlap is mathematically expected even without a biological mechanism that increases *between-animal* segregation more than *within-animal* dispersion. The two source-weighted column-mean O values must not be divided to reconstruct R_3D. The historical source instead computes, at the eligible pair level,

`R_3D(pair) = 1 - O_XYZ(pair)/O_XY(pair)` (defined when O_XY > 0),

then forms **S_native = weighted mean(other R_3D) − weighted mean(self R_3D)**. A positive descriptive S_native in two panels is not a calibrated terrain-relative result. The subsequent terrain adjustment yields S_rel and its original label-permutation null: **no panel supported positive S_rel**. *H. monstrosus* supported the negative direction (two-sided p = 0.0362), which must not be reported as universally "no effect".

## What the combined results support

- **Identity:** The source conditional vertical-fidelity comparison within shared horizontal cells and original terrain-relative V_rel tests support individual vertical organization in all four structurally eligible 500-m panels. Separate larger samples passed the original centered-shape whole-distribution tests; these are **not the same n**.
- **No consistent evidence of an extra vertical layer:** Positive terrain-relative S_rel is unsupported in 0/4 panels. Contemporaneous excess co-use separation is supported in 1/4 panels only, under the 2023 600-s all-space condition; the other protocols differ.
- **An existing horizontal baseline:** Same-animal O_XY exceeds other-animal O_XY descriptively in 4/4 original source panels. Therefore no conclusion of universally shared horizontal ranges, no horizontally unpartitioned niches and no absence of spatial differentiation is licensed.
- **No identified cause or benefit:** Neither competition, learned route reuse, within-task flight strategy, wind response, diet, fitness gain nor experimental-to-field transfer has been causally established. The frozen scalar lab-to-field bridge remains PASS/PASS/FAIL/STRUCTURAL STOP, below its 3/4 gate.

## Publication-safe language

**Use:** "Individually repeatable conditional flight-height use persists after coarse context standardization, but these original tropical bat panels show no consistently supported *additional terrain-relative vertical segregation* at the tested scales."

**Avoid:** "Bats do not partition space", "vertical niche overlap is 80–92% of shared 3D habitat", "horizontal partitioning is absent", "competition is absent", "the native O_XY to O_XYZ decrease demonstrates extra height segregation", "the 2016 and 2022 literal tags prove six-year individual persistence", or "the lab experiments explain the field patterns".

**Provenance:** original native source result `figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json` (Git blob `c1d37e42f72f59e5aba364daec9aef68b47778b6`, original successful workflow 36881187913); original terrain source `figures/ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json`; source calibration `figures/ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json`. The source-recovery manifest and historical code-import smoke checks establish provenance/function loading, **not** a new full GPS/DEM or 9,999-permutation rerun. Coauthor review, source licences, anonymous versioned DOI and actual authorship/disclosure remain hard stops.
