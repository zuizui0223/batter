# Finite dynamic personal-state synthesis v2

## Status

Cross-programme post-outcome synthesis. This document combines already-opened results and support-matching diagnostics; it is not a new confirmatory analysis.

## Central mathematical claim

The current evidence is inconsistent with both extremes:

1. bat individuality is an irreducible, endlessly expanding high-dimensional fingerprint;
2. every bat carries one immutable scalar that determines every trajectory.

The evidence is better represented by a **finite-dimensional personal state with context-dependent expression and task-specific realization**:

[
mathbf z_i(t)inmathbb R^d,
]

[
mathbf y_{i,e,t}
=
oldsymbolmu_{e,t}
+
mathbf A_{e,t}mathbf z_i(t)
+
mathbf h_{i,e,t}
+
oldsymbolepsilon_{i,e,t},
]

with possible state transition

[
mathbf z_i(t+1)
=
mathbf F(mathbf z_i(t),mathrm{experience}_{i,t})
+
oldsymboleta_{i,t}.
]

## I. Rhinolophus obstacle-flight system: finite portable state

### Minimal dimension

Training-only cross-environment diagnostics:

- full 8-D policy K = +0.9436, 5/5 positive, p=.0001;
- PCA dimension 1 already sufficient: K=+0.9578, 5/5, p=.0006;
- supervised identity subspace dimension 1 sufficient: K=+0.8848, 5/5, p=.0021.

Thus the stable between-individual component is approximately one-dimensional even though PC1 explains only ~46.7% of total behavioural variance.

### Interpretable scalar

[
FlightIntensity=
rac{z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})}{4}.
]

- K=+0.4966;
- 5/5 positive;
- p=.0003.

Personal coordinates:

[
A=+1.070,quad C=+0.303,quad B=+0.175,quad E=-0.473,quad D=-0.790.
]

### Parameter recovery / convergence

Held-out MSE as independent training environments accumulate:

- 1 environment: .5359
- 2 environments: .4019
- 3 environments: .3573
- all non-target environments: .3409

[
MSE_1-MSE_3=+0.1786,
]

bootstrap 95% CI [+0.0527,+0.3336].

Three environments recover **91.6% [88.1,98.1]** of the finite-data improvement toward the full-training estimator.

All five bats individually show lower MSE at m=3 than at m=1.

Therefore the scalar behaves as a recoverable finite parameter rather than merely a discriminative embedding.

### Descriptive variance component

Bat × environment FlightIntensity centroids fitted as

[
y_{ie}=eta_e+u_i+epsilon_{ie}
]

give:
- bat variance .6239;
- residual variance .2300;
- descriptive ICC=.731.

This is descriptive because n_bats=5.

## II. Ordinary obstacle change mostly preserves the personal coordinate

Using theta estimated only from other environments:

[
y_{ie}approxmu_e+alpha_e	heta_i+epsilon_{ie}.
]

Six evaluable configurations give:

[
alpha_e=
0.77, 2.00, 0.93, 1.01, 1.00, 0.93.
]

All 6/6 are positive.

Permutation calibration:
- p for 6/6 positive alpha directions = .0364;
- mean-alpha magnitude p=.114.

Thus the direction of the same personal coordinate transfers broadly, while expression magnitude can vary.

## III. The Rhino result survives Mini-like sparse support

### Exactly two training environments

Even forcing every self/donor centroid to use exactly two non-target environments:

- PCA1 K=+.9098, 5/5 positive, p=.0005;
- FlightIntensity K=+.4690, 5/5 positive, p=.0002.

### Four bats + two environments + one training trajectory per environment

All five leave-one-bat-out four-individual subsets pass.

PCA1:
- omit A: K=.511, p=.0203
- omit B: K=1.202, p=.0007
- omit C: K=1.162, p=.0004
- omit D: K=.717, p=.0061
- omit E: K=1.021, p=.0010

FlightIntensity:
- omit A: K=.290, p=.0118
- omit B: K=.615, p=.0007
- omit C: K=.647, p=.0004
- omit D: K=.350, p=.0075
- omit E: K=.498, p=.0017

Therefore the Rhino–Mini contrast is not explained solely by:
- five versus four bats;
- more than two training environments;
- or within-environment averaging of repeated training trajectories.

## IV. Miniopterus: no detected portable linear personal state

N=19 trajectories, four bats; each bat occurs in exactly three environments.

### Family-wise calibrated unsupervised PCA dimensions 1–8

No dimension supported.

Representative results:
- d1 K=-.169, adjusted p=.372;
- d3 K=+.012, adjusted p=.286;
- d4 K=+.022, adjusted p=.280;
- d8 K=-.014, adjusted p=.328.

Yet PC1 explains ~58.8% of behavioural variance and four PCs explain ~97.1%.

### Family-wise calibrated supervised identity dimensions 1–3

No dimension supported:
- d1 K=.0195, adjusted p=.286;
- d2 K=.0222, adjusted p=.286;
- d3 K=-.0103, adjusted p=.286.

Therefore:

[
	ext{low-dimensional behaviour}
eq	ext{low-dimensional portable individuality}.
]

The current Mini archive supports no stable cross-environment **linear** personal parameter.

This does not imply infinite dimensionality; context switching, nonlinear structure, or weak stability remain possible.

## V. Strong learning can reorganize a finite personal state

Independent Yamada naive-to-familiar maximum-speed series.

### Reflective / smaller shared learning shift

- mean shift +.273 m/s;
- alpha=.800;
- r=.898;
- late/early SD ratio=.891;
- alpha exact p=.00218.

The naive personal ordering is strongly preserved.

### Permeable / larger shared learning shift

- mean shift +.892 m/s;
- alpha=.002;
- r=.003;
- late/early SD ratio=.771;
- alpha p=.498.

Individual variation remains substantial, but **which individual is high or low is reorganized**.

The between-condition alpha contrast is suggestive but not calibrated at .05:
p=.0997.

This motivates:

[
z_i^{late}=alpha z_i^{early}+eta_i^{learn}.
]

Low dimensionality therefore does not require immutability.

## VI. Task-specific spatial realization is a second component

Within obstacle configurations, absolute XY route/lane identity is supported:

[
A_{XY}approx+.226,quad p=.0003.
]

But:
- start position alone fails;
- end position alone fails;
- displacement vector fails;
- start-centered route identity fails;
- chord-residual route shape fails.

Thus the task-specific term is better described as **lane/spatial placement** than as one invariant memorized curve.

A single portable FlightIntensity theta therefore does not explain the entire trajectory.

The evidence requires at least:

[
oxed{
portable personal state z_i
+
task	ext{-}specific realization h_{i,e}
}
]

## VII. Ontogenetic timing does not follow one slow convergence curve

Harten first-outdoor-flight programme:

- personal self-history advantage already positive at the earliest estimable target day 3;
- late history strongly predictive, p=.0001, 12/14 positive;
- the frozen common monotonic-formation rule fails because only 8/14 individual slopes are positive despite a positive programme mean.

Thus the current data do not support one universal slow canalization curve.

A more compatible architecture is:

1. rapid early establishment / symmetry breaking;
2. persistent but noisy personal state;
3. individual-specific refinement;
4. possible reorganization after sufficiently strong task/learning transitions.

## VIII. Current taxonomy

### Type A — portable finite personal state

[
d	ext{ small},quad z_i(t)approx z_i
]

over ordinary environmental changes.

Current example:
*Rhinolophus nippon* obstacle FlightIntensity.

### Type B — finite but plastic personal state

[
z_i(t+1)
eq z_i(t)
]

under a strong learning transition while between-individual variance remains.

Current candidate:
Yamada permeable learning condition.

### Type C — nonportable/context-dominated individuality

No single environment-general linear z_i is detected.

Current example:
*Miniopterus fuliginosus* archive.

## IX. Answer to the “pi” question

The strongest non-convergence hypothesis is rejected for at least one system.

For Rhinolophus:
- d=1 is sufficient;
- theta estimates stabilize rapidly;
- held-out magnitude is predictable;
- the result survives severe support thinning.

Therefore the portable individual component is not behaving like an ever-expanding list of coefficients.

But exact trajectories are not one-dimensional because environment/task-specific realization and stochasticity remain.

The best present mathematical statement is:

> **Bat individuality can be a finite-dimensional dynamical state rather than either an immutable scalar or an irreducible trajectory fingerprint.**

The main unresolved object is now the transition law

[
mathbf F:
mathbf z_i(t)ightarrowmathbf z_i(t+1),
]

especially what environmental or experiential changes preserve, attenuate, or replace the personal state.
