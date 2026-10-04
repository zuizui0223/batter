# Schema file-opening allowlist v1

## Status

**FROZEN BEFORE ANY ROUTE GEOMETRY OR NEW ROUTE-SIMILARITY OUTCOME IS OPENED.**

Programme:
`prospective/ontogenetic-path-dependence-v1`

This document authorizes only the minimum file-content inspection required to determine whether the frozen schema/support gates can be evaluated.

The JAE v0.4.0 firewall remains absolute.

## General rule

Opening a file for **schema inspection** does not authorize opening the prospective biological outcome.

Allowed operations are restricted by file class:

- archive: list member names, sizes and source-code text only where explicitly allowed;
- spreadsheet: sheet names, dimensions, column headers, data types and structural ID/date/category fields only;
- MATLAB file: variable directory, variable names, shapes, classes and metadata using `whosmat`/HDF5 object metadata; do **not** load movement-coordinate arrays;
- source code: read transformations, variable definitions and file relationships; do not execute code that computes route similarity, route overlap, route entropy or mother/self predictive contrasts.

No download URL may be followed for a file not covered below.

---

## Source A — Goldshtein maternal navigation dataset

Dataset:
`gpcg9m5758`, version 1.

### A1. Code.zip — ALLOW schema/source-code inspection

- file id: `85077631-f5b9-469a-a628-1ce652944cf8`
- filename: `Code.zip`
- size: 32,244 bytes
- SHA256: `bfe2fe7a691c33a24b00a8cf56511c3668cce0ce3ebc33c8cc911df61579d773`

Allowed:
1. verify size/hash;
2. list archive member names;
3. read text source files;
4. extract variable names, source file paths, mother/pup linkage rules, independence definitions, flight/trip identifiers, destination labels and coordinate semantics;
5. record which raw files would be required later.

Forbidden:
- executing any route-comparison endpoint;
- calculating a new route distance/similarity;
- using hard-coded published result values as prospective outcomes.

### A2. data_age_fa_all.xlsx — ALLOW structural columns only

- file id: `4bd0e11b-8329-422a-aed6-2bc3e7299f81`
- filename: `data_age_fa_all.xlsx`
- size: 47,700 bytes
- SHA256: `c7bfa0489d04c028d1d8dee565865da74dfb3499245eecf9234b14509aa54e81`

Allowed:
- workbook/sheet names;
- dimensions and headers;
- ID, mother/pup relationship, age/date, flight index, categorical independence/status fields if present;
- counts needed by `SCHEMA_PREFLIGHT_CONTRACT_V1.md`.

Forbidden:
- reading coordinate trajectories;
- inspecting route-distance, route-angle or route-similarity values as biological outcomes.

### A3. FA-FlightIndex-Lab.xlsx — ALLOW structural columns only

- file id: `1d8da58c-162b-4558-9117-b96d9229f5c2`
- filename: `FA-FlightIndex-Lab.xlsx`
- size: 10,471 bytes
- SHA256: `88cf76825a3fbf49dc613fe61afc7c5f02f474f38a3510255736440a0f177f08`

Same restrictions as A2.

### Explicitly NOT authorized from Source A

Do not open at this stage:
- `FlightDistanceAngle_ImprintedColony.xlsx`;
- `FlightSpeedCaptivity.xlsx`;
- `GPS data adult males.zip`;
- `GPS data stationary error.zip`;
- `GPS data.zip`;
- `Temperature data.zip`.

In particular, the 1.55-GB `GPS data.zip` stays closed until:
1. schema/support PASS;
2. the exact route estimator and sampling contract are frozen;
3. only the required individual/trip files are explicitly promoted.

---

## Source B — Harten first-flight dataset

Dataset:
`n9d8gbz3xr`, version 1.

### B1. batSex.mat — ALLOW MATLAB metadata only

- file id: `03002db4-e81c-4f91-81e2-dd825b571f5f`
- filename: `batSex.mat`
- size: 1,142 bytes
- SHA256: `4f5d10f50fcd2838700cbd1decc5d785c2253835f4494c9e8c7f88ae40d2bdf1`

Allowed:
- MAT-file variable directory, names, shapes/classes;
- if the variable is plainly a non-spatial ID/sex lookup, load that lookup only.

### B2. buildingTableWithBatNo.mat — ALLOW metadata; non-spatial lookup if unambiguous

- file id: `eb46274b-2fc9-4165-9bf9-fd399a7b7075`
- filename: `buildingTableWithBatNo.mat`
- size: 4,788 bytes
- SHA256: `efd2c500d6dea7db83c118dc4daba6633aa852f8677b583d2a81aa42a475e6e5`

Allowed:
- variable directory;
- identifiers and categorical building/destination lookup only if its non-trajectory meaning is source-clear.

### B3. trees.mat — ALLOW metadata only at first pass

- file id: `65c7574e-a3c5-4105-bcc0-a1551d6e2f0c`
- filename: `trees.mat`
- size: 17,247 bytes
- SHA256: `26acb2199bacd5244d505cbeb91c9c46bd9a1ac0a01f6bf5926a17250461c6cf`

First pass:
- variable directory only.

Tree coordinates/identities may be opened later only if required to establish a destination-matching design and before any target route comparison.

### B4. Per-individual MAT schema probe — deterministic ALLOW

The public metadata show nested individual folders containing a named `<individual>.mat` and/or `data.mat`.

To learn the raw schema without selecting a biologically favourable animal, authorize exactly the ordinary raw hierarchy:

- root `Pure data`, id `10119824-3ab6-46b4-927e-1b2de8abe242`;
- `GPS_2016_2017`, id `e92b9150-3ee7-49c7-9f1f-b34e6aba6ac9`;
- `GPS_2017_2018`, id `d66d9326-798c-4d88-9491-85d903cf1b75`.

The four sibling roots `pure data2`, `pure data50`, `pure data100`, and `pure data250` are derived/resampled copies and are excluded from schema selection. The `Translocations - GPS_2016_2017` subtree is also excluded.

Within the ordinary cohorts, the lexicographically first individual folders are now fixed from metadata:

- 2016–2017: `Ali`, folder id `f148a7d1-8ca7-4b99-b64d-5bf0adb6dc08`;
- 2017–2018: `Anka`, folder id `ea9161e3-b368-4cce-8aa4-753fc6b9ffe2`.

Authorize exactly those two schema probes;
- from each selected folder, inspect the named individual MAT file and `data.mat` only by MAT variable-directory metadata (`whosmat` or HDF5 object names/shapes/classes);
- do not load array values.

If the two cohorts use identical variable directories, stop after confirming identity.
If they differ, document the difference; do not add more individuals until a new schema amendment is frozen.

This deterministic rule is based only on folder names and cannot depend on route outcome.

### Explicitly NOT authorized from Source B

At this stage do not load:
- any per-individual coordinate/time arrays;
- `droneTable.mat` values;
- `weather.mat` values;
- translocation movement values;
- route geometry from any `data.mat`.

---

## Structural quantities authorized after schema is understood

Only non-outcome support counts required by the existing contract may then be produced:

### Source A
- number of reproducible mother-pup pairs;
- independent-flight boundary availability;
- number of independent trips per pup;
- number of pups meeting the frozen 4-trip / prior-history / early-late support rules;
- exact-destination identity availability.

### Source B
- number of juveniles with recoverable first-flight chronology;
- number of independent trips per juvenile;
- number meeting the frozen >=6-trip and prior-history target rules;
- exact-destination identity availability.

Do not calculate:
- route similarity;
- self advantage;
- maternal advantage;
- corridor width;
- entropy;
- trajectory overlap;
- experience slopes.

## Promotion rule

A route/coordinate file can move from CLOSED to OPEN only through a new committed estimator/data-opening contract written **before** its prospective endpoint is computed.
