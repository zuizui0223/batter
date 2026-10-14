# Unified bat individuality manuscript — integration v1

This directory develops a **single manuscript** by integrating the existing *Journal of Animal Ecology* wild 3D ecology candidate and the *Behavioral Ecology* controlled/developmental synthesis, without changing or superseding either frozen source in place.

## Start here

1. [INTEGRATED_MANUSCRIPT_V1.md](INTEGRATED_MANUSCRIPT_V1.md) — full new draft, including rewritten Abstract, Introduction, Methods, Results, Discussion, Conclusion and selected working references.
2. [EVIDENCE_CROSSWALK_V1.md](EVIDENCE_CROSSWALK_V1.md) — audited source-to-claim table, with experimental and wild evidence hierarchies and claims this integration does **not** establish.
3. [FIGURES_AND_SI_PLAN_V1.md](FIGURES_AND_SI_PLAN_V1.md) — six rendered main figure designs, SI transfer, word budget and release safeguards.
4. [INTEGRATION_QA_V1.md](INTEGRATION_QA_V1.md) — 35 selected numeric keys reconciled at source-text level, plus epistemic and submission gate checklist.
5. [FIGURE_ATLAS_AND_CAPTIONS_V1.md](FIGURE_ATLAS_AND_CAPTIONS_V1.md) — six manuscript figures, including [Figure 5 A+B at 177 × 238 mm](figures/FIGURE_5_COMPOSITE_177x238MM_V2.svg), with source-aware captions.
6. [SUPPORTING_INFORMATION_DRAFT_V1.md](SUPPORTING_INFORMATION_DRAFT_V1.md) — integrated source-level experimental and wild supplementary tables, null architectures, uncertainty and source-permission caveats.
7. [figures/FROZEN_FIGURE_DATA_V1.json](figures/FROZEN_FIGURE_DATA_V1.json) + [figure builder](figures/generate_integrated_figures_v1.cjs) + [validator](figures/validate_integrated_figures_v1.py) — pinned summary inputs, reproducible rendering, exact original-profile hash checks and scientific/XML gates.
8. [ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md](ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md) — unaltered 103-individual JAE figure/data provenance and SHA256.
9. [BIBLIOGRAPHY_MERGE_AUDIT_V1.md](BIBLIOGRAPHY_MERGE_AUDIT_V1.md) — 45 source-manuscript DOIs plus two separately verified outside-union ecology papers (Carlson 2021; Calderón-Capote 2025), yielding 37 main scholarly references.
10. [FIGURE_RENDER_VISUAL_QA_V1.md](FIGURE_RENDER_VISUAL_QA_V1.md) — preliminary SVG render and original-image preview QA.
11. [INTERNAL_SCIENCE_REVIEW_GATE_V1.md](INTERNAL_SCIENCE_REVIEW_GATE_V1.md) — reviewer-level limits and final submission blockers.
12. [BE_LAY_ABSTRACT_V2.md](BE_LAY_ABSTRACT_V2.md) — shortened 215-word abstract, 73-word Lay Summary and 69-character title for Behavioral Ecology.
13. [COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md](COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md) — reproducible anonymous manuscript with the journal-ordered sections, also built as a 22-page line-numbered review PDF in GitHub Actions.
14. [SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md](SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md) — reviewer-facing source/analysis tables with S1–S7 labels, also rendered to a single anonymous draft SI PDF.
15. [FIGURE_ALT_TEXT_V1.md](FIGURE_ALT_TEXT_V1.md) — evidence-aware accessible text descriptions of all six main figures.
16. [SUBMISSION_READINESS_GATE_V2.md](SUBMISSION_READINESS_GATE_V2.md) — official journal requirements, passed machine checks and mandatory human archive/ethics/AI approvals.
17. [SOURCE_DOI_AND_METADATA_AUDIT_V2.md](SOURCE_DOI_AND_METADATA_AUDIT_V2.md) — corrected original Phyllostomus study-year DOI mapping, and targeted publisher/index verification of 2026 citations.
18. [COVER_LETTER_BEHAVIORAL_ECOLOGY_UNIFIED_DRAFT_V1.md](COVER_LETTER_BEHAVIORAL_ECOLOGY_UNIFIED_DRAFT_V1.md) — editor-facing scientific cover letter template, with required publication-overlap and AI disclosure placeholders.
19. [validate_source_attribution_v2.py](validate_source_attribution_v2.py) — CI regression test for wild source DOI/year identities and verified citations.
20. [ECOLOGICAL_PRIOR_ART_POSITIONING_V1.md](ECOLOGICAL_PRIOR_ART_POSITIONING_V1.md) — prior white-stork and bat research demonstrates overlapping persistent individual niches; no false conceptual first claim.
21. [ECOLOGICAL_IDENTIFIABILITY_AND_DECISIVE_TESTS_V1.md](ECOLOGICAL_IDENTIFIABILITY_AND_DECISIVE_TESTS_V1.md) — formal distinction between latent task allocation, within-task use and actual co-use, with prospective discriminators.
22. [figures/FROZEN_MAINTENANCE_BOUNDARY_INPUTS_V1.json](figures/FROZEN_MAINTENANCE_BOUNDARY_INPUTS_V1.json) and [validate_ecological_identifiability_v1.py](validate_ecological_identifiability_v1.py) — seven source-SHA-pinned maintenance/conditioning and wind-STOP receipts plus executable exact mixture-identity counterexample.

### Review PDF CI outputs

- [Anonymous complete manuscript review PDF workflow](https://github.com/zuizui0223/batter/actions/workflows/unified-anonymous-main-v1.yml) — continuous line and page numbers; manuscript copy is a **draft**, not a final journal upload.
- [Anonymous and internal SI PDF workflow](https://github.com/zuizui0223/batter/actions/workflows/unified-si-draft-v1.yml) — two separate single-file proof variants; anonymous SI now contains Methods S1–S13 and eight source/result tables.
- [Figure source guard](https://github.com/zuizui0223/batter/actions/workflows/unified-manuscript-figures-v1.yml) — six main results plus the Figure 5 A+B 177 × 238 mm exact-source composite.

The final journal data repository URL and author/coauthor approvals are **not** available yet; do not label these proof files submission-ready.

## New exploratory descriptive output: within-cohort 1D vertical shape overlap

- [Design fixed before overlap calculation](DESCRIPTIVE_VERTICAL_PROFILE_OVERLAP_CONTRACT_V1.md): 103 original individual profiles, pairs restricted to the **same frozen panel and source cohort**; no cross-country/colony/year dyads, no randomization/null/claim of new confirmation.
- [Figure S1 SVG](figures/FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg), [cohort/panel summary](figures/FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json), [all 684 dependent within-cohort pairs](figures/ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv) and [deterministic pure Node generator](figures/derive_centered_vertical_overlap_v1.cjs). Original frozen 103-profile JSON checksum is required to regenerate all three derived outputs.
- Per-panel 10-bin **median overlap of estimated session-centered probability SHAPES** = 0.817 / 0.801 / 0.919 / 0.899 / 0.802 for Eidolon / Hypsignathus / P. hastatus 2022 / 2023 / 2016. **Not full 3D habitat overlap, synchronized co-use, diet or independent dyad replication.**
- [SI internal and anonymous source](SUPPORTING_INFORMATION_DRAFT_V1.md) now contain Table U8/S8 and Methods U13/S13, with the vector Figure S1 embedded in the anonymous SI PDF. This is a post-outcome descriptive secondary display and does not upgrade the previously frozen S_rel 0/4 positive or I 1/4 results.

## Source-ID and earlier horizontal overlap safeguards

- [Source study-year/individual-ID audit](PROFILE_PANEL_IDENTITY_SCOPE_AUDIT_V1.md) and [independent verifier](validate_profile_panel_identity_scope_v1.py): the archived JAE heatmap contains **103 individual-by-panel records**, but only **101 different literal ID strings**; two are shared across the 2016 and 2022 P. hastatus La Gruta panels. Published PIT tagging and low recapture make continuity possible but actual 6-year same-animal identity has **not** been independently verified.
- Calderón-Capote et al. (2025; [source](https://doi.org/10.1371/journal.pone.0313782)) had already evaluated **horizontal foraging-area overlap** from these same 2016/2022 archives (~0.20 Bhattacharyya overlap). The new Figure S1 coefficient ~0.80–0.92 measures **one-dimensional session-centered altitude-shape similarity** and is **not** a competing estimate of horizontal or three-dimensional co-use.
- Global cross-panel biological independence, competition mechanisms and longitudinal memory remain **unproven**. The original JAE/BE frozen results were not changed.

## One biological question

**What persists when behavior remains individually predictable, and when does that persistence require ecological spatial partitioning?**

Three distinguishable empirical axes:

- **Maintenance:** acute context manipulations can preserve the correct individual correspondence.
- **Realization:** a coarse identity-bearing movement representation can transfer when fixed fine-grained trajectory geometry does not.
- **Ecological consequence:** individually repeatable wild vertical probability distributions can overlap without evidence of positive added segregation.

Developmental/early-history results constrain how the differences form. A frozen lab-style FlightIntensity field bridge **failed** its 3/4 threshold (PASS/PASS/FAIL/structural STOP); this remains a central limit on a causal interpretation.

## Critical source-of-truth rule

- JAE rc2: branch release/jae-v0.4.0-rc2, manuscript blob c4ef51a7f3f291a6f203d303dbf73f5b54fb7683.
- BE v1: branch prospective/public-causal-synthesis-v1, manuscript blob a83fed81a141c62df29f3c12f2fb5fd36399c160.

The older JAE manuscript copy on the BE branch is NOT authoritative. The unified draft only adds files under this new directory. **No existing experimental or field outcomes were recalculated or relabeled as newly confirmatory.**

## Publication rule

This is the **alternative one-paper route**, not a third simultaneous submission alongside both underlying research manuscripts. It requires a single coordinated human/coauthor publication decision and new submission approvals before any journal upload.

## Figure status (2026-10-14)

All six proposed main figures now exist as editable SVG. The source-generated figure suite treats S_rel null envelopes and co-use dyad-bootstrap intervals as distinct uncertainty objects. Field encounter windows are pinned at 60/60/600/600 seconds, with 2023 all-space and 2016 endpoint-excluded. The original JAE individual-profile descriptive heatmap has been **recovered and restored unchanged**, together with the source CSV/JSON for 103 individual-by-panel profiles (101 literal source IDs; biological cross-year identity unverified), using the checksum-verified artifact restoration workflow. See the [original profile recovery receipt](ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md) and [original PNG](figures/original_jae/figure6_individual_centered_shape_profiles.png). SVG deterministic reproduction, science-status checks and exact restored original-profile file hashes run in [the dedicated PR workflow](../../.github/workflows/unified-manuscript-figures-v1.yml); the most recent observed CI runs passed. Preliminary rendered-figure review is recorded in [FIGURE_RENDER_VISUAL_QA_V1.md](FIGURE_RENDER_VISUAL_QA_V1.md). Final journal-size human-coauthor visual approval and submission assembly remain pending.
