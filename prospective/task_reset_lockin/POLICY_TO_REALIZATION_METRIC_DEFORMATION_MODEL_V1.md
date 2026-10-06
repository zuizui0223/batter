# Policy-to-realization metric deformation model v1

## Status

**THEORETICAL INTERPRETATION OF ALREADY-OBSERVED REPRESENTATION BOUNDARIES.**

This note does not introduce a new empirical endpoint.

It is motivated by the empirical combination:

- portable policy coordinates predict held-out individual states;
- policy pair-displacement vectors are stable across obstacle configurations;
- scale-free route geometry remains identity-bearing;
- route-geometry pairwise distance structure is not stable across configurations;
- one I/M -> geometry map learned in other environments leaves residual identity;
- peer-defined environment-specific linear maps are not predictively adequate.

The purpose is to formalize how all of these can coexist.

---

# 1. Latent personal policy

Let individual i carry a persistent d-dimensional personal policy:

[
	heta_iinmathbb R^d.
]

For the transparent Rhino representation:

[
d=2
]

is an empirically useful approximation, not a claim of literal neural dimensionality.

Let:

[
delta_{ij}=	heta_i-	heta_j.
]

If (	heta_i) is portable, (delta_{ij}) can remain relatively stable across tasks.

---

# 2. Environment-specific realization

Let the detailed behavioral realization in environment e be:

[
z_{i,e}
=
mu_e
+
G_e	heta_i
+
epsilon_{i,e}.
]

Here:
- (mu_e) is the population-level environmental shift;
- (G_e) is a context-specific expression operator;
- (epsilon) is task-specific and measurement residual.

The present archive does not identify (G_e) directly.

This is a generative representation.

---

# 3. Environment induces a metric on personal policy differences

Ignoring residual noise, the realized pair difference is:

[
z_{i,e}-z_{j,e}
=
G_edelta_{ij}.
]

Squared realized distance is therefore:

[
oxed{
d_e^2(i,j)
=
delta_{ij}^T
M_e
delta_{ij}
}
]

where:

[
oxed{
M_e=G_e^TG_e.
}
]

Thus each environment induces its own positive-semidefinite metric on the same latent personal-policy differences.

This is the key distinction.

Persistent latent individuality does **not** imply one invariant realized distance matrix.

---

# 4. When would realized relational geometry be stable?

If:

[
M_e=c_e M
]

for all environments, with only a positive scalar (c_e) changing, then all pairwise distances are rescaled together.

Pair rankings are preserved.

If (G_e) differs only by an orthogonal rotation:

[
G_e=R_eG
]

with:

[
R_e^TR_e=I,
]

then:

[
M_e=G^TG
]

and pairwise distances are exactly invariant.

Therefore strong cross-environment relational stability requires a restricted class of expression changes.

---

# 5. How can identity survive while metric structure changes?

Suppose (G_e) remains sufficiently injective over the occupied policy region but changes anisotropically across environments.

Then:
- each individual remains recognizably mapped from its personal state;
- same-individual correspondence can survive;
- but directions in policy space are stretched or compressed differently;
- pairwise distance rankings can change.

Thus:

[
oxed{
	ext{identity correspondence}

otRightarrow
	ext{metric invariance}.
}
]

This is exactly the logical distinction between:
- positive cross-configuration geometry identity;
- unsupported geometry relational stability.

---

# 6. Eigenvector interpretation

Let:

[
M_e=V_eLambda_eV_e^T.
]

Then environment e assigns different expression gains to different policy directions.

A personal difference aligned with a large eigenvalue of (Lambda_e):
- becomes strongly expressed.

The same difference aligned with a low-gain direction in another environment:
- becomes compressed or hidden.

Therefore two individuals can:
- look strongly different in one environment;
- weakly different in another;
- remain distinct in the upstream policy representation.

This gives a precise meaning to:

> **context-gated individuality.**

---

# 7. Spatial niche as one observation metric

If z is spatial use, then:

[
M_e^{space}=G_{e,space}^TG_{e,space}
]

describes which personal-policy directions are visible as spatial differentiation.

If an individualized direction lies near the null space:

[
G_{e,space}delta_{ij}approx0,
]

then policy differences remain but spatial partition is weak.

Thus:

[
oxed{
	ext{no spatial partition}
]

can mean:

[
oxed{
	ext{the current spatial observation map is insensitive to the individualized direction}
}
]

rather than absence of individual specialization.

---

# 8. Empirical correspondence

## Policy space

Transparent I/M:
- held-out coordinate R² = **0.4666**;
- pair-displacement-vector R² = **0.5797**;
- 97.1% positive pair-vector cosine.

This is strong relational transfer.

## Route geometry

Scale-free geometry:
- self/other identity remains supported;
- geometry-distance relational stability is unsupported:
  - Spearman rho = **+0.0782**
  - p = **0.349**.

Policy-distance -> held-out geometry-distance coupling is also unsupported:
- rho = **+0.191**
- p = **0.244**.

Thus route-space metric structure is much less stable than policy-space relational structure.

## Decoder tests

A single map learned in other environments leaves residual geometry identity:
- K = **+0.2016**
- 5/5 positive
- p = **0.0156**.

Peer-defined environment-specific linear maps are not predictively adequate:
- prior peer-map R² = **-1.419**;
- independent donor-only LOBO implementation R² = **-0.365**.

Therefore (G_e) should currently be treated as an abstract environment-dependent realization operator, not an empirically identified shared linear decoder.

---

# 9. Biological interpretation

The individual may carry a relatively stable rule/state upstream of realized route geometry.

The environment does not simply add noise to that state.

It can change which aspects of the state become behaviorally visible.

Thus the same persistent individual organization can be expressed as different combinations of:
- route efficiency;
- horizontal maneuver;
- vertical movement;
- absolute spatial use.

This is stronger than ordinary mean plasticity.

It concerns the **geometry of among-individual differences** under changing contexts.

---

# 10. Relation to behavioral reaction norms

Behavioral reaction norms separate:
- individual intercept;
- population environmental response;
- individual-specific slope.

That framework is compatible with the present model.

But the present empirical problem is multivariate and geometric:

> **Does the relational arrangement among individuals survive when behavior is expressed in a different task?**

A scalar random-intercept/random-slope model does not by itself require:
- stable pairwise geometry;
- stable mapping among different multivariate behavioral representations;
- identity correspondence under non-isometric realization.

The current programme therefore complements reaction-norm theory rather than replacing it.

---

# 11. New experimental prediction

Manipulate the environment while repeatedly estimating the same upstream personal policy.

For each environment estimate the realized among-individual metric:

[
D_e(i,j).
]

Prediction:

- upstream policy distances should be more stable across environments;
- realized distance matrices should rotate/compress as constraints change;
- environmental conditions that constrain one policy direction should reduce the corresponding eigenvalue of the realized metric;
- restoring the original environment should restore the earlier realized metric if the upstream state was retained.

This directly distinguishes:
- stored-policy change;
- expression-map change.

---

# 12. Conservation / ecological implication

Environmental change can alter observed among-individual niche overlap without changing the amount of underlying individual differentiation.

Therefore changes in:
- spatial overlap;
- habitat overlap;
- route similarity

cannot automatically be interpreted as creation or loss of specialization.

They may instead reflect a change in:

[
M_e,
]

the ecological expression metric.

This matters whenever individual diversity is inferred only from realized space use.

---

# 13. Claim ceiling

The model establishes a coherent mathematical interpretation.

Current data support:
- stable policy relational structure;
- context-sensitive route relational structure.

Current data do **not** identify:
- (G_e);
- (M_e) directly;
- linearity;
- neural coordinates;
- universal latent dimensionality.

Use:
> **environment-dependent metric deformation**

as a theoretical description, not as a fitted mechanistic parameter.

---

# Bottom line

A persistent individual strategy does not require a persistent realized niche geometry.

The mathematically relevant distinction is:

[
oxed{
	heta_i	ext{ can be stable}
}
]

while:

[
oxed{
M_e=G_e^TG_e	ext{ changes with environment}.
}
]

Therefore:

> **individual identity can be conserved while the geometry of individual differences is environmentally deformed.**

This is the strongest current formal explanation for why persistent specialization can coexist with changing or overlapping spatial niches.
