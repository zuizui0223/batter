# Configuration-conditioned estimator implementation clarification v1

## Status

**FROZEN BEFORE ANY TRAJECTORY NUMERIC VALUE IS OPENED BY THE PRIMARY PROGRAMME.**

Parent:
`CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md`

This clarification changes no biological question, threshold, feature family, or support rule. It fixes implementation details that were underspecified in the parent contract.

## Primary A permutation

Within each species × eligible environment independently:

1. treat every structurally valid trajectory as one indivisible unit;
2. retain the observed number of trajectories assigned to each bat label;
3. uniformly shuffle the trajectory units;
4. repartition the shuffled units into bat labels using the original bat-specific trajectory counts;
5. recompute all target-level self and donor distances and the full equal-weight aggregation.

Thus the null preserves:
- environment;
- number of bats;
- trajectory count per bat;
- each trajectory's complete 3-D geometry;

and breaks only trajectory-to-individual identity.

## Horizontal turning-rate formula for Primary B

After finite filtering, chronological sorting and duplicate-time removal:

For consecutive positions p_t:

- horizontal displacement vector: `v^H_t = (X_{t+1}-X_t, Y_{t+1}-Y_t)`;
- segment heading: `theta_t = atan2(dY_t, dX_t)`;
- retain headings only when horizontal displacement magnitude > 0 and segment dt > 0.

For two successive valid horizontal segments t and t+1:

- wrapped heading change:
  `dtheta = atan2(sin(theta_{t+1}-theta_t), cos(theta_{t+1}-theta_t))`;
- effective elapsed time:
  `dt_turn = 0.5 * (dt_t + dt_{t+1})`;
- absolute horizontal turning rate:
  `|dtheta| / dt_turn`.

Require at least 50 finite positive-dt movement intervals for Primary B as already frozen.

No angular smoothing.

## Environment residualization

For each species × environment × feature:

- use all Primary-B-valid trajectories in that environment;
- compute arithmetic mean and sample SD across trajectories;
- z-score every trajectory feature with those values.

If one feature has zero or non-finite SD in any environment that contributes to that species' Primary B, drop that feature for the **entire species**, as already specified.

Primary B requires >=6 retained features.

## Cross-environment centroid weighting

For bat j when target environment is e:

1. within each other environment e' != e, average j's standardized feature vectors across its valid trajectories in e' equally;
2. average those environment-level centroids equally across all eligible e'.

Thus an environment with many recorded trajectories does not receive greater weight than one with few trajectories.

Require at least 2 contributing other environments.

## Primary B permutation

The null must break the continuity of individual identity **across environments** while preserving within-environment repeated-trial structure.

For each permutation and each species:

1. within each environment independently, treat each observed bat × environment trajectory cluster as an indivisible unit;
2. randomly permute the bat labels assigned to those clusters among the bat labels present in that environment;
3. keep all trajectories from one observed bat × environment cluster together under the permuted label;
4. preserve the number of trajectories in every cluster and the set of bat labels present in each environment;
5. recompute environment residualization, leave-one-environment-out centroids, K_q and K_species through the complete pipeline.

This preserves:
- environment;
- within-environment route/kinematic repeat structure;
- number of bats per environment;
- number of trajectories per bat × environment cluster;

and breaks only the cross-environment continuity of bat identity.

A single global relabeling across every environment is explicitly forbidden because it would leave the identity statistic invariant.

## Permutation counts and seeds

Unchanged:
- Primary A: 9,999; seed 202610042201.
- Primary B: 9,999; seed 202610042202.

## Missing/invalid target handling

Observed and permuted statistics use the same structurally valid trajectory set fixed from the coordinate-support rules.

No permutation-specific outcome filtering is allowed.


## Primary A target and donor eligibility

Within an eligible species × environment:

- a bat is an evaluable **target bat** only if it has >=2 route-valid trajectories in that environment, because D_self requires at least one held-out same-bat comparator;
- every route-valid trajectory of an evaluable target bat is used once as a target;
- any other bat with >=1 route-valid trajectory may contribute as an other-bat donor;
- donor distances are averaged within donor bat first and donor bats equally second.

Bat-level direction consistency is calculated only for evaluable target bats.

Because Primary A permutations preserve the trajectory count assigned to every bat label, the set of target-eligible labels is invariant across permutations.

## Primary B contributing-environment rule

Before environment residualization, an environment is usable for Primary B only if it contains:

- >=2 Primary-B-valid trajectories;
- from >=2 distinct bat identities.

An environment failing this purely structural condition is excluded from Primary B for that species before any identity statistic is calculated.

Candidate-bat >=3-environment support and leave-one-environment-out centroid support are then evaluated using only these usable environments.

For every usable environment, sample SD is evaluated for all eight frozen features. Feature dropping follows the parent rule:
if a feature has zero or non-finite SD in **any usable environment**, that feature is dropped for the entire species.

If fewer than six features remain, STOP Primary B for that species.

## Claim boundary

This clarification does not restore temporal order. The programme remains configuration-conditioned, not a relearning/reset-time analysis.
