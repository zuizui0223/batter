# Original macroecology paper — evidence-bounded direction after pilot V1
2026-11-25 JST. Internal research note, not submission-ready. No new source search, ecological refit, or change to the frozen original SDM design.

## Candidate title and independent contribution
**Vertical forest structure improves prediction of observed bat species sorting beyond canopy height: a spatially blocked test**

We constructed our own occurrence–wing-trait–climate–land-cover–vertical-structure database from public data products, rather than taking one author's response table and reanalyzing it. The new question concerns the incremental information in vegetation vertical architecture at matched observation-source/year/block support, after scalar height and baseline landscape covariates. The novel contribution to establish is the cross-species, spatially transferable comparison, not the invention of height-profile proxies, state-dependent ecology, or an empirical estimate of three-dimensional airspace occupancy. The present evidence is a pilot on recorded species labels, not causal biological sorting or a validated distribution map.

## Empirical pilot result
Exact area-weighted common-grid source artifact 15007174727; run 45591260188, job 139125762824, artifact 15010737104; receipt OBSERVED_LABEL_SORTING_RECEIPT_V1.json. Fourteen previously geographically eligible taxa, 1796 recorded forest cells, 51 spatial blocks, 1626 pair-by-source/year/block groups and 31601 composite pair comparisons (not independent replicates). Five fixed block folds.

| Increment | Mean held-out gain, nats/pair | Positive folds | Positive blocks | Delete-one-block mean range |
|---|---:|---:|---:|---|
| Baseline B1 − neutral B0 | 0.02684827 | 5/5 | 31/51 | [0.02171897, 0.03098545] |
| Vertical profile B2 − B1 | 0.01439786 | 5/5 | 37/51 | [0.01260101, 0.01530269] |
| Trait sharing B3 − B2 | −0.00155291 | 0/5 | 17/51 | [−0.00181068, −0.00111797] |
| Combined B3 − B1 | 0.01284495 | 5/5 | 37/51 | [0.01100245, 0.01373294] |

B3−B1 passes the frozen joint descriptive screen, including a positive median training AR×R50 coefficient 0.01186786; training range [−0.03503441, 0.04015492]. But B3−B2 worsens all five folds, so do not call the morphological sharing hypothesis supported. B2 and B3 are differently regularized parameterizations of the same representable species contrasts, not additional independent information or a test of absence of morphological effects. B2−B1 improvement in all five folds is the principal descriptive pilot finding, independently computed from all archived held-out scores; not a calibrated significance test. No absolute risk, habitat preference, coexistence, ecological mechanism, or true flight-height inference.

## Paper structure (provisional)
1. Why scalar forest height cannot encode within-column structure.
2. Independent construction of a harmonized database; clarify source-year conditioning and remaining detectability.
3. Spatially blocked recorded-label allocation: profile contribution vs trait-sharing contribution.
4. Larger frozen snapshot: prospective check of profile increment, separate from the original 20-taxon SDM; avoid treating overlapping GBIF records as independent replication.
5. Implications and limitations: vertical environmental structure can contain useful information, but height-quantile proxies do not identify altitude-specific utilization; morphological explanation remains open. Prior bat tracks and resource work are background only, not pooled results.

Figure plan: F1 data/estimand schematic; F2 fixed model contrast by all five pilot folds (and per-block diagnostics in supplement); F3 reserved for fixed-snapshot validation, not fabricated; F4 only if actual admitted SDM and evidence. No claims from data availability alone. The original 20-species/forest/effort/terrain/roost/PAVD gates and independent-region requirements remain unchanged. No manuscript submission or main merge.
