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

That figure shows that individual shape differences correspond visibly to:

- central concentration around the session-specific median;
- upper-tail use;
- lower-tail use;
- tail asymmetry.

No clustering or strategy classes are inferred.

## Methodological contribution

Prediction-based individuality statistics require calibration against the finite-sample
exchangeability distribution of the complete pipeline.

Observed examples include:
- negative exchangeability expectations for the original conditional-minus-marginal statistic;
- pairwise self-identification null means of approximately 0.50-0.58;
- a positive null mean for the focal absolute height-separation statistic.

## Validated v0.3.8 package

Main manuscript/figure workflow:
- run: **36380837565**
- head: `d6d0cd51854c9ada2eefbd069a08bc1db514bbf9`
- conclusion: **success**
- manuscript CI estimate: **7,542 words**
- abstract: **264 words**
- Introduction: **685 words**
- Results: **1,270 words**
- Discussion: **1,686 words**
- keywords: **7**
- main figures: **6**
- Supporting Figures: **2**

Main-figure artifact:
- id: `10952945637`
- digest: `sha256:65ef32e64d355694720791f74daad764e8ac9bedd117fefd7ad5e65137fcab6d`

Supporting-figure artifact:
- id: `10953025517`
- digest: `sha256:a94e779c17ea091ec8a3dca16760df5f47daaccc254d1e6d5f851718b7fc16c7`

Descriptive profile artifact:
- id: `10951779884`
- digest: `sha256:a730606c21fe79ef74e676fc1bf93ba4bf5980b8ecb396dea3a453aad4f1f120`

Anonymous review workflow:
- run: **36380837508**
- head: `cc38e0a65de59149c84baef5dbc502563f089309`
- conclusion: **success**
- anonymity guard: **PASS**
- review PDF: **26 pages**
- artifact id: `10953190261`
- digest: `sha256:8aded294361636a945383f0b3064dc49e126df74ec84cff6070985cb806a8cb6`

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
- descriptive between-individual differences in profile concentration and tail use;
- stationary-offset corroboration in both structurally eligible comparative panels;
- pipeline-specific exchangeability calibration as a general methodological lesson.

Not established:
- device-independent centered-shape individuality in *Tadarida*;
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
