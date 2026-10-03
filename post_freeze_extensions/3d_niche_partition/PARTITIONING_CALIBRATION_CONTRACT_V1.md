# Partitioning calibration contract v1

## Status

POST-OUTCOME DIAGNOSTIC, frozen after the terrain-relative geometry and synchronous co-use outcomes were known.

This analysis does not create a new mechanism test. It calibrates two quantities already used in the completed 3D synthesis so that the manuscript can distinguish repeatable individual vertical strategy from strong vertical partitioning without interpreting non-significance as evidence of zero effect.

## Fixed panel universe

The four original panels already structurally evaluable in the terrain-relative 500-m analysis:
- Hypsignathus monstrosus
- Phyllostomus hastatus 2022
- P. hastatus 2023
- P. hastatus 2016

No panel may be added after calibration outputs are opened.

## A. Calibration of S_rel

S_rel is unchanged:
S_rel = other R3D - self R3D,
computed from the terrain-relative 3D geometry already fixed in ORIGINAL_TERRAIN_GEOMETRY_CONTRACT_V1.

The null uses exactly the same within-cohort individual-label permutation used for V_rel in the completed terrain-relative geometry analysis. For every one of the already-fixed 9,999 permutations, recompute the full geometry and record S_rel.

Report:
- observed S_rel;
- null mean, median, 2.5% and 97.5% quantiles;
- calibrated excess = observed - null mean;
- two-sided permutation p = (1 + number(|S_null-null_mean| >= |S_obs-null_mean|)) / (B+1).

S is a secondary geometric diagnostic. No panel-level significance result is promoted to a new primary claim.

## B. Compatibility bounds for synchronous co-use excess I

I remains:
observed equal-dyad median vertical separation - phase-shift null mean.

The biological resampling unit is the frozen usable dyad, because the primary panel statistic weights dyads equally. Within each panel, sample the frozen dyad medians with replacement, retaining the original number of dyads, and calculate their equal-weight mean. Repeat B=9,999 times.

The already-completed phase-shift null mean is held fixed. For each bootstrap replicate:
I_b = bootstrap observed equal-dyad mean - completed phase-shift null mean.

Seeds:
- Hypsignathus 20261002201
- P. hastatus 2022 20261002202
- P. hastatus 2023 20261002203
- P. hastatus 2016 20261002204

Report the percentile 95% interval for I and especially its upper endpoint. This is a compatibility interval for the panel-level excess under dyad resampling, not a post-hoc power calculation and not a formal equivalence test.

Interpretation:
- an upper endpoint near zero constrains large positive co-use-dependent separation;
- an interval spanning positive values leaves those magnitudes compatible with the data;
- the 2023 positive primary result remains an exception and is not generalized.

## Claim ceiling

Allowed:
- quantify how large a positive interaction-dependent vertical-separation excess remains compatible with each panel;
- state whether S_rel is unusual relative to the inherited individual-label null;
- synthesize that terrain-relative strategy fidelity can occur without strong evidence for mutually exclusive vertical layers or systematic co-presence-dependent separation.

Not allowed:
- “competition is absent”;
- “niche partitioning is disproved”;
- equivalence to exactly zero unless a separate equivalence margin was fixed independently;
- intentional avoidance, resource identity, diet partitioning, or adaptive benefit.

## Stop rule

After this contract is committed:
- do not change panel eligibility;
- do not change S_rel;
- do not change the inherited label-permutation null;
- do not change the dyad resampling unit;
- do not tune interval level or seeds;
- do not add alternative effect-size definitions to rescue interpretation.
