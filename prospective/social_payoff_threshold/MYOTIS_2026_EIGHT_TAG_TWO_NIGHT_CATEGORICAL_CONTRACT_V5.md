# 2026 Myotis: eight-tag same-bat across two-night categorical gate V5

**Source contract frozen 2026-10-10 before opening the seven additional tag series' CSV rows.** Original source identity is OSF `sg6dz`, Hernández-Montero et al. 2026 doi:10.1002/ece3.73604. Official source metadata CI 38011119952 established *eight matching exact filename prefixes* for `20240515` and `20240516`, and the author README explicitly says each dated CSV belongs to a **tagged bat**. Corrected independent one-tag categorical audit [38011908943](https://github.com/zuizui0223/batter/actions/runs/38011908943) confirms constant RFID/TX for tag series `0A62` across both nights, with no missing identifiers and correct midnight-crossing date support. No actual receiver co-detection or acoustic/position values opened.

## Exact allowlist, no arbitrary searching

Use only these sixteen OSF original files in 8 predeclared two-night matched filename pairs; identity must be independently checked against the OSF original file metadata `id` and `name`:

| File prefix | 20240515 OSF resource ID | 20240516 OSF resource ID |
|---|---|---|
| 0A62 | 698dad850d35ac498ec72cd3 | 698dadb876b09fd62fe255fe |
| 4ECA | 698dad87ab12904856dfcaed | 698dadb80d35ac498ec72cfe |
| AC37 | 698dad880d35ac498ec72cd5 | 698dadb78ef9cd34ebdfd42d |
| A42D | 698dad88ab06d8ff5ae255b6 | 698dadb70bd29b8ed4e24ba5 |
| 922C | 698dad89ab12904856dfcaef | 698dadb7ab12904856dfcb2d |
| 418B | 698dad895888d84fdec733b7 | 698dadb7ab12904856dfcb2b |
| A24D | 698dad890d35ac498ec72cd7 | 698dadb855339dbcd4c731c6 |
| 663E | 698dad8aa731d64729dfc99a | 698dadb85888d84fdec733d7 |

Each file <1 MiB original metadata. Read data rows only for categorical `rfid`, `tx`, `date` fields. Preserve the 21:00–05:00 sampling-night concept; accepted civil dates in file `YYYYMMDD` are that date and the following day. Never parse/print `timestamp`, `time`, `rx`, `grid_sn`, `lon_sn`, `lat_sn`, `rssi`, `records`, `dyad`, prey, altitude or derived co-detection values.

## Evaluation

- Per file: source name/hash, nonmissing `rfid` and `tx`, one distinct value of each, date support, technical row count; **all raw actual IDs withheld**.
- Per tagged series: are the singleton `rfid` and `tx` values IDENTICAL across the two separate dated files?
- Across all eight series: are all singleton RFID IDs **mutually distinct** in each night and remain one-to-one across nights? Likewise for TX tags. If not, report structural confusion/duplication without revealing which ID is involved beyond series label.
- Report only numbers of passed/tagged pairs and number of distinct physical RFIDs and transmitters; do not leak raw RFID strings.
- `PASS_EIGHT_DISTINCT_CROSS_NIGHT_TAGS_CATEGORICAL_ONLY` only if exactly eight distinct nonempty stable RFID mappings and distinct TX devices on both nights, no unexpected date, no structural changes.
- Otherwise `HOLD_PARTIAL_STABLE_BAT_SUPPORT`, `STOP_INCONSISTENT_BAT_TAG_IDENTITY`, or `STOP_SOURCE_FILE_INACCESSIBLE` as appropriate.
- **Never call this eight independent observations of a behavioral treatment**: it is eight biologically identifiable tags with possibly different technical event effort, not replicated randomized social/acoustic manipulations.

## Next question, not authorized here

If eight stable individuals pass, at most 28 pairwise dyads are *possible* within the two-night tag cohort, **not observed direct contacts**. Before testing any dyad co-visitation at receiver resolution, freeze independent source integrity for clock synchronization, station overlap, RSSI effort/detection bias, bat×station×night support, preselected co-detection time tolerance, and a blocked time-shift or matched conditional null preserving bat-day activity/serial autocorrelation. Two nights are a sparse floor, not a validated generality sample. No 3D altitude, captured prey, fitness or learning inference follows.
