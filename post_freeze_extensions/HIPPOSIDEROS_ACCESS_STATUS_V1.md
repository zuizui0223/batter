# Hipposideros external-validation access status v1

## Status

**TECHNICAL ACCESS STOP — NOT A STRUCTURAL OR SCIENTIFIC FAIL.**

Prospective structural branch:
`prospective/hipposideros-structural-gate-v1`

Source was already present in the outcome-blind external-candidate ledger before the Nyctalus result:
- Dryad DOI `10.5061/dryad.j0zpc86r1`
- file `GPS_data.csv`
- native vertical field: `height` (AGL)
- 17 tracked adults reported by the source metadata.

The structural contract was frozen before any numeric height value was read.

## Frozen structural gate

- session: deterministic nightly date rule;
- minimum >=50 presence-qualified fixes per session;
- repeat individual: >=2 qualifying nights;
- PASS requires >=5 repeat individuals;
- numeric `height` values prohibited during structural screening;
- failure cannot be rescued by lowering the >=50 threshold.

## Access attempts

GitHub Actions attempted only transport/access operations.

Latest fail-closed HTTP/content results:
- `https://datadryad.org/downloads/file_stream/4102381` -> **200 HTML**, not the frozen CSV;
- `https://datadryad.org/stash/downloads/file_stream/4102381` -> **200 HTML**, not the frozen CSV;
- `https://datadryad.org/api/v2/files/4102381/download` -> **401 JSON**;
- `https://datadryad.org/api/v2/files/4102381/content` -> **404 HTML**.

The structural script now accepts a download only when its first CSV line contains the frozen required fields. The 200 HTML responses therefore fail closed before any table is parsed.

Latest diagnostic run:
- workflow `36696650337`
- head `380c0d62f6eb900ce2fbbbf98863d43cbe1dcc13`

## Outcome-blindness status

Numeric height magnitudes remain **UNOPENED** in this prospective family.

No individual was admitted or rejected using height.

No structural verdict was reached because the raw table could not be downloaded in the unauthenticated Actions environment.

## Decision

Do not:
- relabel the access failure as a structural FAIL;
- lower the fix threshold;
- use a height-based subset;
- click/open the data table manually merely to inspect its vertical values.

The candidate remains **PENDING_ACCESS**.

A future authenticated Dryad API download may resume the already-frozen structural gate without changing its scientific criteria.
