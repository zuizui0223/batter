# Leptonycteris external-validation access status v1

## Status

**TECHNICAL ACCESS STOP — NOT A STRUCTURAL OR SCIENTIFIC FAIL.**

Prospective structural branch:
`prospective/leptonycteris-structural-gate-v1`

Source was already present in the pre-Nyctalus outcome-blind external-candidate ledger:
- Dryad DOI `10.5061/dryad.stqjq2cfg`
- file `GPS_data_Leptonycteris_nivalis__Summer_2024_GPS__TX__USA.xlsx`
- taxon: *Leptonycteris nivalis*
- 21 tagged bats according to source metadata
- native vertical field: `Altitude (m)`

The structural contract was frozen before any numeric altitude value was read.

## Frozen structural gate

- individual: `Tag ID`;
- session: local calendar date from `Fix Date-Time (UTC-5)`;
- minimum >=50 nonvertical-valid fixes per session;
- repeat individual: >=2 qualifying nights;
- PASS requires >=5 repeat Tag IDs;
- numeric `Altitude (m)` values are excluded from the structural read;
- failure cannot be rescued by lowering the >=50 threshold.

## Access result

Public unauthenticated download routes were tested fail-closed.

For file-stream id `4192796`:
- ordinary download endpoint returned an HTML page rather than an XLSX file;
- stash endpoint returned an HTML page rather than an XLSX file;
- API `/download` endpoint returned **401**;
- API `/content` endpoint returned **404**.

The script requires XLSX ZIP magic before any workbook is opened, so the returned HTML was rejected.

Latest diagnostic workflow:
- run `36696655049`
- head `d5cbb53d9489a33f3a513147fb3f2aaefc40dd7e`

## Outcome-blindness status

Numeric altitude magnitudes remain **UNOPENED**.

No Tag ID or date was admitted/rejected using altitude.

No structural verdict has been reached.

## Decision

Candidate status: **PENDING_ACCESS**.

Do not:
- call this a structural failure;
- lower the frozen >=50-fix rule;
- inspect altitude manually to choose a subset;
- substitute a different endpoint after access becomes available.

An authenticated Dryad download can resume the already-frozen gate without changing the scientific criteria.
