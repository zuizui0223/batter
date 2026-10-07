# Theta variance-component diagnostic v1

## Status

Descriptive post-outcome diagnostic from the already-authoritative FlightIntensity bat × environment centroid table. Not an independent hypothesis test.

## Model

Using the 25 observed *Rhinolophus nippon* bat × environment FlightIntensity centroids:

[
y_{ie}=eta_e+u_i+epsilon_{ie},
]

with:
- environment as a fixed categorical effect;
- bat as a random intercept;
- REML estimation.

The scalar had already been standardized within environment at the trajectory level before bat × environment centroids were constructed.

## Result

- bat random-intercept variance: **0.6239**
- residual bat × environment variance: **0.2300**

Descriptive repeatability:

[
ICC=
rac{0.6239}{0.6239+0.2300}
=
mathbf{0.731}.
]

## Interpretation

At the bat × environment centroid level, roughly 73% of the variance remaining under this model is assigned to a stable between-bat component rather than bat × environment residual variation.

This is consistent with the stronger held-out evidence:
- one-dimensional identity transfer;
- theta convergence;
- held-out magnitude calibration;
- positive expression direction across obstacle configurations.

Because there are only five bats and the model was fitted after these outcomes were known, this ICC is descriptive and should not be promoted as a population repeatability estimate.
