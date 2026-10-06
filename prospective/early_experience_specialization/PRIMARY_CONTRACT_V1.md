# Early-experience specialization primary contract v1

## Status

**PROSPECTIVE RE-ANALYSIS CONTRACT — FROZEN BEFORE PUBLIC DATA VALUES ARE OPENED IN THIS PROGRAMME.**

## Source

Rachum et al. (2025),
*Early experience affects foraging behavior of wild fruit bats more than their original behavioral predispositions*,
eLife 14:RP103220.
DOI: `10.7554/eLife.103220.3`.

Public data:
Mendeley Data `10.17632/wh7c636y3t.1`.

Published design:
- 40 juvenile Egyptian fruit bats;
- baseline personality measured before treatment;
- bats then randomly divided between enriched and impoverished environments;
- season 2 contains a pre-release post-enrichment Trial 3;
- season-2 post-enrichment sample: 14 enriched + 15 impoverished = 29 bats.

## Biological question

The published paper establishes that early environmental treatment changes later average foraging behavior in the wild.

The untested individual-specialization question is:

> **Did enriched early experience merely shift the group mean, or did it increase the degree to which individuals diverged from one another in their behavioral change?**

This is a variance/individualization question, not another mean-treatment test.

## Confirmatory cohort

Primary cohort:

- season 2 only;
- exactly the bats with valid baseline 1, baseline 2, and post-enrichment Trial 3;
- treatment assigned before Trial 3;
- no post-release or outdoor-survival selection in the primary.

Expected source support:
- enriched: 14;
- impoverished: 15.

If the public source produces a different structurally valid cohort, report the discrepancy before opening the primary outcome and freeze a support amendment.

## Frozen behavioral vector

Use exactly the three source personality traits:

[
y=(B,E,A)
]

where:
- B = boldness;
- E = exploration;
- A = activity.

No PCA primary.

No trait deletion.

## Baseline state

For individual i, define pre-treatment baseline:

[
b_i = rac{y_{i,1}+y_{i,2}}{2}.
]

## Post-treatment change vector

[
Delta_i = y_{i,3}-b_i.
]

Before constructing Euclidean distances, standardize each of the three raw traits using the **pooled pre-treatment baseline values only**, without using treatment labels:

- pool Trials 1–2 across the complete primary cohort;
- compute one mean and sample SD per trait;
- require finite nonzero SD;
- transform Trials 1–3 with those frozen baseline scales.

Thus Trial 3 outcomes never define the measurement scale.

## Mean-shift removal

The target is individualization beyond a common treatment shift.

Within each randomized treatment group g:

[
r_i = Delta_i-arDelta_g.
]

This removes the treatment-group mean change vector.

## Primary statistic

For each group:

[
V_g = rac{1}{n_g}sum_i ||r_i||_2^2.
]

Primary contrast:

[
D = V_{enriched}-V_{impoverished}.
]

Positive D means enriched early experience generated more among-individual divergence in behavioral change after removing the shared enriched-group shift.

## Randomization null

Primary randomization test must respect the original assignment architecture as recoverable from the public data.

Preferred:
- preserve season = 2;
- preserve source-colony strata if individual origin is available;
- preserve the observed enriched/impoverished counts within each stratum.

If source-colony membership is not recoverable at individual level:
- use the documented season-2 group sizes 14 enriched / 15 impoverished in a complete-label randomization;
- label this as a design-approximate randomization because the paper also reports origin balancing.

Enumerate all assignments if feasible; otherwise use >=99,999 Monte Carlo assignments with frozen seed.

One-sided test:
[
p=P(D_{perm}ge D_{obs}).
]

## Support rule

Support requires:
- D > 0;
- one-sided randomization p <= 0.05.

No separate positive-individual threshold.

## Positive control — not a co-primary

Reproduce the published absence of pre-treatment group differences on Trials 1–2.

This is a data/design audit only.

Do not use failure of the positive-control reproduction to redefine the primary; instead return SOURCE_REPRODUCTION_STOP.

## Secondary — state rewriting

Only after the primary is frozen:

Compare predictability of Trial 3 from:
1. own baseline state;
2. treatment-group mean shift;
3. own baseline + treatment shift.

This is secondary and cannot rescue a failed variance primary.

## Outdoor extension

The wild GPS analysis is secondary because only 19 bats were tracked and post-release retention introduces selection.

It may test whether the treatment-associated individualization signal, if any, persists into wild foraging.

It cannot replace the pre-release randomized primary.

## Claim map

### D supported

Allowed:

> **Randomized enriched early experience increased among-individual divergence in behavioral change beyond its common mean effect, providing direct evidence that experience can generate individual differentiation rather than merely shift a population average.**

### D unsupported

Allowed:

> **The randomized enrichment manipulation changed later behavior in the broader study, but the pre-release laboratory data do not show that enrichment increased among-individual divergence beyond a shared treatment shift.**

This would favor common calibration over treatment-induced individualization in the laboratory phenotype.

## Hard prohibitions

After outcome opening do not:
- switch to one favorable trait;
- switch to PC1;
- select only bats retained outdoors;
- alter baseline averaging;
- change scaling to Trial 3;
- use post-release Trials 4–5 to rescue;
- choose a variance metric post hoc;
- claim individualization from a treatment mean difference.

## Programme role

This is the strongest currently available public-data test of:

[
	ext{experimentally manipulated early experience}
ightarrow
	ext{formation of individual differentiation}.
]

It is conceptually distinct from:
- persistence across current-context perturbation;
- cross-task portability;
- wild spatial partitioning.
