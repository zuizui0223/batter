# Phyllostomus 2023 support-matched sparsity diagnostic v1

## Status

**POST-OUTCOME BOUNDARY DIAGNOSTIC. NOT A RESCUE OF THE FAILED 2023 PANEL.**

Parent:
`WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md`.

Observed field outcome is already open:
- *P. hastatus* 2022: positive FlightIntensity persistence;
- *P. hastatus* 2023: negative FlightIntensity persistence.

This diagnostic asks whether the 2023 failure could plausibly arise solely from its sparser repeated-session support.

No threshold, panel classification or JAE claim may change as a result.

## Source comparison

Use only *P. hastatus* 2022 as the donor year.

Reason:
- same species;
- same two source colony architecture;
- same GPS-derived FlightIntensity estimator.

Do not pool *Hypsignathus*.

## 2023 support template

From the already-frozen 2023 panel after the policy-valid-session and >=2-session individual filters:

For each source colony separately record:
- number of eligible individuals;
- the multiset of eligible session counts per individual.

This exact colony-specific support pattern is the target template.

## Support-matched 2022 pseudo-panels

For each Monte Carlo replicate and each corresponding 2022 colony:

1. randomly select the same number of biological individuals as in the 2023 template;
2. assign the 2023 per-individual session-count multiset randomly to selected 2022 individuals;
3. require every selected 2022 individual to possess at least its assigned target session count;
4. sample exactly that many sessions without replacement from each selected individual.

If a random assignment is infeasible, retry within the same replicate.
A replicate is invalid only after 10,000 failed assignment attempts.

## Re-standardization

For every pseudo-panel replicate, within each 2022 colony separately:

- recompute means and sample SDs of the four raw session features using only the sampled sessions;
- z-score those sampled sessions;
- define FlightIntensity exactly as the mean of the four z-scored features.

Thus every pseudo-panel has the same sparse-support standardization problem as the 2023 panel.

If any feature SD is zero/nonfinite, that replicate is invalid.

## Statistic

Compute exactly the original wild-field self-history statistic:

`H_panel`.

Also compute:
- eligible-individual positive fraction.

Do **not** run a nested permutation p-value inside each pseudo-panel.

## Monte Carlo target

Valid pseudo-panels:
**9,999**

Seed:
`202610051401`.

Require >=9,500 valid pseudo-panels.

## Diagnostic comparisons

Observed 2023:
- `H_2023`;
- positive fraction `F_2023`.

Report under support-matched 2022 pseudo-panels:
- median H;
- 2.5–97.5% interval;
- fraction `H <= H_2023`;
- fraction `H <= 0`;
- median positive fraction;
- fraction `F <= F_2023`.

## Interpretation

### If H_2023 lies comfortably inside the support-matched 2022 distribution

Sparse repeated support remains a plausible explanation for the apparent year reversal.

### If H_2023 is in the extreme lower tail

The 2023 failure is unlikely to be explained by support sparsity alone.

This strengthens a biological/year-specific boundary interpretation, but does not identify its cause.

## Stop rules

Do not:
- change the 2023 panel status;
- lower the >=3/4 cross-panel rule;
- reopen the vertical-shape bridge;
- choose a different policy axis;
- remove influential 2023 individuals after seeing this result.
