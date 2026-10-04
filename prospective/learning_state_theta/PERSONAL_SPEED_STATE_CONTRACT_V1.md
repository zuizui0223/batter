# Yamada personal speed-state persistence contract v1

## Status

**SEPARATE PROSPECTIVE SCALAR PRIMARY.**

Frozen after:
- the 8-D raw-coordinate policy route STOPPED on its >=100-row support rule;
- no `max_flight_speed` row value has been opened by this programme.

This is **not** a rescue of the 8-D primary. It tests the source-native one-dimensional speed-state analogue anticipated in `SOURCE_RECEIPT_V1.md`.

## Data

Source workbook:
`raw_analysis_data_by_yamada.xlsx`

Sheet:
`1st_table`

Use exactly:
- condition;
- bats_id;
- trial;
- `max_flight_speed [m/s]`.

Use the already-passed structural population:
- 14 bats;
- 7 condition 1 (permeable/chain);
- 7 condition 2 (reflective/acrylic);
- one trial-1 row and one trial-12 row per bat.

No pulse or meandering outcome enters this test.

## Biological question

Published Yamada results establish a learning-dependent population shift in maximum flight speed, especially in the permeable condition.

The new question is:

> **after removing that common condition-specific learning shift, does each bat retain a personal faster/slower speed state from its naive first flight to its familiar twelfth flight?**

## Remove common learning shift

For condition c and trial t in {1,12}:

[
mu_{c,t}=mean_i(v_{i,c,t}).
]

Residual:

[
r_{i,c,t}=v_{i,c,t}-mu_{c,t}.
]

Pooled within-state scale per condition:

[
s_c =
sqrt{
rac{
sum_i r_{i,c,1}^2+sum_i r_{i,c,12}^2
}{
(7-1)+(7-1)
}
}.
]

Require finite positive `s_c`.

Standardized personal speed state:

[
z_{i,c,t}=r_{i,c,t}/s_c.
]

Thus the source-published mean learning shift is removed before individual persistence is evaluated.

## Primary P — self-versus-other speed-state persistence

For each bat i:

[
D_{self,i}=|z_{i,c,12}-z_{i,c,1}|.
]

[
D_{other,i}
=
mean_{j
eq i}|z_{i,c,12}-z_{j,c,1}|.
]

[
K_i=D_{other,i}-D_{self,i}.
]

Positive means the bat's familiar speed state is closer to its own naive speed state than to other bats' naive states.

Condition statistic:
equal-bat mean `K_c`.

Programme statistic:

[
K_P=(K_1+K_2)/2.
]

## Null

Within each condition independently:

- keep trial-12 values and labels fixed;
- permute the seven trial-1 bat labels;
- preserve all speed values and condition membership;
- break only first↔twelfth personal correspondence.

9,999 permutations.

Seed:
`202610052111`.

One-sided p.

## Primary support rule

Supported only if all hold:

1. `K_P > 0`;
2. p <= 0.05;
3. >=10/14 bats have `K_i > 0`;
4. >=5/7 condition-1 bats positive;
5. >=5/7 condition-2 bats positive.

No rule may be relaxed after opening.

---

# Secondary rank and magnitude diagnostics

These do not rescue the primary.

## R1 — within-condition Pearson persistence

For each condition:
- Pearson correlation between trial-1 and trial-12 `z`.

Also compute a pooled 14-bat Pearson correlation after the condition-specific standardization.

Null:
same condition-wise trial-1 label permutation.

## R2 — pairwise order persistence

Within each condition and unordered bat pair:

- compare sign of trial-1 speed difference with sign of trial-12 difference;
- ties score 0.5.

Report:
- condition-specific accuracy;
- equal-condition mean accuracy.

Null:
same label permutation.

## R3 — magnitude calibration

Across 14 bats:

through-origin slope

[
eta =
rac{sum z_{1}z_{12}}{sum z_{1}^2}.
]

Report descriptively with the same permutation null.

No equivalence claim to beta=1 is authorized.

---

# Published mean learning shift

For transparency, reproduce:
- mean raw max speed at trial 1 and 12 within each condition;
- mean within-bat change.

These are **reproductions of a published source result**, not new confirmatory findings.

## Interpretation

### Primary supported

> A condition-specific learning shift occurs on top of a persistent individual speed-state prior.

Together with Teshima's cross-configuration one-parameter result, this supports:

[
control state
=
personal prior
+
plastic learning shift.
]

### Primary fails but correlation/order remains positive

The personal speed state is suggestive but not strong enough under the strict self-vs-other criterion.

### All persistence diagnostics fail

Learning reorganizes individual speed state strongly enough that the naive speed state does not predict the familiar one.

## Ceiling

A supported result does not establish that:
- speed is the entire personal policy;
- the Yamada scalar is numerically identical to the Teshima `FlightIntensity`;
- the stable component is genetic or morphological.

It establishes only within-individual persistence of a one-dimensional movement-speed state across learning.
