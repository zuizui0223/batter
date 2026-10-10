# Post-outcome central observation-window sensitivity — frozen V2 (2026-10-10)

**EVIDENCE TIER: exploratory sensitivity, not confirmatory animal-behavior test.** This contract is recorded AFTER the same-source all-night V1a/J scores and V1b two-night binary intersection were opened. All original V1a results (17/28 and 14/28 bat pairs, 13/28 positive both nights) remain authoritative all-night descriptors and are not replaced or reclassified.

## Biological motivation from the published paper

Hernández-Montero et al. (2026), Ecology and Evolution DOI 10.1002/ece3.73604, Methods §2.2 set fixed receiver sampling at **21:00–05:00**; Methods §2.7 excluded data from the first **2 h after local sunset** and final **3 h before sunrise** when interpreting UDs to avoid day-roost departure/return bias. Both are established prior art from the author, not discovered here.

Author source R parsed ISO-naive `timestamp` with `lubridate::ymd_hms(timestamp)`, without an explicit timezone. This establishes a *consistent code parsing convention*, not verified wall-clock timezone nor logger drift/phase. Exact solar sunset and sunrise for this original site are NOT recovered or computed in this project. Do **not** call a clock-window cut the author's precise solar-based window.

## Exactly one fixed sensitivity window

Restrict each of the 16 *previously fixed* original OSF bat×night files to 23:00 ≤ source clock hour < 02:00 **across midnight**; equivalently `hour in {23,0,1}`. It is the central **3-hour portion** of the declared eight-hour nightly logger programme 21:00–05:00, and is a conservative **monitoring-midnight window**, NOT proven foraging-only or astrophysically aligned to the author's sunset/sunrise cut.

Use the original `myotis_2026_one_minute_same_receiver_descriptive_v1a.py` unchanged:
- 8 RFID-linked tagged bats, 2 separately dated original source nights 20240515/16, same exact 16 allowlisted OSF resource IDs.
- Original author RSSI **>-90 dB**, identical station ID and same **60-second raw-source-clock minute**; at most one co-receiver minute counted per dyad per minute regardless of number of station detections.
- Require all 16 original file source QA checks PASS, and exact V1a all-night margins remain 17/28 and 14/28 (source integrity guard). No bat, night, station, or pair selection after outcomes.
- For each source-night, report only count of 8 bat files with at least one RSSI-qualified record in the fixed core, number of eligible bat×minute keys (not unique flight events), number of 28 possible bat pairs positive within window, pair×minute co-receiver total, median of 28 counts.
- At pair level, report only the *count* positive in **both** core-window nights, core only-May15, core only-May16, neither (sum 28), and optionally overlap with the already-opened all-night 13 repeated pairs **as a descriptive paired subset count**. These are not p-values and not biologically independent pairs.
- Report aggregated source technical event fraction in central window **without raw clocks, coordinates, RFID, exact station IDs or per-pair identities**. No source-event table in output.

## Fixed deterministic expectations

- Central-window total co-receiver minute incidences <= all-night 347/516, central-positive pairs <= 17/14 per corresponding night, and cross-night positive pairs <= previously open 13.
- Because central subset is nested, raw losses should not be interpreted as social avoidance; shorter observation exposure necessarily reduces co-detections.
- Do not count 20240515 source-file next-civil-day timestamps as a third sampling night; each original dated file remains part of that fixed source-night.
- Clock timezone, sun position, logger-uptime, device transmission quality, roost overlap and prey availability remain uncontrolled. Without a time-and-site-conditioned calibrated null, cannot infer attraction/competition, independent social encounters or payoff.
- No exploratory search over 5, 10, 30, 120-second tolerances, timezone offsets, other hour ranges or RSSI limits after seeing the core result. One read, then close.
- The original paper's May 2024 UD cohort had 7/8 eligible, whereas these source-file descriptors cover all 8; no valid same-subject comparison of UDOI versus our co-receiver outcome is claimed.

## Safe statuses

`EXPLORATORY_CORE_LOGGER_WINDOW_DESCRIPTIVE_ONLY` if QA/margin gates pass and the counts are valid.
`STOP_SOURCE_QA_OR_MARGINS` if any original source, V1a margin or nested-subset consistency check fails.

**Scientific ceiling:** time-restricted station-scale co-detection, not foraging interactions, niche-partition mechanism, prey capture, fitness, 3D height or learned social preferences.
