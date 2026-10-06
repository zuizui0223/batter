# Auditory perturbation acoustic-policy primary v1

## Status

**FROZEN BEFORE ACOUSTIC OUTCOME VALUES ARE OPENED.**

Source:
Diebold et al. 2024, Zenodo `10.5281/zenodo.13857870`.

## Question

After removing the shared Saline-versus-Ligand shift, does individual identity still predict multivariate acoustic organization across the reversible auditory perturbation?

## Individuals

Exactly:
- jane
- bea
- jason
- stella

## Conditions

Exactly:
- Saline = source treatment 1
- Ligand = source treatment 2
- source restriction: `trialtype < 4`

## Frozen trial features

For every eligible trial:

1. mean call duration;
2. mean call bandwidth;
3. mean inter-pulse interval = mean(diff(call onset));
4. call rate = number of calls / source adjusted trial length.

No feature addition, deletion, PCA, or fitted weights.

Each bat must have >=5 valid trials in each condition or the primary stops.

## Shared-context residualization and scaling

For each feature separately:

1. pool all valid trials from all four bats;
2. within each observed `treatment × trialtype` cell, calculate the pooled feature mean **without using bat identity**;
3. subtract that shared cell mean from every trial in that cell;
4. pool the resulting residuals across saline and ligand;
5. calculate one common sample SD (ddof=1);
6. require that SD to be finite and >0;
7. divide all residuals by that one common SD.

Thus the primary removes:
- the shared saline-versus-ligand mean shift;
- shared source trial-class mean shifts.

It deliberately does **not** remove:
- treatment-specific variance changes;
- individual offsets;
- individual × treatment effects.

No bat label enters centering or scaling.

## Bat centroids

For each bat and condition, average the four standardized trial features equally across valid trials.

This yields one 4-D Saline centroid and one 4-D Ligand centroid per bat.

## Primary statistic

For each Ligand bat i:

- self distance = Euclidean distance to its own Saline centroid;
- other distance = mean Euclidean distance to the other three Saline centroids;
- K_i = other distance - self distance.

Programme statistic:

`K = mean(K_i)`.

Positive K means Ligand expression remains closer to the same bat's Saline organization than to other bats.

## Exact null

Permute the mapping between the four Ligand identities and the four Saline identities.

Enumerate all `4! = 24` mappings.

One-sided exact p:
fraction of permuted K values >= observed K.

Minimum possible p:
`1/24 = 0.0416667`.

## Support

Confirmatory support requires:
- K > 0;
- exact p <= 0.05.

Report all K_i and all 24 null values.

## Boundaries

- sham n=2 is descriptive only;
- deposited trajectory layer has only three DREADD animals and cannot support a confirmatory identity permutation;
- no Baseline inclusion;
- no feature switching;
- no bat removal;
- no trial-level pseudoreplication;
- no trajectory/audio combination after outcome opening.

## Allowed conclusion if supported

A reversible auditory-processing perturbation changes expressed behavior while preserving a detectable individual-specific multivariate acoustic organization across the perturbation.

It does not identify where that organization is stored, whether it is learned or intrinsic, or whether it is the same carrier as Rhino I/M or wild vertical individuality.


## Structural opening receipt

The outcome-blind structural audit completed before numerical opening.

Frozen receipt:
- jane: Saline 37 / Ligand 25 source-eligible trials;
- bea: Saline 41 / Ligand 47;
- jason: Saline 36 / Ligand 36;
- stella: Saline 30 / Ligand 8;
- all four required acoustic fields present.

Verdict:

**PASS_OPEN_NUMERIC_PRIMARY**

This receipt changes no endpoint, scaling, statistic, support threshold, null, or claim boundary.
