# V6 fixed-source sensor-clock and receiver-key structural QA (pre-data contract)

**2026-10-10, frozen BEFORE reading timestamp/rx source cells.** Prior [categorical V5 CI 38012020164](https://github.com/zuizui0223/batter/actions/runs/38012020164) confirms that eight original tagged-bat CSV prefixes each have a distinct, nonmissing RFID and transmitter ID on both 2024-05-15 and 2024-05-16. That is an animal identity/source-structure result, **not a social interaction or 3D movement result**.

## Next narrow scientific gate

Can the 16 original bat×dated-night event tables support a defensible time-conditioned receiver-footprint *co-detection* analysis, or are their timestamps and receiving-station identities structurally inadequate?

Use ONLY the sixteen original OSF resource IDs and names frozen in `MYOTIS_2026_EIGHT_TAG_TWO_NIGHT_CATEGORICAL_CONTRACT_V5.md`; no other files or source variations, and no new bat selection by measured behavior.

From CSV files, inspect **only** `timestamp`, `date`, and `rx` values (and source row count). All RFID/TX comparisons have already been evaluated in separate V5, so do not inspect identifier values in this gate. Do not inspect `dyad`, `time`, `rssi`, `lon_sn`, `lat_sn`, `grid_sn`, `box`, `batch`, `records`, altitude, original prey captures, derived space co-use or any pairwise bat response.

Original article context: 65 stationary BLE receiver loggers, 2-second mobile/station sample schedules 21:00–05:00, a gateway for time synchronization, receiver footprints overlapping with nominal ~35m detection range. None of that proves the actual source clocks are synchronized, or that non-detection represents absence when a station is offline.

## Predefined structural indicators, never show raw values

Per file, at most 900KB verified original OSF CSV contents:
1. exact first-row header; required `timestamp`, `date`, `rx` fields; original OSF file metadata ID↔filename confirmation;
2. number of technical rows; nonempty receiver-key count/fraction; distinct receiver keys **count only** (never actual station IDs or station coordinates);
3. valid timestamp fraction using an explicitly fixed parser:
   - decimal POSIX epoch seconds (10 integer digits, optional fractional part), or integer milliseconds (13 digits), always mapped to UTC;
   - strict ISO8601 date/time with an explicit offset or `Z` mapped to UTC; naive ISO datetimes may be parsed but flagged **timezone unknown**, not silently assumed local time.
   - Reject unrecognized time strings; accepted parsed years restricted to [2024,2025] for this original source.
4. fraction of adjacent original rows with nondecreasing parsed timestamps, and number of exact duplicate timestamps (technical source quality only; source may not be sorted); no original clock times written to output;
5. proportion of valid original date categories, allowing the dated folder civil date and the following date, without inferential timezone conversion.

No inferential p-values, dyad enumeration, station-sharing counts, overlap ratios, lat/lon, site maps, actual event times or exact animal identifiers may be emitted.

## Go/no-go criteria

`PASS_EVENT_TIME_RECEIVER_SCHEMA_ONLY` if all 16 files are retrievable, source ID metadata matches, ≥95% timestamps parse in a declared time format (including flagging timezone ambiguity), ≥95% `rx` nonblank, positive records, and declared `date` values are valid and within source filename day or its next day. A PASS is an engineering/schema eligibility assessment **only**, NOT evidence of co-detection.

`HOLD_TIMEZONE_AMBIGUITY` if source times are mostly naive or epoch conventions cannot be related to field sampling schedule without an author-code dictionary. Do not silently compute simultaneous occupancy in different clock frames. `STOP_UNUSABLE_TIMESTAMP_OR_RECEIVER_SCHEMA` for failure of structural thresholds, `STOP_ORIGINAL_SOURCE_ACCESS` on inaccessible or modified original files.

If PASS/HOLD, a **separate** new pre-outcome contract is mandatory for temporal co-detection, including station-uptime and missingness safeguards; the eight recurring tags imply a maximum of 28 *potential* dyads, not observed contacts. The sampling unit is bat/night or dyad/night, not individual beacons. Kinship/social causality, 3D altitude, acoustic masking and prey capture remain entirely unmeasured here.
