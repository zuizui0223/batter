# Dynamic personal-parameter synthesis v1

## Core update

The current evidence supports a low-dimensional personal parameter, but not a universally immutable one.

For *Rhinolophus nippon* obstacle-flight data:

- one latent dimension is sufficient for cross-configuration identity;
- a transparent FlightIntensity scalar transfers across obstacle configurations;
- the scalar estimate converges rapidly as independent environments accumulate;
- ordinary obstacle configurations preserve the individual axis well enough for held-out magnitude prediction.

For the independent Yamada learning experiment:

- a shared learning shift occurs;
- personal information persists overall;
- but the expression of naive individual position differs sharply between acoustic learning contexts.

## Two distinct forms of plasticity

### Reflective condition

- mean shift: +0.273 m/s
- alpha = 0.800
- r = 0.898
- late/early SD ratio = 0.891

Approximately 81% of familiar-state between-individual variance is linearly associated with the naive individual ordering:

[
r^2approx0.806.
]

This is close to:

[
	ext{shared shift} + 	ext{preserved personal coordinate}.
]

### Permeable condition

- mean shift: +0.892 m/s
- alpha = 0.002
- r = 0.003
- late/early SD ratio = 0.771

The key point is that individual variation itself does **not** vanish. Familiar-state SD remains 77% of naive-state SD.

What disappears is the correspondence between the naive and familiar individual positions.

Thus the pattern is not simply:

[
alpha	o0 Rightarrow 	ext{individuality disappears}.
]

It is closer to:

[
	ext{old personal coordinate loses predictive value}
]

while

[
	ext{new individual differences remain}.
]

## Revised dynamic model

A better representation is

[
x_{i,e,t}
=
mu_{e,t}
+
alpha_{e,t}	heta_i^{0}
+
eta_{i,e,t}
+
epsilon_{i,e,t},
]

where:

- (	heta_i^{0}): portable pre-existing personal coordinate;
- (alpha_{e,t}): context-dependent expression of that prior;
- (eta_{i,e,t}): newly acquired / task-specific individual deviation;
- (epsilon): residual variation.

Equivalently,

[
	heta_i(t)=alpha_t	heta_i^{0}+eta_i(t).
]

This preserves the main mathematical result:

> individuality can remain low-dimensional while the coordinate itself is plastic.

Low dimensionality therefore does not require lifetime constancy.

## What the public data cannot resolve

The Yamada archive allows identified trial-1 and trial-12 comparisons but does not provide a comparable identified individual policy series for all intermediate flights under the frozen raw crosswalk.

Therefore it cannot determine whether personal-state reorganization is:

- abrupt after the first few successful flights;
- gradual over 12 flights;
- a temporary exploratory phase followed by restabilization;
- or driven by one particular learning event.

A same-individual dense learning trajectory is required.

## Current strongest mathematical statement

The data now argue against both extremes:

1. **irreducible / infinite-dimensional individual behaviour**;
2. **one immutable scalar permanently attached to each bat**.

The current best model is:

[
oxed{
	ext{finite low-dimensional personal state}
+
	ext{context-dependent state transition}
}
]

rather than an infinite coefficient sequence.
