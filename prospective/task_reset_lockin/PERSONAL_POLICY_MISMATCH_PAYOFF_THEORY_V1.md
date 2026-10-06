# Personal-policy mismatch and payoff theory v1

## Status

**MECHANISTIC THEORY / ECOLOGICAL PAYOFF SYNTHESIS.**

This note extends the policy-to-space observation-map framework from:
- formation;
- storage;
- expression;
- spatial realization

to the ecological consequence of **policy-environment match or mismatch**.

It is motivated by:
- controlled bat sensory perturbation;
- external route-choice experiments with individually biased animals;
- the portable-policy results in batter.

It is not a new empirical fitness endpoint.

---

# 1. Why payoff is the next missing layer

A persistent personal policy is not automatically:
- adaptive;
- neutral;
- costly.

The same stored bias can be useful in one environment and mismatched in another.

Therefore the relevant chain is:

\[
\boxed{
\text{personal policy}
\xrightarrow{G_e}
\text{realized action}
\xrightarrow{\text{environment}}
\text{performance/payoff}
}
\]

The ecological question is no longer merely:

> does individuality persist?

It is:

> **when does retaining a personal prior help, and when does the current environment force that prior to be suppressed or updated?**

---

# 2. Realized policy versus environment-specific optimum

Let:

\[
\theta_i
\]

be the persistent personal policy coordinate.

Let realized behavior be:

\[
z_{i,e}
=
\mu_e
+
G_e\theta_i.
\]

Let the task-specific performance optimum for individual i be:

\[
z^*_{i,e}
=
\mu^*_e
+
H_e\theta_i.
\]

Here:

- \(G_e\) = how strongly current behavior expresses persistent individuality;
- \(H_e\) = how strongly the environment/task actually benefits from retaining that individualized direction.

The two maps need not be equal.

---

# 3. Quadratic mismatch loss

Let task loss near the optimum be:

\[
L_{i,e}
=
(z_{i,e}-z^*_{i,e})^T
Q_e
(z_{i,e}-z^*_{i,e}),
\]

where \(Q_e\) describes how strongly deviations matter for performance.

After removing the population mean shift, the individuality-related mismatch is:

\[
(G_e-H_e)\theta_i.
\]

With:

\[
Var(\theta_i)=\Sigma_\theta,
\]

the expected individuality-related loss is:

\[
\boxed{
E[L_e^{id}]
=
tr\left[
Q_e
(G_e-H_e)
\Sigma_\theta
(G_e-H_e)^T
\right].
}
\]

This gives a precise meaning to **policy-environment mismatch**.

---

# 4. Three ecological regimes

## Regime A — individuality is task matched

If:

\[
G_e \approx H_e,
\]

personal differences expressed by the animal align with personal differences that improve performance.

Persistent individuality can be retained with little mismatch cost.

## Regime B — environment favors convergence

If:

\[
H_e\approx0,
\]

the task has a narrow common solution.

Persistent expression:

\[
G_e\theta_i
\]

then creates excess loss.

Selection / behavioral plasticity should favor:
- smaller expression gain;
- stronger convergence;
- faster updating.

## Regime C — environment has broad or multiple optima

If the performance surface is flat or contains several adequate solutions, \(Q_e\) is weak along some directions.

Then even large personal-policy variation can persist with low performance cost.

This is the direct link to functional abundance / degeneracy.

---

# 5. Functional abundance is a flat-performance-surface hypothesis

Multiple adequate solutions mean that the performance surface has directions with low curvature.

In the quadratic approximation, those are small-eigenvalue directions of:

\[
Q_e.
\]

Individual differences can accumulate along these directions because:

\[
\theta^TQ_e\theta
\]

changes little even when \(\theta\) differs substantially.

Thus functional abundance predicts:

> **persistent individuality should preferentially occupy behavior-space directions with relatively shallow performance penalties.**

This is stronger than saying "many routes are possible."

It predicts which dimensions of individual policy are most likely to persist.

---

# 6. Why environmental constraint can compress individuality

Suppose one personal axis is sufficient for intuition:

\[
z_{i,e}
=
\mu_e+\alpha_e\theta_i.
\]

If the current task-specific optimum has little individual differentiation:

\[
H_e\approx0,
\]

then individuality-related expected loss is:

\[
E[L_e^{id}]
=
q_e\alpha_e^2 Var(\theta).
\]

As task penalty \(q_e\) increases, expressing the old personal bias becomes more costly.

This makes attenuation of \(\alpha_e\) ecologically sensible.

It does **not** imply that stored \(\theta_i\) is erased.

---

# 7. Switching / updating cost explains incomplete convergence

Why not always set:

\[
\alpha_e=0
\]

when the environment favors one common solution?

Because changing or suppressing a learned personal policy can itself have costs.

Represent a generic retention/switching penalty:

\[
C_{switch}
=
\lambda_e(\alpha_e-1)^2.
\]

For a common optimum \(H_e=0\), minimize:

\[
J(\alpha_e)
=
q_e Var(\theta)\alpha_e^2
+
\lambda_e(\alpha_e-1)^2.
\]

The optimum is:

\[
\boxed{
\alpha_e^*
=
\frac{\lambda_e}
{q_eVar(\theta)+\lambda_e}.
}
\]

Therefore:

- weak environmental penalty \(q_e\) -> personal bias remains strongly expressed;
- strong environmental penalty -> individuality is compressed;
- strong switching/history cost \(\lambda_e\) -> residual personal bias persists even under constraint.

This creates a mechanistic reason for:

\[
0<\alpha_e<1.
\]

---

# 8. Connection to the controlled bat sensory perturbation

In the *Pipistrellus kuhlii* masker experiment:

- sensory challenge caused a shared movement shift;
- personal baseline bias remained predictive;
- post-primary expression gain was stronger at 30 cm than 10 cm.

Observed descriptive gains:

\[
\alpha_{30}\approx0.863,
\qquad
\alpha_{10}\approx0.324.
\]

The source paper independently shows that reducing angle of attack weakens background echoes and improves signal-to-noise conditions.

Therefore the system has the qualitative ingredients expected under a mismatch model:

- prior personal movement bias;
- an environment-imposed sensory performance pressure;
- plastic suppression/reorientation of behavior;
- incomplete retention of identity.

Do **not** fit \(q_e\) or \(\lambda_e\) from these six bats post hoc.

The equations are explanatory theory, not identified parameters.

---

# 9. Cross-taxon external ecological example

In the honeybee two-aperture experiment:

- individuals possess persistent left/right route-choice biases;
- the environment changes the relative widths of the two apertures;
- population choice shifts toward the wider aperture;
- when a strong personal bias directs a bee toward the narrower aperture, transit time increases.

This is a direct behavioral example of:

\[
\text{persistent personal bias}
\times
\text{environmental asymmetry}
\rightarrow
\text{performance cost}.
\]

It shows why a personal policy can be real and persistent without being universally beneficial.

This is external triangulation, not bat evidence.

---

# 10. Specialization can therefore carry a hidden trade-off

A personal policy can reduce:
- search cost;
- decision time;
- relearning;
- sensorimotor uncertainty

in familiar recurring conditions.

But the same policy can increase:
- mismatch;
- maneuvering cost;
- error risk;
- transition time

after environmental change.

Thus the maintenance problem can be written as:

\[
\boxed{
\text{reuse benefit}
-
\text{mismatch cost}
-
\text{switching cost}.
}
\]

Persistent specialization is favored when long-run reuse benefits exceed the expected costs of mismatch and updating.

---

# 11. Why spatial partition is still optional

The payoff model does not require individuals to occupy different spatial niches.

Two bats can:
- share the same physical volume;
- carry different internal policies;
- achieve similar performance through different control solutions.

If the performance surface is flat along those differences:

\[
Q_e \approx 0
\]

in the individualized directions.

Then policy diversity can persist without:
- competition;
- resource partition;
- current fitness differences.

Spatial separation is one possible realization, not the maintenance condition.

---

# 12. New empirical predictions

## P1 — constraint-dependent compression

When a task's performance surface becomes steeper along an individualized axis:
- between-individual expressed variation should decrease;
- portable identity may remain detectable in other axes.

## P2 — mismatch cost

Individuals whose stored bias points away from the current task optimum should show:
- longer adjustment time;
- larger energetic/kinematic correction;
- lower success;
- or higher transit cost.

## P3 — hysteresis

After the environment returns to a familiar state:
- a stored-policy model predicts faster recovery of the old individual ordering than de novo learning predicts.

## P4 — flat-direction persistence

Individual variation should persist most strongly along behavior-space dimensions with weak performance curvature.

## P5 — history × constraint interaction

History-dependent specialization should be strongest where:
- several solutions are adequate;
- repeated reuse is possible;
- switching/search costs are nonzero.

---

# 13. Decisive experiment

For the same identified bats:

1. train a stable personal policy under a broad/degenerate solution set;
2. impose a narrow solution set with a measurable performance optimum;
3. quantify:
   - expression gain;
   - performance cost;
   - adjustment speed;
4. reopen the broad solution set;
5. test:
   - recovery of prior policy;
   - hysteresis;
   - whether prior bias predicts recovery route.

This directly estimates the trade-off between:
- storage;
- plastic expression;
- mismatch;
- switching.

---

# 14. Relation to niche theory

A realized individual niche can be beneficial, neutral or costly depending on the current environment.

Therefore individual specialization should not be interpreted automatically as:
- adaptive niche partitioning;
- optimized resource differentiation.

The stronger framework is:

\[
\boxed{
\text{stored personal policy}
+
\text{environment-specific opportunity}
\rightarrow
\text{performance}
}
\]

with realized spatial niche as one downstream phenotype.

---

# Bottom line

Persistent individuality is best viewed as a reusable prior.

A reusable prior is valuable because it avoids solving every recurrent movement problem from scratch.

But when the world changes, the same prior can become a mismatch.

This yields a simple ecological principle:

> **individual specialization persists when the long-run value of reusing a personal solution exceeds the cost of being wrong when environmental constraints change.**

The current bat programme establishes the persistence and context-gated expression sides of this trade-off.

Direct fitness/performance quantification of the mismatch remains prospective.
