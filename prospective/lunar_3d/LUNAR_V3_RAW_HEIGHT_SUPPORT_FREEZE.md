# V3 lunar paired-height source admission: frozen BEFORE numeric altitude (2026-11-22)

Purpose: tighten the outcome-blind spatial/time v2 source screen so a leave-one-night-out vertical-height test does not invent support from single fixes, manipulated animals, year-mismatched deployments or GPS tagging changes. The v1 and v2 outcomes remain unchanged; v3 is a separately described, more restrictive design, not a retroactive repair. Both original sources are from the pinned `contract/phyllostomus_replication_v1.json` and `contract/hypsignathus_replication_v1.json`. Use the same verified GPS/reference file MD5 and sizes.

### Metadata-only input policy

Inspect source field headers, UTC timestamps, finite latitude/longitude, animal ID, nonempty height **string presence** (numeric height not parsed or transformed), source outlier flags and the independently sourced reference spreadsheet fields (study_site, manipulation_type, deployment_id, tag identifiers). Exclude source outliers and individuals with a nonempty non-"none" manipulation_type, ambiguous study_site, or missing unique study_site. Check whether more than one `tag_id` or `tag_local_identifier` appears on the same individual×year; flag mixed-tag exposure for the subsequent altitude calibration; before using a tag-specific height claim, both exposure classes must share the same tag or be otherwise demonstrably calibrated. If the GPS file does not carry tag linkage, tag-mixing cannot be resolved and remains explicit uncertainty.

### Strict within-animal space/night/clock support

- Geometry: reuse v1's Sun <-12°, bright Moon >=10° and illumination >=0.8, dark Moon <=-5° OR illumination <=0.2. Reuse v1's 15-min / 0.25-degree ephemeris cache.
- Match records by **individual × unique source study_site × local-solar year × same 0.05° lat/lon cell × same two-hour local-solar clock band**.
- Require, for each exposure, at least **2 distinct local-solar nights with >=8 valid GPS fixes each**, not simply two dates of 1 and 19 fixes; at least **20 total source fixes per exposure**; and at least one cross-exposure night pair no farther than **45 days**.
- Record source-header-available GPS height/satellite accuracy tags, but do not infer or impute them.
- Pass for prospective *conditional RAW vertical location* comparison only if >=5 individuals meet all criteria and each has at least one eligible matched stratum. This is **not** admission for a validated above-ground-height ecological response or a causal lunar mechanism.
- Need target/source-model heldout support: each retained stratum has at least one dark and one bright training night after any one entire local night is held out. This follows from >=2 exposure nights.
- Report aggregate numbers only: source, MD5, metadata dispositions, qualified matched strata and independent individuals, time span, number of mixed-tag individuals, presence of sensor accuracy flags. Preserve original privacy/individual IDs in memory only.

### If v3 passes

Freeze height-model numeric bins, proper scoring rule, night-block validation, equal-individual averaging, sensor error sensitivity and negative controls **before opening numeric height values**. Do not promote a favorable exploratory post-gate fit as preregistered if protocol changed after observing heights. No source data or animal IDs should be committed.

### STOP

If fewer than 5 v3 matched animals, do not force a confirmation with v2-only strata, between-animal comparisons, pooling years, looser bins or GPS-row holdout. Report descriptive support and seek new external source under a different prospectively scoped study instead. Existing JAE manuscript and main branch unchanged.
