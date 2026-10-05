# Condition-specific exact maintenance robustness contract v1

## Status

**POST-PRIMARY ROBUSTNESS DIAGNOSTIC.**

Frozen after the prospective pooled primary passed:
- K_policy = 0.67436;
- 11/14 positive;
- p = 0.0027.

This diagnostic cannot redefine or rescue the primary.

## Question

Is the personal-state maintenance signal present in both acoustic learning conditions, or is the pooled primary carried mainly by one condition?

## Data and state definition

Use exactly the same 14 subjects and exactly the same condition × trial standardized 2-D state as the primary:

- standardized maximum flight speed;
- standardized meandering width.

Analyse conditions separately.

Each condition contains exactly seven subjects.

## Statistic

Within condition c:

For subject i:
- D_self = distance from its trial-1 state to its own trial-12 state;
- D_other = mean distance from its trial-1 state to all other trial-12 subjects in that condition;
- K_i = D_other - D_self.

Condition statistic:

`K_c = mean_i K_i`.

## Exact null

Enumerate **all 7! = 5,040** permutations of trial-12 subject labels within the condition.

Trial-1 labels stay fixed.

Exact one-sided p:

`p = # {K_null >= K_observed} / 5040`.

The identity permutation is part of the null enumeration.

## Report

For each condition:
- K_c;
- K_i;
- number positive;
- exact p;
- null mean;
- null 95% interval.

## Interpretation

- both conditions positive with exact p <= 0.05:
  maintenance replicates across both acoustic contexts;
- one supported and one not:
  maintenance is context-dependent;
- both unsupported:
  pooled primary remains the preregistered result, but condition-level generality is weak.

No endpoint reweighting or condition pooling is changed.
