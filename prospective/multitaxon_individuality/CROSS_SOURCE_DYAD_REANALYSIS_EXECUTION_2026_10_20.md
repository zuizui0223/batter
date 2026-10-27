# Follow-up source verification: nearby-pair seasonal overlap (v2)

**Research status: October 20, 2026 — additional *post-inspection* sensitivity analysis, not a preregistration.** This continuation preserves the verified deer source analysis and the newer 2026 source-verified exploratory cross-source aggregates. It does not overwrite the first cross-source run.

## Already verified and independently audited in the branch

The original-source v1 artifacts (source commit `c1c8d1116f814c2bb4b8adcb07f4b05cfd040a79`, independently checked in `CROSS_SOURCE_SEASONAL_X_AGGREGATE_AUDIT_2026_10_20.md`) show the following *source-wide* unshifted 5-km winter–summer examples on same supported dyads:

| Source-year | Matched animals | Dyads | Winter X | Summer X | Difference |
|---|---:|---:|---:|---:|---:|
| Wild turkey, 2019 | 19 | 171 | 0.316919 | 0.224328 | +0.092591 |
| Wild turkey, 2020 | 8 | 28 | 0.496194 | 0.212201 | +0.283993 |
| Connecticut black bear, 2020 | 17 | 118 | 0.031017 | 0.030495 | +0.000522 |

The bear 2020 pair transitions are **100 neither, 1 winter-only, 10 summer-only, 7 both**; the seasonal mean difference is the algebraic sum of an incidence component **−0.025519** and positive-sharing-strength component **+0.026041**. The mean's sign reverses with grid scale/origin (9 positive, 7 negative of 16). The original Bighorn Mountain moose source failed ISO datetime parsing, not a biological test. Snowy Range moose lacks valid winter–summer pair support and permits only a different early-versus-late comparison. The earlier conversational 12-source figures, including black-bear “6 vs 14” and a supposed winter–summer moose reversal, were **not** source-verified and must never be cited as replications.

**Critical unresolved issue in v1:** its data packages have no usable source reference site labels for these source-wide comparisons. Different animals can represent distinct local populations or study regions. A low all-source overlap may simply reflect geographically distant individuals. Pair contacts, social associations, resources, and real simultaneous encounters have **not** been measured.

## What this distinct v2 continuation changes

Files: `cross_source_seasonal_x_v2.py`, `validate_cross_source_seasonal_x_v2.py`, their two synthetic test modules, and `.github/workflows/cross-source-original-x-v2.yml`. They run **without raw animal locations entering GitHub commits**. Source originals are downloaded in an ephemeral GitHub Actions runner, complete file bytes and publisher MD5 verified, then aggregate JSON is uploaded for independent inspection. The workflow is not an assertion that every source will yield a supported biological cohort.

Source queue, fixed prior to viewing **v2** outputs:

| Dataset | Original archive DOI | License | Distinction |
|---|---|---|---|
| Wild turkey | `10.5441/001/1.671` | CC0 | Previously verified winter-high X; retest near pairs |
| Black bear | `10.5441/001/1.706` | CC BY 4.0 | Previously verified incidence/strength cancellation; retest near pairs |
| Snowy Range moose | `10.5441/001/1.700` | CC BY-NC 4.0 | Compare *early vs late only* if winter–summer remains unsupported |
| Bighorn Mountain moose | `10.5441/001/1.714` | CC0 | Preserve known parse STOP unless a defensible parser resolves it |
| Western Virginia white-tailed deer | `10.5441/001/1.718` | CC0 | New source candidate; animal and season support unconfirmed |

Source study years are restricted to **2019–2020**. Two prespecified *calendar* windows: winter Dec/Jan/Feb versus summer Jun/Jul/Aug, and early Jan/Feb versus late Mar/Apr. Within a month a dyad must have ≥7 shared observed dates; a dyad must qualify in ≥2 months per season and must be the **same pair** across both seasons. Dates and monthly scores are balanced equally. Both missing risk sets and valid observed zeros are kept, never conflated.

At each 1-, 2-, 5-, and 10-km grid width and its four zero/half-grid offsets, **five fixed risk-set comparisons** are retained:

1. `source_wide` — every pair in the original package satisfying shared-date support; may include distant populations.
2. `near_centroid_25km` — both source-year animal geographic-use centers are ≤25 km apart.
3. `near_centroid_50km` — analogous 50-km cutoff.
4. `near_centroid_100km` — analogous 100-km cutoff.
5. `same_reference_label` — an exactly matching, unambiguous original `study-site` or `animal-group-id` label; returns missing if labels are unavailable.

Yearly centers use **equal-weight observed dates** and normalized spherical vectors to handle longitude wraparound. Exact coordinates, centers and pair IDs remain internal; only aggregate sample sizes, overlap values and paired state counts are exported. The three distance cutoffs are **geometric exposure proxies**, neither proven common resource access nor observed contact opportunity. They were added after the source-wide v1 effects were known, so any robustness findings are post-inspection sensitivities.

The expected scenario matrix per downloaded dataset is **320** rows (2 years × 2 windows × 4 scales × 4 origins × 5 risk modes). For each scenario report the complete matched-denominator counts of 00/10/01/11 pairs, incidence p, conditional positive overlap m, mean X=p×m, symmetric exact decomposition, sign counts, and all estimability reasons. Cross-source scales/origins are repeated *sensitivity settings*, not independent ecological replicates.

## Validation, privacy and stop rules

The offline synthetic suite tests source-reference joins, duplicate conflicts, explicit GPS/outlier flags, MD5 and byte lengths, non-leaking STOP stages, null-vs-zero outcomes, dyad transition arithmetic, grouping and nested nearby-pair risk sets (including across the longitude dateline). The separate output validator rechecks all 320 scenarios, state sums, positive-mean identities, exact decomposition, nested risk sets and prohibited source-field names. **35 local tests passed** across this additional program and its original offline companion (count includes 10 legacy tests; CI runs the v2 subset). No source GPS was available to the current container, so no v2 numerical result is claimed until CI runs.

The workflow refuses incomplete original files; a bounded download can STOP without sampling only favourable animals. It reports the safe processing stage rather than exception details containing private animal names or locations. The source absolute UTC/GPS clock basis, location uncertainty, population identity, sex/age, tagging cadence and seasonal ecological states remain source-specific limits. The original CC BY / BY-NC licence terms, citations and noncommercial conditions must be respected. For bear: Hawley JE (2026), Movebank DOI `10.5441/001/1.706`, CC BY 4.0.

**Do not:** treat a valid X overlap as trophic segregation E; treat an intersected range as a simultaneous encounter T; infer biological movement identity R in these sources; derive P-values from dependent dyads; interpret one-source year pairs as independent populations; or assert universal seasonal convergence/divergence from the limited sample.

## Running the new source verification

```bash
python3 -m unittest discover -s prospective/multitaxon_individuality/tests -p 'test_cross_source_seasonal_x_v2.py' -v
python3 -m unittest discover -s prospective/multitaxon_individuality/tests -p 'test_validate_cross_source_seasonal_x_v2.py' -v
# Original GPS retrieval and source-by-source aggregate output runs via:
# .github/workflows/cross-source-original-x-v2.yml
```

GitHub Actions artifacts are retained for 14 days. **Next evidence gate:** retrieve each successful aggregate file and checksum receipt, inspect source-specific sample sizes and all 320 scenario statuses, compare `source_wide` values to v1, then only commit source-verified aggregate summaries after manual review. The branch remains an exploratory DRAFT, separate from the bat manuscript integration PR #99.
