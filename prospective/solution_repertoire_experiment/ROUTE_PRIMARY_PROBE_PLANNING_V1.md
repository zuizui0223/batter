# P1 route-primary probe planning v1

## Status

**PROSPECTIVE DESIGN STRESS TEST. NOT AN EMPIRICAL EFFECT-SIZE CLAIM.**

Purpose:
compare candidate common-OPEN probe lengths for the direct route-specialization P1 before any confirmatory outcome is opened.

Architecture simulated:
- 20 animals;
- five complete restricted-randomization blocks;
- four route categories;
- first half of probe = individual route history;
- second half = held-out target;
- Dirichlet alpha = 0.5;
- exact 1,024-assignment treatment randomization test.

The simulation varies the Dirichlet concentration governing among-individual route distributions.

Lower concentration for OPEN-acquired histories means stronger among-individual route differentiation.

These concentration values are illustrative only.

## Results

600 Monte Carlo replicates per scenario × trial-count cell.

| scenario | illustrative k_OPEN | illustrative k_CONSTRAINED | 8 total (4+4) | 12 total (6+6) | 16 total (8+8) |
|---|---:|---:|---:|---:|---:|
| strong | 4 | 40 | 0.635 | 0.780 | 0.853 |
| moderate | 6 | 30 | 0.347 | 0.485 | 0.565 |
| mild | 8 | 30 | 0.240 | 0.320 | 0.345 |

Values are rejection fractions at exact randomization p <= 0.05 under each illustrative generative scenario.

## Decision

Remove 8 total probe trials per family from the confirmatory planning set.

Reason:
- with four route categories, 4 early trials provide a very noisy individual categorical history;
- across every illustrative scenario, 8 total trials is dominated by 12 and 16;
- the gain from 12 -> 16 remains meaningful in the strong/moderate scenarios.

Pilot candidates are therefore:

- **12 total valid common-OPEN trials per family = 6 early + 6 late**;
- **16 total = 8 early + 8 late**.

Prefer 16 if welfare, fatigue and tracking reliability permit.

Use 12 if the engineering pilot shows that 16 materially compromises completion, tracking quality or welfare.

Do not choose between 12 and 16 using individual-specialization p-values.

The pilot selection criterion remains measurement burden / stability only.

## Boundary

This simulation does not estimate the true biological effect and cannot be cited as achieved power.

The actual P1 effect is unknown.

Its role is only to reject an obviously sparse 4+4 categorical design before outcome opening.

Reproducible script:
route_primary_probe_planning_v1.py.
