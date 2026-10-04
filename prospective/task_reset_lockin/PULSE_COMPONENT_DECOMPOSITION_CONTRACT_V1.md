# Post-primary pulse-component decomposition contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- cross-configuration pulse identity was supported;
- movement-conditioned pulse identity remained supported.

No component-specific identity result has yet been calculated.

## Question

Is portable sensing individuality merely a difference in overall pulse emission rate, or does it also reside in the temporal structure of inter-pulse intervals (IPI)?

## Data and preprocessing

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories and the six pulse features frozen in `RHINO_PULSE_IDENTITY_CONTRACT_V1.md`.

Within each environment and retained feature:
- subtract the environment mean;
- divide by the environment sample SD.

Use the exact leave-one-environment-out identity estimator and environment-wise cluster-label permutation null from the pulse diagnostic.

## D1 — pulse-rate only

Feature:
- `log_pulse_rate`.

9,999 permutations.
Seed:
`202610042261`.

## D2 — IPI structure without pulse rate

Features:
- median log IPI;
- p10 log IPI;
- p90 log IPI;
- IQR log IPI;
- SD log IPI.

This removes explicit total pulse rate.

9,999 permutations.
Seed:
`202610042262`.

## D3 — IPI variability only

Features:
- IQR log IPI;
- SD log IPI.

This removes:
- pulse rate;
- median timing;
- p10/p90 location.

9,999 permutations.
Seed:
`202610042263`.

## D4 — IPI central/quantile timing only

Features:
- median log IPI;
- p10 log IPI;
- p90 log IPI.

9,999 permutations.
Seed:
`202610042264`.

## Diagnostic support

For each component report:
- P;
- individual P_i;
- positive fraction;
- null mean and 95% interval;
- one-sided permutation p.

Call a component descriptively supported if:
- P > 0;
- p <= 0.05;
- >=70% evaluable bats have P_i > 0.

No multiple-testing claim is made. The four decompositions are mechanism diagnostics, not four confirmatory hypotheses.

## Interpretation

- D1 supported only: sensing individuality may mainly be an individual pulse-rate scale.
- D2 supported: identity extends beyond overall emission rate.
- D3 supported: individual temporal variability/burstiness itself transfers across configurations.
- D4 supported: individual central/quantile timing structure transfers across configurations.

## Ceiling

Even broad pulse-component identity does not distinguish learned style from stable physiology or morphology.
