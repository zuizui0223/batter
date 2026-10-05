# Self-maintaining specialization synthesis v6

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V5.**

JAE v0.4.0 remains frozen and unchanged.

The new field variance decomposition and peer-plus-past forecast refine the central mechanism claim.

The persistent object is no longer best represented as one immutable individual point in policy space.

It is better represented as a **persistent individual distribution over policy states**.

---

## 1. Central biological question

JAE established that repeatable individual vertical strategies need not be maintained by persistent vertical partitioning.

The post-JAE question is:

> **If specialization is not stored in exclusive physical space, what exactly persists with the individual?**

The combined laboratory and field evidence now supports a bounded answer:

> **persistent individuality can reside in a low-dimensional movement-policy distribution: individuals have repeatable regions of policy space, while environmental context, learning and residual state determine where within those regions a particular bout is expressed.**

---

## 2. The key distinction is now place, policy and realization

Three objects must be kept separate.

### Physical occupancy

Where the animal is in 3-D space.

### Personal policy

How the animal tends to execute movement:
- movement intensity;
- vertical movement intensity;
- maneuvering / route organization;
- other low-dimensional control tendencies.

### Realized bout

The actual trajectory or session produced by:

[
x_{iet}
=
F(E_e,\boldsymbol\theta_{it},m_{i,e})
+
\epsilon_{iet}.
]

Here:
- (E_e) = task/environment geometry;
- (m_{i,e}) = learned scene-specific solution;
- (oldsymbol\theta_{it}) = current personal policy state.

---

## 3. Portable low-dimensional structure exists

### Rhinolophus nippon

Across obstacle configurations:
- full 8-D movement-policy identity: K = **0.94356**, p = **0.0001**;
- one training-derived PC is already sufficient for held-out identity;
- transparent FlightIntensity: K = **0.49656**, p = **0.0003**;
- transparent ManeuveringExtent: K = **0.23375**, p = **0.0027**;
- transparent two-axis identity: K = **0.55428**, p = **0.0001**;
- residual calibrated identity after removing the two-axis span is unsupported.

Thus measured cross-configuration individual information is approximately low-dimensional.

### Carollia perspicillata external boundary

The fixed Rhino-derived representation externally succeeds:
- fixed 2-D K ≈ **0.348**;
- 6/7 positive;
- p = **0.0007**.

The strongest transferable component is FlightIntensity:
- K ≈ **0.368**;
- p = **0.0014**.

The second maneuver axis has weaker cross-species support and no demonstrated incremental value beyond intensity.

Therefore low-dimensional personal policy is recurrent but not a universal fixed two-axis bat law.

---

## 4. Wild field data contain a persistent low-dimensional carrier

For *Phyllostomus hastatus*, a field-specific two-dimensional policy coordinate uses:

- H = horizontal movement intensity;
- V = vertical movement intensity.

Frozen fixed-bin carrier:

### 2022
- K_2D = **0.65314**;
- 32/34 positive;
- p = **0.0001**.

### 2023
- K_2D = **0.27052**;
- 9/11 positive;
- p ≈ **0.033**.

Thus free-ranging behavior contains repeatable individual information in low-dimensional policy space.

---

## 5. Persistent policy is not a fixed deterministic point

The new variance decomposition makes this explicit.

### 2022

Equal-axis descriptive variance fractions:
- stable individual = **52.5%**;
- cohort-day = **17.3%**;
- residual = **30.1%**.

But the axes differ strongly.

Horizontal intensity:
- individual **31.7%**;
- day **31.4%**;
- residual **36.9%**.

Vertical intensity:
- individual **73.4%**;
- day **3.2%**;
- residual **23.4%**.

The vertical-intensity axis is therefore strongly individualized in 2022.

### 2023

Equal-axis descriptive fractions:
- individual **33.6%**;
- day **1.7%**;
- residual **64.7%**.

Horizontal:
- individual **28.1%**;
- residual **68.6%**.

Vertical:
- individual **39.1%**;
- residual **60.9%**.

Individual policy remains detectable, but single-session expression is much less tightly concentrated around the stable individual component.

The full models converged. Some leave-one-out refits produced boundary/Hessian warnings, so these are descriptive variance partitions rather than formal variance-comparison tests.

---

## 6. A personal-history centroid is not a universal forecasting rule

After subtracting contemporaneous peer-day policy, strictly prior personal history was used to forecast the next residual H/V state.

### 2022
- average Delta = **+0.10876**;
- pooled no-refit R² = **0.0801**;
- permutation p = **0.0009**;
- positive individual forecast gain = **16/30 = 53.3%**.

### 2023
- average Delta = **+0.40484**;
- pooled no-refit R² = **0.1664**;
- permutation p = **0.0140**;
- positive individuals = **4/7 = 57.1%**.

Both years fail the frozen >=70% individual-consistency requirement.

Therefore:

> a fixed centroid of past personal behavior is not an adequate population-wide dynamical rule.

The average forecast benefit is real relative to the pipeline null, but it is heterogeneous.

This is exactly what is expected if each individual occupies a persistent **distribution or region** of policy space rather than one deterministic point.

---

## 7. Shared context and stable individuality coexist

Earlier peer-day analyses showed:
- short-term state autocorrelation largely disappears after contemporaneous-peer correction;
- yet individual identity remains after the same peer-day correction.

This is the key separation.

A session can be decomposed as:

[
\boxed{
\boldsymbol\theta_{it}
=
\boldsymbol\theta_i
+
\boldsymbol\eta_{d(t)}
+
\boldsymbol\xi_{it}
}
]

as a minimal descriptive model.

A more general prospective model is:

[
\boldsymbol\theta_{it}
=
\boldsymbol\theta_i
+
\mathbf B_i\mathbf c_t
+
\boldsymbol\xi_{it},
]

where:
- (oldsymbol\theta_i) is the persistent personal center;
- (mathbf c_t) is environment/context;
- (mathbf B_i) is an individual reaction norm;
- (oldsymbol\xi_{it}) is residual within-individual variation.

The present data establish the persistent component and substantial within-individual variation.

They do **not** yet identify (mathbf B_i).

---

## 8. Learning changes realization without necessarily erasing individuality

Independent Yamada learning-state evidence:

- 14 naive *Rhinolophus*;
- substantial trial-1 to trial-12 population-level behavioral updating;
- after condition × trial standardization, personal-state maintenance:
  - K = **0.67436**;
  - 11/14 positive;
  - p = **0.0027**.

Condition-level exact diagnostics are heterogeneous:
- acoustically permeable: K = +0.32264, p = 0.1327;
- reflective: K = +1.02609, p = 0.00278.

Thus policy expression can change with learning and may depend on environmental information structure.

The raw two-axis external replication is structurally unadjudicated because all 28 Yamada trajectories contain only 43–91 usable rows against the frozen >=100-row rule.

No support threshold was relaxed.

---

## 9. Literal route and portable policy remain distinct

External task-reset evidence and internal route diagnostics support:

- literal route placement can be scene-specific;
- familiar routes can be retained/retrieved;
- a mirror/reset geometry can force a new route;
- portable movement-policy identity can survive across configurations.

The best hierarchy remains:

[
\boxed{
\text{persistent personal policy distribution}
+
\text{learned scene-specific solution}
+
\text{current environment}
\rightarrow
\text{realized movement}
}
]

A learned route is therefore one realization of individuality, not the only carrier.

---

## 10. Policy differentiation still does not imply partitioning

In the same wild *P. hastatus* system, dyads farther apart in persistent H/V policy space are not more vertically separated during synchronous local co-use.

2022:
- rho(policy distance, vertical separation) = **+0.188**;
- p = **0.2743**.

2023:
- rho = **-0.190**;
- p = **0.6887**.

Therefore:

[
\boxed{
\text{persistent policy differentiation}
\not\Rightarrow
\text{spatial partitioning}
}
]

This remains true even in 2023, where the panel-level co-use analysis detects a context-dependent excess vertical-separation signal.

Policy difference does not identify which dyads separate.

---

## 11. Policy is also not identical to realized vertical-distribution shape

Field policy similarity does not predict the complete centered vertical-use distribution:

- 2022 p = **0.4548**;
- 2023 p = **0.5627**.

So:

[
\text{policy state}
\neq
\text{realized spatial phenotype}.
]

This is not a failure of the policy framework.

It is a necessary consequence of the hierarchy:
the same control tendency can generate different spatial outcomes under different geometry, resources and environmental context.

---

## 12. What happened to the Pólya / rapid-lock-in idea?

The Pólya model remains an exact proof that path dependence is **sufficient** to produce individual specialization without competition or spatial exclusion.

But the wild data do not identify autonomous self-reinforcement as the maintenance process.

In particular:
- short-term residual state persistence is not robust after peer correction;
- the fixed past-centroid forecast fails its individual-consistency rule.

Therefore the Pólya mechanism should remain a theoretical existence proof, not the empirical mechanism headline.

Rapid early differentiation remains plausible from juvenile data, but its carrier may be:
- learning;
- developmental divergence;
- persistent performance traits;
- stochastic early history;
- combinations.

---

## 13. Updated mechanistic object

The most defensible object is now:

> **a personal probability distribution over a low-dimensional movement-policy space.**

It has:
- a persistent individual center;
- axis-specific stability;
- context-dependent displacement;
- residual within-individual breadth;
- learned scene-specific realizations.

Individual specialization is therefore not binary.

Its strength can be described by the ratio:

[
\frac{\Sigma_{individual}}
{\Sigma_{individual}+\Sigma_{context}+\Sigma_{within}},
]

and this ratio can differ among axes, years and ecological conditions.

This formulation naturally explains:
- strong repeatability without spatial exclusion;
- strong individuality in one year and weaker individuality in another;
- learning-related shifts without identity erasure;
- overlap among individuals;
- failure of one deterministic personal forecast rule.

---

## 14. Strongest current ecological statement

> **Individual specialization can persist as a stable bias in how an animal moves rather than as exclusive ownership of where it moves. That bias is low-dimensional but probabilistic: individuals repeatedly occupy different regions of policy space while environmental context and learning move their realized behavior within those regions.**

The important conceptual shift is:

[
\boxed{
\text{individual niche as exclusive space}
\quad\longrightarrow\quad
\text{individual specialization as persistent policy distribution}
}
]

Spatial partitioning is one possible downstream consequence.

It is not the necessary storage mechanism of individual specialization.

---

## 15. Decisive next causal test

The next experiment should estimate both the personal distribution and its response to a controlled reset.

For the same individuals:

1. estimate baseline policy distributions across multiple task geometries;
2. learn a stable scene-specific route;
3. impose a true geometry/resource reset;
4. measure the first post-reset bout before relearning;
5. follow repeated exposure;
6. restore the original scene;
7. measure morphology/performance independently.

The key quantities are not just mean policy coordinates.

Estimate:
- individual center;
- within-individual covariance;
- context displacement;
- individual-specific context slope.

Competing predictions:

### Stable performance prior
Personal center/order transfers immediately across reset.

### Learned scene solution
Literal route collapses at reset and re-forms with experience.

### Individual reaction norm
Context displacement differs reproducibly among individuals.

### Autonomous reinforcement
Post-reset behavior should progressively depend more on new personal history even after shared context is removed.

This design can finally identify what part of the personal policy distribution is learned versus physically constrained.

---

## Bottom line

The evidence has moved past both:

> “individuals occupy different niches”

and

> “each individual has one fixed flight parameter.”

The stronger synthesis is:

> **individuals can carry persistent, low-dimensional but stochastic movement policies through shared space.**

That is how specialization can be maintained without continuous spatial partitioning.
