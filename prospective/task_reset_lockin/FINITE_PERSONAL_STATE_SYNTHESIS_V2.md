# Finite personal-state synthesis v2 — two-axis revision

## Status

Post-primary mathematical synthesis.

This revision corrects the overly strong reading that one dimension is sufficient **and exhaustive**.

The current evidence distinguishes:

- **one dimension is sufficient for held-out identification**;
- **two transparent dimensions approximately exhaust the calibrated linear portable identity signal**.

## 1. Axis 1 — FlightIntensity

[
I_i
=
rac{z(v_{med})+z(v_{90})+z(|v_z|_{med})+z(|v_z|_{90})}{4}.
]

This is the dominant movement-intensity / vigor coordinate.

Known results:
- scalar identity K = +0.49656;
- 5/5 positive;
- p = 0.0003;
- pairwise order stability = 0.8217;
- held-out magnitude calibration beta = 1.0314, r = 0.5548;
- direct theta learning curve shows rapid convergence:
  three environments recover 91.6% [88.1%,98.1%] of the finite-data improvement toward the full estimator.

Thus I behaves like a recoverable personal coordinate.

## 2. Axis 1 is not exhaustive

Scale-free geometry identity survives linear removal of FlightIntensity:

- parent geometry K = +0.38857;
- residual after I removal K = **+0.30775**;
- 5/5 positive;
- p = **0.0029**;
- residual retains 79.2% of the parent geometry K.

Therefore a one-scalar biological interpretation is too strong.

## 3. Axis 2 — ManeuveringExtent

A stable training-only PC2 exists across held-out environments.

Fold-to-fold PC2 cosine:
- minimum 0.9709;
- median 0.9923;
- maximum 0.9984.

Transparent approximation:

[
M_i
=
mean(-z_{median speed},
z_{median turn},
z_{p90 turn},
z_{path efficiency},
z_{vertical range}).
]

Equivalently, under the frozen feature notation:

[
M=mean(-z_1,z_5,z_6,z_7,z_8).
]

ManeuveringExtent alone:
- K = **+0.23375**;
- 4/5 positive;
- p = **0.0027**.

Its dominant PC2 loadings are:
- median horizontal turn rate: +0.610;
- p90 horizontal turn rate: +0.467;
- path efficiency: +0.375;
- vertical range: +0.455;
- median speed: -0.254.

The axis is close to orthogonal to FlightIntensity:
median absolute cosine ≈0.112.

## 4. Transparent two-dimensional personal state

Define:

[
oldsymbol	heta_i=(I_i,M_i).
]

Held-out cross-configuration identity in the transparent 2-D plane:

- K = **+0.55428**;
- 5/5 positive;
- p = **0.0001**.

After projecting the original eight movement summaries orthogonally away from the fixed I/M span:

- residual K = +0.08771;
- 5/5 positive;
- p = **0.0863**;
- unsupported under the frozen calibration rule.

Thus no calibrated linear portable identity remains after removing the transparent two-axis span.

## 5. Independent geometry challenge

The stronger geometry representation gives the same conclusion.

After removing FlightIntensity alone:
- geometry residual K = +0.30775;
- p = .0029.

After label-free within-environment removal of both I and M:
- geometry residual K = **-0.01467**;
- only 1/5 positive;
- p = **0.4509**.

Thus the I/M pair also absorbs the calibrated portable identity contained in the separate scale-free route-geometry feature family.

## 6. Current finite personal model

For the measured portable movement-policy component, the best compact representation is therefore:

[
oxed{
oldsymbol	heta_i=
(I_i,M_i)
}
]

rather than a single scalar.

A wider generative model is:

[
x_{i,e,t}
=
mu_{e,t}
+
A_{e,t}oldsymbol	heta_i
+
h_{i,e}
+
epsilon_{i,e,t}.
]

Where:
- (oldsymbol	heta_i): approximately two-dimensional portable personal state;
- (A_{e,t}): context-dependent expression / deformation;
- (h_{i,e}): configuration-specific spatial realization;
- (epsilon): trial variation.

## 7. What is finite and what is not yet identified

### Finite/recoverable in current data

The portable individual component is strongly compressible.

It does not behave like an ever-expanding coefficient list:
- one axis already identifies individuals;
- a second stable axis captures residual portable coordinative identity;
- after two transparent axes, calibrated residual identity is absent in both the original 8-D policy and an independent scale-free geometry representation.

### Not yet finite-parametrized

The environment-specific realization (h_{i,e}) is not explained by theta alone.

Direct theta -> route-centroid held-out linkage failed:
- prediction gain = -0.0878;
- p = .292.

Public obstacle coordinates are unavailable, and peer-only environment maps predict detailed geometry poorly.

Therefore the remaining mathematical uncertainty lies mainly in the environment-dependent realization operator, not in the dimensionality of the portable personal state.

## 8. Relation to the “pi” question

The strongest current answer is:

> The portable individual state does not look mathematically irreducible. In this Rhino system, it is approximately a two-coordinate object: movement intensity and maneuvering extent.

The exact trajectory can still remain complex because the environment maps that two-dimensional state into different route geometries.

So the difficult object is better written as

[
g_{i,e}
=
mathcal R_e(oldsymbol	heta_i,u_{i,e}),
]

not as an infinite-dimensional personal constant.

## Ceiling

“Two-dimensional” applies to calibrated linear identity in the measured feature families.

It does not prove:
- two neural variables;
- two physiological traits;
- exact nonlinear intrinsic dimension = 2;
- universal two-dimensionality across bat species;
- that all biological individual differences are exhausted.
