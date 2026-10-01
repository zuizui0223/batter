# 3D niche-partition analysis contract v1

## Status and inferential class

POST-OUTCOME GENERATED ANALYSIS; SPECIFIED BEFORE ANY 3D-OVERLAP OUTPUT IS COMPUTED OR INSPECTED.

The original centered-height outcomes and previously reported analyses are already known. This analysis therefore cannot be called a prospective replication or outcome-blind confirmation. Its purpose is narrower: to ask, with a newly specified geometric estimand, whether the previously detected individual vertical organization corresponds to repeatable individual-specific use of three-dimensional space within shared horizontal landscapes.

The integrated JAE submission branch remains scientifically frozen. This analysis is isolated on post-freeze/3d-niche-partition-v1 and is not added to the submission unless a later explicit manuscript-unfreeze decision is documented.

## Ecological question

Do bats that use overlapping horizontal space repeatedly occupy different parts of that shared space in the vertical dimension?

The target interpretation is repeatable individual 3D niche partitioning, not deliberate avoidance. A positive result can show that an individual's vertical configuration within shared horizontal space is more similar across its own sessions than to conspecific sessions. It cannot by itself establish competition, intentional avoidance, diet partitioning or causal resource depletion.

## Fixed source universe

Use all six original archive panels with no outcome-based source selection: Tadarida teniotis, Eidolon helvum, Hypsignathus monstrosus, and Phyllostomus hastatus 2022, 2023 and 2016. No external source is added in v1.

## Fixed preprocessing

- Same raw source files, parsers and retained sessions as the centered-shape audit.
- Subtract each retained session's median native height before vertical binning.
- Same source-specific projected coordinate systems.
- Primary horizontal grain: 500 m.
- Vertical edges: -inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, +inf m.
- Jeffreys smoothing alpha = 0.5 for vertical conditional probabilities.
- No alternate primary grid after overlap output is opened.

## Session-level distributions

For session s, p_s(c) is the empirical probability of 500-m horizontal cell c. p_s(z|c) is the smoothed centered-height distribution within occupied cell c. The joint 3D distribution is p_s(c,z) = p_s(c) p_s(z|c). Each session is normalized to probability 1 before pairwise comparison.

## Pairwise support gate

A session pair is evaluable only when both sessions are in the same admitted cohort, share at least one 500-m horizontal cell, and each session contributes at least 50 fixes within the shared-cell set. No pair is rescued by changing grid size or lowering this threshold.

## Geometric overlap estimands

Horizontal overlap: O_XY(a,b) = sum over cells of min[p_a(c), p_b(c)]. Range 0-1.

Full 3D overlap: O_XYZ(a,b) = sum over cell-height voxels of min[p_a(c,z), p_b(c,z)]. Range 0-1.

PRIMARY GEOMETRIC ENDPOINT: common-horizontal conditional vertical overlap. For cells occupied by both sessions, define weights w_c proportional to min[p_a(c), p_b(c)] and normalize them to sum to 1. Within each shared cell, O_Z(c) = sum over height bins of min[p_a(z|c), p_b(z|c)]. Then O_Z|XY(a,b) = sum_c w_c O_Z(c). This directly asks how much the two vertical distributions overlap after horizontal location is matched to the same shared cells.

Descriptive geometric decomposition: L_3D(a,b) = O_XY(a,b) - O_XYZ(a,b). When O_XY > 0 also report R_3D(a,b) = 1 - O_XYZ(a,b)/O_XY(a,b). These quantify overlap lost when height is added and are secondary descriptive quantities, not extra primary tests.

## Primary individual-partitioning statistic

For each evaluable target session: (1) compute O_Z|XY against every other evaluable session of the same individual in the same cohort; (2) average those self overlaps equally; (3) for each other individual, average O_Z|XY across that individual's evaluable sessions; (4) average those other-individual means equally; (5) define D_s = mean_self(O_Z|XY) - mean_other(O_Z|XY).

Aggregate target sessions equally within biological individual, then biological individuals equally within panel. The panel statistic D_panel is the equal-individual mean of D_i. Positive D means the same individual reuses a more similar vertical configuration within shared horizontal cells than do different individuals.

## Structural panel gate

An individual is evaluable only if it has at least one evaluable self-session comparison and evaluable comparisons to at least two other individuals. A panel is inferentially evaluable only if at least 5 biological individuals satisfy this rule. Otherwise report structural non-evaluability; do not rescue by changing grid, threshold or subset.

## Identity-exchangeability null

Within each cohort, keep each complete session and its x-y-z geometry fixed, permute individual labels across whole sessions, and preserve the exact multiset of session counts per individual. Recompute the complete eligibility and aggregation pipeline.

B = 9,999 per panel. Seeds: Tadarida 2026100201; Eidolon 2026100202; Hypsignathus 2026100203; Phyllostomus 2022 2026100204; Phyllostomus 2023 2026100205; Phyllostomus 2016 2026100206.

Primary panel support requires the structural gate, D_panel - mean(null) > 0, and one-sided p(null >= observed) <= 0.05. Always report null mean, q025, q50 and q975.

## Predeclared secondary geometry summaries

Report equal-individual self and other O_XY, O_XYZ, O_Z|XY, L_3D and R_3D; individual-by-individual aggregate-session matrices of O_XY, O_XYZ and O_Z|XY for visualization; and the distribution of between-individual O_Z|XY values. These may describe whether individuality is expressed through horizontal separation, vertical separation within shared space, or both, but do not create separate significance claims.

## Interpretation matrix

- D supported and horizontal overlap substantial: evidence consistent with repeatable individual-specific 3D niche geometry within shared horizontal landscapes.
- D supported but horizontal overlap generally low: repeatable individual 3D niches, but apparent separation may be dominated by horizontal segregation; do not emphasize vertical partitioning.
- D not supported: existing vertical identity does not translate into stable pairwise 3D overlap geometry under this 500-m definition; no rescue.
- Tadarida remains a boundary regardless of sign; a positive overlap result does not overwrite the established centered-shape boundary.

## Claim ceiling

Allowed if supported: individuals can repeatedly reuse different vertical configurations within horizontally shared space; population 3D space use can be assembled from partially segregated individual spatial niches; adding height can reveal separation invisible in horizontal overlap alone.

Not allowed from this analysis alone: intentional avoidance, competition causation, diet partitioning, adaptiveness, or resource competition as the cause. Those require direct resource identity, simultaneous competitor exposure, dietary data or manipulation.

## Stop rule

After the first 3D-overlap output is produced, do not change the 500-m primary grid, vertical bins, alpha, support threshold, panel gate or primary overlap index; do not exclude contradictory panels/individuals; and do not use descriptive L_3D or R_3D to rescue a negative primary result.
