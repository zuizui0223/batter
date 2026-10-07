# Rhino personal theta–sigma predictive model contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- one-dimensional personal-policy sufficiency;
- FlightIntensity scalar support;
- held-out scalar magnitude calibration;
- rapid convergence of the personal mean parameter theta;
- descriptive evidence that individuals differ in between-environment spread.

No held-out probabilistic comparison of individual-specific versus common variability has been calculated before this contract.

## Question

Is a bat's portable cross-environment behavioural signature adequately represented by one personal location parameter,

[
	heta_i,
]

plus common noise, or does each individual also carry a reproducible personal context-sensitivity / variability parameter,

[
sigma_i?
]

The two candidate stochastic models are:

### M1 — one personal parameter

[
y_{ie} = 	heta_i + epsilon_{ie},
qquad
epsilon_{ie}sim CommonNoise.
]

### M2 — two personal parameters

[
y_{ie} = 	heta_i + epsilon_{ie},
qquad
epsilon_{ie}sim IndividualNoise(sigma_i).
]

Here (y_{ie}) is the bat × environment mean FlightIntensity after the already-frozen within-environment standardization.

## Cross-environment folds

Leave one complete obstacle environment out.

For target environment e:

- training = all bat × environment centroids from environments other than e;
- target = all available centroids in e;
- target bat i requires at least **3** training environments.

All means and variance parameters are estimated from training environments only.

## Personal mean

For each target bat:

[
hat	heta_{i,-e}
=
mean(y_{i,e'}, e'
eq e).
]

This is exactly the scalar architecture already supported by the theta-convergence programme.

## M1 — common predictive variability

Within each training fold:

1. estimate one theta for every bat with >=2 training environments;
2. calculate residuals around each bat's training mean;
3. pooled residual variance:

[
s^2_{pool}
=
rac{sum_isum_{e'}(y_{ie'}-hat	heta_i)^2}
{sum_i(n_i-1)}.
]

For target bat i with n_i training environments use a Student-t predictive density with:

- location = (hat	heta_i);
- df = pooled residual df;
- scale = (s_{pool}sqrt{1+1/n_i}).

## M2 — personal predictive variability

For target bat i, estimate its training sample SD (s_i).

Use the exact finite-sample Student-t predictive distribution for a normal mean/variance with location and variance estimated from the focal individual's training environments:

- location = (hat	heta_i);
- df = (n_i-1);
- scale = (s_isqrt{1+1/n_i}).

No shrinkage or clipping of (s_i) is allowed after outcome opening.

If (s_i=0) or nonfinite, that target is structurally invalid.

## Primary endpoint

For every held-out target centroid:

[
G_{ie}
=
log p_{M2}(y_{ie})
-
log p_{M1}(y_{ie}).
]

Aggregate:
1. equal target environments within biological bat;
2. equal biological bat.

Primary programme statistic:

[
G = mean_i(mean_e G_{ie}).
]

Positive G means a personal variability parameter improves held-out probabilistic prediction beyond personal mean theta plus common variability.

## Uncertainty

Cluster bootstrap biological bats with replacement.

- B = 9,999
- seed = 20261007921

Report percentile 95% CI for G.

Support requires:
- G > 0;
- 95% lower bound > 0;
- at least 3/5 bats have positive individual mean G.

## Secondary diagnostic

For each held-out target compute:
- training personal SD (s_i);
- held-out absolute deviation (|y_{ie}-hat	heta_i|).

Report Spearman correlation across target bat × environment points.

This is descriptive and cannot rescue a failed primary endpoint.

## Interpretation

### M2 supported

> Individuals differ not only in a portable mean policy coordinate theta, but also in how strongly that policy is perturbed across environments.

The compact stochastic representation becomes:

[
y_{ie}
=
	heta_i
+
sigma_i z_{ie},
]

with additional task-specific structure allowed elsewhere in the full movement model.

### M2 unsupported

> The current archive supports a personal mean theta, but does not show that individual-specific variability improves prediction beyond a common-noise model.

## Claim ceiling

A supported sigma does not uniquely mean behavioural plasticity. It can also absorb:
- measurement error;
- unobserved task differences;
- state dependence;
- unequal within-environment sampling.

It is a predictive individual context-sensitivity parameter, not automatically a biological reaction-norm slope.
