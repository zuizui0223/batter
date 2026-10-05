# Sparse-support species-boundary stress test v1

## Status

**POST-PRIMARY GENERALITY / POWER DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- strong cross-configuration policy identity in *Rhinolophus nippon*;
- no policy identity in *Miniopterus fuliginosus* with 4 bats and 19 trajectories;
- fixed-axis transfer and Miniopterus-specific PCA1 also failed.

## Question

Could the Miniopterus negative result be explained simply by having only four bats and 19 trajectories?

The two species have different environment-by-individual support patterns, so an exact design match is impossible without synthetic duplication or dropping required environments. This diagnostic therefore tests **sparse sample size**, not exact-design equivalence.

## Source

Use only the 45 authoritative *R. nippon* feature-valid trajectories from the frozen task-reset programme.

Use the exact eight Primary-B environment-standardized features and the exact cross-configuration K statistic.

## Sparse subsample design

For each subsample:

1. choose 4 of the 5 Rhino bats uniformly without replacement;
2. choose 19 trajectories uniformly without replacement from trajectories belonging to those four bats;
3. accept only if:
   - every chosen bat contributes >=3 trajectories;
   - every chosen bat is represented in >=3 distinct environments;
   - at least 3 bat identities remain evaluable under the exact leave-one-environment-out K architecture;
4. compute the full 8-D cross-configuration K with the original biological labels.

No label permutation p-value is calculated per subsample.

## Monte Carlo

Target:
- 9,999 accepted sparse subsamples.

Seed:
`202610051401`.

Attempt ceiling:
- 1,000,000 proposals.

If fewer than 9,500 accepted, STOP.

## Outputs

Report:
- accepted subsamples;
- K median;
- K 2.5% and 97.5% quantiles;
- fraction K > 0;
- fraction K <= the observed Miniopterus full-8D K (-0.0135975253);
- fraction K >= the full Rhino K (+0.9435600965);
- distribution of selected four-bat sets.

## Interpretation

If sparse Rhino subsamples usually remain positive, the Miniopterus negative result is not readily explained by 4-bat/19-trajectory sample size alone.

If sparse Rhino subsamples often collapse to zero/negative, the apparent species boundary is substantially confounded by support.

## Ceiling

This is not a formal cross-species power analysis and does not equalize the exact environment-by-bat design.

It cannot prove a biological species difference.
