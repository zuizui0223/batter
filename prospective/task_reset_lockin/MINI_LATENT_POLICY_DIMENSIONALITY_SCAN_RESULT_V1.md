# Miniopterus latent-policy dimensionality scan — authoritative result v1

## Execution

- workflow run: **37625879870**
- head SHA: `2497d17b09dd6e97143f3f2f595129fab808234d`
- conclusion: **success**
- artifact: **11483569925**
- artifact zip SHA256: `d7aedf82eb818a8304041886a00ae9c26468c1cd653e52e68ca3e1d719e49513`

## D1 — unsupervised training-only PCA

No dimension 1–8 satisfies the frozen support rule.

| d | K | positive bats | p |
|---:|---:|---:|---:|
| 1 | -0.1688 | 2/4 | 0.2736 |
| 2 | -0.0032 | 2/4 | 0.2698 |
| 3 | +0.0121 | 3/4 | 0.2830 |
| 4 | +0.0220 | 3/4 | 0.2434 |
| 5 | +0.0130 | 3/4 | 0.2456 |
| 6 | +0.0050 | 3/4 | 0.2416 |
| 7 | -0.0027 | 2/4 | 0.2577 |
| 8 | -0.0136 | 2/4 | 0.2339 |

PC1 alone explains a median **58.8%** of training behavioural variance, rising to 87.8% by d=3 and 97.1% by d=4.

Thus high variance compression does not produce stable cross-environment individual identity.

## D2 — training-only supervised identity subspace

Even an axis explicitly fitted to between-individual training centroids fails in held-out environments.

| d | K | positive bats | p |
|---:|---:|---:|---:|
| 1 | +0.0195 | 2/4 | 0.2921 |
| 2 | +0.0222 | 3/4 | 0.2463 |
| 3 | -0.0103 | 3/4 | 0.2319 |

Minimal sufficient dimension:
**none**.

## Interpretation

The missing 2–7 dimensional gap is closed.

Under the current 19-trajectory archive, Miniopterus does not show calibrated evidence for a portable **linear** individual policy at any available dimensionality.

This is qualitatively different from *Rhinolophus nippon*, where one dimension is already sufficient.

The contrast is not:

[
Rhinolophus = low-dimensional,quad Miniopterus = high-dimensional.
]

It is currently:

[
Rhinolophus = stable low-dimensional personal component,
]

[
Miniopterus = no detected stable cross-environment linear personal component.
]

That can arise from stronger context dependence / plasticity, weaker individual repeatability, nonlinear structure, or limited data. It is not evidence of infinite mathematical dimensionality.

## Important variance-versus-identity distinction

Miniopterus PC1 explains ~59% of behavioural variance but carries no stable individual identity.

Therefore:

> low-dimensional behaviour does not imply low-dimensional individuality.

The mathematical object of interest is the dimension of the **persistent between-individual component**, not the intrinsic dimension of all observed movement variation.
