# Frozen description rule: within-cohort centered vertical-profile similarity

**Set before computing new pairwise overlap values:** 2026-10-14. **STATUS: POST-OUTCOME EXPLORATORY DESCRIPTIVE ONLY.** This rule is being specified after source wild/centered-shape results and individual profiles had already been opened and original Figure 6 rendered. It is NOT a preregistered scientific null or a new confirmatory family.

## Ecological question and non-goals

How similar do the **archived, already estimated 10-bin, session-median-centered self-prediction profiles** look among different bats admitted to the **same original source cohort**?

This quantifies one-dimensional **vertical shape similarity on the common binned, session-centered altitude axis**. It does **NOT** estimate overlap in three-dimensional flight habitats, overlapping 500-m cells, co-presence, resource use, dietary niche overlap, pairwise competition or a validated shared behavioral task.

The underlying 103 original individual source profiles (Figure 5B) are **weighted, leave-one-session-out, identity-matched self-predictor estimates** from other eligible sessions, averaged within individual; they are not simple GPS fix histograms. Different bats can have **different jointly supported horizontal cells and self-derived cell weights** even if assigned the same cohort. Source cohorts (site/colony/year) differ and must not be mixed.

## Source and immutable file

- Repository `zuizui0223/batter`, integration branch `prospective/unified-be-jae-individuality-v1`.
- Archival record `prospective/unified_individuality/figures/original_jae/centered_shape_individual_profiles_v1.json`.
- **Exact original source SHA256**: `9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2`.
- Original profile source script: `scripts/build_centered_shape_profile_descriptive_v1.py` from JAE `release/jae-v0.4.0-rc2`, blob SHA `7040e110de738766683c3cc06797a191dd4ff29e`.
- The generator must validate the immutable source bytes before parsing, accounting for the Python JSON's literal `-Infinity` and `Infinity` solely in the **height-bin edge metadata**. It may not modify the original archived source file.

## Prespecified descriptive transformation (no significance testing)

1. Use **all** 103 originally evaluable individual profiles across five original comparative panels (20/24/33/16/10 individuals in `eidolon`, `hypsignathus`, `phyllostomus_2022`, `phyllostomus_2023`, `phyllostomus_2016`). Exclude `Tadarida` because the original descriptive contract excluded its centered-shape FAIL.
2. Each source individual profile must have exactly ten `bin_probabilities` on the original centered-height bins, each in [0,1], with sum 1 within numerical tolerance 1e-9. Cross-check the source `upper_tail_mass_ge_100m` and optionally archived CSV row counts.
3. Define strata **only by the exact original `panel` and exact `cohorts` string** in the frozen source. These represent source collection cohorts/colony-year groupings, not guaranteed simultaneous co-presence. Never compare different cohorts or different panels, even within a species. The structural read of the profile metadata showed original *Eidolon* spans multiple years/countries; cross-cohort comparisons would be ecologically misleading.
4. Include **all unordered pairs of different biological individuals** (one pair `i < j`) within each exact (panel, cohort) stratum with `n>=2`; for `n<2` report zero possible pairs, without inventing values. Do not select pairs using their outcome profiles, similarity or inferred behavior.
5. For each pair compute the one-dimensional probability overlap coefficient

   [
   O_{ij}^{centered}=sum_{b=1}^{10}min(p_{ib},p_{jb})=1-	frac12sum_{b=1}^{10}|p_{ib}-p_{jb}|.
   ]

   The equality to 1 minus total variation must be numerically verified. This is a **shape-distribution intersection on a 1D residual-height axis**, not empirical 3D spatial overlap statistic S_rel and not co-use dyad separation I.
6. Produce machine-readable pair CSV for audit keyed by source panel, source cohort, original source `row_order` indices, and overlap coefficient, **not** personal animal identifiers. Produce one deterministic summary JSON of each stratum and one per-panel **descriptive** distribution summary.
7. Summary: pairs n, min, **10th quantile**, **median**, **90th quantile**, max; use **sorted samples with linear interpolation at index `(n-1)*q`** for q = 0.10,0.50,0.90. For n=1, these are equal to the one observed pair value. For no eligible pair report `n_pairs:0`, null quantiles. Report **no pooled whole-103 score** or global inferential effect across unrelated species and cohorts. The per-panel quantiles pool **nested nonindependent dyads across included strata** and are only descriptive; strata table is the primary interpretive unit for site/year differences.
8. Render **one supplementary SVG Figure S1** with per-panel median and 10–90th across-dyad range, actual `n_pairs`, and descriptive labels. These ranges are **not confidence intervals**, and neither dyads nor source cohorts are independent biological replicates. The original Figure 5 is untouched.
9. No source-null recalibration, permutations, bootstrapping, optimized thresholds, clustering, individual classification, habitat attribution or new hypothesis tests are allowed. Do **not** compare the amount of overlap to a calibrated empirical null or claim significance relative to a scale threshold.
10. Add a brief SI table, figure and cautious sentence to Results/Discussion **only if** explicitly labeled exploratory descriptive, while retaining source original positive/negative identity and S_rel/I interpretations. Do not claim 'individual niches overlap biologically' on the basis of this 1D centered shape coefficient alone.

## Structural eligibility bookkeeping, before pairwise outcome values

- Source individuals: Eidolon 20 across six site/year cohorts (n=8,5,1,2,2,2); Hypsignathus 24 in one source cohort; Phyllostomus 2022 n=33 across two colonies (n=14,19), 2023 n=16 across two colonies (n=10,6), 2016 n=10 in one source cohort.
- This implies exactly **41, 276, 262, 60, 45** unordered within-cohort pairs by panel, **684 pair records in total**, plus the one singleton Eidolon cohort with no pair. This is purely a combinatorial calculation from original cohort labels, not an overlap outcome. These **684 are NOT independent biological observations** and must never replace source individual n.
- Cohort names and original row_order are retained internally for audit, not as geographic claims or as independent replication of the original 4-panel terrain/interaction tests.

## Source-panel animal identity QA amendment (AFTER this descriptive outcome)

After the original source profiles and all 684 dyad overlaps were already processed, the archived original CSV and JSON were checked for **cross-panel literal animal-identifier reuse**. There are **103 individual-by-panel records** but **101 distinct identifier strings**, with two strings recurring in the 2016 and 2022 La Gruta *P. hastatus* panels. Calderón-Capote et al. (2025; DOI 10.1371/journal.pone.0313782) published a separate analysis of these 2016/2022 source populations with PIT-tag marking and **low recaptures**. Although actual recapture is plausible, literal ID reuse has **not** been independently crosswalked to the original long-term PIT registry; global unique living bat n is unresolved.

**Original descriptive sampling rule is unchanged**: no pair compares across source panels or cohorts and every within-panel biological identifier is unique. The source-based 684 dyad overlap values, figures and descriptive percentile rules remain exactly the original outputs. This amendment protects the language "103 source-panel profiles" from being misreported as 103 proved different bats. No six-year within-animal movement persistence is inferred from two identifier matches.

For further context, the same-source 2025 publication reported about **0.20 horizontal foraging-area overlap** using a Bhattacharyya coefficient, fundamentally different from the current **0.80–0.92 one-dimensional centered relative-height shape** overlap. Those coefficients are not estimates of the same volume of physical habitat.

## Post-outcome v2 visualization-only amendment (after seeing cohort-weight results)

The original v1 rule above specified a **five-panel** Figure S1 summary of dependent-dyad medians and 10th–90th percentile ranges. After opening the 684 original dyad overlap values and finding unequal cohort sizes, the display was **revised, transparently post-outcome**, into a **12-original-cohort** Figure S1 instead of adding a new hypothesis or modifying the core data transformation. All original 103 source-panel profiles and 684 pair coefficients remain unchanged; panels, source-cohort strata, binning, pseudocounts, 1D overlap formula, ranks and inferential status stay fixed. The new plot shows cohort median overlap by actual source cohort, exact n profiles and dyad pair counts; empirical 10th–90th bars for cohorts with at least three pairs and hollow points for single-pair cohorts. A singleton *Eidolon* source cohort is explicitly shown as non-estimable. Plotting conventions were chosen for communication after inspection of the descriptive values; **nothing about the v2 visualization is preregistered or independently confirmatory**. The original five panel-pool numeric summaries remain in SI Table S8 and the 12 source-cohort breakdown in Table S9. The renderer is `figures/render_cohort_resolved_s1_v2.cjs` and is rebuilt/compared in CI.

## Claim and publication boundary

Even a high (O_{ij}^{centered}) may arise partly by **constructive session centering, ten broad bins, regularizing pseudo-counts and/or common structural flight demands**. It cannot demonstrate co-location, same resources or interindividual competition; direct 3D/source terrain-co-use null results already test separate things and remain authoritative. Conversely moderate or low 1D overlap does not imply active avoidance.

If this post-outcome plot does not add biological clarity, keep it in the SI or omit it from journal figures. The main positive inference **remains the source-frozen held-out individual predictive tests**, not the newly computed overlap coefficient.
