# Mini-Rhino scalar-support power diagnostic v1

## Status

POST-PRIMARY POWER DIAGNOSTIC. Frozen before this scalar matched-support outcome is opened.

## Question

Can the exact 12 occupied Mini bat×environment cells detect the already-established Rhino one-parameter FlightIntensity signal?

## Common preprocessing

For each species:
1. calculate the same eight movement features;
2. subtract each environment feature mean;
3. divide by species-wide pooled environment-centered SD;
4. define FlightIntensity as the mean of the first four standardized speed / vertical-speed features;
5. collapse each occupied bat×environment cell to one scalar centroid.

## Mini endpoint

Use the 12 source-native Mini occupied cells.

For each held-out environment:
- own predictor = equal-environment mean of the same bat's other occupied cells, require >=2;
- donor predictors = equal-environment means of other eligible bats;
- target advantage = mean absolute distance to donors minus absolute distance to own predictor.

Aggregate equal target cell -> equal bat.

Calibrate with 9,999 within-environment label permutations.
Seed 20261008101.
Support: K>0, p<=.05, >=3/4 positive bats, >=9,500 valid permutations.

## Rhino matched-support positive control

Use all 4,212 feasible bat/environment mappings from the frozen centroid-support preflight.

For each mapping, relabel the 12 mapped Rhino scalar centroids back into the Mini support pattern and compute observed K.

Select the same deterministic 256 mapping indices as the PCA power programme.

For each selected mapping:
- 1,999 within-environment label permutations;
- seed 20261008200 + mapping rank;
- detection requires K>0, p<=.05, >=3/4 positive, >=1,900 valid permutations.

Primary quantity:
fraction of 256 Rhino mappings detected.

Interpretation:
- >=0.80: Mini support adequate for a Rhino-like scalar theta;
- <0.50: power-limited;
- otherwise ambiguous.

This asks about detectability of a Rhino-like effect, not the true Mini effect size.
