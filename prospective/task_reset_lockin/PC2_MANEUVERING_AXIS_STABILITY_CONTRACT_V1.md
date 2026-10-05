# PC2 maneuvering-axis stability contract v1

## Status

**POST-PRIMARY INTERPRETABILITY DIAGNOSTIC.**

Frozen after:
- PC1 was shown to be a highly stable flight-intensity axis;
- PC1 removal left significant cross-configuration individual identity;
- removal of PC1+PC2 eliminated calibrated residual identity;
- PC2 squared loadings were observed to concentrate on turning-rate, path-efficiency and vertical-range features.

No signed PC2 stability result has yet been calculated.

## Question

Is PC2 itself a stable cross-environment direction, and what signed combination of measured movement features does it represent?

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories and the eight Primary-B environment-standardized features:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

## Foldwise PC2

For each held-out environment e:

1. fit ordinary PCA to all standardized trajectory vectors from the other six environments;
2. retain PC2 loading vector;
3. orient its sign so that the loading on **median absolute horizontal turning rate** is positive.

The target environment is not used to fit or orient the axis.

## M1 — foldwise axis stability

Across the seven oriented PC2 vectors report:
- all 21 pairwise cosine similarities;
- minimum;
- median;
- mean.

## M2 — signed loading summary

For every original feature report across folds:
- median loading;
- minimum;
- maximum;
- SD.

Also report median squared loading for reference.

## M3 — orthogonality to FlightIntensity

For each fold compute cosine with:

`v_FI = (1,1,1,1,0,0,0,0)/2`.

Report min/median/max absolute cosine.

This is a diagnostic that the second axis is distinct from overall flight intensity.

## Interpretation

A stable PC2 with:
- positive turn-rate loadings,
- substantial path-efficiency and/or vertical-range loading,
- weak speed loading,

supports a second **maneuvering / route-organization** policy axis.

The exact descriptive name will be chosen only after seeing the signed loading pattern.

## Ceiling

This diagnostic does not establish a causal motor variable and does not test a new population hypothesis.
