# Acoustic-condition persistence diagnostic result v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC.**

Parent:
`CONDITION_PERSISTENCE_DIAGNOSTIC_CONTRACT_V1.md`

Authoritative workflow:
- run: **37245448006**
- artifact: **11318584087**
- artifact ZIP SHA256: `3ef2101596208d138d7352d99c0983bfe83025128366b6af754d6f1e81244d16`

This diagnostic was frozen only after the overall scalar primary passed. It is not an independent confirmatory result.

## Condition 1 — permeable / stronger learning shift

Published/source-reproduced mean speed shift:
**+0.8925 m/s**.

Personal-state persistence:
- K = **+0.17577**;
- positive bats = **5/7**;
- exact 7! permutations = 5,040;
- one-sided `p_K=0.2593`.

Rank/magnitude:
- Pearson residual correlation: `r=0.0026`, `p=0.4983`;
- pairwise-order accuracy: 0.5714, `p=0.3864`.

Thus this condition does not independently provide calibrated evidence for preserved individual ordering.

## Condition 2 — reflective / weaker learning shift

Published/source-reproduced mean speed shift:
**+0.2734 m/s**.

Personal-state persistence:
- K = **+0.87965**;
- positive bats = **7/7**;
- exact 7! permutations = 5,040;
- one-sided `p_K=0.00159`.

Rank/magnitude:
- Pearson residual correlation: **r=0.8980**, `p=0.00238`;
- pairwise-order accuracy: **0.9524**, `p=0.00159`.

This condition shows strong persistence of personal faster/slower state.

## Between-condition contrast

Observed:

[
\Delta K =
K_{reflective}-K_{permeable}
=
+0.70389.
]

99,999 post-primary randomization draws:
- null mean: -0.00120;
- null 95% interval: [-0.78684, +0.78749];
- two-sided `p=0.0822`.

Therefore the apparent persistence difference is **suggestive but not statistically calibrated at 0.05**.

## Mechanistic interpretation

The evidence is compatible with:

[
x_{i,c,t}
=
\mu_{c,t}
+
\alpha_{c,t}\theta_i
+
\epsilon_{i,c,t},
]

where:
- `theta_i` is a personal control prior;
- `mu_c,t` is the shared learning-state shift;
- `alpha_c,t` is the context-dependent expression strength of the personal prior.

In the reflective condition, individual order is strongly retained.
In the permeable condition, the larger learning transition coincides with much weaker rank persistence.

However, with only two acoustic conditions:

> **do not claim that stronger learning causally suppresses individuality.**

Condition and learning opportunity are confounded, and the direct between-condition persistence contrast is p=0.0822.

## JAE firewall

No change to JAE v0.4.0.
