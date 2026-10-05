# PC1 axis-stability and transparent-axis alignment contract v1

## Status

**POST-PRIMARY INTERPRETABILITY DIAGNOSTIC.**

Frozen after:
- one-dimensional leave-one-environment-out PCA identity was sufficient;
- transparent FlightIntensity was supported;
- scalar-plus-noise law was supported.

No foldwise PC1 alignment statistic has yet been calculated.

## Question

Is the one-dimensional policy axis itself stable across obstacle configurations, and is it close to the transparent FlightIntensity direction?

## Data

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories and the eight Primary-B environment-standardized movement features.

## Foldwise PC1

For each held-out environment e:

1. fit ordinary PCA to all trajectory-level standardized feature vectors from the other six environments;
2. retain PC1 loading vector `lambda_-e`;
3. orient its sign so that the sum of the first four loadings
   (median/p90 speed and median/p90 absolute vertical speed)
   is positive.

No target-environment data enter the loading fit.

## A1 — loading-vector stability

Across the seven oriented fold PC1 vectors report:

- all 21 pairwise cosine similarities;
- minimum pairwise cosine;
- median pairwise cosine;
- mean pairwise cosine.

A value near 1 means the same one-dimensional direction is recovered when any one obstacle configuration is omitted.

## A2 — alignment with transparent FlightIntensity

Define the normalized transparent vector:

`v_FI = (1,1,1,1,0,0,0,0)/2`.

For every fold report:

`cos(lambda_-e, v_FI)`.

Report min/median/max.

## A3 — loading dispersion

For each of the eight original features report:
- median oriented loading;
- minimum;
- maximum;
- SD across folds.

## Interpretation

High foldwise cosine plus high FlightIntensity alignment supports:

> the low-dimensional individual policy is not an arbitrary PCA embedding; it is a stable direction dominated by speed and absolute vertical-speed magnitude.

Lower alignment would imply that the transparent scalar is only a partial proxy.

## Ceiling

This is an observed interpretability diagnostic. It has no new inferential p-value and cannot establish causal origin of the axis.
