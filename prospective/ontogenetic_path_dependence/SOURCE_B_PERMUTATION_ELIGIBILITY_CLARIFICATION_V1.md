# Source B permutation eligibility clarification v1

## Status

**TECHNICAL NULL CLARIFICATION — frozen before the primary biological outcome is opened.**

Parent:
`SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`.

## Problem clarified

The frozen target universe requires >=20 valid movement days because targets span valid-day ordinals 3..20.

The observed other-individual comparator at target ordinal t allows any same-cohort juvenile with at least t valid days.

A juvenile with fewer than 20 valid days can therefore be a legitimate donor for an early target but cannot serve as a pseudo-self history for the same focal target across the complete 3..20 formation series.

Allowing such a partial library to be permuted into pseudo-self identity would change target support across permutations and violate the frozen requirement to preserve experience-day/history support.

## Frozen clarification

### Primary target / pseudo-self permutation universe

Within each cohort, define:

`P_c = juveniles with >=20 structurally valid movement days`.

Only members of `P_c`:
- are primary target individuals;
- participate in the whole-history identity permutation as assignable pseudo-self libraries.

For one permutation, draw one bijection of complete history libraries across `P_c` and retain that mapping for **all target ordinals 3..20**.

This preserves a coherent pseudo-individual history across ontogeny.

### Other comparator

For target i at ordinal t, the observed or permuted other comparator includes:

- every same-cohort juvenile with >=t valid movement days;
- excluding whichever complete-history individual is currently assigned as pseudo-self.

Thus juveniles with <20 total valid days:
- remain available as other-individual donors where structurally eligible;
- are never assigned as pseudo-self;
- are never primary targets.

## What does not change

This clarification does not change:
- the observed self library;
- the observed donor eligibility rule;
- target ordinals;
- history cap;
- spatial estimator;
- experience axis;
- B_i;
- B;
- permutation count/seed;
- primary support thresholds.

It only makes the frozen whole-history permutation executable without support changing across null replicates.

## Stop rule

If a cohort has fewer than 4 complete-history individuals in `P_c`:
- targets in that cohort cannot satisfy self + >=3 same-cohort complete-history donor support through ordinal 20;
- do not pool cohorts or relax the donor floor.

## JAE firewall

No effect on JAE v0.4.0.
