# Rhino configuration alpha — authoritative result v1

## Execution

- workflow run: **37626439002**
- head SHA: `549008de0f76c4122c6e21f867da960030c4bac4`
- conclusion: **success**
- artifact: **11483479893**

## Per-environment expression

Using theta estimated only from other environments:

| environment | n bats | alpha | Pearson r |
|---:|---:|---:|---:|
| 1 | 4 | 0.772 | 0.519 |
| 2 | 4 | 1.997 | 0.924 |
| 3 | 4 | 0.931 | 0.818 |
| 4 | 5 | 1.014 | 0.750 |
| 5 | 3 | 0.997 | 1.000 |
| 6 | 3 | 0.928 | 0.889 |

All **6/6** structurally evaluable environments have positive alpha.

Summary:
- mean alpha = 1.107
- median alpha = 0.964
- positive environments = 6/6

## Null calibration

Within-environment bat-label permutations, B=9,999.

Mean-alpha statistic:
- null mean = 0.002
- p = **0.114**

Positive-environment count:
- null mean = 2.98 / 6
- observed = 6 / 6
- p = **0.0364**

## Interpretation

The directional result is supported:

> a scalar individual coordinate estimated from other obstacle configurations tends to be expressed in the same direction in every evaluable held-out configuration.

The magnitude of the gain is not separately calibrated strongly enough to claim a common alpha near one.

Thus the current model is compatible with

[
y_{ie}=mu_e+alpha_e	heta_i+epsilon_{ie},
qquad alpha_e>0
]

for ordinary obstacle-configuration changes, while alpha magnitude can vary.

This strengthens the distinction between:
- stable portable personal coordinate theta;
- context-dependent expression gain alpha.
