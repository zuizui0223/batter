# Allocation-axis to vertical-spread consequence contract v1

## Status

**CONDITIONAL POST-OUTCOME MECHANISM DIAGNOSTIC.**

This contract is frozen before the transparent allocation-axis identity outcome is known.

It may open only if
`FIELD_ALLOCATION_AXIS_CONTRACT_V1.md`
supports the transparent allocation carrier

[
A=(H-V)/sqrt 2
]

in **both** P. hastatus 2022 and 2023 under its predeclared support rule.

If either year fails, STOP and do not calculate this consequence endpoint.

This diagnostic cannot reopen the frozen JAE field bridge or modify JAE v0.4.0.

## Biological question

If A is a persistent horizontal-versus-vertical allocation policy, does that personal policy have the expected specific consequence for held-out vertical-use breadth?

Prediction:

> individuals whose prior policy is more horizontal-dominant should express narrower centered vertical use; individuals whose prior policy is more vertical-dominant should express broader centered vertical use.

This is deliberately narrower than the unsupported claim that nearby policy vectors must have similar complete vertical-distribution shapes.

## Policy coordinate

Use exactly the fixed-bin 360-s allocation scalar from
`FIELD_ALLOCATION_AXIS_CONTRACT_V1.md`:

[
A=(H-V)/sqrt 2
]

where H and V use the already-frozen within-cohort standardizations.

For target session t of individual i:

[
	heta_{A,i,-t}
=
	ext{equal-session mean A over all other valid fixed-bin sessions of i}.
]

If target t is not fixed-bin valid, use all fixed-bin-valid sessions of i.

Require at least one allowed policy-history session after exclusion.

## Vertical consequence

Use the same source-admitted vertical sessions and native height field as the JAE/frozen field architecture.

For each target session:

1. use all source-valid finite height fixes in that session;
2. center heights by the target session median;
3. require >=50 finite centered fixes;
4. define robust vertical breadth

[
W_t = Q_{0.90}(z_t)-Q_{0.10}(z_t).
]

No terrain, smoothing, interpolation or new binning enters this endpoint.

The 90–10 width is frozen because it measures vertical breadth without depending on the tails beyond a few extreme fixes.

## Cohort standardization

Within each frozen cohort, z-score W across eligible target sessions:

[
Z^W_t=(W_t-ar W_c)/sd(W_c).
]

If cohort SD is zero/nonfinite, stop that cohort.

Do **not** re-standardize A; use the already-frozen A coordinate.

## Primary statistic

For each target session t:

- predictor = (	heta_{A,i,-t});
- response = (Z^W_t).

Prediction is negative.

To preserve equal biological weighting:

1. assign equal weight to target sessions within each individual;
2. assign equal total weight to each individual within year.

Compute the weighted covariance-like statistic

[
B_{	ext{year}}
=
-rac{sum_t w_t(	heta_{A,i,-t}-ar	heta_c)(Z^W_t-ar Z^W_c)}
{sum_t w_t}
]

where cohort means use the same target weights.

Thus:
- (B>0) means horizontal-dominant A predicts narrower vertical breadth;
- (B<0) means the opposite.

Report also a weighted descriptive Pearson correlation with the original sign.

## Null

Within each frozen cohort independently:

- permute complete individual A histories among biological individual labels;
- preserve all vertical target data, policy-session vectors, support and cohort structure;
- recompute target-specific leave-one-session-out theta where the assigned history contains the same session ID; otherwise use all assigned-history sessions.

9,999 permutations.

Seeds:
- 2022: `202610051511`
- 2023: `202610051512`.

One-sided p for (B>0).

Require >=9,500 valid permutations.

## Support rule

A year supports the directional consequence if:

- B_year > 0;
- one-sided p <= 0.05;
- at least 70% of evaluable individuals have negative individual mean signed association contribution
  ((	heta_A-ar	heta_c)(Z^W-ar Z^W_c)).

## Interpretation

### Both years supported

Evidence that the persistent field allocation policy has a specific spatial consequence:

> horizontal-versus-vertical movement allocation predicts how broadly an individual uses the vertical dimension, even though it does not determine the complete vertical-distribution shape.

This would support a layered phenotype:

[
	ext{policy} ightarrow 	ext{specific shape component},
]

not a one-to-one policy-to-shape mapping.

### Both unsupported

The allocation carrier is persistent but its ecological consequence is not detectable in centered vertical breadth.

This strengthens the separation between movement-policy individuality and vertical-distribution individuality.

### Mixed

Context-dependent consequence; no general bridge.

## Hard ceiling

Even success does not establish:
- causal mediation;
- learned versus morphological origin;
- that A explains the full JAE vertical identity signal;
- applicability outside P. hastatus.

The frozen JAE bridge remains unchanged regardless of this result.
