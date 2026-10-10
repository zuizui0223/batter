# Myotis 2026: two-date categorical stable-tag audit V4 (frozen before row-level structural inspection)

**Pre-data contract, 2026-10-10**. Verified at previous independent stages:
- OSF project `sg6dz` is authentic and publicly accessible;
- official README [GitHub Actions 38011625165](https://github.com/zuizui0223/batter/actions/runs/38011625165) states `sn_prox` has a subfolder for each sampling date and data for each **tagged bat** stored in individual CSV files;
- two same-tag filename entries `0A62_20240515.csv` / `0A62_20240516.csv` exist with source resource IDs **698dad850d35ac498ec72cd3** / **698dadb876b09fd62fe255fe**;
- [corrected header-only source CI 38011659642](https://github.com/zuizui0223/batter/actions/runs/38011659642) returns identical source headers `timestamp,date,batdate,time,rx,tx,rfid,dyad,rssi,batch,box,grid_sn,lon_sn,lat_sn,records`. The compact `rx`, `tx`, `rfid` aliases are **candidate** receiver, transmitter and biological RFID identifiers; `dyad` semantics are still unverified.

## Fixed narrow categorical objective

**Does the same original dated tag file contain consistent, nonblank RFID and mobile transmitter identifiers on both days?**

This is a source integrity gate, not a new animal behavior hypothesis, not a test of co-detection, and **not** proof of independent dyadic temporal co-use.

### Scope restriction

- Open exactly the two previously frozen original OSF file IDs using the canonical regional OSF download path, with the already source-verified HTTPS regional/object-storage hosts. Require OSF metadata identity and source byte sizes <=1MiB per file.
- Read rows only to extract **categorical** fields `rfid`, `tx`, and declared `date`. `dyad` can only be counted as presence/missing, not interpreted as interaction. Do not inspect or compute any `timestamp`, `time`, `rssi`, `records`, `grid_sn`, `rx`, `lon_sn`, `lat_sn`, `box`, `batch` value.
- No raw RFID, MAC, tag IDs, equipment IDs, receiver names, precise roost coordinates, or individual detections printed. All identifying categorical strings must be kept only as transient local variables and compared for equality across days; report only cardinalities, boolean equality, row totals, content hashes and missingness.
- All row counts are **technical events**; they do not become independent animal observations. A header saying `dyad` is not proof of a confirmed simultaneous encounter.
- Date column must match its source dated file folder after canonical conversion `YYYYMMDD`, `YYYY-MM-DD`, or `YYYY/MM/DD` with no new timezone interpretation.
- If RFID is absent, inconsistent or nonmatching between the two files: `STOP_NOT_STABLE_BIOLOGICAL_TAG`. If RFID matches and transmitter matches within each file and across both days, `PASS_CATEGORICAL_SAME_TAG_TWO_DAYS_ONLY` (still **NOT** proof of same mother/daughter dyad or independent social interaction).
- If actual rows cannot be accessed safely, `STOP_CATEGORICAL_SOURCE_INACCESSIBLE`.
- No p-values, behavioral effect sizes, social co-detection values or adaptive-payoff claims are authorized.

### Next scientific gate if categorical support passes

New independently frozen contract must specify each bat's matched night support, receiver clock quality, detection range, pseudoreplication controls and predeclared time-overlap null **before** inspecting any co-detection times. At least two real bat IDs in the same dates are needed for a dyad, and stable tag identities do not guarantee same-site/same-time exposure.

**Biological claim ceiling:** The source can potentially test receiver-footprint temporal co-use, not 3D fine-altitude policy, actual prey capture or adaptive acoustic buffering.
