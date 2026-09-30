# Next external validation priority v1

## Status

**OUTCOME-BLIND PRIORITY LOCK.**

This priority order uses candidates that were already present in the pre-Nyctalus external-candidate ledger and uses only source metadata / data structure, not any unopened vertical outcome.

## Priority 1 — Hipposideros armiger + H. pratti

Source:
- Dryad DOI: `10.5061/dryad.j0zpc86r1`
- file: `GPS_data.csv`

Public metadata establish:
- 17 tracked adults in total;
- 9 *H. armiger* and 8 *H. pratti*;
- GPS logging nominally every 10 min during the nocturnal tracking window, movement-triggered;
- native `height` in metres above ground level;
- ambient `temp` recorded by the logger;
- source paper reports repeated individual foraging-site fidelity over 7–10 consecutive nights.

Why first:
1. native AGL is directly relevant to vertical space use;
2. repeated-night structure is explicitly reported;
3. two sympatric species provide a biologically interesting independent system;
4. no public pre-processing exclusion of roost-neighbourhood GPS points is reported in the dataset metadata;
5. source-level temperature may later support a separately frozen environmental context test if, and only if, primary replication is first completed under its own contract.

Current status:
- structural gate criteria already frozen on `prospective/hipposideros-structural-gate-v1`;
- numeric height remains unopened in that family;
- direct file download currently fails because Dryad returns HTML / requires authenticated API download;
- status = **PENDING_ACCESS**, not structural FAIL.

Before any vertical analysis:
- acquire the exact raw file through a normal authorized Dryad route;
- verify source checksum;
- resolve individual-to-species mapping without using height;
- execute the already-frozen >=50-fix / >=2-night structural gate;
- if PASS, freeze the full vertical estimator before numeric height is opened.

## Priority 2 — Leptonycteris nivalis

Source:
- Dryad DOI: `10.5061/dryad.stqjq2cfg`
- file: `GPS_data_Leptonycteris_nivalis__Summer_2024_GPS__TX__USA.xlsx`

Public metadata establish:
- 21 tagged bats;
- fixes programmed every 10 min from sunset to sunrise;
- native WGS84 ellipsoidal altitude;
- GPS points within approximately 1 km of the protected roost were removed before public release.

Why second:
- sample size and repeated nocturnal GPS scheduling are promising;
- however the vertical reference is ellipsoidal rather than terrain-relative;
- the public roost-neighbourhood exclusion removes one biologically important central-place context before analysis.

Current status:
- structural gate criteria frozen on `prospective/leptonycteris-structural-gate-v1`;
- numeric altitude remains unopened;
- direct file download currently requires authenticated Dryad access;
- status = **PENDING_ACCESS**.

## Priority rule

Do not reorder candidates after seeing any future vertical outcome.

If Priority 1 becomes accessible:
- run its already-frozen structural gate first.

If Priority 1 is structurally ineligible under the frozen gate:
- retain that failure;
- Priority 2 may then proceed under its already-frozen gate.

If Priority 1 remains technically inaccessible:
- Priority 2 may proceed when accessible, but must be reported as the second pre-existing candidate rather than a replacement selected from vertical outcomes.

## External-validation objective

The next successful external programme should answer only:

> Does centered individual vertical-distribution identity exceed its complete pipeline-specific identity-exchangeability null in a genuinely response-unopened bat tracking source?

Mechanism extensions are not opened unless separately frozen after the external primary result and must never overwrite the primary verdict.
