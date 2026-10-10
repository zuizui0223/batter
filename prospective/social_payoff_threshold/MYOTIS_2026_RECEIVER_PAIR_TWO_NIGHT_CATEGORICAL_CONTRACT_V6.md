# V6: same receiver support across eight identified bats, two nights — categorical pre-data contract

**Frozen 2026-10-10 BEFORE reading any original `rx` data cells.** Child of original V5 stable-RFID success [GitHub Actions #38012020164](https://github.com/zuizui0223/batter/actions/runs/38012020164). The original 16-file allowlist and strict IDs are unchanged. No JAE / 3D spatial outcome or social interaction significance is amended.

## Narrow primary structural question

For eight author-linked independently verified RFID bat identities repeatedly monitored in sampling nights 20240515 and 20240516, did two bats have **at least one matching stationary receiver candidate ID (`rx`) within each night**? This only tests a **potential shared detection footprint**, not synchronous co-detection, direct contact, dyadic avoidance or cooperation.

Only inspect the categorical **`rx` column** from the 16 exact source CSVs in `MYOTIS_2026_EIGHT_TAG_TWO_NIGHT_CATEGORICAL_CONTRACT_V5.md`. Earlier v5 has already verified stable one-to-one `rfid`/`tx` across both nights. Require exact file IDs/name via OSF metadata and the original source's fixed 20240515/16 directory. Do not inspect or log row values from `timestamp`, `time`, `rssi`, `lon_sn`, `lat_sn`, `dyad`, `grid_sn`, prey, body elevation, `records` or `box`. No raw station IDs, tag IDs, MAC addresses, coordinates or roost metadata logged.

**Measurements (structural only)**:
1. Per night: total distinct nonblank `rx` IDs, number of bat files with at least one valid receiver key and fraction of technical event rows missing `rx`; technical row counts are not independent animals/visits
2. Per bat/night: number of distinct receivers (counts, optionally original public filename prefix, no receiver identities)
3. All fixed 28 unordered bat-series pairs: number sharing >=1 receiver ID in 20240515; number sharing >=1 in 20240516; number sharing >=1 receiver in **both separate nights**, and number sharing the **same exact receiver ID** on both nights. The first three summaries do not imply temporal overlap, and the last is even stricter structural eligibility, NOT a detection of actual co-occurrence
4. Report only aggregates; no pairwise identity of the members of social or familial dyads, no p-values or inference from 2-s beacons.

**Quality stops:** if any file missing, invalid source identity, no `rx` schema, unexpected file header, any failed source/date support from original V5, >1MiB source, STOP and do not silently retain successful subsets. Use the exact original OSF download route and previously source-verified regional/object-storage hosts only. Do not silently interpret zero `rx` entries as social avoidance; it could be missing detector coverage. Do not claim physically independent station footprints without the original receiver deployment/RSSI calibration map.

**Pass** `PASS_SHARED_RECEIVER_STRUCTURE_BOTH_NIGHTS_ONLY` if all 16 are structurally sound, every bat has receiver support in both nights, and >=1 bat pair has receiver-ID intersection within *both* nights. **HOLD** `HOLD_NO_CROSS_NIGHT_SHARED_RECEIVER_PAIR` if all data sound but no repeatedly shareable pair. Both statuses **forbid** biological synchrony or behavioral outcome tests.

## Next scientific gate

If V6 positive, a new contract must fix the exact receiver-footprint co-detection time tolerance, station observation effort, clock drift, adjacent-receiver overlap, within-night activity/serial autocorrelation and multi-dyad individual sharing **before** any `timestamp`, RSSI or spatial coordinates are used. Two nights and eight tagged bats are a support floor; 28 possible pairs are not 28 independent animals. Avoid conditioning on the subset of bats that stayed in the patch when measuring any future payoff.
