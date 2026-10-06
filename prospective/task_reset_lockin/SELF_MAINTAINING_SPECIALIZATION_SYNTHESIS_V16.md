# Self-maintaining specialization synthesis v16

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V15.**

JAE v0.4.0 remains frozen.

V16 tightens one crucial point:

> **context-dependent realization is supported, but the realization map itself is not identified as a simple shared linear operator.**

The strongest empirical architecture is therefore:

\[
\boxed{
\text{personal history}
\rightarrow
\text{portable personal policy}
\rightarrow
\text{context-sensitive realization}
\rightarrow
\text{optional spatial partition / payoff}
}
\]

The persistent state is more portable than the detailed movement geometry through which it is expressed.

---

# 1. Formation — personal history refines individuality

Juvenile fruit-bat data show:

### Earliest two structurally valid movement days -> late movement
- E = **+15.19**
- p = **0.1655**
- 8/14 positive
- unsupported.

### Recent two days minus earliest two
- Q = **+144.08**
- null mean = **+0.35**
- p = **0.0001**
- 10/14 positive
- supported identity-specific refinement.

Thus later personal organization is not fully specified by the earliest observable independent movement history.

The developmental process is not one common monotonic ramp, but personal history becomes substantially more identity-informative through early ontogeny.

---

# 2. Maintenance — the personal coordinate is genuinely portable

For adult *Rhinolophus nippon*:

\[
\theta_i=(I_i,M_i)
\]

with:
- I = FlightIntensity;
- M = ManeuveringExtent.

Transparent 2-D identity:
- K = **+0.55428**
- 5/5 positive
- p = **0.0001**.

Held-out no-refit 2-D coordinate prediction:
- R² = **0.4666**
- p = **0.0002**
- median predicted-observed cosine = **0.896**.

Held-out pair-displacement geometry:
- R² = **0.5797**
- p = **0.0001**
- 97.1% positive vector alignment.

Thus the relative personal coordinate predicts behavior in unseen obstacle tasks.

This is stronger than ordinary repeatability.

---

# 3. Portable identity is not merely speed magnitude

Scale-free route geometry removes:
- elapsed time;
- speed;
- turn rate per time;
- absolute path length;
- absolute vertical range;
- absolute spatial offset.

Yet cross-configuration identity remains:

- K_geometry = **+0.38857**
- 5/5 positive
- p = **0.0153**.

Therefore portable individuality includes route organization, not only vigor/performance magnitude.

---

# 4. Geometry identity is compact rather than modular

Global route organization G alone:
- K = **+0.40777**
- p = **0.0088**.

Horizontal maneuver geometry H alone:
- K = **+0.29605**
- p = **0.0089**.

Vertical-slope geometry V alone:
- unsupported.

But cross-fitted residualization gives:

### H after G
- K = **+0.06290**
- p = **0.1064**
- unsupported.

### G after H
- K = **+0.00604**
- p = **0.4035**
- unsupported.

Thus G and H are not supported as independent identity modules.

They are better treated as multiple manifestations of a lower-dimensional personal movement organization.

---

# 5. I/M aligns strongly with geometry within an environment

Remove FlightIntensity only:

- residual geometry K = **+0.30775**
- 5/5 positive
- p = **0.0029**.

Remove I + M jointly **within each environment**:

- residual geometry K = **-0.01467**
- 1/5 positive
- p = **0.4509**.

Thus, within a given obstacle context, the transparent I/M pair statistically absorbs the identity-bearing component of detailed route geometry.

This is a compression result.

It is not proof of causal upstream control.

---

# 6. One universal I/M -> geometry map fails

A stronger test estimates:
- movement scaling;
- geometry scaling;
- linear I/M -> geometry coefficients

using the other six environments only.

Apply that map unchanged to the held-out seventh environment.

Residual geometry identity remains:

- K = **+0.20160**
- 5/5 positive
- p = **0.0156**.

Therefore one universal fixed map

\[
g=B\theta
\]

is inadequate.

The mapping from portable policy to detailed geometry changes with task/environment.

---

# 7. Coarse policy transfers more broadly than detailed geometry

A target-environment profile treats each obstacle configuration as the unseen target.

### Full movement policy
- broadly transferred in **6/7** environments.

### Scale-free route geometry
- broadly transferred in only **3/7** environments.

### Pulse policy
- broadly transferred in **5/7** environments.

The most important contrast is:

\[
\boxed{
\text{coarse movement-policy portability}
>
\text{detailed-geometry portability}
}
\]

Detailed geometry is the most context-sensitive layer.

This is direct empirical support for a coarse-to-fine realization hierarchy.

---

# 8. The environment-specific realization map is not yet identified

A dedicated test asked whether the current environment's I/M -> geometry map could be estimated from **other bats only**.

Frozen support:
- focal bat completely excluded from regression;
- >=3 peer bats required;
- only Env1–Env4 structurally pass.

Across 37 focal trajectories, peer-defined map prediction was:

\[
R^2=-1.419
\]

relative to the environment-centered zero prediction.

Thus the peer-only linear map is not predictively adequate.

Residual identity after this noisy map is also unsupported:

- K = **-0.233**
- 2/4 positive
- p = **0.6599**.

But the residual-identity disappearance is **not** evidence that a shared map was successfully removed, because the map itself predicts geometry very poorly.

Therefore do not write:

\[
g_{i,e}=G_e\theta_i
\]

as an empirically identified shared linear mechanism.

The safer current representation is:

\[
\boxed{
g_{i,e}
=
\mathcal R(
E_e,
\theta_i,
u_{i,e}
)
}
\]

where:
- \(E_e\) is task/environment;
- \(\theta_i\) is the portable empirical personal state;
- \(u_{i,e}\) collects unresolved context-specific and individual × environment realization terms;
- \(\mathcal R\) is not identified as linear.

This is the key V16 correction.

---

# 9. Controlled perturbation independently confirms context-gated expression

In *Pipistrellus kuhlii*:

### baseline -> masker
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**.

### foam no-masker -> foam + masker
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- no-refit R² = **0.641**.

Post-primary:
- K30 = **+8.004°**
- K10 = **+1.878°**
- difference p = **0.00278**.

Thus context can alter movement and the strength with which individuality is expressed without necessarily erasing the personal signal.

This conclusion does not depend on estimating a shared realization operator.

---

# 10. Cross-species generality is coarse-to-fine

A fixed Rhino scale-free geometry representation is unsupported in independent *Carollia perspicillata*:

- K = **-0.0350**
- 3/7 positive
- p = **0.2144**.

But the coarser Rhino-derived low-dimensional policy transfers better, especially FlightIntensity.

For *Miniopterus fuliginosus*, even the coarse portable individual signal is unsupported.

Therefore the current generality hierarchy is:

\[
\boxed{
\text{some systems share coarse low-dimensional individuality}
}
\]

while:

\[
\boxed{
\text{detailed coordinative geometry is strongly system/task specific}
}
\]

There is no universal bat-wide geometry law or universal two-axis law.

---

# 11. Wild spatial consequence remains separate

Wild *P. hastatus* carries persistent low-dimensional H/V individuality.

Yet persistent policy distance does not predict synchronous vertical separation:

### 2022
- rho = **+0.188**
- p = **0.274**.

### 2023
- rho = **-0.190**
- p = **0.689**.

Therefore:

\[
\boxed{
\text{personal-policy differentiation}
\not\Rightarrow
\text{physical-space partition}
}
\]

This is the ecological reason for distinguishing portable state from realized niche geometry.

---

# 12. Functional abundance remains a formation hypothesis, not a current result

External motor-control theory already establishes:
- motor abundance / degeneracy;
- environmental affordances constraining available motor solutions.

Bat loading studies also show multiple kinematic responses to a common mechanical challenge.

The proposed formation mechanism is:

\[
\boxed{
\text{multiple adequate solutions}
\times
\text{personal history}
\rightarrow
\text{individualized policy}
}
\]

The juvenile history result supports the history-refinement side.

But environmental solution abundance itself is not measurable in the current Teshima archive.

A structure-only audit found no public obstacle-geometry schema.

Verdict:

**STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA**

Do not infer abundance from realized trajectory dispersion.

---

# 13. Exact theory remains useful but prospective

With fixed total exploration mass A and K initially equivalent solutions:

\[
P_i(k|n)
=
\frac{A/K+N_{ik}(n)}
{A+n}.
\]

Then:

\[
\theta_i
\sim
Dirichlet(A/K,\ldots,A/K)
\]

and same-individual matching advantage is:

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

This proves that multiple solutions plus history dependence are sufficient for stochastic individualization.

It does not show that the empirical bats implement this algorithm.

---

# 14. Relation to current individualised-niche theory

Current individualized-niche frameworks already recognize:
- dynamic realized niches;
- genotype × environment × life-history effects;
- niche choice;
- niche conformance;
- niche construction;
- individual plasticity.

Motor-control theory already recognizes that affordances constrain motor abundance.

Therefore the contribution is **not**:
- discovery that realized niches are dynamic;
- discovery that environment changes phenotype;
- discovery of motor abundance.

The narrower empirical contribution is:

> **movement individuality can be decomposed into formation, portable state, context-sensitive realization, and spatial consequence, and these levels need not covary.**

In particular:
- history can refine the personal state;
- the personal state can predict unseen tasks;
- detailed geometry can become context dependent sooner than coarse policy;
- physical niche partition can remain weak.

---

# 15. The current mechanistic ceiling

Directly supported:

1. **formation:** recent personal history gains identity-specific predictive information;
2. **maintenance:** a low-dimensional personal coordinate transfers across tasks;
3. **coarse-to-fine hierarchy:** movement policy transfers more broadly than detailed geometry;
4. **expression:** sensory perturbation can alter behavior without erasing personal bias;
5. **spatial consequence:** persistent policy need not imply stronger physical separation.

Not identified:

- a shared linear environment-specific realization map;
- environmental solution abundance;
- causal neural dimensionality;
- exact contribution of biomechanics versus learning;
- fitness benefit.

---

# 16. Decisive next experiment

The next experiment should be designed to estimate the realization process rather than infer it retrospectively.

For the same individuals:

1. train a personal policy under a known multi-solution task;
2. manipulate obstacle/affordance geometry with **known coordinates**;
3. include enough individuals and repeated trials to estimate context maps out-of-sample;
4. manipulate solution abundance independently of generic difficulty;
5. restore the original geometry;
6. quantify performance and spatial overlap.

The decisive test is:

> **Does a portable personal coordinate remain predictable while experimentally controlled changes in the feasible solution set alter its detailed geometric realization and spatial overlap?**

This would directly connect:
- formation;
- storage;
- expression;
- niche realization.

---

# Bottom line

The strongest current statement is:

> **Personal movement information is more portable than the detailed geometry in which it is expressed. Personal history helps build the individual state, current context changes its realization, and persistent spatial partition is not required.**

Compactly:

\[
\boxed{
\text{history}
\rightarrow
\text{portable personal policy}
\rightarrow
\text{context-sensitive movement realization}
\rightarrow
\text{optional niche partition}
}
\]

The realization operator is the major remaining empirical unknown.
