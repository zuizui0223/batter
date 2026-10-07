# Rhino residual-policy dimensionality contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- full 8-D cross-configuration policy identity was supported;
- training-only PCA d=1 was sufficient;
- training-only supervised identity-subspace d=1 was sufficient;
- cumulative d=2 identity statistics were already known to exceed d=1 descriptively.

No residual-after-axis1 identity statistic has been calculated before this contract.

## Question

Does the dominant one-dimensional personal axis contain essentially all portable individual information, or do additional independent stable dimensions remain after axis 1 is removed?

"Sufficient" and "complete" are different:
- d=1 sufficient means one dimension can identify individuals in held-out environments;
- d=1 complete would additionally require little/no calibrated identity in the orthogonal residual subspace.

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories, seven environments, and eight Primary-B movement features.

Use the exact within-environment standardization and leave-one-environment-out folds from `LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md`.

## R1 — unsupervised PCA residual subspaces

For each held-out environment:
- fit PCA on training environments only;
- project training and target trajectories;
- discard PC1 entirely.

Evaluate the following residual coordinate sets:
- PC2 alone;
- PCs2–3;
- PCs2–4;
- PCs2–5;
- PCs2–6;
- PCs2–7;
- PCs2–8.

Use the exact Primary-B identity statistic on each selected coordinate set.

## R2 — supervised identity residual subspaces

For each held-out environment:
- construct the training-only supervised identity SVD exactly as in the prior dimensionality analysis;
- discard identity axis 1.

Evaluate:
- identity axis 2 alone;
- axes 2–3;
- axes 2–4.

The supervised basis must be recomputed under every label permutation.

## Null

Within each environment independently permute complete bat × environment labels, preserving clusters.

Permutations:
9,999 per residual set.

Seeds:
- R1 residual PCA ending at dimension d: `20261008000+d`;
- R2 residual identity ending at dimension d: `20261008020+d`.

Require >=9,500 valid permutations.

A residual set is supported if:
- K > 0;
- one-sided p <= .05;
- >=70% evaluable bats have positive K.

## Interpretation

### No residual set supported

The dominant axis is not only sufficient but approximately exhaustive for the measured portable individual signal.

### Residual identity supported

The individual policy is still finite/low-dimensional, but not reducible to one scalar. The proper representation is a vector theta_i with dimension at least 2.

The smallest supported residual set does not by itself define the total intrinsic dimension; it only proves additional stable information beyond axis 1.

## Ceiling

This diagnostic concerns linear portable identity in eight measured policy summaries. It does not establish nonlinear intrinsic dimension or exact trajectory dynamics.
