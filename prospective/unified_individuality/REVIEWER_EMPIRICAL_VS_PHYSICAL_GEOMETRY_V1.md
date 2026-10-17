# Reviewer-facing distinction: identity, estimated centered 3D geometry, and physical ecological partitioning

**Reconciliation:** 16 October 2026. This is a scientific-claim audit based on **original fixed source estimands**, including newly verified original source code for 3D Jeffreys smoothing and the co-use metric. No new bat GPS or DEM inputs were opened, and no source null-calibrated results were changed.

## What each result actually measures

| Measured object | Original evidence | What it supports | What it cannot establish |
|---|---|---|---|
| Experimental individual correspondence | Source-specific mapping under sensory/navigation manipulations, 4 experimental programmes with small biological n | Within each controlled programme, the correct individual's behavioral mapping can remain informative after a condition change | A common neural carrier across taxa, an invariant path geometry, or a causal connection to wild 3D space |
| Wild centered height-distribution identity | Five comparative wild panels pass whole-session permutation; focal Tadarida does not | Individual predictive information in an estimated **relative-to-own-session-median** height-probability shape under coarse XY weighting | A fixed absolute altitude layer, directly shared physical habitat volume, specific prey use or a learned policy |
| Original 500-m conditional vertical identity and V_rel | Original native conditional estimator in 4/4 structurally eligible panels; terrain-relative V_rel nominally 4/4 and illustrative 12-test Holm 3/4 | Individually predictable smoothed within-session height configuration over pairwise-shared coarse horizontal support | Generality to four independent species, robustness to alternative α/resolution/cell-support rules, physical co-occupancy or ecological adaptation |
| Native O_XY and joint O_XYZ | Same/other repeated-session pair intersections, eligible n = 8/5/6/9 | Descriptive overlap of **estimator-defined** horizontal and smoothed, session-centered XY×relative-height distributions | Direct matching in observed physical three-dimensional grid cells. Fixed α=0.5 gives positive probability to unobserved height bins; 50-fix pair support is aggregated across common XY cells |
| Terrain-relative added S_rel | Four original, post-outcome panel-level permutation comparisons; **0/4 positive-source-supported** | No consistent source-calibrated evidence for *additional segregation of the estimated, centered relative-height distributions* at the tested grain | A formal zero-effect equivalence result, absence of all true altitude separation or resource competition |
| Matched same-cell/time co-use I | One nominal original positive panel (+3.57 m, source p = 0.0231, 600-s all-space); retrospective Holm 4-test p = 0.0924 and 12-test p = 0.2079 | In one heterogeneous panel, selected animals' **session-centered relative-height deviations** were more dissimilar than a fixed-event within-individual×session×cell shifted-deviation null | A bat-to-bat **physical vertical gap** of +3.57 m, instantaneous co-presence, active avoidance, or physical altitude equivalence in the other three panels |
| Laboratory-style carrier → wild | Frozen source PASS/PASS/FAIL/STRUCTURAL STOP against a ≥3/4 criterion, overall FAIL | The fixed tested cross-domain scalar cannot be claimed to explain the wild conditional-height signatures | A shared lab-field latent strategy or causal process |

## A minimal source-backed probabilistic language

For an individual i, source-estimated vertical use at horizontal location h and context c may be written conceptually as p_i(z_relative | h,c). Here z_relative is defined **after source/session centering** for the underlying geometry; estimates also depend on finite binning, α=0.5 pseudocounts and structural support.

This is **not** a universal learned bat flight law. A latent mixture p_i(z_relative | h,c)=Σ_k π_i(k|h,c)q_i(z_relative|k,h,c) can reflect unobserved task allocation, within-task behavioral/morphological solutions or environmental responses. Even a perfectly estimated p_i cannot identify π versus q without genuine task observations or prospective intervention.

The separation question then asks whether individual-specific *estimated* relative-height use is additionally disjoint under a declared source null. The original S_rel source result provides **non-support for consistently positive excess**, not positive proof of an absence. The separate I source result cannot fill the physical-altitude gap because each individual session's median was subtracted *before* pairwise encounter differences were calculated.

## The physical co-use gap is not a minor terminological nuance

Let h_A and h_B be terrain-relative heights for two co-use events and m_A and m_B their session medians. The historical original corrected code's endpoint is

\[
I_{\rm event}=|(h_A-m_A)-(h_B-m_B)|,
\]

whereas actual terrain-relative physical altitude separation would instead be |h_A−h_B| (itself still only a proxy until vertical datums and DEM/geoid alignment are verified). If m_A ≠ m_B, these are different statistics. A synthetic event can have a 100 m physical separation but 0 m centered-deviation difference, or 0 m physical separation but 100 m centered-deviation difference. Thus the source-reported metre-valued compatibility bounds do not constrain physical between-bat altitude separation.

## Science and editorial decision

**Strong supported contribution:** original experimental individual mapping information across conditions, plus field identification of individually predictable *estimated* height-use shapes after coarse XY/session-context controls; the field information remains in three of four eligible terrain-relative field panels under the broader illustrative twelve-test Holm sensitivity.

**Narrower contribution than formerly written:** additional vertical segregation, co-occurrence and topographic effects are about the source's statistical estimators and preprocessing. We have **not** demonstrated an adaptive cognitive flight solution, physical shared airspace, physical avoidance/nonavoidance or resource partitioning.

**Publication strategy:** a unified manuscript can coherently compare measured *formation, conditional persistence, expression and ecological tests*, but its title and Abstract must not imply that the laboratory programmes causally explain physical bat 3D partitioning. The strongest positioning is an **evidence-ranked comparative reanalysis of persistent individual information and its non-equivalent ecological estimands**, not a claimed reconstruction of the true learned flight policy.

## Fixed evidence and remaining barriers

The source-wide original 23-parent screening, 2016 relative-date limitation, external boundary failures, small-n laboratory panels and failed lab-to-wild scalar carrier remain negative/boundary evidence. The original native 500-m source (commit 819acc82, source α=0.5), original corrected co-use runner (commit 7d5f310b; Git blob 1f528f0343ac9e6e26851e4adad5c106e8e5dffc), exact original nulls, and machine values are preserved unchanged. The original data, equipment vertical bias, measured actual resource height, prospective task labels, independent source-input numerical replay, licence permissions and human coauthor approval remain unresolved.

Source audits: [smoothed 3D and shared-cell support](SMOOTHED_3D_OVERLAP_SUPPORT_AUDIT_V1.md) and [the true centered co-use metric](COUSE_CENTERING_PHYSICAL_GAP_SCOPE_AUDIT_V1.md). Both have source-Git-blob-guarded synthetic-only tests.
