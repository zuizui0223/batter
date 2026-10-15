# Unified bat individuality manuscript — integration v1

This directory develops a **single manuscript** by integrating the existing *Journal of Animal Ecology* wild 3D ecology candidate and the *Behavioral Ecology* controlled/developmental synthesis, without changing or superseding either frozen source in place.

**2026-10-15 multiplicity update:** Two source-hash-guarded post-outcome Holm sensitivities now distinguish [four separate within-endpoint families](FOUR_PANEL_MULTIPLICITY_SENSITIVITY_V1.md) from [one expanded twelve-test family across the three displayed field endpoints](TWELVE_TEST_MULTIPLICITY_SENSITIVITY_V1.md). V_rel remains below 0.05 in **4/4** within its four-test family (maximum adjusted p = 0.03453), but only **3/4** under the broader twelve-test family (P2016 adjusted p = 0.27622; the other three 0.0012). S_rel and co-use I remain 0/4 below 0.05 in either family; isolated nominal negative S_rel and positive co-use results persist as historical source outcomes but not multiplicity-robust findings. **Neither retrospective family is exhaustive programme-wide error control.** [Four-test machine table](figures/FROZEN_FOUR_PANEL_MULTIPLICITY_V1.json) · [Twelve-test table](figures/FROZEN_TWELVE_TEST_MULTIPLICITY_V1.json) · [independent verifier](validate_four_panel_multiplicity_v1.py).

**2026-10-15 claim calibration:** The working title now explicitly concerns **consistent evidence for additional vertical segregation**, *not* absence of all spatial partitioning. Source-native 500-m horizontal O_XY was descriptively higher within than between animals, and the O_XY-to-O_XYZ reduction is not itself a test of added segregation. The probability-intersection proof, per-panel values and exact wording boundary are in [the horizontal-versus-added-vertical audit](HORIZONTAL_VS_ADDED_VERTICAL_SEGREGATION_CLAIM_AUDIT_V1.md). Original field outcomes and frozen branches remain unchanged.

**2026-10-15 spatial ecology/measurement audit:** [Matched native-versus-terrain 3D sensitivity](TERRAIN_DATUM_AND_GEOMETRY_SENSITIVITY_V1.md) now separates the GPS-reference dependence of apparent added segregation from retained terrain-relative individual fidelity. H and P2016 native S contrasts are materially attenuated after DEM subtraction, while the four-panel response is not uniform. The historical runner bilinearly interpolates DEM elevation **for each GPS fix**, then computes space use over **500-m XY cells**; original GPS heights include different ellipsoid/MSL datums, and derived terrain-relative heights are **not measured AGL**. These are original-source descriptive differences, not new animal-data tests. [Exact source-locked numbers](figures/FROZEN_TERRAIN_DATUM_CONTRAST_V1.json) · [Independent validator](validate_terrain_datum_contrast_v1.py).


**2026-10-16 critical estimator correction:** The original 500-m O_XYZ source uses **ten height bins with α=0.5 pseudocounts per occupied cell**, and its shared-cell pair gate requires 50 fixes **in aggregate**, not per cell. Therefore source-positive O_XYZ is a smoothed *estimated* intersection, not observed physical 3D co-occupancy. More importantly, the source co-use endpoint subtracts **each session's own median terrain-relative height** before measuring an encounter gap. Hence the nominal 2023 **+3.57 m** is a relative-height-deviation mismatch over the fixed-shift null, **not a physical altitude gap between two bats**. These findings do not alter original p-values (V_rel original 4/4, 12-test Holm 3/4; positive S_rel 0/4; co-use I nominal 1/4 only). Read the [reviewer evidence/physical geometry matrix](REVIEWER_EMPIRICAL_VS_PHYSICAL_GEOMETRY_V1.md), [smoothed overlap audit](SMOOTHED_3D_OVERLAP_SUPPORT_AUDIT_V1.md) and [co-use median-centering audit](COUSE_CENTERING_PHYSICAL_GAP_SCOPE_AUDIT_V1.md); independent synthetic-only, source-hash verifiers run in CI. **No physical habitat-sharing, avoidance or ecological causal carrier is established.**


**2026-10-16 V/S coupling and revised working title:** [Exact original-source overlap-slack audit](V_S_ALGEBRAIC_COUPLING_AND_INDEPENDENCE_AUDIT_V1.md) reconstructs **S_native = V_native − (mean epsilon_other − mean epsilon_self)** in all four 500-m source panels; epsilon is a nonnegative horizontal-probability-weight interaction term. Source native V exceeds S in all four; the gap is **algebraic, not independent biological confirmation**. A source-Git-blob-guarded [numeric record](figures/NATIVE_3D_V_S_OVERLAP_SLACK_DECOMPOSITION_V1.json) and [median-consistent synthetic validator](validate_original_v_s_overlap_coupling_v1.py) keep the result reproducible without reopening bat GPS. The manuscript is now titled **Persistent behavioral individuality and the limits of 3D niche inference in bats** (80 characters) to avoid implying that physical spatial segregation was ruled out.

**2026-10-16 field eligibility crosswalk:** The field programme has **three differently selected eligible animal sets** even inside the same named study/year: fine 500-m place×speed-turning n=**19/23/11/9**, geometry V/S n=**8/5/6/9**, co-use I n=**11/6/6/5** (H/P2022/P2023/P2016). Source numeric receipts and [the original-source hash-guarded ledger](figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json) establish the counts but **not the intersecting individual identities**. Figure 6 now displays both V/S and I n; no source-level within-bat V-to-I behavioral association was demonstrated. [Independent guard](validate_cross_estimand_eligibility_v1.py) · [scientific eligibility interpretation](CROSS_ESTIMAND_ELIGIBILITY_SCOPE_AUDIT_V1.md). Original field tests, figures' numerical axes and frozen source branches were not changed.

## Start here

1. [INTEGRATED_MANUSCRIPT_V1.md](INTEGRATED_MANUSCRIPT_V1.md) — full new draft, including rewritten Abstract, Introduction, Methods, Results, Discussion, Conclusion and selected working references.
   - [Original replay-input manifest](source_recovery/terrain_replay_input_manifest_v1.json) and [offline checksum verifier](source_recovery/verify_terrain_replay_input_manifest_v1.py) enumerate 4 GPS, 4 reference and 2 DEM inputs and provide optional **authorized local-file checksum** checks; no raw data are redistributed or independently rerun.
   - [Separate S_rel permutation-source manifest](source_recovery/partitioning_s_calibration_provenance_v1.json) and [validator](source_recovery/verify_partitioning_s_provenance_v1.py) pin the second original successful null-calibration workflow and prevent incorrectly attributing S_rel p-values to the earlier terrain-geometry source run.
2. [EVIDENCE_CROSSWALK_V1.md](EVIDENCE_CROSSWALK_V1.md) — audited source-to-claim table, with experimental and wild evidence hierarchies and claims this integration does **not** establish.
3. [FIGURES_AND_SI_PLAN_V1.md](FIGURES_AND_SI_PLAN_V1.md) — six rendered main figure designs, SI transfer, word budget and release safeguards.
4. [INTEGRATION_QA_V1.md](INTEGRATION_QA_V1.md) — 35 selected numeric keys reconciled at source-text level, plus epistemic and submission gate checklist.
5. [FIGURE_ATLAS_AND_CAPTIONS_V1.md](FIGURE_ATLAS_AND_CAPTIONS_V1.md) — six manuscript figures, including [Figure 5 A+B at 177 × 238 mm](figures/FIGURE_5_COMPOSITE_177x238MM_V2.svg), with source-aware captions.
6. [SUPPORTING_INFORMATION_DRAFT_V1.md](SUPPORTING_INFORMATION_DRAFT_V1.md) — integrated source-level experimental and wild supplementary tables, null architectures, uncertainty and source-permission caveats.
7. [figures/FROZEN_FIGURE_DATA_V1.json](figures/FROZEN_FIGURE_DATA_V1.json) + [figure builder](figures/generate_integrated_figures_v1.cjs) + [validator](figures/validate_integrated_figures_v1.py) — pinned summary inputs, reproducible rendering, exact original-profile hash checks and scientific/XML gates.
8. [ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md](ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md) — unaltered 103 individual-by-panel JAE figure/data records and SHA256; source IDs recur across two independent study panels.
9. [BIBLIOGRAPHY_MERGE_AUDIT_V1.md](BIBLIOGRAPHY_MERGE_AUDIT_V1.md) — 45 source-manuscript DOIs plus two separately verified outside-union ecology papers (Carlson 2021; Calderón-Capote 2025), yielding 37 main scholarly references.
10. [FIGURE_RENDER_VISUAL_QA_V1.md](FIGURE_RENDER_VISUAL_QA_V1.md) — preliminary SVG render and original-image preview QA.
11. [INTERNAL_SCIENCE_REVIEW_GATE_V1.md](INTERNAL_SCIENCE_REVIEW_GATE_V1.md) — reviewer-level limits and final submission blockers.
12. [BE_LAY_ABSTRACT_V2.md](BE_LAY_ABSTRACT_V2.md) — current 233-word abstract, 73-word Lay Summary and 69-character title for Behavioral Ecology.
13. [COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md](COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md) — reproducible anonymous manuscript with the journal-ordered sections, also built as a line-numbered review PDF (27 A4 pages in the current proof) in GitHub Actions.
14. [SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md](SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md) — reviewer-facing source/analysis tables S1–S10, methods S1–S15 and vector Figures S1/S2, also rendered to a single anonymous draft SI PDF.
23. [HISTORICAL_TERRAIN_SOURCE_CLOSURE_V1.md](HISTORICAL_TERRAIN_SOURCE_CLOSURE_V1.md) — 21 exact single-success-commit source files, including the three missing JAE rc2 imported native-terrain modules/contracts, packaged into a Git-blob-verified source-only ZIP; no raw GPS/DEM rerun claimed.
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
- [Anonymous and internal SI PDF workflow](https://github.com/zuizui0223/batter/actions/workflows/unified-si-draft-v1.yml) — two separate single-file proof variants; anonymous SI now contains Methods S1–S15 and ten source/result tables, plus original-source Figures S1 and S2.
- [Figure source guard](https://github.com/zuizui0223/batter/actions/workflows/unified-manuscript-figures-v1.yml) — six main results plus the Figure 5 A+B 177 × 238 mm exact-source composite.

The final journal data repository URL and author/coauthor approvals are **not** available yet; do not label these proof files submission-ready.

## New exploratory descriptive output: within-cohort 1D vertical shape overlap

- [Design fixed before overlap calculation](DESCRIPTIVE_VERTICAL_PROFILE_OVERLAP_CONTRACT_V1.md): 103 original individual profiles, pairs restricted to the **same frozen panel and source cohort**; no cross-country/colony/year dyads, no randomization/null/claim of new confirmation.
- [Figure S1 SVG](figures/FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg), [cohort/panel summary](figures/FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json), [all 684 dependent within-cohort pairs](figures/ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv), the [original-profile pair generator](figures/derive_centered_vertical_overlap_v1.cjs) and [12-cohort Figure S1 v2 renderer](figures/render_cohort_resolved_s1_v2.cjs). Original frozen 103-profile JSON checksum is required to regenerate all derived outputs.
- Per-panel 10-bin **median overlap of estimated session-centered probability SHAPES** = 0.817 / 0.801 / 0.919 / 0.899 / 0.802 for Eidolon / Hypsignathus / P. hastatus 2022 / 2023 / 2016. **Not full 3D habitat overlap, synchronized co-use, diet or independent dyad replication.**
- [SI internal and anonymous source](SUPPORTING_INFORMATION_DRAFT_V1.md) now contain Table U8/S8 and Methods U13/S13, with the vector Figure S1 embedded in the anonymous SI PDF. This is a post-outcome descriptive secondary display and does not upgrade the previously frozen S_rel 0/4 positive or I 1/4 results.

## Source-cohort weighting sensitivity for Figure S1 (post-outcome descriptive)

- [Full cohort/weighting audit](COHORT_WEIGHT_SENSITIVITY_AUDIT_V1.md), [frozen results JSON](figures/COHORT_WEIGHT_SENSITIVITY_V1.json) and [independent original-CSV validator](validate_cohort_weight_sensitivity_v1.py) describe all 12 source strata and the dependence of dyad-pooled medians on cohort sizes. The source files, 684 within-cohort pair values and original JAE scientific test verdicts were not changed.
- The largest *Eidolon* source cohort supplies **28/41 = 68.3%** of all the within-panel dyads; the largest *P. hastatus* 2023 source cohort supplies **45/60 = 75.0%**. Their original dyad-pooled medians 0.817 and 0.899 become 0.855 and 0.865 when taking the median of equally weighted eligible cohort medians. The latter **does not** correct statistical non-independence; three pair-eligible *Eidolon* cohorts have only one pair each.
- Supporting Information Table **U9/S9** lists the 12 source strata; Methods **U14/S14** documents calculations and excludes species-wide estimates, confidence intervals, or an inference of actual 3D spatial co-use. Figure S1 v2 now **shows each of the 12 collection cohorts separately**, with n profiles and dependent dyad counts; Table S8 preserves the pooled panel medians. The display-only revision was made **after inspecting** the cohort dominance. Original pair values are untouched; the figure's percentiles are descriptive, not confidence intervals.

## Source-ID and earlier horizontal overlap safeguards

- [Source study-year/individual-ID audit](PROFILE_PANEL_IDENTITY_SCOPE_AUDIT_V1.md) and [independent verifier](validate_profile_panel_identity_scope_v1.py): the archived JAE heatmap contains **103 individual-by-panel records**, but only **101 different literal ID strings**; two are shared across the 2016 and 2022 P. hastatus La Gruta panels. Published PIT tagging and low recapture make continuity possible but actual 6-year same-animal identity has **not** been independently verified.
- Calderón-Capote et al. (2025; [source](https://doi.org/10.1371/journal.pone.0313782)) had already evaluated **horizontal foraging-area overlap** from these same 2016/2022 archives (~0.20 Bhattacharyya overlap). The new Figure S1 coefficient ~0.80–0.92 measures **one-dimensional session-centered altitude-shape similarity** and is **not** a competing estimate of horizontal or three-dimensional co-use.
- Global cross-panel biological independence, competition mechanisms and longitudinal memory remain **unproven**. The original JAE/BE frozen results were not changed.

## Original gridded 3D overlap and historical code recovery (2026-10-15)

The previous supplementary Figure S1 quantifies **1D session-centered vertical shape similarity** in 103 individual-by-study-panel profile rows (101 distinct literal source ID strings, two unverified cross-study repetitions) and **684 nonindependent same-cohort dyads**. These are **not** true joint 3D habitat overlaps or 103 globally verified independent animals. Cohort-specific medians and Table S9 reveal substantial cohort-size bias.

A distinct **original, already completed native-height 500-m 3D analysis** has now been recovered *byte-identically* from the original successful GitHub workflow and incorporated into the working one-paper manuscript:

- [Original native O_XY, O_XYZ, O_Z|XY and R_3D numerical source result](figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json) — exact upstream historical Git blob `c1d37e42f72f59e5aba364daec9aef68b47778b6`, workflow **36881187913**.
- [Supplementary Figure S2](figures/FIGURE_S2_NATIVE_HORIZONTAL_AND_JOINT_3D_OVERLAP_V1.svg), [deterministic original-source SVG renderer](figures/render_original_native_3d_overlap_s2_v1.cjs), and [source-inference/closure audit](NATIVE_3D_GEOMETRY_AND_SOURCE_CLOSURE_AUDIT_V1.md).
- [Original terrain-corrected result](figures/ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json) and [S_rel permutation/compatibility source](figures/ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json) preserve exact historical values. Adding native-height vertical information reduced joint spatial overlap, but **native extra-segregation S_native is not the post-terrain permutation-tested S_rel**.
- The original JAE rc2 frozen branch alone is **not a complete rerunnable checkout** of its historical terrain pipeline: specifically, `run_v1.py`, `run_external_geometry_v1.py`, and `contract_v1.json` are absent even though the original terrain driver and source contracts remain byte-identical. A new [21-file single-commit terrain source closure](HISTORICAL_TERRAIN_SOURCE_CLOSURE_V1.md) now reconstitutes all directly imported original code and input contracts from the successful original Git commit `819acc82`; [CI recovery PASS](https://github.com/zuizui0223/batter/actions/runs/38685340549). It is **source-code provenance closure only**, **not** an end-to-end GPS/DEM or permutation rerun, and copies no third-party raw data. The later [module-import/synthetic-formula CI also passed](https://github.com/zuizui0223/batter/actions/runs/38685805292) in an explicitly modern pinned Python compatibility environment, without opening bat tracking or DEM data.
- The scientific source universe remains closed: **original native conditional vertical fidelity 4/4 eligible panels**, **terrain-relative V_rel 4/4**, **positive S_rel 0/4** and separately defined co-use **1/4**, across **two field species**. No causal resource, competition, memory or laboratory-to-wild mechanism is established.

The SI now includes native-gridded Table U10/S10, Figure S2 and full native/source-closure Methods U15/S15. The compiled anonymous review proofs currently contain **27 main pages** and **18 SI pages**, reproduced in CI; these are review proofs and may change again during human editing.

## One biological question

**When individual height-use patterns remain predictable within shared coarse horizontal support, do they also show added terrain-relative vertical segregation?**

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
