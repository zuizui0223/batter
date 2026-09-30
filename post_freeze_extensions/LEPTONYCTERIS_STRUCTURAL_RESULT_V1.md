# Leptonycteris outcome-blind structural gate result v1

## Status

**STRUCTURAL FAIL BEFORE ANY NUMERIC ALTITUDE WAS OPENED.**

Authoritative workflow:
- run: `36720431876`
- head: `0185f517ce9e30dabda120cf0d355185eccd5b11`
- artifact: `11098047282`
- artifact digest: `sha256:18cfb8cd4bb61bb279822c19c2d32386bd29a55d02550211892971ef802ce92f`

Source:
- *Leptonycteris nivalis*
- Dryad DOI `10.5061/dryad.stqjq2cfg`
- file `GPS_data_Leptonycteris_nivalis__Summer_2024_GPS__TX__USA.xlsx`
- raw SHA256 `4283cac5eb8461665b4bb9482f44785da6df0825d18c634f6a626cc808237036`

## Outcome-blind schema audit

Workbook structure was verified without reporting numeric cells:
- GPS data sheet: `LENI GPS Data`
- 21 Tag IDs
- 2,402 rows with valid nonvertical fields
- vertical field `Altitude (m)` verified by header only
- numeric altitude values read: **false**

The source notes that GPS points within approximately 1 km of Emory Peak were removed before public release and points with HDOP >20 were excluded.

## Frozen structural rule

The contract was frozen before access:
- candidate session = Tag ID × local calendar date;
- >=50 nonvertical-valid fixes per session;
- repeat individual = >=2 such sessions;
- PASS requires >=5 repeat individuals.

No threshold was changed after opening the structure.

## Result

- individuals: **21**
- qualified nights with >=50 fixes: **0**
- repeat-eligible individuals: **0**
- required repeat individuals: **5**
- verdict: **FAIL**

Per-individual maximum fixes in any candidate night ranged from 12 to 49.

The closest cases were:
- Tag 57231: max **49**
- Tag 57236: max **49**
- Tag 57240: max **49**
- Tag 57238: max **47**
- Tag 57226: max **43**
- Tag 57241: max **43**

No individual had even one >=50-fix night, so the failure is not marginal at the repeat-individual gate.

## Interpretation

This source cannot evaluate the frozen centered vertical-identity estimator under the programme's >=50-fix session requirement.

This is a **structural ineligibility result**, not a negative biological result.

Therefore:
- do not open numeric `Altitude (m)`;
- do not lower the session threshold to 49 or another value after seeing the structure;
- do not redefine sessions;
- do not use Leptonycteris as a serial rescue after the Hipposideros primary FAIL.

## Programme consequence

The candidate is closed as **STRUCTURALLY INELIGIBLE UNDER THE FROZEN COMMON ESTIMATOR**.

It may only enter a future programme if that programme defines a different estimand and structural threshold **before** any Leptonycteris vertical outcome is opened. Such a future programme must not be presented as the original external replication test.
