# Masker-strength expression diagnostic result v1

## Status

**POST-PRIMARY EXPLORATORY DIAGNOSTIC.**

Authoritative workflow:
- run: **37390826159**
- job: **112035220929**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`MASKER_STRENGTH_EXPRESSION_DIAGNOSTIC_V1.md`

This contrast was motivated after the frozen personal-bias primary had already been opened.
It is therefore not confirmatory and does not alter the P1 error rate.

## Question

Within the same six bats and the same styrofoam target, is the pre-perturbation personal movement bias expressed less strongly under the 10-cm masker than under the 30-cm masker?

The source experiment defines 10 cm as the stronger masking condition.

## Identity-retention contrast

Frozen P1 condition components:
- 30 cm masker: `K30 = +8.00448 deg`
- 10 cm masker: `K10 = +1.87833 deg`

Difference:

[
D_K=K_{30}-K_{10}=+6.12614^circ.
]

All 720 baseline-label permutations were enumerated.

Calibration:
- null mean ≈ 0;
- null 95% interval: **[-3.5181, +4.6159] deg**;
- one-sided exact **p = 0.00278**.

Thus the identity-retention advantage is much stronger in the 30-cm than in the 10-cm condition.

## Expression-gain diagnostic

With centered baseline bias (	heta) and centered target state (y_c), define:

[
alpha_c=rac{	heta^Ty_c}{	heta^T	heta}.
]

Observed:
- (alpha_{30}=0.86322)
- (alpha_{10}=0.32371)
- (D_alpha=+0.53951)

Exact permutation calibration:
- null mean ≈ 0;
- null 95% interval: **[-0.4932, +0.4666]**;
- one-sided **p = 0.01667**.

This is a descriptive context-expression gain, not a physiological or neural parameter.

## Dispersion

Between-bat SD of centered condition means:

- baseline: **9.079 deg**
- 30 cm: **8.456 deg**
- 10 cm: **6.035 deg**

Relative to baseline:
- 30 cm SD ratio: **0.931**
- 10 cm SD ratio: **0.665**

Thus the stronger masker is accompanied by compression of expressed between-individual variation in this source-native movement coordinate.

## Important boundary

Do **not** promote a general rule:

> harder sensory task -> weaker individuality.

The separately frozen foam-target perturbation gives strong identity retention:
- 5/5 positive;
- K = +6.779 deg;
- exact p = 0.025;
- no-refit R2 = 0.641.

Therefore the defensible interpretation is narrower:

> **the expression strength of a persistent personal movement bias can be context dependent.**

The 30-cm versus 10-cm contrast shows attenuation in one controlled masker series.
The foam-target result demonstrates that attenuation is not a universal monotonic function of generic task difficulty.

## Mechanistic consequence

The minimum model should allow a context-specific expression term:

[
x_{ic}=mu_c+alpha_c	heta_i+delta_{ic}.
]

Current evidence supports:
- persistent (	heta_i);
- context variation in how strongly that bias is expressed.

It does not establish:
- a stable individual-specific reaction slope;
- a universal scalar (alpha);
- the origin of (	heta_i).

## Claim ceiling

This is post-primary mechanistic localization.
Use it to motivate context-gated expression, not as a new confirmatory headline.
