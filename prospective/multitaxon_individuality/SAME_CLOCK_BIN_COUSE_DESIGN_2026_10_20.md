# Fixed design: 2D geographic sharing versus coarse same-clock-bin sharing

**Exploratory extension (20 Oct 2026). This is not independent preregistration.** Earlier R/X, source-specific seasons and 25-km pair risk sets have already been inspected. This document is committed before opening *new* time-matched outputs.

## Biological question
Can two animals have substantial seasonal geographic occupancy overlap without excess use of the same grid cells in the same **6-hour source-clock block** on identical observed calendar days? Measure the timing dimension independently rather than assuming 2D X means synchronous co-use. The outcome is observational **T6**, *not physical encounter or social interaction*; six hours is too broad to assert proximity/contact.

## Fixed source frame and QC
Evaluate all three previously analyzed published sources, not outcome-selected taxa:
- wild turkey, Movebank DOI 10.5441/001/1.671
- black bear, DOI 10.5441/001/1.706
- white-tailed deer, DOI 10.5441/001/1.718.

Original GPS files and unique reference original must exactly pass previously recorded source file **MD5 and SHA256** receipts. Read the *complete originals* with the same sensor, visibility, taxon, outlier, deployment-ID reference join and unique animal/timestamp rules in `cross_source_seasonal_x_v2.py`. An independent temporal timestamp read must reconstruct exactly the same count and multiset of `(animal, source calendar day, latitude, longitude)` source fixes. Reject any mismatch, unparseable timestamp, conflict or original checksum. No original coordinates, IDs or exact dates may be published.

The native GPS timestamp is parsed without claiming UTC/local solar-clock accuracy. For each exact source-calendar date, define 6-hour bins as floor(source-hour/6), and secondary 3-hour bins as floor(source-hour/3). Evaluate years **2019 and 2020** and calendar seasons winter=(Jan,Feb,Dec within the same year), summer=(Jun,Jul,Aug). They are *categorical* winter months, not a contiguous chronological winter or actual migration stages.

## Fixed dyad opportunity before any T computation
Reconstruct the prior V2 full-day risk set: two or more calendar months per season with at least **seven pair-common observed dates per month**, annual day-balanced center distance ≤25 km; verify reference 5-km V2 pair counts for each source/year. No site/group labels in the selected references are independently usable; the 25-km distance is geometric only, not ecological-population evidence.

For each time-bin width separately, tighten the support: a *qualifying date* must contain **at least two 6-hour (or 3-hour) bins observed in both animals**, each with at least one GPS fix. Keep a dyad only if at least two winter and two summer months each have **≥7 qualifying dates**. Report attrition from the previous source-year V2 dyad mask. A dyad with only one supported clock bin/date is NOT eligible; missing is not zero T. Fix eligibility before using cell identity or overlap values. Use exactly two eligible months per season and seven matched qualifying dates per month, selected uniformly without replacement by reproducible seeded pseudo-draws. Twelve fixed seed replicates (0–11). A dyad uses the same month/date samples for all spatial grids.

## One original GPS fix per source-clock bin
On each selected pair/date and each clock bin shared by both animals, draw **one original GPS fix for each animal** uniformly without replacement within that animal/bin. Each animal-bin-day draw is deterministic from SHA256(source, year, animal, date, bin, seed) and shared across evaluated pairs. This equalizes the number of sampled positions per animal/time opportunity; the number of shared bins (2–4 at 6h, 2–8 at 3h) may vary across dates. Cell width and grid origin do not alter the sampled original positions.

At each date, let (c_i(b)) and (c_j(b)) be the spatial cell for the two animals in the same source-clock bin (b). There are (m≥2) common bins. Define:

- (X_{day} = \sum_c \min(n_i(c)/m,n_j(c)/m)). This is overlap of *the same sampled fixes with their clock bins pooled* within the shared bins.
- (T_{day} = m^{-1}\sum_{b} 1[c_i(b)=c_j(b)]). This is **coarse contemporaneous cell coincidence** (within the same 6h/3h block), not an encounter; exact GPS timestamps in the block can be hours apart.
- (N_{day} = m^{-2}\sum_c n_i(c)n_j(c)). This is the **exact expected T under independent random within-day permutation of each animal's spatial cell assignments over its m observed common clock bins**, preserving per-day sampled cells and both animals' observed measurement time bins. It is a conditional reference *not* an exchangeable causal null or p-value.
- (D_{day}=T_{day}-N_{day}), the observed coarse time-label alignment beyond that conditional random-label reference.

All metrics are bounded, and by a finite coupling inequality (0≤T_{day}≤X_{day}≤1) and (0≤N_{day}≤X_{day}≤1). Both organisms' actual positions in unmatched bins are excluded from *both* X and T. Do not substitute an unconditioned monthly X or use T as resource overlap.

Average equally over seven matched dates, equally over the chosen two months in each season, then equally across eligible dyads within source/year/time-width. Report each seed as **aggregate cohort values only**, with winter/summer X, T, N, D, matched dyad counts, total evaluated date pairs and distributions of common-bin counts. Report all seeds, signs of winter-minus-summer and mean T−N, no significance or confidence intervals; do not count shared-animal pairs or seeds as independent replicates.

## Predeclared spatial sensitivity and STOP
Primary grid: 5 km and origin (0,0); additional grids: 1 km origin (0,0), 10 km origin (0,0), 5 km half-cell shift in both axes. Fixed time-bin widths: 6h (primary) and 3h (secondary, if eligible). Total declared 2 clock widths ×4 grid settings ×12 seed samples per eligible source-year. A source-year lacking at least **two qualifying dyads** is NOT_ESTIMABLE. Report lost support; never pick a spatial/clock scale posthoc by the observed sign.

Validation must independently check exact original source receipts and positional QC equality, V2 risk set, absence of track-level outputs, output bounds and mathematical identities, seed reproducibility, independent synthetic cases (same spatial set but asynchronous clock bins, exact-label alignment, all-zero X), date/month availability gates and null semantics.

The conditional permutation reference assumes within-day bin-label exchangeability of positions, which is not biologically assured under autocorrelated movement or circadian behavior. Thus (D>0) or (D<0) is *relative to this descriptive reference*, not proof of synchronized interaction or avoidance.

## Interpretive boundary
Even if D differs among taxa or seasons, the result is a source-clock pattern in coarse GPS timing, not true synchronous physical encounters, a population-general inference, an environmental resource contrast E or an identity-to-niche causal mechanism. Source-specific population membership, GPS fix errors, clock offset, multiple independent annual populations and unequal missing-day processes remain unresolved. Data are fully source public but individual tracks/coordinates and other identifying records must never enter repository artifacts or logs.
