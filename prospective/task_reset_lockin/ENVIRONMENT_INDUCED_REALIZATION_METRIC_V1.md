# Environment-induced realization metric note v1

## Status

**POST-PRIMARY MATHEMATICAL INTERPRETATION.**

This note formalizes the newest empirical contrast:

- relational structure in portable personal policy space is strongly transferable;
- relational structure in detailed route-geometry space is not.

It does not identify a literal neural manifold or a unique physical metric.

JAE v0.4.0 remains frozen.

---

# 1. Empirical contrast

## Portable policy space

For transparent personal policy:

\[
\theta_i=(I_i,M_i),
\]

held-out prediction across obstacle configurations gives:

- individual-coordinate R² = **0.4666**;
- pair-displacement-vector R² = **0.5797**;
- 97.1% positive vector-direction agreement.

Thus relative individual arrangement in the coarse personal-policy space is substantially stable across tasks.

## Detailed route-geometry space

Two distance-magnitude diagnostics are unsupported.

### Non-target policy distance -> target geometry distance

- Spearman rho = **+0.191**
- p = **0.2437**

### Other-environment geometry distance -> target geometry distance

- Spearman rho = **+0.078**
- p = **0.3490**

Thus detailed route-space pair-distance magnitudes are not reliably preserved across obstacle contexts.

## 1b. Vector correspondence survives more than distance magnitude

A matched vector-level diagnostic gives a subtler result.

For each bat pair and target environment, the pair's mean 8-D scale-free geometry difference vector from other shared environments was used directly to predict the target-environment difference vector.

Observed:
- pair-vector no-refit R² = **+0.10407**;
- median cosine = **0.59748**;
- positive cosine = **75.8%**;
- magnitude Pearson r = **+0.1734**;
- magnitude Spearman rho = **+0.0180**;
- environment-wise permutation p for vector R² = **0.0027**.

Thus detailed geometry is not completely context arbitrary.

> **The direction of relative geometry retains partial cross-task correspondence, while the magnitude/ranking of geometric separation is strongly context dependent.**

By comparison, transparent I/M policy pair vectors are much more stable:
- pair-vector R² = **+0.5797**;
- median cosine = **0.8631**;
- positive cosine = **97.1%**.

This supports a graded hierarchy rather than a binary invariant/non-invariant split.

Yet same-individual detailed geometry remains identity-bearing overall.

Therefore:

\[
\boxed{
\text{identity correspondence can persist without metric preservation}
}
\]

---

# 2. A generic realization map

Let:

\[
\theta_i
\]

be the portable personal-policy coordinate.

Let the detailed realized route phenotype in environment e be:

\[
g_{i,e}
=
\mathcal R_e(\theta_i,u_{i,e}),
\]

where:
- \(\mathcal R_e\) is an environment/task-dependent realization process;
- \(u_{i,e}\) contains unresolved individual × environment state and noise.

The current data do not identify \(\mathcal R_e\) as:
- linear;
- shared perfectly across individuals;
- deterministic.

---

# 3. Local metric interpretation

Ignore \(u\) momentarily and suppose \(\mathcal R_e\) is differentiable around a local region of policy space.

For a small personal-policy difference:

\[
\Delta\theta
=
\theta_i-\theta_j,
\]

the corresponding realized-geometry difference is approximately:

\[
\Delta g_e
\approx
J_e(\theta)\Delta\theta,
\]

where:

\[
J_e
=
\frac{\partial \mathcal R_e}{\partial\theta}
\]

is the local Jacobian of realization.

Then squared realized separation is:

\[
\|\Delta g_e\|^2
\approx
\Delta\theta^T
M_e(\theta)
\Delta\theta,
\]

with:

\[
\boxed{
M_e(\theta)=J_e(\theta)^T J_e(\theta)
}
\]

the local metric induced on policy space by the current realization environment.

This is a mathematical interpretation, not an estimated object.

---

# 4. Why relational geometry can change while identity persists

If:

\[
M_e
\]

changes among environments, the same latent pair difference \(\Delta\theta\) can be:

- amplified;
- compressed;
- rotated into different observed geometry axes;
- nearly hidden.

Therefore:

\[
\|\theta_i-\theta_j\|
\]

need not rank pairs in the same order as:

\[
\|g_{i,e}-g_{j,e}\|.
\]

And:

\[
\|g_{i,h}-g_{j,h}\|
\]

in one environment need not predict their distance in another.

This is exactly the empirical pattern.

---

# 5. Special cases

## Pure translation

If environments only add a common shift:

\[
g_{i,e}=b_e+B\theta_i,
\]

with fixed B, pairwise geometry is preserved across environments.

The data reject this as a sufficient description.

## Scalar gain

If:

\[
g_{i,e}=b_e+\alpha_e B\theta_i,
\]

pairwise ranks remain stable within a positive scalar rescaling.

The weak held-out distance correlations are not consistent with scalar gain alone as a complete description.

## Environment-specific linear deformation

If:

\[
g_{i,e}=b_e+B_e\theta_i,
\]

then:

\[
M_e=B_e^TB_e.
\]

Changing \(B_e\) changes the realized metric.

A universal cross-environment B is empirically inadequate.

A peer-estimated \(B_e\) could not be recovered predictively from the current small archive.

## 5b. A simple shared environment decoder is not identified

Two peer-only tests attempted to estimate an environment-specific linear I/M -> geometry map from other bats and apply it to a completely excluded focal bat.

Both failed the predictive prerequisite:
- first peer-map implementation: held-out geometry R² = **-1.419**;
- donor-only-scaling LOBO implementation: held-out geometry R² = **-0.365**.

Residual identity was unsupported after these maps, but because the maps themselves predicted geometry worse than a zero-centered baseline, that disappearance cannot be interpreted as successful identification of a shared (B_e).

Therefore:
- one universal cross-environment linear map is inadequate;
- a peer-estimable same-environment linear map is also not established.

The realization operator remains an abstract context-dependent object.

## Nonlinear realization

For:

\[
g=\mathcal R_e(\theta),
\]

the induced metric can also vary over policy position:

\[
M_e=M_e(\theta).
\]

Current data cannot distinguish this from higher-dimensional latent state or individual × environment interactions.

---

# 6. Ecological meaning

The ecological distance between two individuals in realized movement space is therefore not necessarily an intrinsic property of the pair.

It can be an **environment-dependent projection of persistent personal differences**.

This gives a precise reason why:

\[
\boxed{
\text{distance in personal policy}
\not\equiv
\text{distance in realized niche}
}
\]

and why physical-space overlap can change without erasing the stored individual state.

---

# 7. Relation to individual-niche theory

Current individualized-niche theory already treats realized niches as dynamic and context dependent.

The additional value of this formulation is narrower:

> the bat results empirically distinguish a comparatively portable upstream personal coordinate from a less metrically stable downstream movement geometry.

Thus the realized individual niche can be treated as an environment-conditioned measurement of personal organization rather than the personal organization itself.

This is not proposed as a replacement definition of niche.

---

# 8. Relation to the wild non-partition result

In wild *P. hastatus*:

- policy identity persists;
- policy distance does not predict synchronous vertical separation.

The metric interpretation gives a natural explanation.

The spatial observation map can place a substantial part of policy differentiation along directions that:
- overlap spatially;
- project weakly onto vertical separation;
- or rotate into other behavioral dimensions.

Thus weak partition does not imply weak personal differentiation.

---

# 9. Strong prediction

A designed experiment with known obstacle geometry should estimate whether environment changes:

1. only the mean;
2. scalar expression gain;
3. orientation/anisotropy of the realization metric;
4. nonlinear local geometry.

The key prediction from the current data is:

> **at least some environments should change the relative geometry of individual differences, not merely the population mean or overall variance.**

The current held-out relational diagnostics are consistent with this prediction.

---

# 10. What is not identified

Do not claim that the present data estimate:
- \(J_e\);
- \(M_e\);
- a Riemannian manifold;
- a neural latent state;
- environmental obstacle affordance coordinates.

The metric formulation is the minimal mathematical explanation for the observed loss of pairwise distance stability downstream of a portable personal coordinate.

---

# Bottom line

The newest evidence suggests:

\[
\boxed{
\text{personal identity is portable, but realized niche distance is context made}
}
\]

A more technical formulation is:

> **environment changes the metric by which persistent individual differences become geometrically separated in realized movement space.**

This is why persistent specialization can survive while the geometry and degree of spatial differentiation among individuals change.
