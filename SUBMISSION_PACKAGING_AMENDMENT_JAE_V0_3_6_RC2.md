# JAE v0.3.6 rc2 packaging amendment

Date: 2026-09-27

## Purpose

RC2 is a **packaging-only** successor to v0.3.6 rc1.

The scientific manuscript, figures, audit results and claim boundary are unchanged.

## Correction

The v0.3.6 title-page template accidentally retained the superseded v0.3.5 CI word count
(7,047 words). It now correctly states:

- current v0.3.6 manuscript CI estimate: **7,932 words**;
- the combined journal word count must be reconfirmed after final title-page metadata are inserted.

## Validation

Corrected main submission run:

- workflow run: `36330015862`
- head: `864a6908b09b0dcdbcb1b1468b87aa2a59cdf6cc`
- conclusion: **success**
- figure artifact: `10935526906`
- digest: `sha256:f2aebffbc7d51b4081cd217dd9ef963cb9629b1e2e9459ad54a85667020d6e9b`

The final anonymous review PDF remains the already validated 26-page build from run
`36329796749`; the title page is separate and does not enter that anonymous PDF.

## Scientific freeze

No dataset, endpoint, permutation, grid, bin, smoothing rule, result, figure-data input or
manuscript scientific claim changed in RC2.

Remaining blockers are human/archive metadata only.
