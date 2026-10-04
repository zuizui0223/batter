# Flight-intensity component decomposition contract v1

## Status

**POST-PRIMARY INTERPRETABILITY DIAGNOSTIC.**

Frozen after:
- one-dimensional Rhino PCA1 was sufficient;
- PCA1 squared loadings were dominated by the four speed / vertical-speed features;
- the transparent four-feature FlightIntensity scalar was supported.

No component-specific scalar result has yet been calculated.

## Question

What does the one-dimensional Rhino policy axis actually represent?

Use the exact environment-standardized Primary-B features for the 45 *Rhinolophus nippon* trajectories.

## Scalars

### S1 — total-speed scalar

`Speed = mean(z_median_speed, z_p90_speed)`.

### S2 — vertical-speed scalar

`VerticalSpeed = mean(z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`.

### S3 — coupled intensity scalar

Reference:
`FlightIntensity = mean(Speed components, VerticalSpeed components)`.

This is the already-supported transparent scalar and is reported only for comparison.

### S4 — verticality contrast

`Verticality = VerticalSpeed - Speed`.

This asks whether individuals differ not just in movement vigor but in vertical motion relative to overall speed.

## Cross-configuration estimator

For S1, S2 and S4 use the exact leave-one-environment-out scalar identity estimator:
- target environment held out;
- training environment bat means first;
- equal training-environment weighting within bat;
- target advantage = mean absolute distance to other-bat centroids - distance to own centroid;
- equal target -> equal bat.

## Null

Within every environment independently permute complete bat×environment scalar clusters among labels.

9,999 permutations.

Seeds:
- S1: 202610042321
- S2: 202610042322
- S4: 202610042324

One-sided p.

## Diagnostic support

A scalar component is descriptively supported if:
- K > 0;
- p <= 0.05;
- >=70% evaluable bats positive.

## Interpretation

- S1 and S2 both supported: dominant axis is broad movement intensity/vigor.
- S1 supported, S2 weak: mostly total flight-speed tendency.
- S2 supported, S1 weak: mostly vertical movement intensity.
- S4 supported: individuals differ in relative verticality beyond common vigor.
- S1/S2 supported but S4 unsupported: vertical speed likely covaries with a common vigor axis rather than forming a separate vertical strategy.

No morphology or physiology is inferred.
