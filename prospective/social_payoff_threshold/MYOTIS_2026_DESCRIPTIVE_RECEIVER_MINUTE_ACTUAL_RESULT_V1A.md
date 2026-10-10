# Original Myotis 2026: executed descriptive same-receiver 1-minute co-detection V1a

**STATUS (2026-10-10): ACTUAL PUBLIC OBSERVATIONAL DATA, DESCRIPTIVE ONLY. Not a causal test, no bat behavioral null p-values, no 3D flight-altitude, audio-masker or prey-capture results.**

## Provenance and freeze integrity

- Original Hernández-Montero et al. (2026), *Ecology and Evolution*, DOI 10.1002/ece3.73604; original author OSF node `sg6dz`.
- Pre-outcome hypothesis/metric frozen in `MYOTIS_2026_TIME_CONDITIONED_CO_USE_PREOUTCOME_V1.md` before **any dyad co-detection outcome**.
- Source-clock & RSSI analytical boundary frozen in `MYOTIS_2026_DESCRIPTIVE_RECEIVER_MINUTE_AMENDMENT_V1A.md` **before calculating pairwise time overlap**.
- Source eligibility: original [eight distinct biological tag/tx series repeated in two dated files](https://github.com/zuizui0223/batter/actions/runs/38012020164) and [22/28 potential pairs sharing a receiver in both nights](https://github.com/zuizui0223/batter/actions/runs/38012351593), both categorical-only checks.
- Clock syntax/receiver key quality: original 16 bat×night sources all pass parseability and nonblank receiver QA. Original timestamp strings have no explicit timezone; author R code (source-only [CI 38012635050](https://github.com/zuizui0223/batter/actions/runs/38012635050)) parses `timestamp` via `lubridate::ymd_hms(timestamp)`, which has a default `tz="UTC"`. This is a **common author parsing convention**, NOT independent verification of the true logging time zone. All conclusions below are about minute bins in that same original source clock representation.
- **Authoritative execution:** successful GitHub Actions [38012845003](https://github.com/zuizui0223/batter/actions/runs/38012845003), job `114096510764`, source/script committed at `89924b60b49ec4844bcd36a9037f1ce59382ce57`; artifact `11654846326` named `myotis-2026-preregistered-descriptive-receiver-minute-v1a`.
- Executed `myotis_2026_one_minute_same_receiver_descriptive_v1a.py`, with full list of 16 immutable original file IDs from the prior source contract; no source-selection substitutions. Entire job compilation, synthetic guard, source QA, receipt and file-presence checks all succeeded.

## One original-published source-consistent definition

The original article Methods filter out weak RSSI <= -90 dB; we used **strict RSSI > -90 dB**, predeclared before outcome opening, to classify eligible station detections. For each physical tagged animal and source-night, form a set of stationary receiver IDs detected at least once within each 60-second raw clock bin. For each of the fixed 28 possible unordered animal pairs, count a minute once if their receiver sets intersect at that minute, regardless of duplicate technical 2-second beacons and number of receivers.

This is **same-receiver, same-minute co-detection** at a station-footprint scale; not directly measured physical interaction or confirmed actual same-coordinate simultaneous presence. Raw receiver IDs, animal RFID/transmitter strings, precise coordinates, event clock values and per-dyad identities were not emitted.

## Source-backed actual observed results

| Descriptive aggregate | Source-night 20240515 | Source-night 20240516 |
|---|---:|---:|
| Fixed tagged bats | 8 | 8 |
| Possible unordered bat pairs | 28 | 28 |
| Pairs with >=1 shared receiver within a clock minute | **17/28** | **14/28** |
| Summed pair×minute co-receiver incidences | **347** | **516** |
| Dyad-specific 1-min count median (including 0) | **1.0** | **1.0** |
| Dyad-specific count 5th percentile | **0.0** | **0.0** |
| Dyad-specific count 95th percentile | **82.0** | **100.6** |

The summed 347/516 are **not** unique social-event minutes: multiple dyads can contribute within the same source minute and time bins recur across the two nights. They are not 347 or 516 independent biological observations.

In the prior categorical-only spatial support gate, **22/28** potential pairs shared at least one of the same receiver IDs across both nights; those are not the same criterion as the observed 17/28 and 14/28 time-binned pairs. **The overlap of the two sets of 17 and 14 pairs across nights has NOT been tested or reported**; no claim of repeatable dyad synchrony is supported.

## Interpretive result and hard ceiling

1. The extreme assertion that bats with overlapping station use **never** appear at the same receiver during the same minute is contradicted descriptively by observed station detection records in these two nights. This is **not** a test of lack of spatial exclusion at fine vertical scale, which these stations cannot resolve.
2. Existence of time-binned shared receiver signals does **not** establish social interaction, intentional meeting, cooperation, competition, acoustic interference or adaptive gain. With ~35m receiver footprints, bats can be at substantially different positions and at different instants in one minute.
3. Temporal co-detection intensity is markedly concentrated in some pairs relative to the median, but the 28 dyads share eight animals and are not independent sampling units. We did not validate persistence of any **particular pair** across nights, estimate source-conditioned random expected J, or compute any p-values. Do not posthoc select pairs with high J.
4. Station uptime/source coverage and changing prey/roost activity patterns were not independently measured as synchronized availability controls. Thus no *excess synchrony* or *temporal avoidance* inference is warranted. Absolute logger timezone origin is not independently verified. 
5. The May 2024 source batch reports **zero mother–daughter dyads** in the original study's analyzed batch; this two-night subset cannot test kinship-mediated attraction.
6. No 3D altitude, prey captured, energetics, sonar spectra or experimental opportunity manipulation: cannot causally explain JAE's individual vertical-use strategy or estimate personal-payoff thresholds. The meaningful new observation is a **coarse middle layer of independently observed temporal co-use** alongside prior marginal UD overlap.

## Next decisive test, not executed

Verify station logger uptime and common sampling-clock reliability from original source documentation, then compare observed same-receiver minutes against the **predeclared**, bat-hour/receiver-preserving surrogate in the pre-outcome contract, with serial dependence and clustered biological units. If the station availability/clock assumptions cannot be substantiated, STOP at descriptive result above. No interpretation of source 347/516 as excess over null or social strategy until then.

**Scientific verdict:** `SUPPORTED_ACTUAL_MINUTE_BIN_SAME_RECEIVER_CO_DETECTION_DESCRIPTIVE_ONLY`; `NO_CAUSAL_SOCIAL_AVOIDANCE_OR_PAYOFF_RESULT`.
