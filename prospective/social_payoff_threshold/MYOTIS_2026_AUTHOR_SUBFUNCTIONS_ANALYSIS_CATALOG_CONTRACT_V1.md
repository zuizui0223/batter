# 2026 Myotis OSF: one-time original analytical-code structure gate (source-only)

**Frozen 2026-10-10 BEFORE exploring additional author-code directories.** No animal detections, time windows, receiver positions, kinship labels, p-values, or output artifacts may be read here.

## Motivation
- [Melber et al. (2013), Ethology](https://doi.org/10.1111/eth.12123) already report long-term spatial sharing by maternal kin without frequent joint foraging among 22 *Myotis bechsteinii*. The 2026 article [Hernández-Montero et al.](https://doi.org/10.1002/ece3.73604) explicitly says its 65-receiver grid at **the same study site** was designed using those earlier VHF data. It is improper to claim novel bat spatial-vs-temporal partitioning from the 2024 OSF two-night source.
- In independent published work, [Kerth, Wagner & König 2001](https://doi.org/10.1007/s002650100352) already tested roost-together/forage-apart on *M. bechsteinii*.
- Current OSF source-backed observational layer: eight RFID-stable tag file series 2024-05-15/16, V1a full-night same-receiver-minute positive 17/28 and 14/28, post-outcome V1b 13/28 repeat positive, post-outcome V2 middle-of-logger-window 6/28,8/28 and 5/28 repeat. None gives a time-of-night- and station-effort-conditioned expectation or verified prey captured.
- Original 2026 article §2.7 excludes detections 2 h after sunset and 3 h before sunrise for foraging UD analysis, and retains **7/8** tagged May-2024 bats for that published UDOI analysis; V1a/b/V2 uses all 8. Its original author R script parses timezone-naive `timestamp` with `ymd_hms()` without explicit timezone; logger local time and clock drift are unresolved.

## Exact allowed original OSF node catalog URLs

Original project `sg6dz`, source-verified directory IDs:
- `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698db56f1300e956dfbc8a54/` — `proximity_UD/scripts/sub_functions/`, potentially time/date parse and source QA functions.
- `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698dbe01fae4711f5ac72f78/` — `proximity_UD/analysis/`, possibly author analysis scripts or README.

Only enumerate **first-page JSON file/directory names, sizes, OSF resource IDs** (max 100 names; record pagination presence; do not automatically follow subsequent pages, nested folders or any file-content links). Use the original public view-only token query as metadata-only fallback. Do not fetch `data/sn_prox`, biological output tables, `box_coords`, `sn_coords`, other source nodes or any direct CSV download.

## Decision criteria and scientific stop
- If script names plausibly indicate roost/sunset/sunrise filtering, source eligibility (7 of 8), or station uptime calibration, freeze an **exact individual script-ID and sanitized keyword/line extraction** contract before opening source code text.
- A script *named* `overlap`, `UD`, `time` does NOT validate clock or replicate eligibility; raw script must explicitly document the adjustment.
- If neither directory exposes relevant methods, log `HOLD_NO_SOURCE_CALIBRATION` and STOP time-conditioned behavioral inference, rather than scanning other time windows or claiming new social avoidance.
- Even explicit author time alignment and receiver coverage would not establish **causal** social responses or JAE 3D vertical policy mediation. There is no capture success, sonar mechanism or 3D altitude in these received station data.

**Status pre-query:** `AUTHOR_CODE_CATALOG_NOT_YET_OPENED`.
