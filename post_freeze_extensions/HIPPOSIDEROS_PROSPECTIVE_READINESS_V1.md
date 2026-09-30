# Hipposideros prospective external-validation readiness v1

## Current status

**READY EXCEPT FOR AUTHENTICATED DRYAD FILE ACCESS.**

No numeric GPS `height` value has been opened in this prospective family.

Source:
- Dryad DOI `10.5061/dryad.j0zpc86r1`
- file id `4102381`
- file `GPS_data.csv`
- taxa reported by the source paper: 9 *Hipposideros armiger* and 8 *H. pratti*
- source vertical field: AGL `height` in metres

## Outcome-blind species mapping is frozen

Contract:
`species_mapping_contract_v1.json`

Rule:
1. read GPS `id` strings only;
2. extract leading alphabetic prefix;
3. require exactly two prefix groups containing exactly 9 and 8 unique IDs;
4. map the 9-ID group to *H. armiger* and the 8-ID group to *H. pratti*;
5. otherwise stop as `MAPPING_UNRESOLVED`.

No specific prefix letter is assumed to denote a species.

## Structural preflight is frozen

Authenticated preflight:
`authenticated_preflight_v1.py`

It may read:
- id;
- timestamp;
- longitude/latitude;
- presence/nonblank status of height.

It may not parse numeric height.

It freezes:
- exact raw-file SHA256;
- species mapping;
- nocturnal session rule;
- >=50-fix nightly sessions;
- repeat-individual universe;
- EPSG:32648 projected 5-km cells;
- exact target common-support counts;
- estimator-evaluable individuals;
- exact training-night universe;
- exact evaluable target-night universe.

Gates:
- >=50 presence-qualified fixes/night;
- >=50 common-support target events;
- >=3 estimator-evaluable individuals for a species panel;
- >=5 estimator-evaluable individuals source-wide.

If these gates fail, Height remains unopened and no threshold is lowered.

## Primary estimator is frozen

Contract:
`primary_design_v1.json`

Primary response:
- session-median-centered source AGL height;
- fixed residual-height bins:
  `(-inf,-400,-200,-100,-50,0,50,100,200,400,inf)`.

Horizontal context:
- WGS84 -> EPSG:32648;
- fixed 5-km grid;
- common-cell weighting identical for self and other profiles.

Prediction architecture:
- same-individual profile: equal other eligible nights;
- other profile: pool nights within each other individual, then equal-weight other individuals;
- equal target night within individual;
- equal individual within species;
- equal eligible species panel at source level.

Null:
- permute whole-night identity labels within species;
- preserve exact session-count multiset per identity;
- replay target support and complete prediction pipeline.

Calibration:
- B=9,999;
- seed=2026093007;
- upper-tail test.

Primary PASS requires:
1. frozen structure/receipt match;
2. source observed-minus-null mean > 0;
3. p(null >= observed) <= 0.05.

Species-specific results are secondary diagnostics and cannot replace the source-level verdict.

## Height-opening firewall

The preflight writes `height_opening_receipt_v1.json`.

The primary validator refuses to run unless:
- that receipt is committed;
- receipt status is `HEIGHT_MAY_OPEN`;
- source SHA matches;
- committed primary-design SHA matches the SHA frozen in the receipt;
- `DRYAD_API_TOKEN` is present.

Observed target support is checked against the preflight receipt before the vertical statistic is accepted.

## Access route

Dryad now requires authenticated file download for this file.

Workflow:
`hipposideros-authenticated-preflight-v1.yml`

It reads:
`secrets.DRYAD_API_TOKEN`

The token is never written to analysis output.

Official Dryad endpoint:
`GET https://datadryad.org/api/v2/files/4102381/download`
with
`Authorization: Bearer <token>`.

## CI

Prospective-design lint:
- workflow: `36715410331`
- conclusion: **SUCCESS**

Validated:
- JSON contracts parse;
- preflight compiles;
- primary validator compiles;
- primary workflow is receipt-gated;
- Dryad token is required rather than bypassed.

## Execution order

1. create a Dryad API token through the user's Dryad account;
2. store it as GitHub Actions repository secret `DRYAD_API_TOKEN`;
3. manually run `hipposideros-authenticated-preflight-v1`;
4. inspect only its structural output;
5. if PASS, commit the generated `height_opening_receipt_v1.json` unchanged;
6. manually run `hipposideros-primary-validation-v1`;
7. retain PASS or FAIL exactly as returned;
8. do not open mechanism extensions as rescue after a FAIL.

## Scientific role

A PASS would supply the genuinely response-unopened external confirmation that Nyctalus could not provide under its first frozen protocol.

A FAIL would be equally informative and must be retained as the external prospective result.

The frozen JAE v0.3.8 submission remains unchanged.
