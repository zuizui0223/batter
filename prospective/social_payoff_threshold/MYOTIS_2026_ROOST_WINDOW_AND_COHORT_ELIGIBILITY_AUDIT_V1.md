# Biological applicability audit: roost-window bias, source cohort and prior art

**2026-10-10. POST-OUTCOME SOURCE-BASED ROBUSTNESS / INTERPRETATION AUDIT.** No newly opened dyad outcomes, no changed V1a/V1b source statistic. Citation to original paper, not a preregistered new effect.

## The main factual result, with strict unit and sampling context
Original OSF sg6dz, eight source-tag series repeatedly identifiable in 2024-05-15/16, 16 original daily CSVs. Pre-frozen 60-second same-receiver rule, original author RSSI >-90 dB: 17/28 pairs with >=1 bin on 15 May, 14/28 on 16 May, totals of 347 and 516 *pair×minute incidences*; this is already recorded in `MYOTIS_2026_DESCRIPTIVE_RECEIVER_MINUTE_ACTUAL_RESULT_V1A.md`. Post-outcome exploratory repeat table, with exact unchanged V1a margins: 13/28 positive on both nights, 4 only first, 1 only second, 10 neither, [successful CI 38014108133](https://github.com/zuizui0223/batter/actions/runs/38014108133), documented in `MYOTIS_2026_CROSS_NIGHT_DYAD_PERSISTENCE_ACTUAL_RESULT_V1B.md`.

### Important additional source-method issue A: original paper intentionally restricts foraging-window spatial analyses

[Hernández-Montero et al. 2026, original Methods §2.7](https://pmc.ncbi.nlm.nih.gov/articles/PMC13158582/) excluded detections in the **first two hours after sunset and last three hours before sunrise** to reduce effects of activity near the day roost. The present V1a and V1b **do not** implement those original exclusions; they apply the original RSSI quality threshold and include eligible source minutes across the full recorded night. The received co-minute pairing thus can be driven by coincident emergence/return or local roost transit, not necessarily foraging site sharing.

No rescue by inventing sunset times from an unverified processed-file timezone; original source naive ISO timestamp strings are interpreted with author R `lubridate::ymd_hms()` but their true wall-clock zone was not independently verified. A source-based validated astronomical clock and roost-independent foraging window need to be fixed BEFORE making a foraging-specific claim. Do not pretend 13 repeatedly co-detected pairs implies repeated shared feeding sites.

### Source-method issue B: source cohort eligibility 8 tagged versus 7 UD-analysis eligible

[Original 2026 Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC13158582/) labels May 2024 as **8 tagged, 7 with >1 night meeting the original *UD overlap analysis* support rule**, and 21 potential eligible pairs (7 choose 2), zero mother–daughter dyads. Our categorical V5 source gate established eight unique same-RFID/TX file series for two dated original CSV folders, and our descriptive receiver-minute analysis reports all eight file series and 28 pairs.

**The analysis cohorts are not identical by default.** The original paper may apply event coverage/day or home-range eligibility rules not equivalent to source-file presence. We have not independently identified which source-tag series the authors excluded from UD analysis, nor why. Thus the 13/28 is a source-file-scope event descriptor, **not** the co-detection outcome of the seven source-paper UD-eligible bats. Avoid framing it as a direct within-subject comparison to the published UDOI table until the author selection crosswalk is proved. It is invalid to assume the eighth source series meets the author's home-range inclusion just because original CSV files exist on two days.

### Source-method issue C: receiver availability and detection are not known animal absence

The original author Methods §2.2 describe 65 stationary loggers, 35-m conservative detection footprints, 2-second rate, nightly 21:00–05:00 window, and gateway downloads that erase station memory after retrieval. Published detection rate can decline beyond 40m and logger memory is finite (up to 4,000 meetings); a reception-free minute is **not** documented continuous empty habitat. Original article source analysis acknowledges bounded grid area. Thus a null for pair avoidance or social attraction needs receiver station uptime, effort and detection probabilities, not simply “not detected” as animal absence.

### Prior-art novelty warning
Spatial-temporal co-use versus simple home range overlap is long-established: Minta (1992), “Tests of Spatial and Temporal Interaction Among Animals” DOI **10.2307/1941774**, and Chaverri et al. (2007), “Range overlap and association patterns in the tent-making bat Artibeus watsoni,” DOI **10.1016/j.anbehav.2006.06.003**, already analyze spatial overlap and associations in animal/bat dyads. A descriptive finding of same-receiver minute recurrence is NOT a novel general ecological law, not a new reaction-norm theory and not evidence of acoustic/spatial payoff substitution.

## Three independent variables that must remain distinct

1. **Space availability/overlap** in marginal UDs (original author primary result);
2. **Measured time-binned co-receiver positivity** in the same 60-second source clock bin (batter supplementary real-data observation, post-outcome repeated-pair secondary);
3. **Causal realized foraging payoff** (not present in this OSF sample at all).

Mathematically, even for the same site and time marginal use probabilities `p_i, p_j`, a joint `P(A_i=1,A_j=1)` lies between `max(0,p_i+p_j−1)` and `min(p_i,p_j)`. Equal home ranges/marginals cannot uniquely determine behavioral co-activity or social interaction. This mathematical nonidentifiability is **standard probability**; the empirical value comes from observing joint source signals instead of inferring them from UDs.

## Current research decision

- Retain the legitimate V1a 17/28 and 14/28 **night-wide** receiver-minute co-detection, plus V1b **13/28 exploratory pair persistence**, with all source and observational qualifiers attached.
- Do not present these as foraging-only, close physical encounters, intentional avoidance, robust dyad social preference, added 3D mechanism, or fitness outcomes.
- Do not retrofit a *foraging-specific* subset without independently validated clock/astronomy and original seven-animal inclusion metadata, and do not scan multiple time windows to chase an apparently strong social result.
- No further post hoc p-value testing on the same two nights until original station-quality/roost/clock source gate is satisfied. JAE frozen results and their original source cohorts remain untouched.

**Verdict:** genuine independent middle-layer observation, **not** a confirmed ecological maintaining mechanism.
