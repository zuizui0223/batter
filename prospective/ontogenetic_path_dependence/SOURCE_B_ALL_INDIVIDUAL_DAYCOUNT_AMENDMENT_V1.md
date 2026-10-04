# Source B all-individual day-count schema amendment v1

## Status

**OUTCOME-BLIND STRUCTURAL AMENDMENT.**

This amendment is frozen before inspecting the number of day records for all Source B juveniles.

Parent contracts:
- `SCHEMA_PREFLIGHT_CONTRACT_V1.md`
- `FIRST_FLIGHT_SELF_PREDICTABILITY_CONTRACT_V1.md`
- `SCHEMA_FILE_OPENING_ALLOWLIST_V1.md`
- `SOURCE_B_CODE_OPENING_AMENDMENT_V1.md`

## Why this opening is needed

The authorized Source B MATLAB code establishes that:
- `data(i)` indexes a chronological track-day object;
- `data(i).timeStart` / `data(i).timeEnd` define each day;
- `createRealDays.m` sets `firstDay = datetime(data(1).timeStart)` and computes elapsed real day from that origin;
- route geometry is stored below `data(i).track`.

The primary Source B structural gate requires at least:
- 6 chronological independent track days for an individual;
- enough later days to permit targets with at least two strictly prior self-history days;
- >=5 biological individuals.

This can be assessed without opening any coordinate or route value.

## Newly authorized opening

For **every ordinary juvenile individual folder** under the two source-defined non-translocation roots:
- `Pure data/GPS_2016_2017`
- `Pure data/GPS_2017_2018`

authorize only:

1. folder name and folder UUID;
2. file metadata for the folder's `data.mat`;
3. MATLAB top-level variable-directory metadata via `scipy.io.whosmat`;
4. the top-level `data` variable's **shape and class only**.

No struct field values may be loaded.

In particular, do not open:
- `data(i).track.x`;
- `data(i).track.y`;
- longitude / latitude;
- route or visit geometry;
- destination identity;
- any derived route statistic;
- any per-day `timeStart` value.

## Frozen interpretation

Before these shapes are opened:

- one element of the top-level `data` struct is treated as one source chronological track-day object, following the source code;
- `n_days = number of elements in data`;
- structural day-count PASS for an individual requires `n_days >= 6`;
- Source B day-count gate passes only if **>=5 individuals** satisfy `n_days >= 6`.

This is a necessary, not sufficient, gate.

A later outcome-blind opening must still establish:
- that the public cohort corresponds to the source's first-outdoor-flight ontogenetic series;
- enough valid chronological self-history after source filtering;
- any destination/task support required by the final estimator.

## No rescue

After all-individual day counts are opened:
- do not lower 6 days;
- do not lower 5 individuals;
- do not add translocation data;
- do not use derived/resampled folders;
- do not use Source A individuals.

## Outcome firewall

This amendment opens **zero movement coordinates and zero route outcomes**.
