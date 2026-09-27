# Tag altitude-bias structural preflight v1 — result

Canonical x-y/time-only run: **36325288331**  
Head: `c059e7567469b00074b3a857608f56f4ccbc73e3`

Numeric vertical values parsed: **false**.

## Stationary correction feasibility

| panel | candidate fixes | shared 100-m cells | supported individuals | frozen threshold | feasible |
|---|---:|---:|---:|---:|---|
| *Tadarida teniotis* | 46 | 0 | 0 | 5 | **NO** |
| *Eidolon helvum* | 4,790 | 3 | 4 | 10 | **NO** |
| *Hypsignathus monstrosus* | 21,430 | 7 | 12 | 12 | **YES** |
| *Phyllostomus hastatus* 2022 | 7,579 | 5 | 13 | 17 | **NO** |
| *P. hastatus* 2023 | 3,784 | 0 | 0 | 8 | **NO** |
| *P. hastatus* 2016 | 26,625 | 1 | 11 | 5 | **YES** |

Only *Hypsignathus* and *P. hastatus* 2016 are therefore authorized for the secondary
stationary-height correction. This list was frozen before any stationary-height outcome was
opened.

## Deployment/tag metadata

Existing reference metadata did not show multiple deployment/tag identifiers for most panels.
The 2022 *P. hastatus* source contained **2 individuals with multiple deployment IDs and 2 with
multiple tag IDs** in the available metadata. No inference is based on this count; it is reported
only because the individual=single-tag equivalence is not universally exact in that source.

## Tracking-window overlap

The timing audit is descriptive only.

| panel | repeat-individual pairs | positive window overlap | median positive overlap | median start-date difference |
|---|---:|---:|---:|---:|
| *Tadarida* | 21 | 0.714 | 29.2 h | 0.005 d |
| *Eidolon* | 107 | 0.860 | 83.5 h | 1.00 d |
| *Hypsignathus* | 276 | 0.917 | 179.9 h | 1.03 d |
| *P. hastatus* 2022 | 295 | 0.766 | 102.5 h | 1.02 d |
| *P. hastatus* 2023 | 66 | 1.000 | 77.9 h | 0.042 d |
| *P. hastatus* 2016 | 45 | 0.311 | 38.4 h | 4.01 d |

Five panels have substantial contemporaneous tracking among repeat individuals. The 2016
*P. hastatus* panel has much weaker temporal overlap and therefore carries a stronger residual
individual-versus-time limitation. Per the frozen contract, this does not trigger a new
time-block permutation family.
