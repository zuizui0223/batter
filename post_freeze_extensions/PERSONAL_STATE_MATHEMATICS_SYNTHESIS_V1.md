# Personal-state mathematics synthesis v1

## Core mathematical object

The current bat results are most naturally represented by a latent personal state:

[
mathbf z_i(t)inmathbb R^d
]

with environment-specific expression

[
mathbf y_{i,e,t}
=
oldsymbolmu_{e,t}
+
mathbf A_{e,t}mathbf z_i(t)
+
mathbf h_{i,e,t}
+
oldsymbolepsilon_{i,e,t}.
]

Personal state can itself change through experience:

[
mathbf z_i(t+1)
=
mathbf F(mathbf z_i(t),,mathrm{experience}_{i,t})
+
oldsymboleta_{i,t}.
]

This separates three mathematical questions that should not be conflated:

1. **dimensionality** — how large must d be?;
2. **portability** — does the same z predict behaviour in a new environment?;
3. **plasticity** — does z remain fixed or transition with experience?

## System 1 — Rhinolophus obstacle flight

### Dimensionality

Training-only PCA:
- minimal sufficient d = **1**;
- K(d=1)=+0.9578, p=.0006, 5/5 positive;
- full d=8 K=+0.9436.

Training-only supervised identity subspace:
- minimal sufficient d = **1**;
- K=+0.8848, p=.0021.

Thus the persistent between-individual component is one-dimensional even though PC1 explains only ~46.7% of total behavioural variance.

### Convergence

FlightIntensity theta estimate:

- m=1 training environment: MSE=.5359;
- m=2: .4019;
- m=3: .3573;
- full non-target estimator: .3409.

Three environments recover:
**91.6% [88.1,98.1%]**
of the finite-data improvement toward the full estimator.

Thus the scalar personal coordinate is recoverable and rapidly stabilizing.

### Environment expression

For six evaluable held-out obstacle configurations:

[
alpha_e =
0.77, 2.00, 0.93, 1.01, 1.00, 0.93.
]

All 6/6 are positive; permutation p for six positive environments = .0364.

Therefore ordinary obstacle changes retain the direction of the personal coordinate even if expression gain varies.

### Current type

[
oxed{	ext{portable convergent low-dimensional personal state}}
]

## System 2 — Rhinolophus learning transition

Yamada naive -> familiar maximum-speed state.

### Reflective / weaker-learning context

- common mean shift +0.273 m/s;
- alpha=.800;
- r=.898;
- familiar/naive SD ratio=.891.

The old personal ordering largely survives.

### Permeable / stronger-learning context

- common mean shift +0.892 m/s;
- alpha=.002;
- r=.003;
- familiar/naive SD ratio=.771.

Individual variation remains substantial, but the naive ordering no longer predicts which individuals are high or low after learning.

Thus this is not simple homogenization.

It is compatible with a personal-state transition:

[
z_i^{late}
=
alpha z_i^{early}
+
eta_i^{learn}.
]

### Current type

[
oxed{	ext{low-dimensional individuality with context-dependent state replacement}}
]

The direct between-condition alpha contrast remains suggestive rather than calibrated at .05 (p=.0997).

## System 3 — Miniopterus obstacle flight

N=19 trajectories, four bats.

### Unsupervised PCA scan

No d=1...8 is sufficient.

Largest positive K values are tiny:
- d=3: +.0121, p=.283;
- d=4: +.0220, p=.243.

PC1 nevertheless explains ~58.8% of total behavioural variance.

### Supervised identity subspace

No d=1...3 is sufficient:
- d=1: K=.0195, p=.292;
- d=2: K=.0222, p=.246;
- d=3: K=-.0103, p=.232.

Thus even an identity-targeted linear subspace fitted on training environments does not transfer.

### Current type

[
oxed{	ext{no detected portable linear personal state in current data}}
]

This does not imply infinite dimension.

Possible explanations include:
- stronger environment dependence;
- rapid state switching;
- nonlinear personal structure;
- weak repeatability;
- insufficient archive size.

## General conclusion

The contrast is not:

> every bat has one immutable scalar.

Nor is it:

> bat individuality is mathematically irreducible.

Instead, individual specialization can occupy different regimes of the same latent-state model.

A useful taxonomy is:

### Type A — stable finite personal parameter

[
d	ext{ small},quad z_i(t)approx z_i,quad A_e z_i	ext{ transfers}.
]

Current example:
Rhinolophus obstacle FlightIntensity.

### Type B — finite but plastic personal state

[
d	ext{ small},quad z_i(t+1)
eq z_i(t),
]

while individual variance remains.

Current candidate:
Rhinolophus under strong spatial-learning transition.

### Type C — context-specific / nonportable individuality

[
z_{i,e}
]

cannot presently be replaced by one environment-general linear z_i.

Current example:
Miniopterus archive.

## Relation to the “pi” question

The strongest version of the non-convergence hypothesis is rejected for at least one system:

- finite d=1;
- estimator convergence is observed;
- cross-environment magnitude calibration is observed.

But the results also reject the opposite extreme of one universal fixed scalar.

The mathematically interesting object is therefore a **finite-dimensional dynamical personal state**, not an infinite decimal-like fingerprint:

[
oxed{
mathbf z_i(t+1)=F(mathbf z_i(t),E_t)+eta_t
}
]

with behaviour generated by

[
oxed{
mathbf y_{i,t}=G(E_t,mathbf z_i(t))+epsilon_t.
}
]

The next major question is no longer whether a compact equation can exist.

It is:

> **what determines the state-transition function F, and when does a stable personal coordinate persist versus reset?**
