# JAE submission readiness v0.3.6

Checked: 2026-09-27

## Scientific gates

- [x] six-panel common-cell identity calibration complete;
- [x] focal AGL calibration complete;
- [x] focal endpoint-neighbourhood failure retained;
- [x] cross-panel endpoint audit complete;
- [x] pairwise and metre-scale null calibration complete;
- [x] final additive tag/device altitude-bias audit frozen before output and complete;
- [x] session-centered shape audit: 5/6 panels PASS;
- [x] focal *Tadarida* centered-shape failure retained (p=0.5121);
- [x] stationary-height structural preflight opened no numeric heights;
- [x] stationary correction run only in the two predeclared eligible panels;
- [x] stationary correction: 2/2 eligible panels retain calibrated identity;
- [x] tracking-window overlap reported descriptively;
- [x] no time-block rescue family opened;
- [x] focal 256-m AGL value removed from headline evidence;
- [x] no further new scientific analysis family authorized before submission.

## Current result ceiling

- original coarse-horizontal standardized identity: 6/6 panels exceed panel-specific exchangeability expectations;
- shift-invariant centered-shape identity: 5/6 panels;
- focal *Tadarida* does not establish device-independent vertical-distribution shape;
- stationary correction corroborates the two structurally eligible panels;
- central-place and temporal context remain panel-dependent limitations.

## Automated package

- [x] v0.3.6 manuscript/figure workflow success — run 36330015862;
- [x] manuscript CI estimate 7,932 words;
- [x] abstract 273 words in five numbered statements;
- [x] seven keywords;
- [x] Figures 1–7 generated and visually inspected;
- [x] anonymous review PDF success — run 36329796749;
- [x] anonymity guard PASS;
- [x] 26-page review PDF;
- [x] final page-26 Figure 7 legend placement re-inspected;
- [x] no clipping, overlap or broken glyphs found;
- [x] title-page word-count field corrected to 7,932 before rc2 packaging freeze;
- [x] one-source metadata infrastructure added and integration-tested;
- [x] active-reference guard success — run 36367893566.

## Remaining human / archive items

All human fields are now centralized in
`submission/jae_v0_3_6_metadata.json`.

### Phase A — before Zenodo

- [ ] copy/fill the metadata template except `archive_doi`;
- [ ] choose/add repository software LICENSE;
- [ ] run the pre-release metadata assembler;
- [ ] make `check_zenodo_release_ready.py` report READY;
- [ ] enable the GitHub repository in Zenodo;
- [ ] publish the GitHub release and obtain the version DOI.

### Phase B — after Zenodo

- [ ] insert the minted version DOI into the metadata JSON;
- [ ] rerun metadata assembly in post-DOI mode;
- [ ] make `check_jae_upload_ready.py` report READY;
- [ ] confirm the generated combined word count remains <=8,500;
- [ ] perform final JAE upload.

The metadata assembly/gate path has an end-to-end synthetic Actions self-test. No additional
ecological analysis is required or authorized before submission.
