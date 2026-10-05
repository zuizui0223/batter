# Self-reinforcing specialization without spatial partitioning v1

## Status

**POST-PRIMARY MECHANISTIC SUFFICIENCY MODEL.**

This note is not a new empirical test and does not modify JAE v0.4.0.

Its purpose is to answer:

> How can persistent individual specialization be maintained if individuals do not need to keep partitioning space?

The model gives one minimal sufficient mechanism.

---

## 1. Minimal process

Suppose a recurring task has \(K\) feasible solutions.

For individual \(i\), let \(n_{ik}(t)\) be the number of times solution \(k\) has been used before decision \(t\).

At the next decision,

\[
P(A_{it}=k\mid \mathbf n_i(t))
=
\frac{\alpha+n_{ik}(t)}
{K\alpha+t},
\]

where \(\alpha>0\) is a baseline exploration / pseudocount parameter.

Previous use of a solution therefore increases its probability of reuse. Crucially, **no term involving another individual appears anywhere in the choice rule**.

Biologically, the reinforcement term can stand for any process by which prior use makes reuse cheaper or more likely:

- learned landmarks;
- reduced search cost;
- sensorimotor familiarity;
- known obstacle geometry;
- route/task memory;
- repeated resource knowledge;
- switching cost;
- success-conditioned habit.

This is a mechanism class, not a claim that bats literally implement a Pólya urn.

---

## 2. Exact asymptotic result

For the symmetric Pólya process,

\[
\mathbf p_i
=
\lim_{t\to\infty}
\frac{\alpha+\mathbf n_i(t)}
{K\alpha+t}
\sim
\mathrm{Dirichlet}(\alpha,\ldots,\alpha).
\]

Initially exchangeable individuals can therefore become persistently different because early stochastic choices are reinforced.

No fixed morphological difference is required for this sufficiency result.

No interaction or exclusion among individuals is required.

---

## 3. Individual specialization increases

Define within-individual concentration

\[
H_i=\sum_{k=1}^{K}p_{ik}^{2}.
\]

Uniform use of all \(K\) solutions gives

\[
H_{\mathrm{uniform}}=\frac{1}{K}.
\]

Under the symmetric Dirichlet limit,

\[
E[H_i]
=
\frac{\alpha+1}{K\alpha+1}.
\]

Hence

\[
E[H_i]-\frac{1}{K}
=
\frac{K-1}{K(K\alpha+1)}
>0.
\]

Thus self-reinforced reuse produces individual specialization from initially symmetric conditions.

As \(\alpha\to\infty\), use approaches uniformity. As \(\alpha\to0\), early choices produce stronger lock-in.

---

## 4. Specialization does not require between-individual partitioning

For two independently reinforced individuals \(i\) and \(j\),

\[
E\!\left[\sum_{k=1}^{K}p_{ik}p_{jk}\right]
=
\sum_k E[p_{ik}]E[p_{jk}]
=
K\left(\frac1K\right)^2
=
\frac1K.
\]

That is exactly the expected overlap of two uniform individuals.

The same process therefore yields simultaneously:

- **within-individual concentration above uniform**;
- **no expected repulsion between individuals**.

In words:

> Individuals can specialize because each reuses its own history, not because different individuals continuously push one another into different solutions.

This is the mathematical separation between **specialization** and **partitioning**.

If several behavioral solutions themselves occupy overlapping physical space, realized spatial overlap can be even greater while individual policy remains distinct.

---

## 5. Why self-history predicts but peer history need not

The next decision depends on \(\mathbf n_i(t)\), not on \(\mathbf n_j(t)\) for \(j\ne i\).

The model therefore predicts:

1. focal self-history remains informative;
2. another individual's history is not an interchangeable predictor;
3. contemporaneous co-use is not required to maintain the focal strategy;
4. removing a competitor does not erase the state already stored in the focal individual's history.

This is the precise sense in which specialization can become **self-maintaining**.

---

## 6. Formation can be rapid rather than smoothly monotonic

Early stochastic events have disproportionate leverage because history is initially short.

A small initial imbalance changes future choice probabilities, which feeds back into the imbalance:

\[
\text{small early difference}
\rightarrow
\text{biased reuse}
\rightarrow
\text{persistent personal state}.
\]

The model therefore does not require a slow monotonic rise in individuality. Self-predictability can appear early and then fluctuate around an established personal state.

---

## 7. Context-specific realization

The discrete urn is only the simplest sufficient model. The empirical movement phenotype can be written more generally as

\[
\mathbf x_{iet}
=
\boldsymbol\mu_e
+
\mathbf\Lambda_{e,s}\boldsymbol\theta_i
+
\boldsymbol\varepsilon_{iet},
\]

where:

- \(\boldsymbol\theta_i\) is a persistent personal policy state;
- \(\mathbf\Lambda_{e,s}\) maps that state into the movement expressed by species \(s\) in environment \(e\);
- \(\boldsymbol\mu_e\) is the shared environmental response;
- \(\boldsymbol\varepsilon_{iet}\) is remaining within-individual variation.

A change in task geometry can therefore change the realized route even if the personal state persists.

---

## 8. Relation to the empirical programme

The current evidence is qualitatively consistent with this mechanism class.

### Adult field data
- persistent individual vertical organization;
- self-history information across independent bouts;
- no general positive terrain-relative spatial segregation;
- no general additional vertical separation during synchronous co-use.

### Ontogeny
- a universal slow monotonic formation ramp was unsupported;
- self-history information was already present at the earliest estimable stage and was strongly informative later.

### Randomized early environment
- broad enriched versus impoverished developmental treatment did not detectably alter history-carrier strength.

### Laboratory task transfer
- in *Rhinolophus nippon*, cross-configuration movement individuality is low-dimensional;
- a dominant flight-intensity axis and a second maneuver / route-organization axis carry the calibrated signal.

### Wild *Phyllostomus hastatus*
- horizontal and vertical movement components form a persistent low-dimensional carrier;
- the scalar average can fail even when the vector carrier persists.

### Important negative bridge
- persistent low-dimensional movement-policy similarity did not predict which other individual had the most similar centered vertical-distribution shape.

Thus the measured persistent policy is **not identical to the full vertical spatial phenotype**.

---

## 9. Revised mechanistic architecture

The simplest current architecture is

\[
\boxed{
\text{early stochastic / performance-biased sampling}
\rightarrow
\text{self-reinforced low-dimensional policy}
\rightarrow
\text{context-specific behavioral realization}
}
\]

rather than

\[
\text{competition}
\rightarrow
\text{persistent spatial exclusion}
\rightarrow
\text{specialization}.
\]

This architecture naturally permits:
- persistent individuality;
- changing exact routes;
- strong spatial overlap;
- species-specific policy axes;
- failure of a single scalar projection;
- additional phenotype layers not explained one-to-one by the measured policy.

---

## 10. Testable discriminators

The sufficiency model is not yet a unique causal explanation.

### History-dependent reuse
Prediction:
- a true task reset weakens old-history prediction;
- exploration rises;
- new self-history rapidly becomes predictive.

### Stable morphology / performance
Prediction:
- pre-existing performance traits predict the new solution immediately after reset;
- individual ordering transfers before substantial new experience accumulates.

### Active competition
Prediction:
- current competitor configuration predicts route/policy change beyond self-history;
- removing competitors rapidly changes strategy.

### Exact resource specialization
Prediction:
- conditioning on exact repeated task/resource removes most personal identity.

The highest-value direct experiment remains repeated-individual 3-D tracking immediately before and after a genuine task reset.

---

## Bottom line

A mathematically sufficient answer to the maintenance problem is:

> **individual specialization can be maintained by positive feedback from an individual's own behavioral history.**

Under self-reinforcing reuse,

> **within-individual specialization can increase while expected between-individual overlap does not decrease at all.**

The empirical programme makes this mechanism class plausible, while the biological implementation of the reinforcing state—memory, switching cost, motor familiarity, stable performance, or a mixture—remains to be identified.
