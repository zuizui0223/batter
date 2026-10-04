# Cross-species target standardization amendment v1

## Status

**FROZEN BEFORE G1/G2 CROSS-SPECIES AXIS OUTCOMES ARE CALCULATED.**

Parent:
`CROSS_SPECIES_POLICY_AXIS_CONTRACT_V1.md`

## Structural issue

The 19 *Miniopterus fuliginosus* trajectories are distributed across environments with several singleton environment cells.

Therefore an environment-specific sample SD is not defined for every target environment.

## Frozen target-species rule

Use exactly the Miniopterus-compatible configuration-removal rule already frozen before the generic Primary-B outcome in:
`PRIMARY_B_STANDARDIZATION_AMENDMENT_V1.md`.

For each of the eight features:

1. subtract the arithmetic mean of that feature within each Miniopterus environment;
2. pool all environment-centered residuals across the species;
3. compute one species-wide residual sample SD per feature;
4. divide every environment-centered residual by that pooled SD.

A singleton environment therefore has residual zero for every feature and contributes no within-environment variation by itself, but remains a valid held-out/training context where identity support rules permit.

## Source Rhino PCA axis

The fixed Rhino PC1 remains fit exactly as stated in the parent contract:
- Rhino features standardized within Rhino environment;
- ordinary PCA on Rhino only;
- PC1 oriented so the sum of the first four speed/vertical-speed loadings is positive.

No Miniopterus value affects that vector.

## No other change

G1/G2 estimators, identity cluster permutations, support criterion, environments and individuals are unchanged.