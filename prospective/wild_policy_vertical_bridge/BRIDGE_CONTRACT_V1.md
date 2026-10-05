# Wild low-dimensional policy -> vertical fingerprint bridge contract v1

## Status

**PROSPECTIVE POST-FREEZE MECHANISM BRIDGE.**

Branch:
`prospective/wild-policy-vertical-bridge-v1`

This programme is outside JAE v0.4.0 and cannot alter the frozen submission.

## Biological question

JAE v0.4.0 shows that centered vertical individuality persists without persistent 3-D spatial partitioning and survives matching on 2-km horizontal place plus broad speed×turn state in four structurally evaluable panels.

The obstacle-flight programme independently identifies a low-dimensional personal movement policy, with a strongly portable intensity-like axis and a second maneuver-structure axis.

The unresolved bridge is:

> **Do individuals with more different movement policies also show more different held-out vertical fingerprints even when compared within the same fine place × broad kinematic context?**

## Panels

Exactly:
- `hypsignathus`
- `phyllostomus_2022`
- `phyllostomus_2023`
- `phyllostomus_2016`

No inference to *Eidolon helvum*.

## Cross-fit split

For each individual independently:

1. order retained sessions by session start time;
2. assign session indices 1,3,5,... to fold A;
3. assign session indices 2,4,6,... to fold B.

Two reciprocal analyses are fixed:

- A-policy -> B-vertical;
- B-policy -> A-vertical.

No session contributes to both predictor and vertical target within a fold.

## Horizontal-only policy predictor

The confirmatory bridge predictor uses **no altitude-derived feature**.

For each retained policy-side session derive:

1. median horizontal speed;
2. p90 horizontal speed;
3. median absolute horizontal turning rate;
4. p90 absolute horizontal turning rate;
5. horizontal path efficiency = net horizontal displacement / total horizontal path length.

Consecutive intervals must be:
- finite;
- >0 s;
- <=1800 s.

Turning-rate definition follows the obstacle-flight implementation:
- heading from consecutive horizontal displacement vectors;
- wrapped absolute heading difference;
- divisor = mean duration of the two adjacent movement intervals.

A policy-side session is valid only if:
- >=30 valid speed intervals;
- >=20 valid turning-rate values;
- positive total horizontal path length.

## Training-only standardization

Within each panel × reciprocal fold:

- pool valid policy-side sessions from all structurally eligible individuals;
- z-score each of the five session features using only that policy-side pool.

No held-out vertical session enters standardization.

## Transparent policy axes

### HorizontalIntensity H

`H = mean(z_median_speed, z_p90_speed)`.

### HorizontalManeuver M

`M = mean(-z_median_speed, z_median_turn_rate, z_p90_turn_rate, z_path_efficiency)`.

This is the altitude-free analogue of the externally supported FlightIntensity / ManeuverStructure architecture.

For each individual:
- average session H equally across valid policy-side sessions;
- average session M equally across valid policy-side sessions.

Policy distance for pair (i,j):

`D_policy(i,j) = sqrt((H_i-H_j)^2 + (M_i-M_j)^2)`.

No axis weights are fit from vertical outcomes.

## Held-out vertical fingerprint

Use only held-out sessions.

Reuse the frozen four-panel nuisance context:
- 2-km horizontal cells;
- cohort-level speed median split;
- cohort-level turn median split;
- four speed×turn states;
- centered vertical residual = height - retained-session median height;
- vertical bins:
  `(-inf,-400,-200,-100,-50,0,50,100,200,400,inf)`.

For each individual and each 2-km cell × broad state stratum:
- pool held-out target events across held-out sessions;
- construct the centered vertical histogram;
- normalize to a probability vector.

A pairwise stratum is usable only if each member has >=10 held-out events in that stratum.

For pair (i,j), require >=3 jointly usable strata.

Within each usable stratum compute Hellinger distance:

`D_H(p,q) = sqrt(1 - sum_k sqrt(p_k q_k))`.

Pairwise held-out vertical divergence:

`D_vertical(i,j) = equal-stratum mean D_H`.

No pseudocount.

## Panel statistic

Within each reciprocal fold:

- include every pair with valid policy coordinates and valid held-out vertical divergence;
- require >=15 eligible pairs;
- calculate Spearman correlation
  `rho_fold = cor_rank(D_policy, D_vertical)`.

Panel statistic:

`R = mean(rho_A_to_B, rho_B_to_A)`.

The observed panel opens only if both reciprocal folds satisfy the pair floor.

## Null

Within a panel, permute complete individual policy labels relative to vertical fingerprints.

Use the **same individual permutation in both reciprocal folds**.

Preserve:
- all policy coordinates;
- all held-out vertical histograms;
- all pair-support structure;
- reciprocal fold structure.

9,999 permutations.

Panel seeds:
- Hypsignathus: `202610051101`
- P. hastatus 2022: `202610051102`
- P. hastatus 2023: `202610051103`
- P. hastatus 2016: `202610051104`

One-sided p:
`(1 + #null R >= observed R)/(1 + n_valid)`.

Require >=9,500 valid permutations.

## Panel support rule

A panel supports the bridge only if:

- `rho_A_to_B > 0`;
- `rho_B_to_A > 0`;
- `R > 0`;
- permutation p <= 0.05.

No pooling may rescue a failed panel.

## Cross-panel synthesis

- 3–4 PASS: strong evidence that a low-dimensional horizontal movement policy is linked to wild vertical individuality beyond 2-km place × broad movement state.
- 1–2 PASS: context-dependent bridge.
- 0 PASS: the lab/external low-dimensional policy architecture does not explain the JAE vertical fingerprint under this strict altitude-free bridge.

## Secondary component diagnostics

Only if the primary outcome is opened, report with separate permutations:

- H distance alone: `|H_i-H_j|`;
- M distance alone: `|M_i-M_j|`.

These are diagnostic components and cannot rescue a failed 2-D primary.

## Claim ceiling

A positive result supports:

> individuals that differ more in an independently defined low-dimensional horizontal movement policy also differ more in held-out vertical organization within the same fine-place × broad-kinematic contexts.

It does not prove:
- that H/M causally generate vertical individuality;
- learned versus innate origin;
- morphology;
- a universal two-axis law;
- that exact lab and wild axes are numerically identical.

## Stop rules

After vertical bridge outcome opening:
- no grid changes;
- no state-threshold changes;
- no session reallocation;
- no pair-floor changes;
- no alternative distance metric;
- no selected individuals;
- no selected strata;
- no panel pooling rescue;
- no use of altitude-derived policy features to rescue the horizontal-only primary.

## JAE firewall

JAE v0.4.0 remains unchanged regardless of outcome.
