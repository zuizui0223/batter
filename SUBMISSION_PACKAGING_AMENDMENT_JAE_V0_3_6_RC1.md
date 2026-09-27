# JAE v0.3.6 rc1 packaging amendment

Date: 2026-09-27

## Role

v0.3.6 rc1 is the first release candidate after completion of the final scientific audit family.

Scientific manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_6.md`

Title:

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

## Final scientific audit incorporated

The predeclared tag/device altitude-bias audit is complete.

- session-centered shift-invariant identity: **5/6 panels PASS**;
- focal *Tadarida*: FAIL, calibrated excess -0.0222, p=0.5121;
- stationary-height correction: **2/2 structurally eligible panels PASS**, both p=0.0002;
- focal raw 256-m AGL translation is descriptive only;
- tracking-window timing remains a stated limitation;
- no further new scientific analysis family is authorized before submission.

## Validated package

Main manuscript/figure run:
- `36329796558`
- head `906a42f841e639d5a4ab1d4397c7425df250d5ab`
- 7,932-word CI estimate
- 273-word abstract
- Figures 1–7
- success

Main anonymous review-PDF run:
- `36329796749`
- head `906a42f841e639d5a4ab1d4397c7425df250d5ab`
- anonymity PASS
- 26 pages
- success

Visual QA:
- all seven figures inspected;
- prior 26-page build inspected in full;
- final build differs only on page 26;
- final page 26 re-inspected after Figure 7 legend placement and anonymous repository wording fix.

## Remaining blockers

All remaining blockers are human/archive metadata:

- repository software LICENSE;
- final authors and affiliations;
- corresponding-author address/email/ORCID;
- CRediT;
- funding and acknowledgements;
- conflict declaration;
- final CITATION.cff or .zenodo.json;
- Zenodo GitHub integration and version DOI;
- DOI insertion into the v0.3.6 title page;
- final JAE upload.

No scientific retuning is permitted in rc1.
