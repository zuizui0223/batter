# Theta signal-to-noise synthesis v1

## Status

Post-primary mathematical synthesis from already-opened *Rhinolophus nippon* FlightIntensity theta summaries.

No new biological endpoint is created here.

## Individual parameter and environmental expression

For each bat i:

[
y_{i,e} = 	heta_i + eta_{i,e},
]

where:
- (	heta_i) is the equal-environment mean FlightIntensity coordinate;
- (eta_{i,e}) is the environment-specific deviation.

Observed theta values:

- A: +1.0699
- C: +0.3028
- B: +0.1746
- E: -0.4735
- D: -0.7904

Between-environment SD:

- A: 0.3061
- B: 0.6104
- C: 0.8319
- D: 0.1613
- E: 0.3943

## Pairwise prediction from a Gaussian signal-to-noise model

For pair i,j define

[
SNR_{ij}
=
rac{|	heta_i-	heta_j|}
{sqrt{sigma_i^2+sigma_j^2}}.
]

If environment-specific deviations are approximately independent Gaussian noise, expected probability that the observed ordering matches the global theta ordering is

[
P_{ij}
approx
Phi(SNR_{ij}).
]

The already-opened pairwise rank-stability data provide an empirical accuracy for every bat pair.

| pair | SNR | observed order accuracy | Gaussian prediction |
|---|---:|---:|---:|
| B-C | 0.124 | 0.333 | 0.549 |
| D-E | 0.744 | 0.800 | 0.772 |
| C-E | 0.843 | 0.750 | 0.800 |
| A-C | 0.865 | 0.667 | 0.807 |
| B-E | 0.892 | 1.000 | 0.814 |
| C-D | 1.290 | 1.000 | 0.901 |
| A-B | 1.311 | 1.000 | 0.905 |
| B-D | 1.529 | 1.000 | 0.937 |
| A-E | 3.092 | 1.000 | 0.999 |
| A-D | 5.377 | 1.000 | 1.000 |

Across pair × common-environment observations:

- observed ordering accuracy: **0.857**
- Gaussian SNR prediction: **0.848**

Mean absolute pair-level difference between observed and predicted accuracy is ~0.088.

Descriptively, pairwise SNR and observed ordering accuracy are strongly monotonic:
Spearman rho ~ **0.833**.

This correlation is post-outcome and not treated as a new confirmatory test.

## Interpretation

The main instability is concentrated in near-ties.

The clearest example is B versus C:

[
|	heta_B-	heta_C|=0.128,
]

while their combined environment-expression noise scale is ~1.032, yielding SNR ~0.124.

Large-separation pairs, especially A-D and A-E, preserve their ordering across every common environment.

Thus a simple model captures much of the apparent complexity:

[
oxed{
observed individual state
=
stable theta_i
+
environmental expression noise
}
]

and predictability is controlled by the ratio of between-individual separation to within-individual environmental variability.

## Consequence

The relevant mathematical question is not only whether theta exists.

It is whether two individuals are **resolvable** given environment-dependent expression noise.

A practical resolution criterion is therefore pair-specific:

[
|	heta_i-	heta_j|
gg
sqrt{sigma_i^2+sigma_j^2}
]

for robust ordering.

This explains how a finite one-dimensional personal parameter can coexist with occasional environment-specific rank reversals.

## Ceiling

This is a descriptive Gaussian approximation.

It does not establish:
- normal residual distributions;
- independence of environment deviations across bats;
- a mechanistic source of sigma;
- lifetime stationarity of theta or sigma.
