# Masker-strength expression diagnostic v1

## Status

**POST-PRIMARY DIAGNOSTIC MOTIVATED AFTER P1 OUTCOME OPENING. NOT CONFIRMATORY.**

Parent:
`PERSONAL_BIAS_RETENTION_RESULT_V1.md`

The frozen P1 already established that baseline 3-D angle bias remains identity-bearing across both styrofoam-masker conditions.

Observed P1 components:
- 30 cm masker: K = +8.00448 deg;
- 10 cm masker: K = +1.87833 deg.

Because this contrast was visible only after P1 was opened, the present analysis is explicitly exploratory/mechanistic and cannot strengthen the formal P1 error rate.

## Question

Within the same six bats and the same styrofoam target:

> is baseline individual ordering expressed less strongly at 10 cm than at 30 cm masker distance?

The source design identifies 10 cm as the stronger masking condition.

## D1 — identity-retention attenuation

Use exactly the centered baseline predictor and centered 30/10 cm target values already opened by P1.

For each masker condition compute the same mean self-vs-other identity advantage K.

Define:

[
D_K = K_{30} - K_{10}.
]

Positive means baseline identity is expressed more strongly at 30 cm than 10 cm.

## D2 — linear expression-gain diagnostic

For centered baseline bias theta and centered condition value y_c define the no-intercept least-squares gain:

[
alpha_c = rac{	heta^T y_c}{	heta^T	heta}.
]

Define:

[
D_alpha = alpha_{30}-alpha_{10}.
]

This is a descriptive expression-gain diagnostic, not a fitted reaction norm.

## Exact calibration

Enumerate all 6! = 720 permutations of baseline-bias labels.

For each permutation recompute:
- K_30;
- K_10;
- D_K;
- alpha_30;
- alpha_10;
- D_alpha.

Report exact one-sided tail fractions for positive observed D_K and D_alpha.

No binary confirmatory verdict is assigned.

## Additional descriptive quantities

Report:
- SD of centered baseline, 30 cm and 10 cm bat means;
- SD ratios relative to baseline;
- Pearson correlations already used in P1;
- condition-specific no-refit R2 under the unscaled baseline predictor.

## Interpretation ceiling

A positive calibrated contrast is compatible with:

> expression of the persistent personal movement bias is context-dependent and is attenuated in the 10-cm masker condition relative to the 30-cm condition.

Do not claim:
- a universal harder-task -> weaker-individuality law;
- loss of stored individual state;
- a causal neural gain parameter;
- that masker distance is the only relevant contextual difference.

The foam-target P2 result is an important boundary: strong identity retention can also occur under another acoustically difficult condition. Therefore any attenuation is context-specific, not a monotonic law of task difficulty.
