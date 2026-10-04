# Source B all-individual data-structure support amendment v1

## Status

**FROZEN BEFORE ANY SOURCE B MOVEMENT ARRAY VALUE IS LOADED.**

Programme:
`prospective/ontogenetic-path-dependence-v1`

Parent contracts:
- `SCHEMA_PREFLIGHT_CONTRACT_V1.md`
- `SCHEMA_FILE_OPENING_ALLOWLIST_V1.md`
- `SOURCE_B_CODE_OPENING_AMENDMENT_V1.md`
- `FIRST_FLIGHT_SELF_PREDICTABILITY_CONTRACT_V1.md`

## Purpose

Determine whether the ordinary first-flight archive has enough chronological replication to justify a later route estimator.

This amendment authorizes **MAT-file directory metadata only** for every ordinary juvenile `data.mat`.

It does not authorize loading the `data` struct values.

## Source topology already fixed from public metadata

Use only the ordinary root:
- `Pure data`, folder id `10119824-3ab6-46b4-927e-1b2de8abe242`.

Use only its two ordinary cohort folders:
- `GPS_2016_2017`, folder id `e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9`;
- `GPS_2017_2018`, folder id `d66d9326-798c-4d88-9491-85d903cf1b75`.

Exclude:
- `Translocations - GPS_2016_2017`;
- `pure data2`;
- `pure data50`;
- `pure data100`;
- `pure data250`;
- any derived/result/code folder.

The public folder metadata contain:
- 8 direct individual folders in 2016–2017;
- 14 direct individual folders in 2017–2018;
- total ordinary individual folders = **22**.

## Why top-level struct length is structural rather than an outcome

The already-authorized source code establishes that:
- `createRealDays(data,...)` sets `firstDay = datetime(data(1).timeStart)`;
- it iterates `data(i)` as successive tracked days;
- route-processing code accesses `data(day).track`.

Therefore the top-level MATLAB shape of variable `data` reports the number of stored tracked-day records.

It does not report route geometry or a route effect.

## Authorized operation

For every direct individual folder under the two ordinary cohort folders:

1. obtain public file metadata for that folder;
2. identify the file named exactly `data.mat`;
3. verify its public filename/id/size/hash metadata;
4. download the MAT container only to allow `scipy.io.whosmat`;
5. call `whosmat` only;
6. report:
   - cohort;
   - individual folder name;
   - file id;
   - file bytes/hash;
   - top-level variable names/classes/shapes;
   - if variable `data` is a 1×N or N×1 struct, report N as `stored_day_records`.

## Explicitly forbidden

Do not call:
- `scipy.io.loadmat`;
- HDF5 array reads;
- MATLAB execution.

Do not read:
- `data(i).timeStart`;
- `data(i).timeEnd`;
- `data(i).track`;
- x/y/lat/lon;
- tree/destination values;
- route tables or derived result MAT files.

Do not calculate:
- route similarity;
- route entropy;
- self-history advantage;
- experience slope;
- destination use;
- movement distance.

## Structural pre-gate

A juvenile can remain a candidate only if:
- `data` exists as a struct;
- `stored_day_records >= 6`.

The Source B programme proceeds to a **second structural field allowlist** only if at least **5 juveniles** meet this pre-gate.

Passing this pre-gate does not establish six valid independent trips. It only establishes that enough stored daily records exist to justify reading a minimal chronology/validity field set under a new frozen amendment.

## Stop rule

If fewer than 5 juveniles have >=6 stored day records:
- STOP Source B;
- do not load movement arrays;
- do not lower the threshold;
- do not substitute derived/resampled copies.
