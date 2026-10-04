# Primary B environment-standardization amendment v1

## Status

**FROZEN BEFORE ANY CSV TRAJECTORY ROW VALUE IS OPENED.**

Parent:
`CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md`

Structural preflight showed that some species × environment cells contain only one trajectory. The parent rule requiring a sample SD separately within every environment would therefore make all features undefined in those cells and could eliminate the entire species for a purely arithmetic reason.

No coordinate or kinematic value has been opened.

## Revised configuration removal

For each species and each predeclared feature k:

1. compute the mean feature value separately within every environment:
   `mu_{e,k}`;
2. subtract that environment mean from every trajectory:
   `r_{q,k} = x_{q,k} - mu_{e(q),k}`;
3. pool all environment-centered residuals for the species;
4. compute one sample SD:
   `s_k = sd(r_{.,k})`;
5. standardized residual:
   `z_{q,k} = r_{q,k} / s_k`.

Thus environment-specific means are removed exactly, while scale is estimated from the species-wide residual variation.

## Singleton environments

If an environment contains one valid trajectory:
- its centered residual is exactly zero for every feature;
- it contributes no within-environment identity contrast by itself;
- it may still serve as a target/training environment in the cross-configuration calculation under the frozen leave-one-environment-out rules.

No special imputation is introduced.

## Feature support

If pooled residual SD `s_k` is zero or nonfinite:
- drop feature k for the entire species.

Primary B opens only if >=6 of the original 8 features remain.

## No other change

All other Primary B rules remain unchanged, including:
- 8 predeclared features;
- leave-one-environment-out own and other centroids;
- >=3 environments for focal bats;
- >=3 candidate centroids per target;
- independently within-environment identity permutation null from `PRIMARY_B_NULL_AMENDMENT_V1.md`;
- 9,999 permutations;
- one-sided p;
- >=70% positive individual means.
