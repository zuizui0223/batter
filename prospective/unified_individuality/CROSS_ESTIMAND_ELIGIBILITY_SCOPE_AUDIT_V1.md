# Original per-bat source membership crosswalk: recovered and verified

**Updated 16 October 2026.** Archival membership audit of the originally successful fine500, native/terrain 3D V/S and corrected co-use I analyses. The previous aggregate-only conclusion that their animal-ID intersections could not be established has been **superseded** by checking the original retained per-individual and dyad result artifacts. No raw GPS/DEM input, source permutation rerun or new within-bat statistical test.

## Verified source-panel bat memberships

The four named source-study panels do not have the same complete eligible animal sets, but **some actual cohort-qualified source individual IDs overlap**.

| Panel | Fine500 eligible | Joint V/S eligible | Co-use I eligible | Fine∩V/S | Fine∩I | **V/S∩I** | All three |
|---|---:|---:|---:|---:|---:|---:|---:|
| *H. monstrosus* | 19 | 8 | 11 | 8 | 10 | **5** | 5 |
| *P. hastatus* 2022 | 23 | 5 | 6 | 5 | 6 | **3** | 3 |
| *P. hastatus* 2023 | 11 | 6 | 6 | 6 | 6 | **5** | 5 |
| *P. hastatus* 2016 | 9 | 9 | 5 | 9 | 5 | **5** | 5 |

**Original native and terrain V/S identity sets match exactly, in all four panels.** The entire V/S eligible set belongs to the larger fine500 set in all four panels. The co-use I set contains additional/nonmatching bats: for H, just ten of eleven co-use bats occur in fine500; for the other three panels all I bats occur in fine500. For P2023, V/S n=6 and I n=6 but the intersection is **five, not six**.

Across the four panels, V/S and I share **18 panel-indexed original animal records**. This is **not** a count of 18 globally distinct living bats across years: the original P2022/P2016 source archives can reuse literal labels without independently established multi-year identity.

## Verification method and integrity evidence

We recovered four original historical GitHub Actions artifact ZIPs for **each** of four panels, from original successful workflows:

- Fine500 source-run 36519747717.
- Native 3D geometry source-run 36881187913.
- DEM-relative 3D geometry source-run 36946126004.
- Corrected co-use I source-run 36953712597.

**16/16 ZIP SHA256 hashes match their authoritative original GitHub Actions artifact digests.** The three predictive/geometry source outputs retain exact original source individual keys and collection-cohort labels under their observed individual-results records; corrected co-use outputs retain individual-a/b pairs and original cohorts in the observed dyad results. All intersections were recomputed from exact (source cohort, individual-ID) tuples in each named study panel. Equal sample n were **never** used to assert equal ID sets.

Original GPS coordinates, full GPS streams, DEM elevation rasters and new source null simulations were not accessed. No individual IDs, individual source rows or tracking paths are committed to this PR; public source artifacts were used to produce **aggregate counts and checksum metadata only**.

The [machine-readable original-source audit](figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json) records per-panel overlaps, original artifact identifiers, original run IDs and published ZIP digests. The [independent verifier](validate_cross_estimand_eligibility_v1.py) checks stored counts against source-frozen aggregates in normal CI and optionally rehashes and recomputes ID-set intersections from operator-supplied authorized original ZIPs when invoked with its artifact-dir option. Default CI does **not** publish or fetch individual tags.

**Archive retention boundary:** original GitHub Actions artifact ZIPs currently expire in December 2026. Long-term reproducibility of the actual ID intersections needs properly permitted retention of source ID-bearing results or authorized independent recomputation. The integration intentionally does not redistribute those artifacts or individuals' identifiers.

## Crucial scientific ceiling

**Membership intersection is not a tested link between two effects.** A shared bat can appear in the native/terrain V/S predictions and in a selected co-use dyad without the existing reported source results estimating the relationship between that bat's own conditional vertical-profile identity and its synchronous residual-height response. The original V/S results are based on same/other repeated session comparisons; I is aggregated as dyad medians over independently selected x-y-time matches and its statistic measures *differences in each bat's session-centered relative-height deviations*, not physical vertical distance.

Therefore the source results do **not** demonstrate that bats with the largest V/S fidelity actively avoid, fail to avoid, cooperate with, or partition resources from their co-use partners. The correct comparison remains between multiple source-defined inferential tests, **now with verified partly shared biological membership** rather than unknown overlap.

No new p-values, source panel outcomes or frozen BE/JAE branches changed. A directly linked V–I biological mechanism would require a separately justified, adequately supported within-animal/dyad design with calibrated common elevation datum and actual task/resource observations; source outcome fishing would not supply that causal identification.

**Recommended manuscript wording:** "The original per-animal result artifacts verify that joint-geometry V/S bats were included in the larger 500-m fine-matched populations, and that 5/3/5/5 cohort-qualified individuals overlap with the co-use assay in the four source panels. The tests retain nonidentical overall eligible sets and do not estimate within-bat V–I coupling."
