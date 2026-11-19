# Lewanzik 2019 original-source retrieval: terminal source-gate receipt

**2026-11-19. STATUS: STOP_SOURCE_ACCESS. This is NOT a statistical rejection of an ecological hypothesis.**

Original dataset: DOI [10.5061/dryad.gp65g2t](https://doi.org/10.5061/dryad.gp65g2t), public page lists `Lewanzik_etal_2019_JAE_DATA.xlsx` (83.76 KB). Published experiment: [Lewanzik et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849779/). Published content visible, file acquisition blocked.

Three retrieval paths were attempted **from a fresh GitHub Actions Ubuntu runner** in a source-only, blind-to-outcome schema gate:

| URL | Observed status | Scope |
|---|---|---|
| `https://datadryad.org/downloads/file_stream/83444` | HTTP 403 Forbidden | Published linked file stream |
| `https://datadryad.org/api/v2/files/83444/download` | HTTP 401 Unauthorized | Documented individual-file API pattern |
| `https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gp65g2t/download` | HTTP 401 Unauthorized | Documented dataset-version download pattern |

Original Actions run: https://github.com/zuizui0223/batter/actions/runs/44452289881 .
The CI status is intentionally **FAILED**; upload of a detailed metadata-only JSON receipt succeeded. This distinguishes a failed public-data transfer from a passed empirical gate. No original XLSX bytes, no sheet schema and no bat activity rows were opened. A local web click to the same file-stream separately returned HTTP403; local runtime network resolution was blocked.

**Diagnostic verdict:** source publication/metadata exists and original file is listed, but available tool and GitHub runner download paths are denied (401/403). This may be an access-path or service policy issue; there is no evidence of a missing or nonexistent dataset. Three distinct attempts gave the same blocker class, so automatic access attempts stop instead of trying arbitrary undocumented bypasses.

## Correctly frozen next computation (not yet executable on original bats)

The registered biological test is the response to buzz-level variation (0,12,24,48,96 buzzes/min) *conditional on receiver baseline activity*, using **absolute playback activity as response**, with a buzz×baseline interaction. Pre-/post-quiet windows and 0-buzz SEARCH-CALL playback are not identical controls. The unit of external prediction is one of 12 independent lakes, not each three-minute recording or 24 emitter×receiver combination.

Synthetic known-truth validation tests whether this prospective estimator avoids interpreting the mathematically negative slope of `(Y_playback-Y_pre)~Y_pre` as an ecological density effect. **It does not convert a synthetic positive control into empirical bat evidence.** See `h1_cue_interaction_known_truth_v1.py` and CI.

## One data-dependent input to continue actual biological estimation

A checksum-verified copy of the specific original XLSX (or an authorized direct source URL that resolves to the same bytes), with the file's provenance, is necessary. Independent data from another primary study with a directly comparable randomized playback×baseline design could also support an external study test. Until then, no cue×density moderation, broad mammal-wide information-use law or H3 cognitive-memory tradeoff is established.
