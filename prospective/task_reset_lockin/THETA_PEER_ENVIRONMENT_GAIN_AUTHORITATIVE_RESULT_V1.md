# Peer-calibrated common environmental gain — authoritative result v1

## Execution and disclosure

- Workflow run: [37724251631](https://github.com/zuizui0223/batter/actions/runs/37724251631)
- Execution SHA: `ef9debc7de46b929db72af62e9d11e4591326094`
- Conclusion: success
- Artifact: 11527685584

This is a **post-outcome mechanism diagnostic**, not independent confirmation.

The first two runs failed an erroneously expected structural count (22), because Env4 actually contains five bats. The [structure-only amendment](THETA_PEER_ENVIRONMENT_GAIN_STRUCTURE_AMENDMENT_V1.md) discloses the correction to **23** eligible targets. The model, inclusion rule, ridge, clipping and scoring were never changed. The correction occurred after a local preliminary outcome had been inspected and is **not** portrayed as preregistration.

## Test

Baseline M0: an individual's own mean relative FlightIntensity from its other configurations.

M1: multiply the same individual estimate by a shared context gain estimated **only from other bats currently in the test configuration**, with the predeclared ridge alpha prior of 1, ridge strength 1 and clip [0,2]. The focal bat's target is excluded from both predictions.

The test asks whether conspecific responses transfer as a single common multiplier.

## Results

23 eligible bat×configuration targets, five bats.

| model | equal-bat MSE |
|---|---:|
| M0: individual theta only | **0.27744893** |
| M1: peer-derived alpha × theta | **0.32294556** |

Mean M0–M1 gain:
\[
G = -0.04549663.
\]

Relative MSE change of M1 versus M0: **+16.4% error**.

Bat-cluster bootstrap (B=9,999, seed 20261008131): 95% CI for gain **[−0.07707, −0.01710]**. All **5/5** bats have negative gain.

| bat | target contexts | M0−M1 MSE gain |
|---|---:|---:|
| A | 4 | −0.106917 |
| B | 3 | −0.000815 |
| C | 5 | −0.055141 |
| D | 6 | −0.023079 |
| E | 5 | −0.041531 |

Frozen descriptive support criterion: **FAIL**.

The peer-informed common environmental multiplier, under the tested estimator and support, did not improve prediction; the fixed personal scalar was better.

## Biological interpretation and ceiling

This argues against the **specific tested operational model** in which bats within a given configuration share a transferable multiplicative change in the personal vigor axis.

It does **not** show alpha is exactly 1, establish that environments have no shared effect, nor prove that individual-specific learning/response norms are required. Other estimators, nonlinear structures, and source sampling effects remain.

The target environment is not entirely unobserved in M1: peer outcomes in that environment are used. M0 is therefore a stronger deployment-friendly baseline.

On the currently accessible data, the better hypothesis is:

\[
y_{ie}\approx\theta_i+h_{ie}+\epsilon_{ie},
\]

where \(h_{ie}\) may encode personally differentiated environmental responses or sampling/context noise.

Together with [the theta correspondence audit](https://github.com/zuizui0223/batter/blob/post-freeze/theta-correspondence-audit-v1/prospective/task_reset_lockin/THETA_CORRESPONDENCE_AUDIT_AUTHORITATIVE_RESULT_V1.md), this yields:
- scalar personal history predicts in the observed five-bat system overall under a proper identity-permutation null;
- single scalar reliability is heterogeneous: positive absolute held-out gains in A,D,E, negative in B,C;
- a shared context multiplier calibrated using peers fails to improve that prediction;
- neither observation establishes a unique dynamical law nor the biological cause of contextual heterogeneity.
