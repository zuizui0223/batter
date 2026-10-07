# Learning-state expression-strength diagnostic contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- the Yamada trial-1 -> trial-12 personal speed-state primary passed overall;
- condition-specific persistence was already known to be strong in the reflective condition and weak in the permeable condition;
- the individual raw speed pairs have not been opened for this new alpha diagnostic in this branch.

## Question

Does learning merely shift the population operating point, or does it also change how strongly a stable personal state is expressed?

Use the model

[
s_{i,c,t} = mu_{c,t} + alpha_{c,t}	heta_i + epsilon_{i,c,t}.
]

For each acoustic condition c:

- trial 1 is the naive state;
- trial 12 is the familiar state;
- (mu) is removed separately within condition × trial;
- (alpha_c) is the through-origin mapping from naive individual residuals to familiar individual residuals.

## Data

Use exactly the 28 source-native maximum-speed rows already frozen in:
`PERSONAL_SPEED_STATE_CONTRACT_V1.md`.

Source:
- Yamada et al. 2020
- Figshare file ID: 33969680
- size: 18,023 bytes
- MD5: cb7e2f738d85ee80becb5949317ff625

Exactly:
- 7 bats in condition 1;
- 7 bats in condition 2;
- one trial-1 and one trial-12 observation per bat.

## Estimator

Within each condition:

[
x_i=s_{i,1}-ar s_{1}
]

[
y_i=s_{i,12}-ar s_{12}
]

and

[
alpha_c = rac{sum_i x_i y_i}{sum_i x_i^2}.
]

Also report:
- Pearson r between x and y;
- SD ratio (q_c=SD(y)/SD(x));
- residual RMSE around (y=alpha_c x).

The mean learning shift

[
Deltamu_c = ar s_{12}-ar s_1
]

is reported separately from alpha.

## Within-condition null

For each condition independently:

- keep familiar residuals y fixed;
- permute complete naive residual values x among the seven bat labels;
- enumerate all 7! = 5,040 permutations.

One-sided p for positive alpha:

[
p_alpha = Pr(alpha_{perm}gealpha_{obs}).
]

No post-hoc sign flipping.

## Uncertainty

Paired biological-bat bootstrap within each condition:
- B = 9,999;
- seed condition 1: 20261007701;
- seed condition 2: 20261007702.

Report percentile 95% CI for alpha.

## Between-condition diagnostic

Primary descriptive contrast:

[
Deltaalpha=alpha_{reflective}-alpha_{permeable}.
]

Calibrate with 99,999 draws formed by independently sampling one exact within-condition permutation from each condition's 5,040-permutation null distribution.

Seed: 20261007703.

Two-sided p:
[
p_Delta = Pr(|Deltaalpha_{null}|ge|Deltaalpha_{obs}|).
]

This is an association-architecture contrast, not a causal randomized-treatment estimand.

## Interpretation

- Both alpha values positive and supported: personal ordering survives learning in both contexts.
- Reflective alpha supported, permeable alpha unsupported: personal-state expression is context dependent.
- Delta alpha calibrated at p<=0.05: stronger evidence that expression differs between conditions.
- SD ratio without alpha persistence means dispersion can remain while individual identity is reordered.

## Claim ceiling

This diagnostic does not establish:
- that alpha is literally neural gain;
- that acoustic condition causally changes alpha;
- that the Teshima FlightIntensity theta and Yamada maximum-speed theta are numerically identical;
- that theta is morphological rather than learned.

It tests whether learning changes the **expression strength of persistent individual differences**, beyond the common mean learning shift.
