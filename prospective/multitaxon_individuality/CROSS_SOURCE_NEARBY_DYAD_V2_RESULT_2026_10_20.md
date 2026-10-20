# Seasonal geographic sharing after matched-dyad and near-neighbour controls

**Exploratory source-verified original GPS comparison — 20 October 2026.** This is the next, clearly marked *post-v1-inspection* sensitivity analysis in the pattern-first programme. It does **not** establish ecological-resource partitioning, actual simultaneous encounters, within-population network interactions, or a universal cross-taxon mechanism.

## Result in one paragraph

The archived wild-turkey winter-high geographic-overlap pattern survives restricting both individuals in a pair to **≤25 km apart in their source-year day-balanced geographic-use centres**. For 2019 and 2020, 15/16 and 16/16 grid/origin choices retain the winter-high direction. The black-bear 2020 mean remains almost invariant across winter and summer at 5 km, but the matched dyads reorganize: **1 winter-only, 10 summer-only and 7 both-positive** pairs among 104 near-centroid pairs. The mean reflects opposed changes in the frequency of overlap and its conditional strength. White-tailed deer has a tiny positive unshifted 5-km winter-minus-summer mean but a *negative* direction in 11/16 (2019) and 13/16 (2020) settings; its direction is **not** robust. Moose offers only a different early-versus-late calendar comparison, not a winter–summer result. None of these records include independently measured physical encounters or dietary/resource overlap.

## Full original-source verification and reproduction

[GitHub Actions run #39386343711](https://github.com/zuizui0223/batter/actions/runs/39386343711) completed all six jobs (offline tests plus five archived source analyses). Each complete package's ORIGINAL GPS and reference files were downloaded and matched to publisher byte counts and **MD5**. The new aggregate results were independently checked against the source archive statuses, the **entire 320-scenario preselected grid per usable source**, the four dyad states, p×m identities, zero-vs-missing status, and the exact symmetric incidence/strength decomposition. No raw animal GPS, coordinates, IDs, date-level fixes, or centroid vectors are committed.

| Original source | Original GPS rows | Retained 2019–2020 fixes | Status |
|---|---:|---:|---|
| Wild turkey (`10.5441/001/1.671`, CC0) | 796,419 | 435,214 | 320 scenarios verified |
| Connecticut black bear (`10.5441/001/1.706`, CC BY 4.0) | 156,366 | 148,394 | 320 scenarios verified |
| Snowy Range moose (`10.5441/001/1.700`, CC BY-NC 4.0) | 123,399 | 123,399 | 320 scenarios verified; **no winter–summer eligible pairs** |
| Western Virginia white-tailed deer (`10.5441/001/1.718`, CC0) | 559,830 | 371,080 | 320 scenarios verified |
| Bighorn Mountain moose (`10.5441/001/1.714`, CC0) | 52,649 | 0 | **STOP** — 52,648 timestamps not understood by declared decoder; one row not visible |

The same source-wide pipeline estimates from the earlier original-source v1 run were recovered independently for **all 64 year/window/grid settings in each of turkey, black bear and Snowy Range moose** (192 exact matched animal/dyad-state comparisons). Maximum numerical error in their seasonal decomposition terms was **1.67×10⁻¹⁶**. The Bighorn moose format STOP recurred and is **not** ecological absence. The earlier first-pass **conversational** values were not independently reconstructible; the archived v1 and this v2 run are the traceable versions.

## Winter (Jan/Feb/Dec) versus summer (Jun/Jul/Aug): 5-km reference grid

All comparisons below keep exactly the **same dyads** across two seasons. A dyad needs ≥7 shared observed dates in each valid month and ≥2 valid months per season. The reference year is held fixed; December is in that same calendar year, not the previous year. The distance cut uses annual day-balanced *spherical* centroids and is a geometric-proximity proxy, not demonstrated shared habitat or interaction opportunity.

| Source-year | Source-wide dyads, ΔX | Within 25 km dyads, ΔX | All-grid signs within 25 km |
|---|---|---|---|
| Turkey 2019 | 171; **+0.092591** | 112; **+0.141367** | 15 positive / 1 negative |
| Turkey 2020 | 28; **+0.283993** | 21; **+0.378657** | 16 positive / 0 negative |
| Black bear 2020 | 118; **+0.000522** | 104; **+0.000592** | 9 positive / 7 negative |
| White-tailed deer 2019 | 55; **+0.003579** | 55; **+0.003579** | 5 positive / 11 negative |
| White-tailed deer 2020 | 206; **+0.006351** | 205; **+0.006382** | 3 positive / 13 negative |

The **16 signs are four grid widths (1, 2, 5 and 10 km) × four grid origins**, not independent tests, and no p-values are calculated. The grid-specific sign reversals prevent any blanket “winter sharing always increases” claim for deer or bear. Even turkey's 2019 direction reverses in one setting. Positive results are observations within these sources, not independent species-level evolutionary replications.

### What the same-pair transitions add

For 2020 black bear the source-wide matched 5-km dyads comprise **100 neither, 1 winter-only, 10 summer-only, 7 both**. Restricting to annual-centroid distance ≤25 km removes 14 **both-zero** dyads and leaves **86 neither, 1 winter-only, 10 summer-only, 7 both**. The mean changes from +0.000522 to +0.000592; the underlying positive-overlap transitions are unchanged. This rules out the explanation that these *specific paired transitions* were entirely generated by including very distant animals. It does **not** prove near animals met, competed or deliberately avoided each other.

For turkey 2020, the 25-km risk set contains **21 pairs**, with **11 winter-only and 10 both-positive**; none are summer-only or both-zero. Its 16/16 positive setting pattern is comparatively stable to the tested spatial discretizations, although within-year individual or habitat histories remain unmeasured.

The identity

\[
\overline X=p\,m, \qquad p=P(X>0),\qquad m=E(X\mid X>0)
\]

and its symmetric exact difference decomposition show why the overall mean alone cannot identify whether the prevalence or conditional strength of overlap changes. For the black-bear source-wide 5-km example, **incidence contributes −0.025519** and **positive-overlap strength +0.026041**, leaving +0.000522. These are **arithmetical components** of observed occupancy, not causal ecological compensation or interaction.

## Separate Jan–Feb versus Mar–Apr result (not winter–summer)

The Snowy Range moose data have no qualified pair set for the defined winter–summer contrast. The shorter early-versus-late comparison has 2019 source-wide **231 pairs and ΔX=+0.005438**, and 2020 **120 pairs and ΔX=−0.002828**. At ≤25 km, they are respectively **85 pairs, +0.014852** and **42 pairs, −0.008080**. Across all 16 grids the corresponding signs are **12 positive/4 negative** (2019) and **4 positive/12 negative** (2020). The seasonal direction is weakly dependent on which *calendar* comparison and grid is chosen; calling this a demonstrated moose summer advantage would be incorrect.

## Biological and statistical boundaries

- Source-original reference tables do not yield usable same-site labels for any of the new sources. Therefore `same_reference_label` is **NOT ESTIMABLE**, not a zero score. The 25/50/100-km cuts are explicit follow-up proxies for potential comparison geography; a shared biological population remains **unverified**.
- The original sources belong to a related 2026 publication family and are not automatically independent ecological replicates. A year, pair, fix or shifted grid is not a separate study. Sample sizes for these comparisons vary sharply (e.g. turkey 8 animals in 2020 versus 19 in 2019).
- Complete data access and exact arithmetic do not resolve unknown sampling accuracy, unequal tagging schedules, day/night coverage, source UTC-versus-GPS clock ambiguity, movement strategies, vegetation, phenology, resources or social groups. Temporal matching here is *observed-day* opportunity, not physical co-presence.
- The programme's **R** (conditional movement individuality) is not yet recalculated for these new taxa; **E** (independent resource exposure) and **T** (observed encounter) are not measured. The hypothesis that individual specificity causes spatial partitioning is unsupported by these results.
- The v2 distance modes were specified **after** earlier archive outcomes were seen, so they are transparent exploratory sensitivities, not a preregistered independent validation.

## Traceability and next research action

- [All source original-file receipts, full 320 grid/mode outcomes, null cases and verified dyad-state tables](CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip)
- [Machine-readable cross-source summary](CROSS_SOURCE_NEARBY_DYAD_V2_SUMMARY_2026_10_20.json)
- [Complete 5-km unshifted summary for all sources, years, calendar windows and modes](CROSS_SOURCE_NEARBY_DYAD_V2_REFERENCE_GRID_2026_10_20.csv)
- [Original-source v1–v2 exact reproduction receipt](V1_V2_RECONCILIATION_2026_10_20.json)
- [Reanalysis source code](cross_source_seasonal_x_v2.py), [independent output validator](validate_cross_source_seasonal_x_v2.py), [source and ecological caveat design](CROSS_SOURCE_DYAD_REANALYSIS_EXECUTION_2026_10_20.md)

**Next biological step** is not to fit a universal threshold from these source-wide statistics. Resolve within-source geography and individual tracking strategy independently of X where possible, test how observation schedule changes the estimated incidence and strength, and add source-measured habitat E or actual encounters T where available. Only then compare ecological causes across independent populations and taxa.
