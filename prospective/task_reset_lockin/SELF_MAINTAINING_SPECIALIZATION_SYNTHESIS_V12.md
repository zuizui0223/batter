# Self-maintaining specialization synthesis v12

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V11.**

JAE v0.4.0 remains frozen.

V12 adds a formal distinction between:
- persistent personal policy;
- its environment-specific expression;
- the realized individualized spatial niche.

The central mechanism is now represented as two linked processes:

\[
\boxed{
\text{solution repertoire + history}
\rightarrow
\text{personal policy}
}
\]

and:

\[
\boxed{
\text{personal policy}
\xrightarrow{G_e}
\text{realized phenotype / spatial niche}
}
\]

This explains both:
- how individuality can form internally;
- why the same individuality need not produce physical niche partitioning.

---

# 1. Empirical formation

Juvenile fruit-bat movement provides evidence that later personal organization is not fully specified by the earliest observable independent history.

For target valid days 11–20:

### earliest two valid history days
- E = **+15.19**
- p = **0.1655**
- 8/14 positive
- unsupported

### recent two valid days versus earliest two
- Q = **+144.08**
- p = **0.0001**
- 10/14 positive
- supported identity-specific refinement

Thus:

\[
\boxed{
\text{personal movement history changes where predictive individual information resides}
}
\]

without requiring one common monotonic developmental trajectory.

---

# 2. Empirical maintenance

Adult *Rhinolophus nippon* carries a portable low-dimensional movement-policy coordinate.

Held-out task prediction:
- 2-D R² = **0.4666**
- p = **0.0002**

Pairwise personal-policy geometry:
- vector R² = **0.5797**
- p = **0.0001**
- 97.1% direction agreement

Therefore the adult personal state is more than an identity label.

Its relative geometry predicts behavior in unseen tasks.

---

# 3. The persistent state is not only performance magnitude

A scale-free geometry diagnostic removes:
- time;
- speed;
- absolute path length;
- absolute vertical range;
- absolute position.

Yet:

- K_geometry = **+0.38857**
- 5/5 positive
- p = **0.0153**

Thus portable individuality includes:
- relative route efficiency;
- turn geometry;
- vertical route organization;
- normalized displacement structure.

This weakens a pure body-size / speed-scale explanation.

---

# 3b. Geometry individuality is distributed across coordinative components

The scale-free geometry signal is not carried by one narrow route statistic.

A frozen post-primary family ablation divided the eight geometry features into:

### G — global route organization
- path efficiency;
- horizontal displacement ratio;
- absolute vertical displacement ratio;
- vertical range ratio.

### H — horizontal maneuver geometry
- median and p90 absolute horizontal turn angle.

### V — vertical maneuver geometry
- median and p90 absolute vertical slope.

Family-only results:

- G only:
  - K = **+0.40777**
  - 5/5 positive
  - p = **0.0088**

- H only:
  - K = **+0.29605**
  - 5/5 positive
  - p = **0.0089**

- V only:
  - K = **-0.04844**
  - 2/5 positive
  - p = **0.5906**

Leave-family-out results:

- drop G:
  - K = **+0.17413**
  - 5/5 positive
  - p = **0.0461**

- drop H:
  - K = **+0.30366**
  - 5/5 positive
  - p = **0.0184**

- drop V:
  - K = **+0.46622**
  - 5/5 positive
  - p = **0.0111**

Frozen diagnostic verdict:

**ROBUST_TO_ALL_FAMILY_ABLATIONS**

Therefore portable scale-free geometry identity is distributed across at least:
- global route organization;
- horizontal maneuver organization.

Vertical slope alone is not a portable carrier.

The strongest bounded interpretation is:

> **the personal movement state is a distributed coordinative organization rather than one scalar speed, verticality or turning trait.**

This remains compatible with motor abundance / degeneracy, but does not prove it.

Direct environmental solution abundance remains unmeasured.

---

# 3c. Geometry portability survives target-normalization removal

The scale-free geometry result also survives a stronger domain-transfer test.

### Target-centered, training-scaled

The held-out environment contributes only its mean; feature SDs come from the other six environments.

- K = **+0.42064**
- 5/5 positive
- p = **0.0040**

### Fully training-only global normalization

The held-out environment contributes neither mean nor SD.

- K = **+0.23140**
- 4/5 positive
- p = **0.0440**

Thus the geometry-level personal signature is not created by target-environment variance normalization.

Even when the unseen obstacle configuration is transformed entirely with statistics learned from other configurations, portable route-organization identity remains detectable.

Together with the family ablation, this supports:

\[
\boxed{
\text{portable personal policy includes distributed, scale-free coordinative geometry}
}
\]

rather than only:
- speed magnitude;
- absolute movement scale;
- one target-normalized shape score.

The fully training-only result is weaker and one bat is negative, so do not claim invariant absolute geometry across every task.

---

# 4. Empirical expression

Controlled *Pipistrellus kuhlii* sensory perturbation shows that the population operating state can move while personal identity remains.

Baseline -> masker:
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**

Foam/no-masker -> foam+masker:
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- R² = **0.641**

A post-primary diagnostic shows context-dependent attenuation:
- K30 = **+8.004°**
- K10 = **+1.878°**
- difference exact p = **0.00278**

Therefore:
- storage can persist;
- expression strength can change.

---

# 5. Empirical spatial consequence

Wild *P. hastatus* shows persistent personal H/V policy.

But pairwise policy distance does not predict synchronous vertical separation:

2022:
- rho = **+0.188**
- p = **0.274**

2023:
- rho = **-0.190**
- p = **0.689**

Thus:

\[
\boxed{
D_{policy}
\not\Rightarrow
D_{space}
}
\]

This is not a contradiction once policy and spatial realization are treated as different levels.

---

# 6. Observation-map formulation

Let the persistent low-dimensional personal state be:

\[
\theta_i.
\]

Let:

\[
Var(\theta_i)=\Sigma_\theta.
\]

In environment e, define the realized phenotype:

\[
z_{i,e}
=
\mu_e
+
G_e\theta_i
+
\epsilon_{i,e}.
\]

Here:
- \(\mu_e\) is the common environmental shift;
- \(G_e\) is the environment-specific expression map;
- \(\epsilon\) is unresolved realization noise.

The identity-attributable realized covariance is:

\[
\boxed{
\Sigma_{z,e}^{id}
=
G_e\Sigma_\theta G_e^T
}
\]

Therefore:

\[
\Sigma_\theta\neq0
\]

does not require:

\[
G_e\Sigma_\theta G_e^T
\]

to be large.

Persistent personal policy can exist while the measured spatial phenotype shows weak differentiation.

---

# 7. Spatial partitioning is an alignment outcome

Expected pairwise policy distance:

\[
E\|\theta_i-\theta_j\|^2
=
2\,tr(\Sigma_\theta).
\]

Expected identity-attributable realized distance:

\[
E\|G_e\theta_i-G_e\theta_j\|^2
=
2\,tr(G_e\Sigma_\theta G_e^T).
\]

Define:

\[
\rho_e
=
\frac{
tr(G_e\Sigma_\theta G_e^T)
}{
tr(\Sigma_\theta)
}.
\]

Then \(\rho_e\) describes how much latent personal differentiation is expressed along the measured realized phenotype.

A population can have:
- large latent individual differentiation;
- small \(\rho_e\);
- strong spatial overlap.

Thus partitioning requires not only individuality, but **alignment between individualized policy dimensions and spatial opportunity**.

---

# 8. Environment can rotate individuality, not only weaken it

\(G_e\) need not be a scalar.

Write:

\[
G_e=R_eD_e.
\]

Then environment can:
- rotate;
- rescale;
- compress

the personal policy dimensions.

The same individual bias can appear as:
- vertical movement in one task;
- horizontal allocation in another;
- turn geometry in another;
- little physical separation in another.

Therefore "the same individual niche" need not look geometrically the same across environments.

A portable personal state can generate different realized niche axes.

---

# 9. Hidden individuality

If a personal-policy dimension lies in the null space of the spatial observation map:

\[
G_e\theta^{hidden}=0,
\]

then that dimension can remain:
- persistent;
- predictive;
- history-dependent;

while being completely invisible to the chosen spatial niche metric.

Therefore:

> absence of spatial partition is not evidence for absence of individual specialization.

It can be evidence that the individualized dimension is upstream of the spatial projection.

---

# 10. Formation theory: solution abundance

The decentralized reinforced-choice model provides an exact candidate mechanism for generating \(\Sigma_\theta\).

With K adequate solutions:

\[
P_i(k|n)
=
\frac{a+N_{ik}(n)}{Ka+n}.
\]

The same-individual matching advantage is:

\[
\boxed{
\Delta(K,a)
=
\frac{K-1}{K(Ka+1)}
}
\]

for K > 1.

Thus:
- multiple feasible solutions;
- repeated history dependence

are sufficient for persistent individuality.

---

# 11. Solution abundance predicts more than "more opportunity -> more specialization"

Under fixed per-solution baseline a:

\[
K^*
=
1+\sqrt{1+\frac{1}{a}}
\]

maximizes the specialization advantage.

Thus:
- one solution -> no solution-choice individuality;
- intermediate solution abundance -> strong lock-in;
- very large solution abundance -> dilution across alternatives.

Under fixed total exploration concentration \(A=Ka\):

\[
\Delta(K,A)
=
\frac{K-1}{K(A+1)}
\]

instead rises and saturates.

Therefore the meaningful quantity is:

\[
\boxed{
\text{solution abundance relative to exploration budget}
}
\]

not abundance alone.

---

# 12. Direct abundance test is not available in the current archive

Figshare 29209493 contains:
- Env × Bat × trial CSVs;
- kiku.pkl;
- yubi.pkl;
- no independent obstacle-layout file.

A structure-only pickle probe:
- executes no pickle;
- opens no numeric arrays;
- finds no obstacle/layout/geometry structural schema.

Verdict:

**STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA**

Therefore do not infer solution abundance from realized trajectories.

This keeps the abundance hypothesis genuinely prospective.

---

# 13. External biomechanics supplies the plausibility premise

Experimental 20% mass loading in *Cynopterus brachyotis* produced different individual kinematic responses to the same physical challenge.

Individuals used different combinations of:
- wing motion;
- camber;
- wing area;
- force-generation mechanics.

The source explicitly discusses functional redundancy / flatter performance surfaces.

This establishes that bat flight can possess multiple adequate coordinative routes to similar task performance.

But those published data do not provide the raw trial-level archive needed for a new batter causal reanalysis.

Therefore this is an external premise, not a new empirical endpoint.

---

# 14. Relation to individualized-niche theory

Existing individualized-niche frameworks already recognize:
- individual differences;
- niche choice;
- niche conformance;
- niche construction;
- developmental and environmental shaping.

Therefore the new contribution is not:
- "individual niches overlap";
- "behavior is plastic";
- "environment changes phenotype".

The stronger mechanistic distinction is:

\[
\boxed{
\text{persistent personal control state}
\neq
\text{realized individualized niche}
}
\]

The realized niche is one environment-specific projection of upstream personal organization.

This provides a mechanistic explanation for why:
- individuality can persist without current partitioning;
- the same individual can express different niche geometry in different contexts;
- environmental change can alter overlap without erasing personal identity.

---

# 15. Unified causal architecture

A schematic developmental-maintenance model is:

\[
\theta_i(t)
=
\theta_i^{intrinsic}
+
h_i(t),
\]

where:
- intrinsic includes stable biomechanics/physiology/developmental predisposition;
- \(h_i(t)\) is history-dependent personal refinement.

Formation occurs inside a feasible solution set:

\[
\mathcal S(E_t,M_i).
\]

History updates policy:

\[
\theta_i(t+1)
=
U(
\theta_i(t),
\mathcal S(E_t,M_i),
x_i(t),
r_i(t)
).
\]

Current environment then projects the stored state:

\[
z_{i,e,t}
=
\mu_e
+
G_e\theta_i(t)
+
\epsilon_{i,e,t}.
\]

Scene/task-specific learned information can be added as:
- task-class policy \(\lambda_{i,k}\);
- scene solution \(m_{i,e}\).

Not every term is independently identified.

The value of the framework is that each empirical programme constrains a different link.

---

# 16. The decisive next experiment

The next experiment should manipulate both sides separately.

## Formation-side manipulation
Change the number/geometry of feasible solutions while holding task goal constant.

Measure:
- exploration;
- consolidation;
- personal-policy dispersion;
- own-history prediction.

## Expression-side manipulation
After personal policy is established, alter environmental mapping while preserving biological identity.

Measure:
- portable \(\theta_i\);
- realized spatial phenotype;
- pairwise overlap.

The strongest demonstration would show:

\[
\theta_i\text{ persists}
\]

while:

\[
G_e
\]

changes enough to alter spatial partitioning.

This would directly prove that specialization is stored upstream of the realized niche.

---

# 17. Programme stop rule

Do not continue using the currently opened archives to estimate:
- solution abundance;
- obstacle opportunity;
- new policy bases;
- post-hoc developmental breakpoints.

The next causal result requires:
- independent environmental geometry;
- an explicit feasible-solution manipulation;
- or a source with designed constraints.

---

# Bottom line

The strongest current general principle is:

> **Individual specialization can be formed by history-dependent selection among multiple feasible behavioral solutions and stored as a portable personal control state. The environment then determines how that state is projected into the realized niche, so persistent individuality does not require persistent spatial partitioning.**

Compactly:

\[
\boxed{
\text{solution repertoire + history}
\rightarrow
\text{personal policy}
\xrightarrow{G_e}
\text{realized niche}
}
\]

This is the current mechanistic ceiling of the evidence.
