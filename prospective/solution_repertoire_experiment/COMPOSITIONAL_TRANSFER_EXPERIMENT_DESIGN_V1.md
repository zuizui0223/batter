# Proposed new bat experiment: Is a practiced 3D route stored as a path or as reusable maneuvers?

**Prospective DESIGN ONLY. No authorized animal study, no observed behavioral result, and no change to frozen PR #72 P1/P2 or JAE.** This note is an independent experiment candidate based on the matched A/B course topology already designed in the batter repository.

## Rationale and literature boundary

Barchi, Knowles & Simmons (2013, *J Exp Biol*, DOI 10.1242/jeb.073197) showed that experienced Eptesicus fuscus bats can resume established obstacle routes after a month and change route under mirrored geometry. That prior result establishes strong spatial memory and geometry dependence; this proposed study instead asks **what building blocks of movement knowledge transfer to routes that were never themselves trained**. Human obstacle-movement research already documents transfer between motor configurations (van Hedel et al. 2002, DOI 10.1113/jphysiol.2002.018473). Accordingly, neither memory nor movement-skill generalization can be claimed novel in general.

## Matched factorial route code

The original four-route objective has two categorical decisions:

| Route | horizontal decision | vertical decision |
|---|---|---|
| R1 | left | low |
| R2 | left | high |
| R3 | right | low |
| R4 | right | high |

For an assigned practiced path S, the three untrained paths can be preclassified as one sharing only the horizontal decision, one sharing only the vertical decision, and one sharing neither decision. Training S is randomized independently of individual baseline route preference, with each path represented once in every complete four-animal block.

## Matched geometries / independent measurement

A: resolve horizontal choice then vertical. B: vertical then horizontal (frozen matching details from PR #72). Training is proposed only in A; **after the same standardized baseline familiarity for all paths**, independently assess pre/post performance on **all four** path combinations in B (different decision order). A possible additional within-A test is secondary, not a substitute for transfer across B.

Measure in advance-defined physical units: spatial clearance/collision/error, trial completion rate, time/3D curvature, independently validated energy-related proxies. Measure with a planned low-burden forced-route assay rather than conditioning the estimate on voluntary selections, to avoid selection bias in which routes are observed. Route feasibility, matched food reward, acoustic visibility, fatigue and animal welfare require a separate engineering pilot; no trial counts or N are approved here.

## Primary ecological contrast: *untrained recombination transfer*

For each animal i, each of four routes r and before/after matching measurement, define gain \(\Delta_{ir}=\mathrm{performance}_{pre,ir}-\mathrm{performance}_{post,ir}\), with positive values indicating a lower cost/safer execution. Transform all bat data to physical comparable units before defining this outcome.

If the randomized trained route is S, let \(r_H\) share only its horizontal component, \(r_V\) share only its vertical component, and \(r_N\) share neither.

\[
C_i=\frac{\Delta_{i,r_H}+\Delta_{i,r_V}}2 - \Delta_{i,r_N}.
\]

**Positive C** is the primary transfer signature under an additive component-learning model. The completely practiced path does not appear in C, so the contrast is not merely evidence that practice helps its own route. A companion diagnostic \(D_i=\Delta_{i,S}-\Delta_{i,r_N}\) checks that assigned practice had any local performance effect at all.

### Key causal-inference guard

Do **not** claim a simple Fisher exact permutation p for the null 'no off-route transfer' by freely relabeling the observed training route S. That null allows a strong treatment effect on the practiced route itself. For a counterfactual training assignment S', its unknown practiced-route potential outcome could enter the off-target contrast, so the **partial-transfer null is not sharp**. Permuting unchanged observed 4-route performance vectors as though they were invariant would not be an exact test of this null.

Balanced random assignment makes the observed mean C an **unbiased estimator of the randomized average off-route transfer contrast** across S labels, even with unrestricted direct benefits on S, provided route measurement is complete and interference absent. For eventual analysis use a predeclared animal-cluster interval / robust blocked estimator suited to the sample size; assess actual small-block finite-sample calibration in an independently preregistered pilot. Preserve whole randomized blocks and all four route outcomes. Fisher permutation is exact only for the much stronger sharp null of *no training effect on any route at all*.

### Mechanistic contrasts (all prospective)

| Rival biological mechanism | trained path | one shared component path | shares neither |
|---|---:|---:|---:|
| Whole route-specific memory/skill | improves | little/no transfer | little/no transfer |
| Reusable horizontal/vertical maneuvers | improves | partial transfer | little/no transfer |
| Generic familiarity | improves similarly | improves similarly | improves similarly |

A positive C does **not** prove motor learning specifically; generalization of sonar cues, landmark recognition, route geometry and task expectations also predicts selective transfer. A cross-environment/order and cue-control series is required to claim the origin is motor control rather than perception.

## Secondary conditional choice signature (not standalone proof)

A purely additive component-choice model implies within individual (at fixed context):

\[
P(L,low)P(R,high)=P(L,high)P(R,low).
\]

This 2×2 independence is equivalent to zero log-odds interaction, whereas an exact preferred-route bonus can induce a nonzero interaction. It is a secondary, explicitly model-dependent prediction; pooled population frequencies can violate or satisfy it spuriously under individual heterogeneity, route reward/geometry interactions or variable task contexts. Do not fit/tune this test on frozen existing Rhinolophus data as a new 'confirmation'.

## Experimental boundary

The new motor-module test differs from the original 4-versus-1 acquisition opportunity study. It cannot be silently grafted onto PR #72. Future approval must specify: independent animals/crossover interference handling, equal pre-randomization path familiarity, randomized extra training dose, cue/route-difficulty matching, ethical flight burden, blind 3D tracking, blocked estimator and explicit attrition policy before any choice/performance outcomes are opened.

**Biological hypothesis:** Personal spatial specialization can persist not just because animals memorize whole routes, but because practice builds reusable movement components whose **novel combinations** create personal routes even where animals share the same environment and food goal. This remains an untested mechanism, not the first mathematical discovery of multistability.
