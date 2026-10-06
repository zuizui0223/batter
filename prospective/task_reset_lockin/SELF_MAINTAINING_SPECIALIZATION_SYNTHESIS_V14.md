# Self-maintaining specialization synthesis v14

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V13.**

JAE v0.4.0 remains frozen.

V14 corrects the interpretation of the geometry programme.

The geometry results do not support an additional independent high-dimensional identity layer beyond the transparent personal-policy representation.

Instead, the evidence now points toward a **compact empirical personal-policy coordinate with multiple observable manifestations**.

The current architecture is:

\[
\boxed{
\text{solution repertoire + personal history}
\rightarrow
\theta_i
\xrightarrow{G_e}
\text{movement realization}
\xrightarrow{Q_e}
\text{performance}
}
\]

where:
- \(\theta_i\) is the persistent personal policy;
- \(G_e\) is the environment/task-specific expression map;
- \(Q_e\) is the environment-specific performance/payoff structure.

Spatial niche geometry is one output of this chain, not the storage medium.

---

# 1. Formation

Juvenile fruit-bat movement shows that the later individualized state is not fully specified by the earliest observable independent movement history.

For late valid-day targets 11–20:

### Earliest two valid history days
- E = **+15.19**
- p = **0.1655**
- 8/14 positive
- unsupported.

### Recent two valid history days versus earliest two
- Q = **+144.08**
- null mean = **+0.35**
- p = **0.0001**
- 10/14 positive
- supported identity-specific refinement.

Thus:

\[
\boxed{
\text{personal movement history materially refines the individualized solution}
}
\]

without one universal monotonic developmental trajectory.

The simplest model of a fully fixed adult-like personal state visible from the first valid independent movements is weakened.

---

# 2. Maintenance

In *Rhinolophus nippon*, the transparent personal policy is:

\[
\theta_i=(I_i,M_i),
\]

where:
- I = FlightIntensity;
- M = ManeuveringExtent.

Transparent 2-D identity:
- K = **+0.55428**
- 5/5 positive
- p = **0.0001**.

Held-out no-refit coordinate prediction:
- R² = **0.4666**
- p = **0.0002**
- median cosine = **0.896**.

Held-out pair displacement vectors:
- R² = **0.5797**
- p = **0.0001**
- 97.1% positive direction agreement.

Therefore the empirical personal-policy coordinate predicts an animal's relative behavioral position in unseen movement tasks.

It is not merely a classifier embedding, but this predictive coordinate is not yet identified as a causal neural/control state.

---

# 3. The policy is not just speed

Scale-free route geometry remains identity-bearing after removing:
- elapsed time;
- speed;
- absolute path length;
- absolute vertical range;
- absolute spatial position.

Geometry-only:
- K = **+0.38857**
- 5/5 positive
- p = **0.0153**.

So portable individuality also appears in:
- route efficiency;
- normalized displacement;
- turning geometry;
- vertical route shape.

This rules out the narrow interpretation:

> some bats are merely faster than others.

---

# 4. Geometry identity appears distributed — but not independently high-dimensional

Family-only geometry localization:

### Global route organization G
- K = **+0.40777**
- 5/5 positive
- p = **0.0088**.

### Horizontal maneuver geometry H
- K = **+0.29605**
- 5/5 positive
- p = **0.0089**.

### Vertical maneuver geometry V
- K = **-0.04844**
- p = **0.5906**.

Deleting any one family from the full geometry representation leaves calibrated identity.

At first glance this looks like a distributed multi-component coordination phenotype.

But two stronger diagnostics narrow that interpretation.

---

# 5. G and H do not carry clear incremental identity beyond one another

A cross-fitted residual test used the other six environments only to learn the relationship between G and H.

## H after removing training-predicted G

- K = **+0.06290**
- 3/5 positive
- p = **0.1064**
- unsupported.

## G after removing training-predicted H

- K = **+0.00604**
- 4/5 positive
- p = **0.4035**
- unsupported.

Thus G and H are not well supported as two independently identity-bearing modules.

A better interpretation is:

> **global route organization and horizontal maneuver organization are two manifestations of a shared lower-dimensional personal coordination state.**

---

# 6. FlightIntensity alone is insufficient, but I + M absorbs geometry identity

Remove FlightIntensity only:

- residual geometry K = **+0.30775**
- 5/5 positive
- p = **0.0029**.

So I alone does not explain the geometry carrier.

Remove I + M jointly:

- residual geometry K = **-0.01467**
- 1/5 positive
- p = **0.4509**.

Median within-environment geometry ~ I+M R²:

- path efficiency = **0.905**
- horizontal displacement ratio = **0.514**
- absolute vertical displacement ratio = **0.648**
- vertical range ratio = **0.845**
- median horizontal turn angle = **0.296**
- p90 horizontal turn angle = **0.785**
- median vertical slope = **0.824**
- p90 vertical slope = **0.685**.

Therefore:

\[
\boxed{
\text{identity-bearing scale-free geometry is largely organized by the same transparent I/M policy pair}
}
\]

within the Rhino obstacle-flight system.

This is the key V14 update.

Do not treat geometry as a third independent latent personal axis.

---

# 7. Why ManeuveringExtent is biologically important

FlightIntensity captures the dominant movement-vigor component.

But FlightIntensity alone leaves most geometry identity intact.

ManeuveringExtent is the additional transparent coordinate needed to absorb that route-organization identity.

Thus the compact policy is better interpreted as:

### I — operating intensity
how vigorously movement is executed.

### M — maneuvering / route-organization state
how that movement is arranged through the task.

Together they generate multiple visible behavioral consequences.

---

# 8. The compact policy is robust to target-domain normalization

Geometry portability survives stronger restrictions.

### Target-centered, training-scaled
- K = **+0.42064**
- 5/5 positive
- p = **0.0040**.

### Fully training-only global normalization
- K = **+0.23140**
- 4/5 positive
- p = **0.0440**.

Thus the held-out environment need not provide its own variance—or even its own mean—for route-organization identity to remain detectable.

This strengthens the interpretation of \(\theta_i\) as a portable state rather than a within-environment normalization artifact.

---

## 8b. Causal-status boundary

The transparent I/M pair is an **empirical coordinate system**, not yet an identified internal controller.

Important overlap:
- ManeuveringExtent contains path efficiency;
- ManeuveringExtent contains vertical range;
- the geometry representation contains related path-efficiency and normalized vertical-range quantities.

Therefore the disappearance of geometry identity after I/M residualization can mean:

1. the same low-dimensional internal state generates both feature sets; **or**
2. the two feature sets are statistically redundant descriptions of the same realized movement organization.

The current archive cannot distinguish those explanations.

Allowed wording:

> **multiple identity-bearing movement observables collapse onto a compact empirical personal-policy representation.**

Do not yet write:

> **I/M is the causal upstream controller that generates route geometry.**

That stronger causal statement requires intervention or independent measurement of the latent state.

---

# 9. Cross-species generality is hierarchical

The fixed Rhino scale-free geometry representation is unsupported in independent *Carollia perspicillata*:

- K = **-0.03504**
- 3/7 positive
- p = **0.2144**
- both date-block means negative.

Leave-one-trial robustness:
- no deletion yields support;
- removing the historically unusual C3_2 trial does not rescue the result.

Yet the earlier fixed low-dimensional I/M programme in Carollia is supported, especially FlightIntensity.

Therefore:

\[
\boxed{
\text{coarse personal policy can recur across systems}
}
\]

while:

\[
\boxed{
\text{exact coordinative geometry can remain species/task specific}
}
\]

For Miniopterus, even the coarse portable individual signal is unsupported.

So there is no universal bat-wide two-axis law.

The more accurate hierarchy is:

\[
\boxed{
\text{recurrent low-dimensional individuality}
+
\text{heterogeneous system-specific realization}
}
\]

---

# 10. Expression

In controlled *Pipistrellus kuhlii* sensory perturbation, source-defined 3-D angle-of-attack bias remains identity-bearing.

Baseline -> masker:
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**.

Foam no-masker -> foam + masker:
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- no-refit R² = **0.641**.

Post-primary expression attenuation:
- K30 = **+8.004°**
- K10 = **+1.878°**
- exact difference p = **0.00278**.

Thus context can move the common operating state and alter expression strength without necessarily erasing the personal bias.

---

# 11. Wild field realization

Wild *P. hastatus* retains a low-dimensional H/V personal carrier.

2022:
- K = **+0.65314**
- 32/34 positive
- p = **0.0001**.

2023:
- K = **+0.27052**
- 9/11 positive
- p ≈ **0.033**.

But:
- one fixed past-centroid forecast is not a universal rule;
- individual peer-context slopes are unsupported;
- stable personal breadth is not established.

Therefore the persistent empirical object is the **personal bias/coordinate**, not one complete deterministic behavioral distribution.

---

# 12. Spatial partition remains optional

Persistent policy distance does not predict synchronous vertical separation.

2022:
- rho = **+0.188**
- p = **0.274**.

2023:
- rho = **-0.190**
- p = **0.689**.

Therefore:

\[
\boxed{
D_{policy}
\not\Rightarrow
D_{space}
}
\]

Individual specialization is upstream of physical niche partitioning.

---

# 13. Observation-map formulation

Let the persistent empirical personal-policy coordinate be:

\[
\theta_i.
\]

Realized phenotype in environment e:

\[
z_{i,e}
=
\mu_e
+
G_e\theta_i
+
\epsilon_{i,e}.
\]

Identity-attributable realized covariance:

\[
\Sigma^{id}_{z,e}
=
G_e\Sigma_\theta G_e^T.
\]

Thus:

\[
\Sigma_\theta\neq0
\]

does not require strong spatial differentiation.

The same personal state can be:
- visible in one movement coordinate;
- compressed in another;
- rotated into another behavioral axis;
- almost invisible to a chosen spatial metric.

This is the mechanistic resolution of the original JAE paradox.

---

# 14. Formation hypothesis — functional abundance × history

External bat biomechanics shows that the same loading challenge can be solved through different combinations of wing-motion and wing-shape adjustments.

The proposed formation mechanism is:

\[
\boxed{
\text{multiple adequate control solutions}
\times
\text{personal history}
\rightarrow
\text{personal policy}
}
\]

The juvenile data supply the history-dependent refinement component.

The adult data show that the resulting state can become portable.

Functional abundance remains a plausible source of the degrees of freedom within which personal history can individualize movement.

It is not directly measured in the current obstacle archive.

---

# 15. Exact abundance theory

With fixed total exploration mass A and K initially equivalent solutions:

\[
P_i(k|n)
=
\frac{A/K+N_{ik}(n)}
{A+n}.
\]

Long-run:

\[
\theta_i
\sim
\mathrm{Dirichlet}(A/K,\ldots,A/K).
\]

Same-individual matching advantage:

\[
\boxed{
\Delta_K
=
\frac{K-1}{K(A+1)}
}
\]

so:

\[
K=1
\Rightarrow
\Delta_K=0.
\]

For fixed A:

\[
\frac{\partial\Delta_K}{\partial K}>0.
\]

Thus several feasible solutions are required for history-driven solution-choice individuality in this minimal model.

---

# 16. Direct environmental solution abundance is still unmeasured

The public Teshima archive contains:
- Env × Bat × trial trajectories;
- kiku.pkl;
- yubi.pkl;
- no standalone obstacle-layout geometry.

A structure-only pickle probe found no recoverable obstacle/layout geometry schema without executing or decoding numeric payloads.

Verdict:

**STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA**

Do not define environmental abundance using:
- route dispersion;
- route clusters;
- number of trials;
- model prediction error.

Those are realized outcomes and would make the analysis circular.

---

# 17. Payoff layer

Persistent personal policy is a reusable prior, not automatically an optimum.

Let current expressed policy be:

\[
z_{i,e}
=
\mu_e+G_e\theta_i.
\]

Let the current task optimum be \(z^*_{i,e}\).

With performance curvature \(Q_e\), mismatch cost rises with the component of personal expression that points away from the current optimum.

Thus the ecological value of personal policy depends on:
- reuse benefit;
- current mismatch cost;
- switching/update cost.

A persistent individual strategy can therefore be:
- beneficial in familiar conditions;
- nearly neutral along flat-performance directions;
- costly after environmental change.

This is more general than an adaptive partition story.

---

# 18. Current general principle

The evidence now favors:

\[
\boxed{
\text{history}
\rightarrow
\text{compact personal policy}
\xrightarrow{\text{context}}
\text{system-specific movement realization}
\xrightarrow{\text{environment}}
\text{payoff}
}
\]

rather than:

\[
\text{competition}
\rightarrow
\text{exclusive niche}
\rightarrow
\text{specialization}.
\]

Spatial partitioning can occur downstream.

It is not required for formation or maintenance.

---

# 19. Decisive next experiment

The current archives have reached their causal ceiling.

The next experiment should independently manipulate:

### Formation-side solution repertoire
- one effective solution;
- several adequate solutions;
- reopen previously available alternatives.

### Expression/payoff environment
- broad low-penalty context;
- narrow high-penalty context;
- reversible sensory or biomechanical perturbation.

For the same individuals measure:
- policy coordinate;
- exploration;
- consolidation;
- route geometry;
- performance;
- spatial overlap;
- hysteresis/recovery.

The decisive demonstration would be:

> **the personal policy persists while the mapping from that policy to realized geometry and payoff changes.**

---

# Bottom line

The geometry programme makes the mechanism more compact, not more complex.

> **A small personal movement-policy state can organize multiple aspects of trajectory geometry. Personal history helps build that state; context controls how it is expressed; and spatial partition is only one possible downstream outcome.**

For *Rhinolophus nippon*, the strongest current candidate state remains the transparent two-coordinate pair:

\[
\boxed{
\theta_i=(\text{FlightIntensity},\text{ManeuveringExtent})
}
\]

to the resolution of the available linear diagnostics.
