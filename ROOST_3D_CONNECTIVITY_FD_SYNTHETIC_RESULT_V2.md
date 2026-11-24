# V2 synthetic sensitivity — terrain arrangement at matched airspace volume
Status: executed locally with NumPy/SciPy; no ecological empirical result.
Reproduce: python scripts/roost_connectivity_sensitivity_v2.py (writes 189-row CSV beside script).

## Design
20 x 20 x 12 six-neighbour voxels. Ground elevation is an integer count of blocked layers; voxel-centre AGL defines the edge conductance exp(-beta*(mean AGL/12-0.5)). Three arbitrary hypothetical trait coefficients (-b,0,+b), b=1,3,6; same species weights and trait distances in every comparison; Rao Q=4/9. Fixed source and three sinks (central low, offset low, central high). For each nominal elevation amplitude (3,6,9), four terrain rank arrangements share the exact ground-height histogram and identical valid-airspace counts (4600,4360,4080 respectively). Patchy arrangement has four seeds; others deterministic. 189 scenarios, 567 solves. Analytical series and parallel resistor checks, source/sink reversal, and global conductance scaling checks passed. Largest Kirchhoff/energy residual 4.20e-12.

## Matched contrasts
Percent difference = 100*(Qspace_arrangement/Qspace_transverse-1), matched on amplitude, endpoint and trait contrast. Patchy results pool its four seeds. Counts are sensitivity scenarios, not independent biological replicates. Qspace uses normalized absolute incident current scores, not observed space use.

| Arrangement | Positive / N | Median % | Min % | Max % |
|---|---:|---:|---:|---:|
| Longitudinal ridge | 27/27 | 9.991 | 1.970 | 30.863 |
| Patchy | 108/108 | 5.000 | 0.511 | 21.653 |
| Gapped ridge | 16/27 | 0.423 | -1.770 | 6.371 |

| Nominal amplitude | Longitudinal median % | Patchy median % | Gapped median % |
|---|---:|---:|---:|
| 3 | 4.549 | 2.141 | -0.658 |
| 6 | 13.779 | 7.571 | 0.423 |
| 9 | 19.720 | 14.831 | 5.469 |

Absolute Qspace across all scenarios = 0.039956 to 0.252156, against constant Rao Q=0.444444. Matched contrast demonstrates that spatial arrangement alone, with equal height histogram and accessible airspace volume, can change the model-derived trait-current dissimilarity index. It does NOT establish true FD or coexistence, universal positive effect, or calibrated resistance. Increasing amplitude also reduces accessible volume across amplitude levels (within-level comparisons control volume, between-level comparisons do not). Fixed ceiling, voxel resolution, smoothness and different local slope/roughness distributions remain potential contributors; the rank rearrangement does not match edge-level geometry. No test of actual wing traits, food, cave locations, wind or actual movement yet.

## Next gate
1. Audit tracking sources for independently verified roost locations, simultaneous x/y/z, altitude datum, coverage and held-out units. Start without claiming all roosts are caves.
2. Validate 2D vs 3D circuit scores against held-out movement or endpoint choice; fit only training data, no trajectory-derived sink leakage.
3. Audit external species trait and cave assemblage data; community FD must be independent of accessibility model fitting, with richness/effort and regional candidate pool controlled. A separate empirical analysis is required before any ecological claim.
