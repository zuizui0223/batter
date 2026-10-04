# Post-primary acoustic-condition persistence decomposition v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after the prospective scalar primary supported personal speed-state persistence:
- overall K = +0.52771;
- p = 0.0052;
- 12/14 positive;
- condition 1: 5/7 positive;
- condition 2: 7/7 positive.

Published/source-reproduced mean learning shift is much larger in condition 1 than condition 2.

## Question

Is personal speed-state persistence similarly supported within each acoustic condition, or is the overall result carried disproportionately by the condition with the smaller learning shift?

## D1 — exact condition-specific persistence

For each condition separately use the exact primary definition:
- state-specific mean removal;
- frozen pooled within-state scale;
- K_i self-vs-other;
- equal-bat K_c.

Enumerate **all 7! = 5,040** permutations of trial-1 labels within that condition.

One-sided exact-style p:

[
p_c=(1+#{K_{null}ge K_c})/(1+5040).
]

Report:
- K_c;
- 7 individual K_i;
- positive fraction;
- exact permutation distribution;
- p_c.

This is diagnostic because condition-specific significance was not part of the primary contract.

## D2 — between-condition persistence contrast

Define:

[
Delta K = K_{reflective} - K_{permeable}.
]

Use 99,999 independent pairs of within-condition random early-label permutations.

Seed:
`202610052121`.

Two-sided p against 0 using absolute contrast:

[
p_Delta=(1+#{|Delta K_{null}|ge|Delta K_{obs}|})/(1+99999).
]

This asks whether standardized persistence differs between conditions.

## D3 — condition-specific rank preservation

Report the already-defined:
- Pearson early→late residual correlation;
- pairwise order accuracy;

for each condition.

For pairwise order accuracy, enumerate all 5,040 early-label permutations and give a one-sided p.

For Pearson r, enumerate the same 5,040 permutations and give a one-sided p.

## Interpretation

If reflective persistence is strong while permeable persistence is weak:

> the personal prior survives most clearly when the learning-induced population shift is modest, whereas a stronger information-enabled learning transition can partially reorganize individual rank.

This is **not** proof that learning magnitude causes lower persistence because condition and learning opportunity are confounded.

If both conditions are individually supported:

> the personal prior persists even under the stronger learning shift, despite weaker rank stability in one condition.

## Ceiling

Do not infer:
- causal suppression of individuality by acoustic information;
- a universal plasticity–individuality trade-off.

Only two experimental conditions are available.
