# Individual-specific vertical strategies in European free-tailed bats

## Scientific question

Do individual *Tadarida teniotis* bats retain temporally repeatable, location-conditioned vertical-use patterns that are not transferable among individuals?

## Starting observation

The preceding ODSP analysis established two facts under a frozen 5-km x-y grid and fixed MSL-altitude bins:

1. species-level vertical support was descriptively thick: 4.022 effective vertical states;
2. the pooled species-level `P(z|x,y)` failed to improve prediction for either sealed bat relative to the pooled marginal `P(z)`.

That endpoint remains negative for species-level transfer.

The present follow-up asks why.

## Prospective follow-up design

All eight tracked bats were retained. The 18 horizontal cells and vertical bins were inherited unchanged from the original frozen ODSP endpoint.

Within each bat, eligible observations were divided chronologically into early and late halves.

Early data were used to construct:

- a species-level cell-specific vertical distribution;
- an individual-specific cell distribution shrunk toward that species distribution;
- a species marginal vertical distribution;
- an individual marginal vertical distribution.

Each early individual map was then scored on every bat's late observations, giving a complete 8 × 8 source-to-target transfer matrix.

The primary statistic was the equal-individual mean of the identity-matched diagonal gains relative to the species-level cell-specific baseline. Its null distribution was obtained from all 8! = 40,320 assignments of early individual maps to late individual identities.

## Result

The identity-matched diagonal mean gain was **+0.1682 nats per late event**.

Across all 40,320 permutations:

- null mean = -0.0367;
- null 5th–95th percentile = -0.1566 to +0.0707;
- one-sided exact permutation **P = 0.000174**.

Thus an individual's own earlier vertical map predicted its later vertical state much better than expected if individual identity were exchangeable.

At the individual level:

- 6/8 bats had positive own-map advantage over the species-level cell-specific map;
- 5/8 had positive own location-conditioned map versus own marginal altitude distribution;
- 5/8 had their own early map as the strict best of all eight candidate individual maps.

The preregistered terminal category was therefore:

**individual_specific_spatial_vertical_strategy**.

## Why this changes the ecological interpretation

The original non-transfer result is not well described as an absence of vertical organization.

Instead, the combined evidence now supports a hierarchical interpretation:

- the species occupies a vertically thick state space;
- vertical organization is not represented well by one species-average x-y-conditioned map;
- individual identity carries temporally persistent predictive information;
- for a majority of individuals under the primary rule, that information includes location-conditioned vertical structure rather than only a different overall altitude distribution.

This is consistent with individual specialization in vertical space use.

## What it does not show

The altitude variable is GPS height above mean sea level, not height above ground. Horizontal cell conditioning helps prevent simple home-range location differences from being mistaken for a common species-level vertical map, but it does not convert MSL altitude into canopy-relative or terrain-relative flight height.

The analysis also does not identify why individuals differ. Sex, reproductive state, colony membership, prey fields, weather, terrain, energetic state and learned route use remain possible explanations.

## Sensitivity

The identity-permutation result was robust to the two frozen shrinkage sensitivities:

- λ=5: diagonal +0.1297, P=0.000942, 6/8 positive total identity gains;
- λ=50: diagonal +0.1576, P=0.000149, 7/8 positive total identity gains.

The finer decomposition into conditional-versus-marginal spatial organization was more sensitive (4/8 positive under both λ=5 and λ=50), so the strongest robust claim is **individual-specific vertical-state prediction**, with the primary λ=20 analysis additionally meeting the prespecified spatial-strategy rule.

## Paper direction

Working ecological claim:

> A species-level vertical niche can be thick yet fail cross-individual transfer because vertical-state organization is partly individualized.

This turns the previous negative transfer result into a biological question about individual specialization rather than a method failure.
