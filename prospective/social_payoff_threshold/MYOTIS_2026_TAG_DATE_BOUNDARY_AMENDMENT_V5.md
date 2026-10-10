# V5 amendment: separate stable physical tag comparison from date-folder boundary

**Frozen 2026-10-10 before V5 data execution. Categorical-only, no behavioral outcomes.**

## Why V4's STOP cannot be interpreted as tag mismatch

V4 (CI 38011826140) accessed two preallowlisted authentic CSVs: `0A62_20240515.csv` (1,368 technical rows) and `0A62_20240516.csv` (350 technical rows). Each has exactly one nonblank RFID and one nonblank transmitter ID in that file. V4 returned `STOP_NOT_STABLE_BIOLOGICAL_TAG` because its `source_consistent` condition also required *every* event's declared calendar date to equal the dated source filename. The first source has **two distinct date labels**. Consequently V4 never evaluated cross-file RFID or TX set equality; `same_rfid=false` and `same_tx=false` in its receipt are gated outputs, NOT demonstrated actual inequality.

A night-spanning file may contain adjacent calendar dates (midnight); alternatively this could be misdated source, reused tags, timezone conversion or mixing of acquisition days. We must not choose among these without original collection definitions. This V5 amendment does NOT assume which explanation is true.

## Fixed reanalysis of already-authorized categorical source columns

- Exact same two original OSF resource IDs `698dad850d35ac498ec72cd3` and `698dadb876b09fd62fe255fe`, no additional files, animals, coordinates or sources.
- Read ONLY `rfid`, `tx`, and `date` fields, and only count technical rows. No `timestamp`, `time`, `rx`, `rssi`, `dyad`, `batdate`, `grid_sn`, `lon_sn`, `lat_sn`, captures, visits or response values may be used.
- Verify exact OSF file ID↔filename metadata, source length <=900KB, UTF-8 CSV and required header columns.
- Compute within-file nonmissing RFID and TX cardinality, cross-file equality of their *transient* sets, and per-file declared-date counts. **Never print raw RFID, TX, MAC address, receiver/roost location, or raw date/time observations.**
- Parse the `date` category in ISO-like `YYYY-MM-DD`, `YYYY/MM/DD`, or `YYYYMMDD` formats only. Check all declared dates are valid and either file-date, previous calendar date or next calendar date. No inference about timezone or unique independent nights. Report booleans and counts only.
- Identity comparison MUST be independent of the date-folder equality check. If both unique nonmissing RFID and TX sets match between files, result is `PASS_CATEGORICAL_CROSS_FILE_RFID_TX_STABILITY_ONLY`, with a separate `CALENDAR_BOUNDARY_OR_SOURCE_DATING_UNRESOLVED` flag when a source has >1 declared date. If IDs differ, `STOP_CROSS_FILE_ID_MISMATCH`; if missing/heterogeneous within file, `STOP_INTRA_FILE_ID_HETEROGENEITY`; if date parser/near-day support fails, `HOLD_SOURCE_DATE_CONSISTENCY` regardless of ID equality; if inaccessible, STOP.
- A positive source-category pass does **not** establish that original same bat physically revisited an independent site on distinct nights, much less that two tagged bats form a repeated dyad. IDs could be reused; the OSF original README claims bat-specific files but independent bat↔tag deployment/time/receiver study support remains to be verified.
- Any downstream co-detection/null/time/behavior test needs independent new design+source freeze first. There is no reason to reinterpret JAE or #79 evidence from this metadata.

## Fixed self-tests before data
1. 1,368/350 rows are *source receipts*, not target acceptance requirements for refreshed files; do not silently rescue corrupted sources.
2. Fake counterexample with date values on consecutive days and same ID must PASS ID comparison with a separate date-boundary warning.
3. Fake example with two different RFID values must FAIL ID comparison even if file dates all match.
4. No original data values or direct identifying category strings printed.

**New evidence tier: source categorical consistency only.**
