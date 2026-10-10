# Actual original Myotis central-logger-window sensitivity V2 — executed source receipt

**2026-10-10 | REAL OPEN SOURCE OBSERVATIONAL DESCRIPTIVE DATA | POST-OUTCOME EXPLORATORY ONLY.** This result is not a new behavioral null test, not inferred social attraction or avoidance, not direct animal contact or a foraging-performance/fitness outcome.

## Source, pre-outcome boundaries and authoritative execution

- Original Hernández-Montero et al. (2026), *Ecology and Evolution*, DOI [10.1002/ece3.73604](https://doi.org/10.1002/ece3.73604); original OSF `sg6dz`. Eight RFID/transmitter-stable original bat file series on both 2024-05-15 and 2024-05-16, 16 source-frozen data files.
- Existing original-data results were observed BEFORE this sensitivity: all-night 17/28 and 14/28 potential bat pairs with at least one same-receiver/same-minute recorded co-detection; 13/28 specific dyads positive on BOTH original source nights. The original V1a and V1b receipts remain intact.
- Original source paper fixed stationary logger schedule at **21:00–05:00** (Methods §2.2); original UD-based home-range work excludes activity within first 2 hours after **sunset** and last 3 hours before **sunrise** (Methods §2.7), to avoid day-roost movements. The present source does not independently document raw timestamp timezone or exact local solar phases; author code `ymd_hms(timestamp)` used timezone-naive input. Therefore the deliberately fixed **23:00–02:00 source-clock** midpoint is an **exploratory central scheduled-logger interval**, and NOT an exact replay of the original astronomical foraging-only exclusion.
- The [frozen V2 contract](MYOTIS_2026_LOGGER_CORE_23_TO_02_EXPLORATORY_CONTRACT_V2.md) was committed **before opening the narrower window outcome** at SHA `ecf710c4151a1a1054fd8da7128dc52fcd01c68c`, then clarified a reporting unit from technical events to bat×minute presence at `89a8a9c10244558f93b7d380994c1f0c310c9672`, also before outcome.
- Frozen sources, RSSI > −90 dB published threshold, one-minute receiver-set intersection, and 28 prelisted bat pairs were identical to V1a. Source processing was imported from frozen V1a, not reselected.
- First [workflow 38014672763](https://github.com/zuizui0223/batter/actions/runs/38014672763) completed **SUCCESS mechanically** but the strict guard produced `STOP_SOURCE_QA_OR_MARGINS`, with no result issued. A code-only diagnostic addition `f42fe55fed7f0c2ffb583625520dc83d19af2b9b` reported boolean QA/source-margins/nested-subset checks, WITHOUT changing source, time window, statistic, RSSI threshold or any data eligibility.
- **Authoritative successful run:** [GitHub Actions 38014791593](https://github.com/zuizui0223/batter/actions/runs/38014791593), code head `f42fe55fed7f0c2ffb583625520dc83d19af2b9b`; strict source QA and all guards PASS. The original issue's underlying reason was not independently ascertained; do **not** claim a biological source difference or known computational bug solely from the first STOP.

## All-night versus central source clock interval: original data

| Fixed descriptive quantity | Full-night 2024-05-15 | Core 23:00–02:00 2024-05-15 | Full-night 2024-05-16 | Core 23:00–02:00 2024-05-16 |
|:--|--:|--:|--:|--:|
| Eight identified bat file series | 8 | 8 | 8 | 8 |
| 28 possible dyads with >=1 same-station same-minute detection | **17** | **6** | **14** | **8** |
| Summed bat-pair×minute co-receiver incidences | **347** | **17** | **516** | **108** |
| Per-dyad co-receiver minute median | **1** | **0** | **1** | **0** |

Further original-data source QA:
- RSSI-qualified **bat×minute presence keys** (NOT raw source technical row count): May-15 full 1,985 / core 727 (**36.62%** of the existing presence keys); May-16 full 1,952 / core 677 (**34.68%**).
- Every source-tag series has >=1 eligible central-minute detection in both dates.
- Core pair counts: May-15 median 0, p05=0, p95≈3.65 minutes; May-16 median 0, p05=0, p95=20.0 minutes.
- Central 2-night same-dyad binary recurrence: **5/28**, with **1** May-15-only, **3** May-16-only, **19** neither. Compare with **13/28** repeated positive in full nights, and full-night 4 May-15-only, 1 May-16-only, 10 neither.

Source invariance/diagnostic guard outputs were all true:
`all_16_source_QA_pass`, `old_margins_match`, `old_both_night_pair_total_match`, `core_nested_in_allnight`, `core_incidence_not_larger_than_allnight`, `core_both_subset`, `has_exactly_28_fixed_pairs`.

No original RFID, transmitter string, receiver ID, exact event timestamp, coordinates, measured RSSI value or individual-pair identity was emitted. No social null/permutation/p-value or task-reward test was run.

## Ecological reading: important NON-identifications

1. **Descriptive sensitivity:** the previously observed high number of repeated positive dyads is strongly dependent on which nightly hours are considered. Broad night-wide receiver-minute sharing is **not equivalent** to central scheduled-night sharing, and should not be casually interpreted as co-foraging.
2. **Hours/exposure confound:** the core is a shorter 3-hour period than the 8-hour logger programme, and presence-key share is only 34.7–36.6%; changes in pair×minute incidence should not be treated as a causal time-of-night effect or normalized by simple 3/8 in the presence of bat/hour/receiver variation. Some observed co-detections may reflect roost departure/return, shared early prey patches, detection changes or common station uptime.
3. **Sunset clock ambiguity:** original authors' precise exclusion uses 2h **after sunset**, 3h **before sunrise**, which have not been recreated using validated local coordinates/timezones in this archive. Thus the 23–02 interval is an *approximate source-schedule middle*, not evidence that 5 positive pairs shared a verified prey foraging patch.
4. **Station-footprint ≠ bat proximity:** two bats detected at the same receiving station in the same 60-second bin may be separated by tens of meters and tens of seconds; this is not directly measured sensory/social contact.
5. **No availability-conditioned reference:** station uptime, detections, night/bat-specific receiver frequency, time-of-night patterns and individual serial dependence are not independently calibrated. There is **no** statistical test of pair attraction, competition, temporal avoidance or individual dyadic preferences. Repeated dyads (max 28) share 8 bats and 2 nights; they are not 28 independent bats.
6. **Cohort provenance difference:** the original publication's May-2024 UD-overlap batch retains **7 out of 8 tagged** individuals; our source V2 uses all 8. Without the original 7/8 eligibility crosswalk, comparing these co-detection outcomes directly against published UDOI is invalid.
7. **No mechanism/payoff:** the original data lack confirmed prey captures, 3D altitude, controlled sensory masking and intervention on route opportunity, so V2 does not explain JAE's persistent vertical-use morphology or the adaptive maintenance of personalized 3D control.

## Stop / decision

**Supported narrowly:** The original source records 6/28 and 8/28 co-receiver positive pairs during the sole fixed middle-of-logger-window sensitivity, of which 5/28 are positive across both source nights.

**Not supported:** Spatially exclusive time-sharing, acoustic jamming, mother-daughter attraction, cooperation, stable personal reaction norm, adaptive prey payoff, or exact author-protocol roost-excluded sharing. Repeating scans over a series of convenient time windows/receiver radii/signal thresholds on these same two nights would be post hoc confirmation laundering; **STOP here**.

**Verdict:** `SUPPORTED_POST_OUTCOME_EXPLORATORY_CLOCK_WINDOW_SENSITIVITY_ONLY`, `NO_CAUSAL_SOCIAL_BEHAVIOR_OR_ADAPTIVE_BENEFIT`. JAE frozen manuscript, Behavioral Ecology and PR #79 are unchanged.
