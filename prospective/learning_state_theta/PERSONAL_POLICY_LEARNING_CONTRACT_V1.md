# Yamada personal-policy persistence across learning contract v1

## Status

**PROSPECTIVE PRIMARY — frozen before any raw trajectory value or speed outcome is opened by this programme.**

Branch:
`prospective/learning-state-theta-v1`

Parents:
- `SOURCE_RECEIPT_V1.md`
- `STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md`
- `RAW_SHEET_CROSSWALK_CONTRACT_V1.md`

## Biological question

Repeated spatial experience changes horseshoe-bat flight behaviour.

The new question is:

> **after removing the common learning-state shift, does a bat retain a personal movement-policy signature from its naive first flight to its familiar twelfth flight?**

This distinguishes:

[
behaviour = learning state
]

from:

[
behaviour = stable personal prior + plastic learning state.
]

## Data

Use exactly the source-defined:
- 14 bats;
- 7 permeable/chain;
- 7 reflective/acrylic;
- trial 1;
- trial 12;

and exactly one raw trajectory sheet per bat × trial under the frozen deterministic crosswalk.

No intermediate trials are introduced into this primary.

## Raw fields

From every mapped raw worksheet, read only:
- `time[s]`;
- first `bat(X)[mm]`;
- first `bat(Y)[mm]`;
- first `bat(Z)[mm]`.

Do not use:
- source-computed velocity;
- source-computed turn rate;
- pulse variables;
- obstacle coordinates;
- max_flight_speed from the small summary workbook.

The policy features are recomputed from raw coordinates to match the Teshima policy architecture as closely as possible.

## Cleaning

For each trajectory:

1. convert X/Y/Z from mm to m;
2. retain rows with finite time, X, Y, Z;
3. stable-sort by time;
4. for duplicate timestamps retain the first row;
5. require >=100 retained rows;
6. require positive total duration and path length;
7. require >=50 positive-time movement intervals;
8. require >=20 finite horizontal turning-rate values.

Any bat missing either valid trial 1 or valid trial 12 is structurally excluded **before** outcome calculation.

Primary opens only if:
- >=5 valid bats in condition 1;
- >=5 valid bats in condition 2;
- >=12 valid bats overall.

No threshold relaxation.

## Eight movement-policy features

Compute exactly:

1. median 3-D speed;
2. 90th percentile 3-D speed;
3. median absolute vertical speed;
4. 90th percentile absolute vertical speed;
5. median absolute horizontal turning rate;
6. 90th percentile absolute horizontal turning rate;
7. path efficiency = net 3-D displacement / total 3-D path length;
8. vertical range = max(Z)-min(Z).

Turning-rate definition matches the frozen Teshima implementation:
- heading = atan2(dy,dx) for positive horizontal movement intervals;
- wrapped heading difference;
- divisor = mean duration of the two adjacent segments.

## Remove the common learning-state shift

For each acoustic condition c, trial state t in {1,12}, and feature k:

[
mu_{c,t,k}=mean_i(x_{i,c,t,k}).
]

Residual:

[
r_{i,c,t,k}=x_{i,c,t,k}-mu_{c,t,k}.
]

Thus any common first→twelfth population shift in that feature is removed.

For each condition and feature, compute the pooled within-state residual scale:

[
s_{c,k}=
sqrt{
rac{
sum_i r_{i,c,1,k}^2+sum_i r_{i,c,12,k}^2
}{
(n_{c,1}-1)+(n_{c,12}-1)
}
}.
]

Standardized personal residual:

[
z_{i,c,t,k}=r_{i,c,t,k}/s_{c,k}.
]

If a feature has zero/nonfinite pooled scale in either condition:
- drop that feature for **both** conditions.

Require >=6 of 8 features.

No feature selection by identity result.

---

# Primary P — first-to-twelfth personal-policy persistence

For bat i in condition c:

- early vector: `E_i = z_{i,c,1}`;
- familiar vector: `L_i = z_{i,c,12}`.

Self distance:

[
D_{self,i}=||L_i-E_i||_2.
]

Other distance:

[
D_{other,i}
=
mean_{j
eq i} ||L_i-E_j||_2.
]

Individual persistence advantage:

[
K_i=D_{other,i}-D_{self,i}.
]

Positive means the familiar-flight policy remains closer to that bat's own naive-flight policy than to other bats' naive policies after the common learning shift has been removed.

Condition statistic:
equal-bat mean `K_c`.

Programme statistic:
equal-condition mean

[
K_P=(K_1+K_2)/2.
]

## Null

Within each acoustic condition independently:

- keep every trial-12 vector and label fixed;
- permute complete trial-1 bat labels among the early vectors;
- preserve 7-vs-7 condition membership and all feature values;
- break only first↔twelfth personal correspondence.

9,999 permutations.

Seed:
`202610052101`.

One-sided:

[
p=(1+#{K_{null}ge K_P})/10000.
]

## Primary support rule

Call personal-policy persistence supported only if all hold:

1. `K_P > 0`;
2. `p <= 0.05`;
3. >=70% of all evaluable bats have `K_i>0`;
4. >=5/7 positive bats in condition 1 if all seven evaluable, otherwise >=70%;
5. >=5/7 positive bats in condition 2 if all seven evaluable, otherwise >=70%.

This prevents one acoustic condition from carrying the whole result.

---

# Secondary S — transparent movement-intensity persistence

Use the same standardized personal residuals, but define:

[
I_{i,c,t}
=
mean(
z_{median speed},
z_{p90 speed},
z_{median |v_z|},
z_{p90 |v_z|}
).
]

For each twelfth-flight target:

[
K^I_i=
mean_{j
eq i}|I_{i,c,12}-I_{j,c,1}|
-
|I_{i,c,12}-I_{i,c,1}|.
]

Equal-bat -> equal-condition mean.

Use the same condition-wise early-label permutation null.

9,999 permutations.

Seed:
`202610052102`.

This secondary directly connects the independent learning dataset to the transparent Teshima FlightIntensity axis.

It is not allowed to rescue a failed 8-D primary.

---

# Interpretation

## Primary supported

> Learning changes the population operating state, but individual policy differences persist across the naive-to-familiar transition.

Together with the published Yamada learning effect, this supports:

[
movement policy =
stable personal prior
+
plastic learning state.
]

## Primary unsupported

Do not infer absence of individual differences.

The result would instead indicate that the first→twelfth learning transition is large enough to reorganize the measured personal policy, or that a naive first flight is not a reliable estimate of the individual's stable prior.

## Condition asymmetry

If the frozen overall statistic is positive but the per-condition sign rule fails:
- primary verdict = FAIL;
- report which acoustic condition lacks persistence;
- do not relax the rule.

This could indicate that information structure changes whether individual priors survive learning.

## Ceiling

Even a supported primary does not identify the origin of the stable prior:
- morphology;
- physiology;
- developmental history;
- earlier lifetime learning

remain possible.

It also does not prove that the Yamada and Teshima latent parameters are numerically identical.

## JAE firewall

No result changes JAE v0.4.0.
