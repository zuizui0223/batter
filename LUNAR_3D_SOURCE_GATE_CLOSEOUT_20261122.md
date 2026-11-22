# Lunar 3D response: first empirical source-admission closeout (2026-11-22)

This record covers **real, public, hash-verified bat GPS source support**. No numerical flight height, any heldout height model, predation exposure, measured prey, or lunar behavioral effect has been inspected or estimated. It concerns a NEW prospective extension only. Existing JAE submission and resource×3D research evidence are not revised.

## Immutable implementation and run provenance

- Branch: `prospective/lunar-3d-response-gate-v1-20261122` (branched from `prospective/resource-behavior-higher-dimensional-sdm-v1-20261120`).
- Prior art/design: `prospective/lunar_3d/LUNAR_3D_SOURCE_GATE_AND_PRIOR_ART_20261122.md`.
- Source/exposure audit v1: `prospective/lunar_3d/lunar_source_gate_v1.py`.
- Frozen pre-height matched-exposure audit v2: `prospective/lunar_3d/LUNAR_COMMON_SUPPORT_V2_PRE_HEIGHT_FREEZE.md`, implementation `prospective/lunar_3d/lunar_common_support_v2.py`.
- Six original Movebank CSV sources from existing `config/bat_panel_sources_v1.json`. Source size and MD5 checked, and only GPS XY, timestamps, individual IDs, flags and string-PRESENCE of source height field read.
- Full v1+v2 GitHub Actions **SUCCESS**: https://github.com/zuizui0223/batter/actions/runs/45021250335; CI v1 synthetic 4/4 and v2 synthetic 3/3 tests passed; archived artifact ID **14753319752**, `lunar-3d-exposure-source-gates-v1-v2`.
- Source exposure is purely astronomical geometry: Sun <-12°; bright if Moon altitude >=10° and illuminated fraction >=0.8; dark if Moon altitude <=-5° or illuminated fraction <=0.2. Neither category represents calibrated under-canopy illuminance. Cloud, terrain, canopy and behavioral state remain unmeasured.

## V1: individual-night exposure replication (whole-dataset timing)

Criteria: >=5 individuals with at least two nights in each exposure; source night population span >=35 days; source night >=30 fixes and exposure group >=20 fixes.

| Taxon / source DOI | Span days | Individuals with 2+ bright & 2+ dark nights | V1 |
|---|---:|---:|---|
| *Hypsignathus monstrosus* / 10.5441/001/1.278 | 19 | 16 | STOP (35-day criterion) |
| *Phyllostomus hastatus* 2016 / 10.5441/001/1.282 | 10 | 0 | STOP |
| *P. hastatus* 2021–22 / 10.5441/001/1.321 | 49 | 15 | PASS |
| *P. hastatus* 2023 / 10.5441/001/1.322 | 7 | 0 | STOP |
| *Tadarida teniotis* / 10.5441/001/1.52nn82r9 | 6 | 0 | STOP |
| *Eidolon helvum* / 10.5441/001/1.k8n02jn8 | 1929 | 5 | PASS |

## V2: within-animal place×clock matched support

**Pre-height, after v1**: matching same animal, 0.05° lat/lon cell, 2-hour local solar time band; at least 2 different nights and 20 fixes in each exposure in the matched stratum; at least one cross-exposure pair <=45 days. Source matched-support PASS if >=5 individuals have a matched stratum. V2 is not a retroactive replacement of V1 criteria.

| Source | Matched strata | Matched animals | V2 | Scientific decision |
|---|---:|---:|---|---|
| *Hypsignathus* | **35** | **13** | PASS | Excellent source support for a **distinct short-period** contrast, despite V1 duration STOP; not a V1 confirmatory PASS |
| *P. hastatus* 2021–22 | **21** | **13** | PASS | **Primary prospective height contrast**: passes both predefined screens |
| *Eidolon* | **0** | **0** | STOP | Long span across years does not guarantee comparable place×clock exposure |
| *P. hastatus* 2016 | 0 | 0 | STOP | No matched comparison |
| *P. hastatus* 2023 | 0 | 0 | STOP | No matched comparison |
| *Tadarida* | 0 | 0 | STOP | No matched comparison |

V2 result also found *Hypsignathus* 15 individual-nights with both geometric exposure types in v1; this should be a SEPARATE within-night diagnostic if used, not a substitution for the v1 population-span criterion.

## Prior art constraining novelty

- Hecker & Brigham (1999) **already** found moonlight×forest-height activity interaction: DOI https://doi.org/10.2307/1383170.
- Roeleke et al. (2018) **already** used 3D GPS *Nyctalus* noctule height/canopy/habitat in the lunar cycle: DOI https://doi.org/10.1186/s40462-018-0131-7.
- A 2019 study of *H. monstrosus*, **not shown to be these same 13 animals**, previously reported the nightly displacement of one tracked female negatively associated with lunar illumination (adjusted R²=0.168, p=0.0045) but not for studied males (adjusted R²=-0.0148, p=0.48). Therefore a new lunar effect in this species **cannot be claimed as unprecedented**: DOI https://doi.org/10.1371/journal.pone.0223139.
- Erkert (1976), PMID 829232, examined lunar activity phase variation in *P. hastatus* and found no statistically significant lunarperiodic change in the observed phase-angle outcome; this is **not** a test of conditional GPS height or absolute absence of lunar effects: https://pubmed.ncbi.nlm.nih.gov/829232/.

These papers further narrow any defensible extension: **transferable, conditional lunar increment in the within-individual vertical-use distribution at comparable XY/time, accounting for height accuracy and environmental confounders**.

## Next gate before opening vertical responses

1. Independently verify each source's vertical field type, ellipsoid/MSL/AGL datum policy, precision and biases; reject if calibrated height cannot be derived with credible uncertainty. Height values still NOT opened by v1/v2.
2. Freeze a proper-scoring-rule analysis using exactly the same heldout fixes for baseline `XY + local time + (individual) + habitat + movement` and augmented `+ lunar geometry × habitat`; hold out nights, not fixes; propagate tag/terrain uncertainty. Check whether same-cell/clock matching preserves enough independently heldout nights; define one inferential unit before outcome opening.
3. Separate `P. hastatus` prospective baseline from `Hypsignathus` independent within-lunation scope; include moon-below-horizon negative control to distinguish illumination from phase/time patterns.
4. Keep predation avoidance, resource tracking and state switching as **unresolved mechanisms** without prey, predators or independent behavioral labels. GPS fixes do not measure total nightly activity.

**Decision**: The source support for new 3D lunar model is nonzero in *P. hastatus* 2021–22; no ecological height effect, transferable gain or causal statement yet.
