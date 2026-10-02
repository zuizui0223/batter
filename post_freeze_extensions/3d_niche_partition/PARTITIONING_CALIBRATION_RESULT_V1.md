# Partitioning calibration result v1

## Status

POST-OUTCOME DIAGNOSTIC under `PARTITIONING_CALIBRATION_CONTRACT_V1.md`.

Authoritative S calibration workflow:
- run: 36992380946
- conclusion: success
- inherited terrain-relative individual-label permutation: 9,999 replicates per panel

## Terrain-relative added segregation S_rel

| panel | observed S_rel | null mean | null central 95% | two-sided p |
|---|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | -0.01581 | +0.00008 | -0.01567 to +0.01380 | 0.0362 |
| *Phyllostomus hastatus* 2022 | -0.00896 | -0.00037 | -0.02081 to +0.01755 | 0.3639 |
| *P. hastatus* 2023 | +0.01626 | +0.00069 | -0.03320 to +0.02602 | 0.2704 |
| *P. hastatus* 2016 | +0.02890 | +0.00018 | -0.09129 to +0.06912 | 0.4796 |

No panel shows permutation-supported positive terrain-relative added segregation. Hypsignathus is unusual in the negative direction: its observed S_rel is slightly below the inherited label-permutation distribution. This is not a predeclared lower-tail test and is not promoted to attraction; it reinforces that the data do not support mutually separated terrain-relative vertical layers.

## Synchronous co-use excess I compatibility

| panel | observed I (m) | dyad-bootstrap 95% interval (m) | upper endpoint (m) |
|---|---:|---:|---:|
| *Hypsignathus monstrosus* | -1.983 | -4.808 to +0.985 | +0.985 |
| *P. hastatus* 2022 | -0.947 | -3.207 to +1.918 | +1.918 |
| *P. hastatus* 2023 | +3.574 | -4.633 to +11.729 | +11.729 |
| *P. hastatus* 2016 | -0.854 | -3.127 to +1.128 | +1.128 |

The original phase-shift test remains authoritative for I: only 2023 supported positive co-use-dependent separation (one-sided p=0.0231). The dyad bootstrap is a compatibility diagnostic, not a replacement test. In the other three panels, its positive 95% upper endpoint is only about 1–2 m.

## Joint inference

All four panels retain permutation-supported terrain-relative vertical-strategy fidelity V_rel, but none shows supported positive S_rel. Three of four additionally show no synchronous co-use separation, with dyad-resampling upper compatibility bounds near 1–2 m. The fourth (P. hastatus 2023) is a heterogeneous exception under a coarser 600-s/all-space design.

Thus the strongest supported synthesis is:

> repeatable terrain-relative individual vertical strategies need not correspond to mutually exclusive vertical layers or to systematic contemporaneous vertical avoidance.

This distinguishes individual specialization from strong spatial niche partitioning. It does not show that competition is absent, because historical competition, resource differentiation, behavioural-state composition and other mechanisms can generate persistent individual strategies without momentary avoidance.

## Claim ceiling

Supported:
- terrain-relative vertical-strategy fidelity in all four structurally evaluable original panels;
- no permutation-supported positive terrain-relative added segregation S_rel in any of the four;
- no supported synchronous additional vertical separation in three of four panels;
- approximately 1–2 m positive upper compatibility bounds for I in those three panels;
- specialization and contemporaneous spatial partitioning are empirically separable dimensions here.

Not established:
- absence of competition;
- absence of resource partitioning;
- equivalence of I to exactly zero;
- intentional attraction or avoidance;
- causal origin or adaptive benefit of the individual strategies.
