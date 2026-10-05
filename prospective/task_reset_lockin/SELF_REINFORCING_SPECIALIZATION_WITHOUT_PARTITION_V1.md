# Self-reinforcing specialization without spatial partitioning v1

## Status

**POST-PRIMARY MECHANISTIC SUFFICIENCY MODEL.**

This note is not a new empirical test and does not modify JAE v0.4.0.

Its purpose is to answer a specific biological question raised by the empirical results:

> How can persistent individual specialization be maintained if individuals do not need to keep partitioning space?

The model below gives one minimal sufficient mechanism.

---

## 1. Minimal process

Suppose a recurring movement task has K feasible solutions.

For individual i, let n_ik(t) be the number of times solution k has been used before decision t.

At the next decision:

[
P(A_{it}=k mid mathbf n_i(t))
=
rac{alpha+n_{ik}(t)}
{Kalpha+t}.
]

where:

- (alpha>0) is the baseline exploration / pseudocount parameter;
- previous use of a solution increases its probability of reuse;
- **no term involving another individual appears anywhere in the choice rule**.

Biologically, the reinforcement term can represent any mechanism by which prior use makes reuse cheaper or more likely:

- learned landmarks;
- reduced search cost;
- sensorimotor familiarity;
- known obstacle geometry;
- route/task memory;
- repeated resource knowledge;
- switching cost;
- success-conditioned habit.

The equation is therefore a mechanism class, not a claim that bats literally implement a Pólya urn.

---

## 2. Exact asymptotic result

The symmetric Pólya process has a standard limiting form.

For every individual i,

[
mathbf p_i
=
lim_{tightarrowinfty}
rac{alpha+mathbf n_i(t)}
{Kalpha+t}
sim
mathrm{Dirichlet}(alpha,ldots,alpha).
]

Thus initially exchangeable individuals become persistently different because early stochastic choices are reinforced.

No fixed morphological difference is required for this sufficiency result.

No interaction or exclusion among individuals is required.

---

## 3. Individual specialization increases

Define within-individual concentration:

[
H_i = sum_{k=1}^{K} p_{ik}^2.
]

Uniform use of all K solutions gives:

[
H_{mathrm{uniform}} = rac{1}{K}.
]

Under the symmetric Dirichlet limit,

[
E[H_i]
=
rac{alpha+1}{Kalpha+1}.
]

Therefore the expected excess concentration is

[
E[H_i]-rac{1}{K}
=
rac{K-1}{K(Kalpha+1)}
>0.
]

So the process creates individual specialization from initially symmetric conditions.

The smaller (alpha), the stronger the lock-in.

Limits:

- (alphaightarrowinfty): nearly uniform use, little specialization;
- (alphaightarrow0): strong concentration onto a small number of personal solutions.

---

## 4. But individuals do not have to partition solutions

For two independently reinforced individuals i and j,

[
Eleft[sum_{k=1}^{K} p_{ik}p_{jk}ight]
=
sum_k E[p_{ik}]E[p_{jk}]
=
Kleft(rac1Kight)^2
=
rac1K.
]

That is exactly the overlap expected if both individuals were uniform.

So the same process gives:

- **within-individual concentration above uniform**;
- **no expected repulsion between individuals**.

In words:

> individuals can become specialized because each reuses its own history, not because different individuals continuously push one another into different solutions.

This is the key mathematical separation between:

- specialization;
- partitioning.

If multiple behavioral solutions themselves occupy overlapping physical space, realized spatial overlap can be even higher while individual policy remains distinct.

---

## 5. Why self-history predicts but peer history need not

The next choice depends on:

[
mathbf n_i(t)
]

and not on:

[
mathbf n_j(t), quad j
eq i.
]

Therefore the model predicts:

1. focal self-history remains informative;
2. another individual's history is not an interchangeable predictor;
3. contemporaneous co-use is not required to maintain the focal strategy;
4. removing the competitor does not erase the state already stored in the focal individual's history.

This is the precise sense in which a specialization can become **self-maintaining**.

---

## 6. Formation is expected to be rapid and non-monotonic

The mechanism does not predict a slow smooth increase in individuality.

Early stochastic events have disproportionate leverage because the history is initially short.

After only a few choices, a small initial imbalance changes future choice probabilities, which feeds back into the imbalance.

Thus the qualitative trajectory is:

[
	ext{small early difference}
ightarrow
	ext{biased reuse}
ightarrow
	ext{persistent personal state}.
]

Individual self-predictability can therefore be detectable very early and then fluctuate rather than rise monotonically.

This matches the currently observed formation boundary better than a universal slow-canalization model.

---

## 7. Task reset

The model is task specific.

Let each ecological task/environment e have its own mapping from latent personal state to realized movement:

[
mathbf x_{iet}
=
oldsymbolmu_e
+
mathbfLambda_eoldsymbol	heta_{it}
+
oldsymbolarepsilon_{iet}.
]

A true change in task geometry can:

- invalidate the old solution set;
- change (mathbfLambda_e);
- reduce the value of old history;
- temporarily increase exploration;
- create a new round of rapid lock-in.

Therefore history-dependent maintenance predicts:

> old solution breaks at a genuine task reset, then a new personal solution rapidly restabilizes.

This differs from a fixed-coordinate memory model.

It also differs from a purely immutable morphology model, which predicts stronger immediate transfer of individual ordering across task resets when the same performance constraints remain.

---

## 8. Relation to the present empirical evidence

The current evidence is qualitatively consistent with this mechanism class:

### Adult field data

- persistent individual vertical organization;
- self-history information across independent bouts;
- no general positive terrain-relative spatial segregation;
- no general additional vertical separation during synchronous co-use.

### Ontogeny

The first-flight programme did not support a common slow monotonic increase in self-history advantage.

Self-history information was already positive at the earliest estimable target and was strongly informative later.

### Randomized early environment

Broad enriched versus impoverished developmental treatment did not detectably alter history-carrier strength.

This weakens a simple model in which broad environmental complexity alone sets the persistence parameter.

### Laboratory task transfer

In *Rhinolophus nippon*, portable movement individuality is approximately low dimensional.

A dominant intensity-like coordinate and a second maneuver / route-organization coordinate carry the calibrated signal across obstacle configurations.

### Wild *Phyllostomus hastatus*

At a harmonized 360-s scale, horizontal and vertical intensity components jointly form a persistent 2-D individual carrier in both 2022 and 2023.

The scalar average can fail even when the vector carrier persists.

### Important negative bridge

Neither the scalar nor the supported 2-D field policy coordinate predicts which other individual has the most similar centered vertical-distribution shape.

Thus:

[
	ext{persistent movement policy}

eq
	ext{vertical shape itself}.
]

The low-dimensional policy is therefore best viewed as one persistent internal/behavioral state layer, not the complete spatial phenotype.

---

## 9. Revised mechanistic architecture

The simplest current architecture is:

[
oxed{
	ext{early stochastic / performance-biased sampling}
ightarrow
	ext{self-reinforced low-dimensional policy}
ightarrow
	ext{context-specific behavioral realization}
}
]

or, statistically,

[
mathbf x_{iet}
=
oldsymbolmu_e
+
mathbfLambda_{e,s}oldsymbol	heta_i
+
oldsymbolarepsilon_{iet}.
]

where:

- (oldsymbol	heta_i) is a persistent personal policy state;
- self-history can stabilize (oldsymbol	heta_i);
- (mathbfLambda_{e,s}) maps that state into the behavior expressed by species s in environment e;
- different output layers such as detailed vertical shape need not be a one-to-one function of the measured movement-policy coordinates.

This naturally explains why:

- individuality persists;
- exact routes can change;
- individuals can overlap in space;
- the same scalar axis need not work in every species/year;
- a multivariate carrier can persist even when a chosen 1-D projection fails.

---

## 10. Testable discriminators

This sufficiency model is not yet a unique causal explanation.

The decisive next contrasts are:

### History-dependent reuse

Prediction:
- true task reset weakens old-history prediction;
- exploration rises;
- new self-history rapidly becomes predictive.

### Stable morphology/performance

Prediction:
- pre-existing individual performance traits predict the new solution immediately after reset;
- individual ordering transfers even before substantial new history accumulates.

### Active competition

Prediction:
- current competitor configuration predicts route/policy change beyond self-history;
- removing competitors rapidly changes the strategy.

### Exact resource specialization

Prediction:
- conditioning on exact repeated task/resource removes most personal identity.

The highest-value empirical design remains a repeated-individual 3-D task-reset experiment with measurements immediately before and after reset.

---

## Bottom line

A mathematically sufficient answer to the maintenance problem is:

> **individual specialization can be maintained by positive feedback from an individual's own behavioral history.**

Under self-reinforcing reuse:

> **specialization increases within individuals while expected between-individual overlap need not decrease at all.**

So persistent specialization does not logically or biologically require persistent spatial partitioning.

The empirical programme now makes this mechanism class plausible, but the exact biological implementation of the reinforcing state — memory, switching cost, motor familiarity, stable performance, or a mixture — remains to be identified.
