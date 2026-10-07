# Finite personal core + context-specific realization synthesis v1

## Status

Post-primary synthesis of already-opened mathematical-structure diagnostics. This file does not create a new confirmatory endpoint.

## Central question

Can individual bat flight differences be recovered as a finite mathematical object, or does each new environment require an indefinitely expanding individual-specific description?

## 1. Portable individual component: finite and one-dimensional in Rhinolophus

For *Rhinolophus nippon*:

- full 8-D cross-configuration movement-policy identity:
  - K = +0.94356
  - 5/5 bats positive
  - p = 0.0001
- training-only PCA:
  - minimal sufficient dimension = 1
  - K_1D = +0.95785
  - 5/5 positive
  - p = 0.0006
- training-only supervised identity subspace:
  - minimal sufficient dimension = 1
  - K_1D = +0.88483
  - 5/5 positive
  - p = 0.0021
- transparent FlightIntensity scalar:
  - K = +0.49656
  - 5/5 positive
  - p = 0.0003

Thus dimensions 2–8 are not required to preserve the transferable individual component.

A compact personal coordinate is

\[
\theta_i \approx
\frac{
z(v_{med})+
z(v_{90})+
z(|v_z|_{med})+
z(|v_z|_{90})
}{4}.
\]

Descriptive full-data coordinates:

- A: +1.0699
- C: +0.3028
- B: +0.1746
- E: -0.4735
- D: -0.7904

## 2. Theta is not merely a classifier coordinate

Held-out one-parameter magnitude calibration:

- through-origin slope = 1.0314
- Pearson r = 0.5548
- equal-pair sign accuracy = 0.8217
- p_beta = 0.0014
- p_r = 0.0162
- p_sign = 0.0065

A scalar estimated in other configurations therefore predicts both ordering and meaningful magnitude of individual differences in a held-out configuration.

## 3. Theta estimate converges as independent environments accumulate

Authoritative convergence workflow:
- run 37620420211
- artifact 11483226773

Held-out MSE:

- 1 training environment: 0.5359
- 2: 0.4019
- 3: 0.3573
- all non-target environments: 0.3409

Primary convergence contrast:

\[
MSE_1-MSE_3=+0.17864
\]

bat-cluster bootstrap 95% CI:

\[
[+0.05266,+0.33357].
\]

Fraction of finite-data improvement toward the full estimator:

- 2 environments: 68.7%
- 3 environments: 91.6%, 95% CI [88.1%,98.1%]

Estimator spread of subset theta estimates:

- m=1: 0.3823
- m=2: 0.2145
- m=3: 0.0985

Therefore the portable individual coordinate behaves like a finite recoverable parameter rather than an indefinitely expanding fingerprint.

## 4. Stable core does not mean fixed expression

Independent learning data from Yamada et al. show that a common learning shift can coexist with personal information.

Prospective personal speed-state result:
- K = +0.52771
- p = 0.0052
- 12/14 bats positive

Post-primary expression-strength diagnostic:

Permeable / stronger-learning condition:
- mean speed shift = +0.8925 m/s
- alpha = +0.00198
- r = 0.0026
- p_alpha = 0.498

Reflective / weaker-learning condition:
- mean speed shift = +0.2734 m/s
- alpha = +0.7997
- r = 0.8980
- p_alpha = 0.00218

Direct difference:

\[
\Delta\alpha=+0.7977,\quad p=0.0997.
\]

Thus context-dependent expression is suggestive, not confirmed.

A useful model is

\[
x_{i,e,t}
=
\mu_{e,t}
+
\alpha_{e,t}\theta_i
+
h_{i,e,t}
+
\epsilon_{i,e,t}.
\]

## 5. How much variance is stable theta?

A descriptive REML model on 25 bat × environment FlightIntensity centroids gives:

- stable bat variance = 0.6239
- residual bat × environment variance = 0.2300
- descriptive ICC = 0.731

So roughly 73% of centroid-level variance under that model is assigned to the stable between-bat component.

This is descriptive because only five bats are available.

## 6. Rank reversals are concentrated in unresolved near-ties

A simple signal-to-noise description uses

\[
SNR_{ij}
=
\frac{|\theta_i-\theta_j|}
{\sqrt{\sigma_i^2+\sigma_j^2}}.
\]

The Gaussian approximation predicts observed pair ordering well:

- observed pair × common-environment ordering accuracy = 0.857
- Gaussian SNR prediction = 0.848
- mean absolute pair-level prediction error ≈ 0.088
- pairwise SNR versus observed ordering accuracy: Spearman rho ≈ 0.833

The unstable B–C pair has very small theta separation relative to environmental expression noise.

Thus occasional rank reversals do not require a non-convergent personal law.

## 7. A separate personal sigma does not improve prediction

Authoritative theta-sigma predictive model:

- personal-sigma gain over common-sigma model = -0.0782
- positive bats = 2/5
- bat-cluster bootstrap 95% CI [-0.3944,+0.2379]

Verdict:
THETA_ONLY_NO_PERSONAL_SIGMA_GAIN.

Therefore the individual is not better represented simply by two parameters \((\theta_i,\sigma_i)\).

## 8. The unresolved term is context-specific realization h_i,e

A shared environment-specific affine transform,

\[
y_{ie}=\gamma_e+\alpha_e\theta_i+\epsilon,
\]

does not improve held-out prediction.

On the 17 structurally eligible target cells:

- portable-theta-only MSE = 0.3216
- context-affine theta MSE = 1.3048

Thus the environment-specific deviations are not captured by a common rescaling of the theta axis.

Unregularized low-rank completion of the residual interaction is numerically non-identifiable in the sparse 5 × 7 incidence matrix and was stopped.

A nested-CV ridge low-rank reaction-norm test of ranks 1–3 also finds no supported incremental rank:

- rank-1 increment I1 = -0.3585, unsupported
- rank-2 increment I2 = +0.2945, unsupported
- rank-3 increment I3 = +0.2744, 95% CI crosses zero
- classification: NO_STABLE_LOW_RANK_REACTION_NORM

This does not mean h is infinitely dimensional.

It means the current sparse centroid matrix does not support a portable rank-1/2/3 reaction-norm representation of h.

## 9. Where h seems to live biologically

Target-environment transfer profiles show:

Movement policy:
- broadly transferred in 6/7 environments

Scale-free geometry policy:
- broadly transferred in 3/7 environments

Pulse policy:
- broadly transferred in 5/7 environments

Thus the most portable part is the movement-policy/performance component, while detailed geometry is more context sensitive.

Within a fixed obstacle configuration, absolute-coordinate route/lane identity is supported, but translation-invariant route shape is not.

The best current biological reading is:

> theta is a portable personal control/performance prior; h is the context-specific realized solution, often expressed through where/how the animal flies in that particular task rather than through a second universal personal axis.

## 10. Miniopterus does not establish an infinite-dimensional counterexample

For *Miniopterus fuliginosus*:

Unsupervised PCA dimensions 1–8:
- no dimension sufficient

Training-only supervised identity dimensions 1–3:
- no dimension sufficient

However, support-matched positive controls impose an important ceiling.

### Severe generic support thinning of Rhino

With four bats, exactly two training environments, and one trajectory per training environment:

- Rhino PCA1 supported in all 5/5 four-bat subsets
- Rhino FlightIntensity supported in all 5/5 subsets

Thus simple reductions in bat count, number of training environments, and within-cell averaging do not erase the Rhino signal.

### Exact Mini occupancy support

When the exact sparse Mini bat × environment occupancy pattern is imposed on Rhino:

- 4,212 exact mappings
- median Rhino K = +0.971
- K > 0 in 96.0% of mappings
- but frozen formal detection occurs in only 101/256 calibrated mappings = 39.45%

Therefore exact sparse occupancy can strongly reduce inferential power even when a positive Rhino-like signal is present.

The correct comparison is:

> Rhino: a low-dimensional personal parameter is positively identified and convergent.

> Mini: no portable linear personal parameter is identified in the current archive.

This is an evidence-strength asymmetry, not proof that Mini is high-dimensional or mathematically non-convergent.

## 11. Current mathematical answer

The strongest supported decomposition is

\[
\boxed{
\text{realized behaviour}
=
\text{environment}
+
\text{finite personal core}
+
\text{context-specific realization}
+
\text{trial noise}
}
\]

or

\[
\boxed{
x_{i,e,t}
=
\mu_{e,t}
+
\alpha_{e,t}\theta_i
+
h_{i,e,t}
+
\epsilon_{i,e,t}.
}
\]

For *Rhinolophus*, the portable individual core is approximately one-dimensional and rapidly estimable.

The exact realized trajectory is not one-dimensional because h and epsilon remain.

Therefore the current answer to the “pi / non-convergent individual equation” question is:

> **the portable individual component is convergent and finite; the unresolved complexity is primarily in how that finite personal core is realized in each environment, not in an endlessly expanding personal parameter vector.**

## 12. Strongest remaining mathematical discriminator

To decide whether h itself is finite-dimensional, the next data need either:

1. denser same-individual × environment coverage; or
2. measured quantitative descriptors of each environment.

Then fit

\[
h_{i,e}=g(\phi_e;\psi_i),
\]

where \(\phi_e\) is the measured obstacle/resource/environment vector.

The decisive question becomes:

> does a small finite \(\psi_i\) predict a new environment after theta is known?

That is the remaining route toward a fuller individual equation.
