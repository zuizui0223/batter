# JAE submission manifest v0.3.4 rc1

Date: 2026-09-27

## Current submission candidate

Target: **Journal of Animal Ecology — Research Article**  
Backup: **Movement Ecology**

Scientific-content commit:
`29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`

The empirical source universe is closed. No new public-data mining, lowered admission gates,
retuned grids/radii/bins, changed smoothing, or rescue of retained negative endpoints is
authorized.

## Central ecological claim

> **Across six bat tracking panels, identity-matched vertical profiles retain more held-out
> predictive information than expected under session-level exchangeability after self and other
> profiles are standardized to the same occupancy among the tested 5-km horizontal cells.**

This does **not** mean that all fine-scale horizontal fidelity has been removed.

## Manuscript

- file: `manuscript/MANUSCRIPT_DRAFT_V0_3_4.md`
- blob SHA: `20a2bc65b29c97b8e83b74649827b0bd7f04778c`
- CI word estimate: **6,384**
- abstract: **286 words**
- numbered abstract statements: **5**
- keywords: **7**

## Automated validation

### Manuscript + Figures 1–6

- workflow: `jae-submission-v0.3.4`
- run: `36308168273`
- result: **success**
- figures artifact: `10928037886`
- digest: `sha256:e529abc806193a12e256e6a792a010222c51592c601acf045edd22d45623e73d`

### Anonymous review PDF

- workflow: `jae-review-pdf-v0.3.4`
- run: `36308168258`
- result: **success**
- artifact: `10927338781`
- digest: `sha256:d40fd2f2d5eb1cf16099e75eb023b753b32c1d64620d14c5d459c05b4305df51`
- rendered pages: **22**
- visual inspection: **passed** on all pages; no clipping, overlap or broken glyphs

## Calibration history that determines the claim

- focal estimator calibration: run `36291669628`, 9,999 session-block permutations;
- cross-panel calibration: run `36292039473`, 4,999 permutations per non-focal panel;
- focal AGL calibration: run `36296387142`;
- focal endpoint/grid robustness: run `36296479565`;
- biological effect translation: run `36296977883`.

The prior conditional-/marginal-dominant architecture classification is superseded.

## Retained negative controls

- stable residual cell × height map: **p = 0.160**, not supported;
- 1-km night-endpoint-neighbourhood exclusion: **p = 0.1109**, not supported;
- focal AGL 10-km grain: **p = 0.1018**, not supported;
- 0.5-km and 2-km endpoint-neighbourhood sensitivities also fail.

Therefore central-place/fine-scale horizontal structure and scale dependence remain explicit
limitations.

## Biological magnitude

Under common horizontal weighting, same-bat vertical profiles win approximately **77–86%** of
direct pairwise comparisons in five panels. The 2016 *Phyllostomus* panel is weaker at 59.4%.

In focal *Tadarida* AGL, same- versus other-individual expected height differs by **256 m** on
average across individuals, with a **145 m** median individual separation and strong
heterogeneity.

## Superseded package

`release/jae-v0.3.3-rc2` and its manuscript are **DO NOT SUBMIT**.

## Human-input items remaining

- permanent archive DOI;
- final authors, affiliations and corresponding-author metadata;
- CRediT statement;
- funding and acknowledgements;
- conflict-of-interest declaration;
- journal upload.
