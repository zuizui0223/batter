# P2 transparent I/M endpoint appendix v1

## Status

**PROSPECTIVE FIXED REPRESENTATION. NO NEW EXPERIMENTAL OUTCOME OPENED.**

This appendix carries the transparent Rhino policy representation into the solution-repertoire experiment without refitting weights to the new identity outcome.

Source definitions:
- TRANSPARENT_TWO_AXIS_POLICY_CONTRACT_V1.md;
- FLIGHT_INTENSITY_SCALAR_CONTRACT_V1.md;
- rhino_configuration_identity_primary_v1.py.

## Raw trajectory features

For every valid flight trajectory, after sorting by time:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. path efficiency;
8. vertical range.

### Speed

For every consecutive pair with positive dt:

speed = Euclidean 3-D displacement / dt.

### Absolute vertical speed

abs_vspeed = absolute vertical displacement / dt.

### Absolute horizontal turning rate

For each horizontal displacement with positive dt and nonzero horizontal length:
- heading = atan2(dy, dx);
- wrapped heading change is atan2(sin(delta heading), cos(delta heading));
- turn interval is 0.5 × (preceding dt + following dt);
- absolute horizontal turning rate = abs(wrapped heading change) / turn interval.

### Path efficiency

path_efficiency = straight-line 3-D displacement from first to last point / summed 3-D path length.

### Vertical range

vertical_range = max(z) - min(z).

## Structural trajectory support

The original Rhino implementation required >=100 rows and >=50 positive-dt movement intervals.

For the new experiment, tracking frequency and trial duration may differ. Therefore the exact minimum row/interval support must be frozen in the engineering/data-acquisition receipt before common-OPEN outcomes are opened.

Do not tune support using identity results.

## Label-free acquisition scaling

The original Rhino analysis standardized features within environment.

For the new experiment, probe data must not define their own scaling.

Therefore, for each matched environment family A and B separately:

1. pool all structurally valid **Phase-1 acquisition trajectories** across all randomized animals;
2. ignore biological identity and OPEN/CONSTRAINED labels when estimating scaling;
3. compute the family-specific mean and sample SD for each of the eight raw features;
4. freeze those 8 means and 8 SDs;
5. apply the same frozen family-specific transform unchanged to:
   - Phase-1 histories;
   - common OPEN probe;
   - suppression;
   - exact reopening;
   - transformed transfer belonging to that family.

If any acquisition feature SD is zero or nonfinite in either family:
**PRIMARY REPRESENTATION STOP.**

No probe/reopening/transfer outcome contributes to scaling.

## Transparent policy coordinates

Let z1...z8 be the eight family-standardized features in the order above.

### FlightIntensity

I = mean(z1, z2, z3, z4).

Equal weights only.

### ManeuveringExtent

M = mean(-z1, z5, z6, z7, z8).

Equal weights only.

Do not:
- refit weights;
- rotate axes;
- rescale I and M separately after construction;
- replace M if it performs poorly;
- substitute an H/V decomposition after outcome opening.

## Primary policy distance

For two policy vectors theta_a = (I_a, M_a) and theta_b = (I_b, M_b):

d(theta_a, theta_b) = ordinary Euclidean distance in the fixed 2-D I/M plane.

No Mahalanobis metric, learned metric or axis-specific weighting.

## P2 common-OPEN held-out identity

P2 is measured entirely inside the frozen common-OPEN probe.

For each individual × family:
1. use the early half of the frozen probe to calculate an equal-trial I/M centroid;
2. use early-probe centroids from all other eligible individuals in the same family as donors, regardless of acquisition treatment;
3. score every late-probe target trial by Euclidean distance to own early centroid versus mean distance to donor early centroids;
4. average target advantages equally within individual × family.

Call the resulting family-specific score A_i,f.

The randomized acquisition assignment is applied only after these family-specific scores are fixed:

Delta_A = mean_i [ A_i,OPEN-family - A_i,CONSTRAINED-family ].

Thus P2 asks whether prior solution opportunity causes stronger reproducible I/M organization under equal current opportunity.

Acquisition trajectories define scaling but are **not** the P2 prediction history.

## Leakage firewall

Nothing from common-OPEN probe, reopening or transformed-transfer outcomes may be used to choose:
- scaling;
- weights;
- feature inclusion;
- trajectory validity thresholds;
- distance metric;
- probe split.

Any structural change before outcome opening requires a new version of this appendix and a documented reason.
