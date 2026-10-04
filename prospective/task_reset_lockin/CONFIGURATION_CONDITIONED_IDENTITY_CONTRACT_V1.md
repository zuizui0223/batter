# Configuration-conditioned individual flight organization contract v1

## Status

**PROSPECTIVE OUTCOME CONTRACT — frozen before any CSV trajectory row value is opened.**

Branch:
`prospective/task-reset-lockin-v1`

Source:
Teshima et al. 2026, Proc. R. Soc. B, DOI `10.1098/rspb.2026.1463`.

Species/file mapping:
`SPECIES_CSV_MAPPING_PROVENANCE_V1.md`.

## Why this programme is configuration-conditioned, not a temporal reset test

The public CSV archive identifies:
- species through the frozen 4-vs-5-individual batch mapping;
- obstacle environment `Env1...Env7`;
- individual bat letter;
- trial token `no#`.

It does not provide source-validated order of environment exposure.

Therefore no claim about:
- before/after reset;
- relearning time;
- collapse and rebuilding after a known switch

is permitted.

The estimand is instead:

> **how much of individual flight organization is tied to a particular obstacle configuration, and how much transfers across configurations?**

---

# Primary A — within-configuration literal-route identity

## Biological question

Under the same obstacle configuration, are repeated 3-D trajectories from the same bat more similar than trajectories from other conspecifics?

This is the most direct test of a personal realized route solution.

## Structurally eligible environment

Within one species × environment:

- >=3 bat identities;
- each of those bats has >=2 structurally valid trajectories;
- each valid trajectory has >=100 finite time/x/y/z rows;
- each has positive duration and positive path length.

A species enters Primary A only if it has >=2 eligible environments.

No threshold relaxation after coordinate opening.

## Trajectory standardization

For each file:

1. retain rows with finite time, X, Y, Z;
2. sort by time;
3. collapse duplicate time stamps by retaining the first row;
4. require >=100 rows;
5. parameterize the trajectory by cumulative 3-D arc length;
6. linearly interpolate X, Y, Z onto **101 equally spaced normalized arc-length positions** from 0 to 1.

No smoothing and no obstacle-dependent trimming.

Coordinates remain in the source arena frame.

## Pairwise route distance

For standardized trajectories a and b:

`d_route(a,b) = mean_s ||r_a(s)-r_b(s)||_2`

over the 101 normalized arc-length positions.

## Target-level individual advantage

For target trajectory q of bat i in environment e:

- `D_self`: mean distance to all other valid trajectories from bat i in environment e;
- `D_other`: first average distances within each other bat j in environment e, then average donor bats equally.

`A_q = D_other - D_self`.

Positive A means the held-out route is closer to the focal bat's own repeated route than to other bats' routes under the same obstacle geometry.

Aggregation:
- equal target trajectory within bat × environment;
- equal bat within environment;
- equal environment within species.

Species statistic:
`A_species`.

## Null for Primary A

Within each species × environment independently:

- permute bat identities among complete trajectories;
- preserve each environment's observed number of trajectories per bat;
- recompute the full statistic.

Permutations:
**9,999**

Seed:
`202610042201`.

One-sided p:
`p_A = (1 + #null >= observed)/(10000)`.

Support requires:
- A_species > 0;
- p_A <= 0.05;
- positive bat-level mean A in >=70% of evaluable bats.

Analyse species separately. No cross-species pooling rescue.

---

# Primary B — cross-configuration transfer of individual movement policy

## Biological question

Once absolute obstacle configuration effects are removed, do individual-specific kinematic signatures transfer across environments?

This distinguishes a task-local route solution from a more stable individual policy/performance constraint.

## Trajectory feature vector

From each structurally valid trajectory, using finite time/X/Y/Z only:

1. median 3-D speed;
2. 90th percentile 3-D speed;
3. median absolute vertical speed;
4. 90th percentile absolute vertical speed;
5. median absolute horizontal turning rate;
6. 90th percentile absolute horizontal turning rate;
7. path efficiency = net 3-D displacement / total 3-D path length;
8. vertical range = max(Z)-min(Z).

Derivatives use consecutive source rows after chronological sorting.
Require positive time increments; non-positive intervals are omitted from derivative calculations.

If fewer than 50 valid derivative intervals remain, the trajectory is invalid for Primary B.

## Environment residualization

Within each species × environment × feature:

- compute mean and sample SD across all structurally valid trajectories;
- z-score the feature within that environment.

If SD is zero/nonfinite, drop that feature **for the entire species**, before identity outcome calculation.

Primary B opens only if >=6 of 8 features remain.

No feature may be selected based on identity performance.

## Leave-one-environment-out identity advantage

For target trajectory q from bat i in environment e:

For every bat j, construct a centroid from j's trajectories in **all environments other than e**.

Require:
- focal bat i has data in >=3 environments total;
- >=3 candidate bat centroids exist;
- every centroid uses >=2 other environments.

Distance:
Euclidean distance in the retained environment-residualized feature space.

`K_q = mean(distance(q, other-bat centroids)) - distance(q, own-bat centroid)`.

Positive K means configuration-invariant movement features identify the bat across environments.

Species statistic:
equal-target -> equal-bat mean `K_species`.

## Null for Primary B

Within species, permute bat identity as complete cross-environment labels while preserving environment membership and per-environment trial structure.

9,999 permutations.

Seed:
`202610042202`.

One-sided p_B.

Support requires:
- K_species > 0;
- p_B <= 0.05;
- positive individual mean K in >=70% of evaluable bats.

---

# Interpretation matrix

## A supported, B supported

> Individual flight organization includes both configuration-specific realized routes and a transferable individual movement-policy/performance signature.

This weakens a purely task-local-history explanation. Stable biomechanics, sensorimotor style or long-lived individual policy remain important candidates.

## A supported, B unsupported

> Individual routes are repeatable within a configuration but individual kinematic identity does not transfer reliably across configurations.

This is the pattern most compatible with **task-specific personal solution lock-in** rather than a single immutable personal flight style.

It does not prove learning because environment order is unavailable.

## A unsupported, B supported

> Literal route reuse is weak, but stable individual movement style transfers across configurations.

This favors stable performance/policy over route lock-in.

## Neither supported

This source does not support individual-level organization beyond the already-published species-level regularities.

---

# Descriptive configuration dependence

If Primary A opens, also report without additional inference:

- within-bat same-environment route distance;
- within-bat different-environment route distance.

Different-environment distances are descriptive because obstacle geometries differ by design.

Do not call their difference a temporal reset effect.

---

# Stop rules

After coordinate outcome opening, no:
- DTW/Fréchet/Hausdorff rescue;
- alternate interpolation length;
- alternate feature set;
- selected environments;
- selected individuals;
- one-sided-to-two-sided switching;
- threshold relaxation;
- species pooling;
- reinterpretation of `no#` as global chronology.

# JAE firewall

No result from this programme modifies JAE v0.4.0.
