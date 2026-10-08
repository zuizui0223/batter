# JAE RC2 overlap prior-art challenge — independent submission audit (2026-10-08)

**REVIEWER-STYLE SCIENTIFIC POSITIONING, NO NEW ORIGINAL BAT OUTCOMES, NO MANUSCRIPT CHANGES.** This is a separate child branch of frozen \`release/jae-v0.4.0-rc2\`. DO NOT retroactively amend JAE, change thresholds, recompute an alternate positive estimator, or silently merge this audit.

## Source problem
The most marketable phrase in the current JAE title is:
> Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species.

A critical reviewer can cite **existing directly relevant bat spatial-specialization studies** to dispute novelty of any generic "individual space-use specialization with home-range overlap" interpretation:

1. **Kerches-Rogeri et al. (2020)**, Journal of Animal Ecology, "Individual specialization in the use of space by frugivorous bats", DOI 10.1111/1365-2656.13339, radiotracked **10** \`Sturnira lilium\` bats, adapting individual specialization metrics to spatial volume intersection (SpatIS/SpatICS). Spatial individual specialization and nonzero overlap are explicitly part of their framework.
   - https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2656.13339
2. **Wang et al. (2023)**, Movement Ecology, "Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (\`Ia io\`)", DOI 10.1186/s40462-023-00394-1. Seasonal spatial specialization and home-range/core-area overlap were jointly quantified, with greater overlap during autumn and lower but still present individual spatial specialization. Its endpoint primarily comprises geographic distributions/overlap rather than conditional vertical shape after within-session centering.
   - https://link.springer.com/article/10.1186/s40462-023-00394-1
3. **Teshima et al. (2026)**, Proc R Soc B DOI 10.1098/rspb.2026.1463, already presented latent bat flight-policy inference from a separate 7-obstacle arena Figshare source, which overlaps with our **non-JAE** Rhino mechanics programme. This is not independent support for current field vertical-niche analysis; do not claim it validates learned movement solutions.
   - https://doi.org/10.1098/rspb.2026.1463

## What the current JAE evidence can honestly add
**NOT new:**
- animal individual specialization in space;
- bat individual specialization or overlapping home ranges;
- behavioral individuality during flight;
- that lack of complete home-range exclusivity can coexist with individual differences;
- that memory/learning creates the observed vertical trajectories (unmeasured).

**Potentially distinctive combination**, scoped to named panels:
1. **VERTICAL DISTRIBUTION SHAPE**, not solely 2-D home-range occupancy;
2. held-out same-individual profile prediction under **identical 5-km horizontal-cell weights**, countering coarse horizontal site fidelity;
3. **session-median-centered altitude**, countering additive satellite tag/device zero-point offset;
4. terrain-relative height fidelity in **four** structurally evaluable panel/periods of \`H. monstrosus\` and \`P. hastatus\` at shared **500-m** cells (all four positive under inherited diagnostic calibration);
5. **no permutation-supported positive *added* terrain-relative 3D segregation in 4/4** panels, but this is LACK OF DIRECTIONAL SUPPORT, not proof the true segregation effect is precisely zero;
6. temporal synchronous local co-use vs circular phase-shift null: 3/4 panels lacked supported extra separation, with exploratory upper compatibility endpoints ~0.98m, 1.92m, 1.13m; ***P. hastatus* 2023** has an exception (~+3.57m, phase shift p=.0231 under a coarser 600-s/all-space design and broad uncertainty).
7. persistence beyond one night and after 500-m place × speed × turning matching in evaluable sets — explicitly **post-outcome mechanism localization** with no causal origin inference.

Thus the core empirical bridge is:
> When *where an individual flies* and additive altitude zero point are controlled, its *vertical-use distribution* may remain predictive across sessions, whereas the measured population's contemporaneous extra vertical segregation is neither universally nor consistently supported.

This is a more specific question than the earlier work's 2-D spatial specialization-vs-home-range-overlap comparison; it requires the specific vertical/measurement normalization and synchronous-encounter tests.

## Exact methodological logical risk
An ordinary upper-tail test of extra segregation with p>.05 cannot establish the sharp statement "partitioning absent". Also, upper 95% bootstrap endpoints from post-outcome dyad analysis are **compatibility bounds** not formal preregistered equivalence tests, and do not exclude small effects everywhere.

The phrase **"need not partition"** is defensible as a counterexample to the proposed *necessary strong, detectable spatial exclusivity* mechanism in the specified datasets, but it must not be interpreted as ecological impossibility of resource partitioning, absence of competition, or verified true zero vertical separation. Some individuals could still partition **prey, times, finer location cells or sensory cues**. The current data do not identify what motivates overlap.

### Safer alternatives for cover letter/reviewer response (not a silent manuscript edit)
- "Detectable persistent differences in vertical-use shape do not consistently coincide with extra spatial separation during local co-use."
- "Comparing the same physical horizontal opportunity and subtracting tag-level altitude constants separates individual vertical distribution shape from strong contemporaneous vertical-layer partitioning."
- "Within two tropical bat species, vertical individuality survived controls that make a purely geographic or constant-device-offset explanation insufficient, but origin and fine-scale resource differentiation remain unresolved."

Avoid:
- "individual specialization requires no separation" as a universal theorem;
- "partitioning does not occur" as exact effect-size/equivalence finding;
- "this is the first bat study to demonstrate spatial specialization with overlap";
- "individual memory/skill development maintains the observed bats" without individual manipulations.

## Evidence structure and boundaries that MUST remain in front
The original \`Tadarida teniotis\` (motivating species) centered-shape primary FAIL p=.5121, main 4 additional external programmes have first-preregistered verdicts **3 fail / 1 pass** (not independent representative prevalence sampling), and in the four panel shared-place synchronous co-use analysis there is one positive exception. No selective "4/4 no partition" claim; 4/4 only applies to terrain-relative identity, not to literal all scales of co-use.

The available JAE rc2 manuscript word count ~7,995 / 8,500 and cover letter are already generated, source-guarded, visually checked and **frozen**. The remaining true submission bottlenecks are human author metadata, licensed software declaration and final release/DOI. This note is an **editorial decision input**, not an instruction to rerun analysis.

## Programme decision
1. **Keep JAE RC2 frozen.** It is a bounded descriptive-predictive comparative study, not a causal motor/acoustic-origin paper.
2. Resist adding negative-return bat datasets from the **post-hoc 2026 acoustic search** into its evidential sample; the public-source screen is different.
3. Publish/submit JAE on its own when human metadata and official release requirements are met, preserving all external failed tests and the 2023 co-use exception.
4. Treat PR #72+ experimental solution-opportunity line as a NEW and conditional causal programme, not an explanation already demonstrated for JAE's field bats.
5. Novelty is methodologically localized **vertical shape after measurement/horizontal standardization vs synchronous separation**. The causal origin/fitness of maintained differences remains *unresolved*, so no Nature-scale causal discovery is currently licensed.

## Reproducibility
This note was prepared by independently comparing:
- the frozen release submission-readiness and current manuscript source in \`batter\`,
- Kerches-Rogeri et al. 2020 JAE article and Wang et al. 2023 Movement Ecology article,
- the already frozen claim ledger (specific n/positive/negative diagnostic gates).

No numerical analysis or new outcomes opened.
