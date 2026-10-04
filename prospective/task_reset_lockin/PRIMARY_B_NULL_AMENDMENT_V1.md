# Primary B null-calibration amendment v1

## Status

**FROZEN BEFORE ANY CSV TRAJECTORY ROW VALUE IS OPENED.**

Parent:
`CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md`

## Problem corrected

The parent contract stated:

> within species, permute bat identity as complete cross-environment labels while preserving environment membership and per-environment trial structure.

A single global permutation of complete individual labels would only rename individuals and would **not break cross-environment identity correspondence**. It therefore cannot serve as a null for cross-configuration identity transfer.

No trajectory value has yet been opened, so this is a design correction rather than a post-outcome rescue.

## Correct null

For each species independently and for each permutation:

1. within every environment separately, take the observed multiset of bat labels attached to trajectories;
2. randomly permute those labels across complete trajectories in that environment;
3. preserve exactly:
   - the number of trajectories in each environment;
   - the per-environment count assigned to every bat label;
   - all trajectory feature values;
4. perform the permutation **independently across environments**.

This preserves:
- environment effects;
- trial replication;
- label frequencies within environment;

while breaking:
- the correspondence between "bat A" in one environment and "bat A" in another.

## Statistic

Recompute the full leave-one-environment-out `K_species` under every independently-permuted labeling.

All other Primary B rules remain unchanged:
- 9,999 permutations;
- seed `202610042202`;
- one-sided p;
- K_species > 0;
- p <= 0.05;
- >=70% positive individual mean K.

## No other change

The feature set, residualization, eligibility, aggregation, thresholds and interpretation matrix are unchanged.
