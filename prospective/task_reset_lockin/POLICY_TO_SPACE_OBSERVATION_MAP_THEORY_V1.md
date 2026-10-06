# Policy-to-space observation-map theory v1

## Status

**MECHANISTIC THEORY / SYNTHESIS.**

This note formalizes why persistent individual movement policy and realized spatial partitioning are distinct ecological quantities.

It is motivated by supported batter results but is not itself an additional empirical test.

---

# 1. Latent personal policy

Let individual i carry a persistent low-dimensional policy coordinate:

\[
\theta_i \in \mathbb R^d.
\]

Across individuals:

\[
E[\theta_i]=0,
\qquad
Var(\theta_i)=\Sigma_\theta.
\]

The adult obstacle-flight results provide empirical support for a low-dimensional, portable \(\theta_i\)-like object.

---

# 2. Realized behavior is an environment-specific projection

In environment e, the realized spatial or movement phenotype is:

\[
z_{i,e}
=
\mu_e
+
G_e\theta_i
+
\epsilon_{i,e}.
\]

where:
- \(\mu_e\) = population-wide condition effect;
- \(G_e\) = environment-specific expression / observation map;
- \(\theta_i\) = persistent personal policy;
- \(\epsilon\) = bout-level residual realization.

This is deliberately more general than a scalar reaction norm.

\(G_e\) can:
- amplify;
- attenuate;
- rotate;
- compress;
- or hide

different dimensions of personal policy.

---

# 3. Persistent policy does not imply spatial differentiation

The identity-attributable covariance in realized phenotype is:

\[
\Sigma_{z,e}^{(id)}
=
G_e\Sigma_\theta G_e^T.
\]

Policy-level differentiation exists whenever:

\[
\Sigma_\theta \neq 0.
\]

But realized spatial differentiation can vanish when:

\[
G_e\Sigma_\theta G_e^T=0.
\]

This occurs whenever the individualized policy variation lies entirely in directions that the current spatial phenotype does not express.

Therefore:

\[
\boxed{
\Sigma_\theta \neq 0
\not\Rightarrow
\Sigma_{z,e}^{(id)} \neq 0
}
\]

and persistent specialization in policy space does not mathematically require physical-space partition.

---

# 4. Expected pairwise distance makes the distinction explicit

For two independently sampled individuals i and j:

\[
E\|\theta_i-\theta_j\|^2
=
2\,tr(\Sigma_\theta).
\]

For the identity-attributable realized phenotype:

\[
E\|G_e\theta_i-G_e\theta_j\|^2
=
2\,tr(G_e\Sigma_\theta G_e^T).
\]

Define a dimensionless expression-to-space ratio:

\[
\boxed{
\rho_e
=
\frac{
tr(G_e\Sigma_\theta G_e^T)
}{
tr(\Sigma_\theta)
}
}
\]

when the denominator is positive.

Then:
- large policy differentiation can coexist with \(\rho_e\approx0\);
- the same population can have different \(\rho_e\) in different environments;
- spatial partitioning is an expression property, not a necessary storage property.

---

# 5. Scalar expression gain is a special case

If:

\[
G_e=\alpha_e I,
\]

then:

\[
\rho_e=\alpha_e^2.
\]

The post-primary sensory-perturbation diagnostic is qualitatively consistent with this special case:

- 30-cm baseline-expression gain:
  \(\alpha_{30}\approx0.863\);
- 10-cm gain:
  \(\alpha_{10}\approx0.324\).

Do not identify those empirical scalars with a universal \(G_e\).

They simply illustrate the idea that current context can change how strongly persistent personal information appears.

---

# 6. Rotation is equally important

A context need not only attenuate individuality.

Suppose:

\[
G_e = R_e D_e,
\]

where:
- \(R_e\) rotates personal-policy axes into environment-specific realized axes;
- \(D_e\) scales them.

Then the same \(\theta_i\) can generate:
- vertical differentiation in one environment;
- horizontal differentiation in another;
- turning-style differentiation in another;
- little spatial differentiation in another.

This explains how individual identity can transfer even when the realized spatial phenotype changes substantially.

---

# 7. Null-space individuality

The strongest separation occurs if policy has dimensions that do not map to the measured spatial phenotype.

Partition:

\[
\theta_i=
\begin{bmatrix}
\theta_i^{visible}\\
\theta_i^{hidden}
\end{bmatrix}
\]

and let:

\[
G_e=
\begin{bmatrix}
G_e^{visible} & 0
\end{bmatrix}.
\]

Variation in:

\[
\theta_i^{hidden}
\]

can remain:
- repeatable;
- history-dependent;
- behaviorally important;

while being completely absent from the chosen spatial niche metric.

Thus failure to detect spatial segregation is not equivalent to absence of specialization.

It may mean the measurement projects away the individualized dimension.

---

# 8. Why policy distance need not predict pairwise spatial separation

The field analysis asks whether:

\[
D_{policy,ij}
\rightarrow
D_{space,ij}.
\]

Under the observation-map model, this relation is not generally monotonic.

If two individuals differ primarily along a policy direction with small singular value under \(G_e\), they can be:
- far apart in policy space;
- close in realized physical space.

Conversely, a small policy difference aligned with a strongly amplified direction can produce a larger physical difference.

Therefore a weak empirical policy-distance / vertical-separation correlation is exactly possible under persistent policy individuality.

---

# 9. Partitioning requires an alignment condition

For personal policy differentiation to generate spatial partitioning, at least three ingredients are needed:

1. persistent between-individual policy variance:
   \(\Sigma_\theta\neq0\);

2. the individualized dimensions must be visible under the spatial map:
   \(G_e\Sigma_\theta G_e^T\) appreciable;

3. identity-attributable spatial variation must exceed within-individual/contextual variation enough to generate stable separation.

Thus spatial partitioning is not the definition of specialization.

It is a downstream outcome requiring alignment between personal policy and spatial opportunity.

---

# 10. Connection to solution abundance

The functional-abundance hypothesis governs how \(\Sigma_\theta\) can form.

A schematic chain is:

\[
\text{solution repertoire}
+
\text{history}
\rightarrow
\Sigma_\theta
\]

followed by:

\[
\Sigma_\theta
\xrightarrow{G_e}
\Sigma_{z,e}^{(id)}.
\]

This separates two questions:

### Formation question
How much personal-policy diversity is generated?

### Expression question
How much of that diversity is visible in physical space?

Ecological opportunity can affect either side:
- it can enlarge the feasible policy repertoire;
- or alter \(G_e\), changing how policy becomes spatial behavior.

These are not equivalent mechanisms.

---

# 11. Mapping current evidence onto the model

## \(\Sigma_\theta\) exists

Supported by:
- cross-configuration individual policy identity;
- held-out policy-coordinate prediction;
- wild H/V carrier;
- scale-free geometry identity.

## \(G_e\) varies

Compatible with:
- sensory perturbation condition shifts;
- post-primary context-dependent expression attenuation;
- learning-state heterogeneity.

## Spatial alignment is weak in the wild field system

Supported by:
- policy distance not predicting synchronous vertical separation;
- lack of general positive added 3-D segregation;
- policy similarity not predicting complete centered vertical-use shape.

Therefore the current evidence is consistent with:

\[
\boxed{
\text{stable }\Sigma_\theta
+
\text{variable }G_e
}
\]

rather than one fixed individual spatial niche.

---

# 12. Strong empirical prediction

The model predicts that environmental manipulations can change spatial differentiation without destroying individual policy identity.

For the same animals:

1. estimate \(\theta_i\) in a portable behavior space;
2. manipulate environment e;
3. estimate a \(G_e\)-like mapping to realized spatial outcomes;
4. test whether:
   - policy identity persists;
   - spatial separation changes.

A decisive result would be:

\[
\theta_i\text{ stable}
\quad\text{while}\quad
\rho_e\text{ changes}.
\]

That directly demonstrates storage-expression separation.

---

# 13. Stronger niche-theory implication

Traditional individual-niche analyses often treat realized environmental/spatial use as the niche itself.

The observation-map formulation says:

> realized niche geometry can be only one projection of persistent individual organization.

Two populations can have the same amount of latent policy specialization but different observed niche partitioning because their \(G_e\) differ.

Conversely, strong physical separation can be produced by environmental projection even when latent policy differences are modest.

This gives a mechanistic reason not to equate:
- individual specialization;
- niche overlap;
- spatial segregation.

---

# Bottom line

The mathematically relevant object is not:

\[
\text{individual policy} = \text{individual spatial niche}.
\]

It is:

\[
\boxed{
\text{personal policy}
\xrightarrow{\,G_e\,}
\text{realized phenotype}
}
\]

with an environment-dependent map.

Persistent individual specialization lives upstream of the spatial projection.

Spatial partitioning appears only when the current environment maps individualized policy dimensions into separable physical outcomes.
