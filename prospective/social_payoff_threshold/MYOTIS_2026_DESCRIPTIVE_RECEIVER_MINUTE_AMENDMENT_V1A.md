# 2026 Myotis same-receiver minute co-detection: descriptive execution amendment V1a

**2026-10-10 — explicitly BEFORE ANY pairwise timestamp overlap calculation.**
Original pre-outcome question `MYOTIS_2026_TIME_CONDITIONED_CO_USE_PREOUTCOME_V1.md` was frozen before receiver/time pair statistics. Subsequent source-only checks confirmed eight distinct physical RFID/transmitter series on both 2024-05-15 and 2024-05-16 (CI 38012020164), 22/28 potential dyads with some identical receiving-station ID in both nights (CI 38012351593), and parseable original event timestamps plus receiver keys in all 16 files (CI 38012274824).

**Clock-scoping amendment:** All raw CSV timestamps are ISO date-times without timezone suffix. A strictly source-verified original author R file `func_cAKDE_amt_v2.R` reads these timestamps as `lubridate::ymd_hms(timestamp)` without an explicit timezone (CI 38012635050). The documented `ymd_hms()` default is `tz='UTC'`, which is an author-analysis **parsing convention**, NOT evidence that the original logger wall clock was truly UTC. Published Methods describe gateway time synchronization. We can compare shared string clock-minute labels across all bats within each original dated source under this common-clock assumption, but cannot infer absolute solar phase or exclude cross-device clock drift.

**Fixed signal-quality filter:** The original publication Methods explicitly excluded weak events with RSSI <= −90 dB as likely noise. Therefore the sole new allowed original cell columns for this descriptive stage are `timestamp`, `rx`, and `rssi`; RSSI is read only to classify each event as stronger than −90 dB, never output its raw magnitude or attach device-specific thresholds. Do not inspect `dyad`, `lat_sn`, `lon_sn`, `grid_sn`, `batdate`, `records`, or any prey capture/altitude field. Reading RSI for this externally published filter is a *pre-outcome* source-quality correction, not a result-dependent threshold.

## One frozen outcome and no inferential p-values

- Source: exactly 16 original files in `MYOTIS_2026_EIGHT_TAG_TWO_NIGHT_CATEGORICAL_CONTRACT_V5.md`, no selection or new tag cohorts.
- Form a set of receiver IDs per tagged bat and integer **one-minute wall-clock string bin** from parsed `timestamp` for each sampling-night source file. Interpret all source times under the author's *common* parsing convention, not as independently verified true UTC instants. No matched station/time is assumed simply from being in the same dated directory.
- Remove source events with unparseable time, missing receiving-station ID, or RSSI <= -90 (as published). Require at least 95% source timestamp/receiver schema support, at least one valid event per bat-night and stable original file hashes/metadata. Non-quantitative partial failure forces whole-stage STOP; do not cherry-pick positive pairs.
- For each **unordered bat pair** in each night, count each minute **at most once** if both bats have a detection at the **identical receiver** during that minute, regardless of duplicated beacons and the number of shared receivers. Define `J_{ij,n}` as this same-receiver, same-minute count.
- The primary report is only (a) number of potential and analysable dyad×nights, (b) number with J>0 across nights and each night, (c) total receiver-minute joint bins and the 5/50/95 percentile of J across all 28 dyads (including zero). Do not print raw RFID or transmitter IDs, receiver IDs, actual time values, coordinates, original RSSI values or per-dyad identities. No live maps.
- **No p-value, surrogate/null simulation or causal model in this execution.** Station uptime/coverage, signal attenuation, overlap between ~35m station footprints, biological encounter distances and robust independent-night replication are not separately calibrated. The current question is merely whether synchronous **co-detection at 60-second resolution** exists in this source, not whether bats choose social contact or avoid each other.

## Explicit scientific limitations

- One receiver can detect two bats up to ~70m apart and at different moments within 60 seconds. J>0 does not prove direct contact, active cooperation, or even simultaneous flight at the same point.
- Common-night sampling schedules and receiver uptime can induce J>0; there is no causal manipulation here. J=0 cannot prove social avoidance because non-detection != animal absence.
- The 28 pairs share eight animals, and two nights are too few for generality/kinship effects. Original May 2024 subset had **zero documented mother–daughter dyads** for tested overlap, so no kinship model from this sample.
- No 3D altitude, detailed flight curves, echolocation spectra, prey capture, fitness or learned history effects exist in this source layer. This is a separate middle-step test and cannot validate the JAE mechanism.

**Status before execution:** `FROZEN_DESCRIPTIVE_J_ONLY_NO_CAUSAL_SOCIAL_CLAIMS`.
