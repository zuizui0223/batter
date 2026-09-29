# JAE submission manifest v0.3.8 rc1

Date: 2026-09-28

## Current manuscript

`manuscript/MANUSCRIPT_DRAFT_V0_3_8.md`

Title:

**Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats**

## Scientific status

All inferential scientific audit families are complete and frozen.

The central ecological result is comparative:

- all five comparative panels retain calibrated vertical-distribution shape identity after
  session-median centering;
- the motivating *Tadarida* panel is the explicit boundary case and does not retain centered-shape
  identity (p=0.5121);
- stationary-height correction retains identity in both structurally eligible comparative panels;
- endpoint-neighbourhood exclusion passes in four comparative panels;
- pairwise self-identification exceeds its pipeline-specific null in five panels.

v0.3.8 adds **no new inferential test**. It adds one frozen descriptive visualization of the
already-tested common-cell centered self profiles.

That figure illustrates visible variation in the estimated profiles in:

- central concentration around the session-specific median;
- upper-tail use;
- lower-tail use;
- tail asymmetry.

These component-wise ranges were not separately calibrated against exchangeability and may include
finite-session profile-estimation noise. They are not used to infer which component carries the
validated whole-profile identity signal. No clustering or strategy classes are inferred.

## Methodological contribution

Prediction-based individuality statistics require calibration against the finite-sample
exchangeability distribution of the complete pipeline.

Observed examples include:
- negative exchangeability expectations for the original conditional-minus-marginal statistic;
- pairwise self-identification null means of approximately 0.50-0.58;
- a positive null mean for the focal absolute height-separation statistic.

## Validated v0.3.8 package

Main manuscript/figure workflow:
- run: **36506593033**
- head: `2c84d11824dc410af3977f12d1fab5e3f6883bc1`
- conclusion: **success**
- manuscript CI estimate: **7,887 words**
- abstract: **282 words**
- Introduction: **723 words**
- Results: **1,328 words**
- Discussion: **1,602 words**
- keywords: **7**
- main figures: **6**
- Supporting Figures: **2**

Main-figure artifact:
- id: `11007013708`
- digest: `sha256:25cf432948626550b0f84257e55d7c924f26bc4f666d59f99e03b84b2203b5b5`

Supporting-figure artifact:
- id: `11007621411`
- digest: `sha256:feff1dc31f777c45b196009d3b07e1c332b45280e7e48825a41b6d42bd177664`

Descriptive profile artifact:
- id: `11007651308`
- digest: `sha256:fec9c49230a426e2883d4ba76928a6d523f60695feb315d52f08c10f9d740b6e`

Anonymous review workflow:
- run: **36506593064**
- head: `67b053eb0a3db2539c8fb4beb593c9e5759910fe`
- conclusion: **success**
- anonymity guard: **PASS**
- review PDF: **26 pages**
- artifact id: `11006968753`
- digest: `sha256:f141c3605147066cf338a1554d4b72d295fa008f4e505bdf4d46a0afdb13bc22`

Visual QA:
- main Figures 1-6 inspected;
- Supporting Figures S1-S2 inspected;
- final 26-page review PDF rendered and inspected;
- no clipping, overlap or broken glyphs found.

## Descriptive Figure 6 provenance

Definition frozen before output:
- `contract/centered_shape_profile_descriptive_v1.json`
- `CENTERED_SHAPE_PROFILE_DESCRIPTIVE_FREEZE_V1.md`

Canonical Linux run:
- `36375056204` — success
- exact evaluable n reproduced: 20 / 24 / 33 / 16 / 10

Independent macOS run:
- `36375120545` — success
- identical panel n and upper-tail ranges

Result summary:
- `CENTERED_SHAPE_PROFILE_DESCRIPTIVE_RESULT_V1.md`

## Claim boundary

Supported:
- repeatable vertical identity beyond coarse 5-km horizontal occupancy;
- repeatable centered vertical-distribution shape in all five comparative panels;
- descriptive, uncalibrated variation in displayed profile concentration and tail use;
- stationary-offset corroboration in both structurally eligible comparative panels;
- pipeline-specific exchangeability calibration as a general methodological lesson.

Not established:
- device-independent centered-shape individuality in *Tadarida*;
- which descriptive concentration/tail component carries the calibrated whole-profile identity signal;
- inferential component-wise differences from the uncalibrated Figure 6 ranges;
- complete removal of fine-scale horizontal fidelity or central-place structure;
- behavioural-state-specific vertical strategies;
- tag-specific variance-free measurement;
- vertical-niche strategy classes;
- personality, learning, adaptation or optimality.

## Final metadata workflow

One human metadata source:
`submission/jae_v0_3_8_metadata.json`

Template:
`submission/jae_v0_3_8_metadata.template.json`

Assembler:
`scripts/apply_jae_v0_3_8_metadata.py`

Stages:
1. pre-release — explicit human metadata + LICENSE; archive DOI empty;
2. post-DOI — insert the minted Zenodo version DOI and regenerate the final journal title page.

GitHub release-preflight target:
- release candidate: `release/jae-v0.3.8-rc1`
- expected tag: `jae-v0.3.8`
- release notes: `RELEASE_NOTES_JAE_V0_3_8.md`

No human identity, authorship, license, funding, conflict declaration, ORCID, postal address or DOI
is inferred.


## Packaging validation

One-source metadata workflow:
- self-test run: `36506593120` — **success**
- pre-release assembly: READY
- post-DOI assembly: READY
- final JAE upload gate: READY
- synthetic combined count: 8,070 words pre-release / 8,065 words post-DOI

GitHub/Zenodo release preflight:
- self-test run: `36398767110` — **success**
- metadata/CITATION/LICENSE synthetic state: READY
- candidate integrity: READY
- target tag/release absence check: READY

Active-reference guard:
- run: `36506593111` — **success**

No authorship, license, funding, conflict declaration, ORCID, postal address or DOI is inferred.
