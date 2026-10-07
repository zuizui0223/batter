# Rhino individual reaction-norm rank contract v1

Status: POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.

Known before freezing:
- transferable Rhinolophus nippon movement-policy signal is supported;
- one movement-feature latent axis is sufficient for identity;
- FlightIntensity scalar converges rapidly as environments accumulate;
- scalar held-out prediction is strong for some individuals but context residuals are large for others, especially B and C.

Question:
Is one portable individual coordinate sufficient across obstacle environments, or are two/three stable context-response parameters needed?

Model:
y_ie = mu_e + u_i^T v_e + epsilon_ie.

Data:
Use exact FlightIntensity bat-by-environment centroids: 5 bats, 7 environments, 25 observed cells.

Outer target gate:
- environment has at least 4 observed bats before holdout;
- bat occurs in at least 4 environments.
Expected 17 outer cells: A=2, B=3, C=4, D=4, E=4, environments 1-4.

Models:
R0 environment-only equal-bat mean.
R1/R2/R3 regularized low-rank models with rank 1,2,3.

Ridge lambda grid: 0.01, 0.1, 1, 10, 100.
Environment intercepts unpenalized.

Fitting:
Alternating ridge least squares.
SVD initialization plus fixed random starts 1101-1105.
Maximum 500 iterations.
Relative objective convergence threshold 1e-10.

Nested lambda selection:
For every outer target and rank, remove outer target. Use training-only inner leave-one-cell-out validation. Inner cells require environment support >=3 and bat support >=3. Choose lambda minimizing inner MSE, largest lambda among ties within 1e-12. Refit on full outer training and predict outer target.

Aggregation:
Equal target cells within bat, then equal bats.
Report equal-bat MSE/MAE and raw-cell MSE.

Primary increments:
I1 = MSE_R0 - MSE_R1
I2 = MSE_R1 - MSE_R2
I3 = MSE_R2 - MSE_R3

Uncertainty:
Cluster bootstrap biological bats, B=9999, seed 20261007901.
An increment is supported if its 95% percentile CI lower bound is >0.

Interpretation:
- I1 supported, I2/I3 unsupported: one individual coordinate sufficient.
- I2 supported: at least two required.
- I3 supported after I2: at least three required.
- no I1: no stable low-rank reaction norm beyond environment means.

Ceiling:
Only 25 centroid cells and five bats. Failure of higher rank does not prove biological absence; support is predictive, not a unique mechanistic decomposition.
