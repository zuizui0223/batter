# Decentralized airway formation by path-dependent reinforcement v1

## Question

How can persistent individual 3-D “airways” arise when:
- no central controller assigns routes;
- individuals need not exclude one another spatially;
- all individuals may initially face the same movement problem and the same set of viable solutions?

The minimal answer is **stochastic path dependence**.

This note is theoretical and prospective. It does not modify JAE v0.4.0 and does not claim that the bats in that paper are literally implementing a Pólya urn or a specific reinforcement-learning algorithm.

---

## 1. Minimal symmetric model

Suppose a recurrent movement problem has **K viable route solutions**.

For individual i, let:

- `N_ik(n)` = number of times route k has been used in the first n trips;
- `a > 0` = common prior accessibility / exploration weight of every route.

All individuals begin identically:

`N_ik(0)=0` for every i,k.

On trip n+1:

[
P_i(k \mid n)=\frac{a+N_{ik}(n)}{Ka+n}.
]

There is:
- no individual-specific parameter;
- no competition term;
- no social rank;
- no central allocation;
- no route exclusion.

The only rule is:

> a route becomes easier to reuse after it has been used.

Ecologically, the reinforcement can stand for any history-dependent reduction in effective cost:
- spatial memory;
- reduced search;
- familiar landmarks;
- known canopy gaps;
- known resource sequence;
- motor / sensory familiarity;
- learned wind handling.

It does **not** require a commitment to a particular cognitive algorithm.

---

## 2. Individual strategies emerge from identical beginnings

The process is the classical symmetric Pólya reinforcement process.

After repeated trips, each individual acquires a persistent route-use vector

[
\theta_i=(\theta_{i1},...,\theta_{iK}),
]

with limiting distribution

[
\theta_i \sim \mathrm{Dirichlet}(a,...,a).
]

The crucial point is that every individual has the **same population-level expectation**:

[
E[\theta_{ik}] = \frac1K.
]

So the population remains perfectly symmetric.

But realized individuals are not identical.

Each animal's early stochastic history selects a different region of the route simplex and later reuse preserves that difference.

This is **stochastic symmetry breaking**:
population symmetry can coexist with persistent individual non-exchangeability.

---

## 3. Exact prediction: self-history must beat another individual

Take two future trips.

### Same individual

The probability that two trips from the same individual use the same latent route is

[
P_{self}
=E\left[\sum_k\theta_{ik}^2\right]
=\frac{a+1}{Ka+1}.
]

### Different individuals

For independent individuals i and j,

[
P_{other}
=E\left[\sum_k\theta_{ik}\theta_{jk}\right]
=\frac1K.
]

Therefore the exact same-individual advantage is

[
\Delta
=P_{self}-P_{other}
=\frac{K-1}{K(Ka+1)}
>0.
]

This is the key result.

> **Repeatable individual route identity appears even though every individual began with exactly the same route preferences and never interacted competitively.**

No central traffic controller is mathematically required.

### Strength of individuality

- small a: early history matters strongly -> strong personal route lock-in;
- large a: prior accessibility dominates experience -> weak individuality;
- as a -> infinity, Delta -> 0.

For K=5:

| a | same-individual route match | between-individual match | advantage |
|---:|---:|---:|---:|
| 0.1 | 0.733 | 0.200 | 0.533 |
| 0.5 | 0.429 | 0.200 | 0.229 |
| 1 | 0.333 | 0.200 | 0.133 |
| 5 | 0.231 | 0.200 | 0.031 |
| 20 | 0.208 | 0.200 | 0.008 |

---

## 4. Individual niche width also emerges spontaneously

For the limiting Dirichlet route distribution, expected individual route entropy is

[
E[H(\theta_i)]
=\psi(Ka+1)-\psi(a+1),
]

where psi is the digamma function.

Population route entropy remains

[
H_{pop}=\log K.
]

Thus

[
I_{spec}
=H_{pop}-E[H(\theta_i)] > 0
]

for finite a.

So individual specialization can arise from path dependence alone even when:
- all animals have identical starting rules;
- the population as a whole remains broad;
- no route is owned by any individual.

---

## 5. From latent routes to overlapping 3-D geometry

Let each latent route k have a 3-D occupancy distribution `g_k`.

Write the route geometry matrix

[
G=[g_1,...,g_K].
]

Individual i's realized 3-D distribution is

[
f_i=G\theta_i.
]

Hence

[
\mathrm{Cov}(f_i)=G\,\mathrm{Cov}(\theta_i)\,G^T.
]

For two independent individuals,

[
E\|f_i-f_j\|^2
=2\,\mathrm{tr}\left(G\mathrm{Cov}(\theta)G^T\right).
]

This connects **personal strategy fidelity** to **spatial segregation**.

If the latent route geometries strongly overlap, the columns of G are similar. Then:

- route-use weights theta_i can differ substantially;
- self-history remains predictive;
- yet `f_i` and `f_j` can occupy largely the same spatial volume.

In the limiting case `g_1=...=g_K`:

[
f_i=f_j
]

for every pair, despite persistent latent route-choice individuality.

Therefore:

> **individual specialization does not mathematically imply spatial partitioning.**

That is the theoretical counterpart of the empirical distinction between vertical-strategy fidelity and added segregation.

---

## 5b. Exact bridge to centered distribution-shape individuality

The model can generate **shape identity with zero mean-position partitioning**.

Let each latent route profile `g_k` be a probability distribution over terrain-relative vertical states z.

Suppose every route has the same mean:

[
\sum_z z\,g_k(z)=\mu
\quad\text{for every }k,
]

but the profiles differ in variance, concentration, skewness or tail allocation.

Because

[
f_i=\sum_k\theta_{ik}g_k,
]

every individual has the same mean vertical position:

[
E_{f_i}[z]=\mu.
]

So a mean-height or centroid-based comparison can show **no individual separation at all**.

Yet if at least two `g_k` differ in shape and individuals have different persistent theta_i, then:

[
f_i \neq f_j
]

as full distributions.

Thus the same mechanism produces:

- session-centered distribution-shape individuality;
- individual differences in concentration / tail use;
- zero required difference in mean height;
- no requirement for mutually exclusive vertical layers.

### General similarity result

Let `G` contain the latent route profiles as columns and define

[
Q=G^T G.
]

Using ordinary distribution inner product as a similarity measure,

[
\mathrm{sim}(f_i,f_j)=f_i^T f_j
=\theta_i^TQ\theta_j.
]

Then the expected same-individual excess over a different individual is

[
E[f_i^T f_i]-E[f_i^T f_j]
=
\mathrm{tr}\left(Q\,\mathrm{Cov}(\theta)\right)
=
\mathrm{tr}\left(G\,\mathrm{Cov}(\theta)G^T\right)
\ge 0.
]

It is strictly positive whenever:
- individual route weights vary; and
- that variation projects onto genuinely different route profiles.

So distribution-level self-predictability is an automatic consequence of persistent individual route mixtures.

At the same time, spatial segregation can remain weak when the columns of G overlap strongly.

This gives an exact theoretical separation between:

1. **identity / fidelity** — persistent theta_i makes self-history predictive;
2. **partitioning / segregation** — determined by how far apart the route geometries g_k actually are.

The two quantities are not mathematically equivalent.

---

## 6. Why contemporaneous avoidance is unnecessary

The minimal model contains no term involving another animal's current location.

Conditional on its own history, individual i chooses independently of current conspecific traffic.

Therefore the model predicts no general additional co-presence-dependent separation.

A competition / avoidance extension would require an explicit interaction term, for example:

[
P_i(k,t)\propto
(a+N_{ik})^\rho
\exp[-\gamma C_k(t)],
]

where `C_k(t)` is contemporaneous use by competitors.

- gamma = 0: path-dependent personal strategies without active segregation;
- gamma > 0: contemporaneous avoidance can appear.

Thus persistent individuality and active spatial partitioning are separate model parameters rather than synonyms.

---

## 7. Social information can seed the destination without assigning the route

Now add two hierarchical levels.

### Destination level

Let d denote destination / feeding sector.

A colony-level or social-information process defines

[
P(d)=\pi_d.
]

Social cues can modify pi and thereby change **where** an individual goes.

### Route level

Conditional on destination d, each individual has its own reinforced route vector

[
\theta_{i,d}.
]

Then:

[
P_i(\text{3-D path})
=
P(d)\times P_i(k\mid d)\times g_{dk}.
]

This yields a natural decentralized architecture:

> **social information can determine the broad destination while individual history determines the detailed route solution.**

No agent needs to assign individual lanes.

This is the theoretical form of:

**social seeding -> personal refinement**.

---

## 8. Formation versus persistence

The symmetric Pólya model proves that persistent individuality can emerge from identical initial conditions, but it does not by itself represent a clean early-exploration -> late-refinement time course.

For that prospective prediction, add a declining exploration rate:

[
P_i(k,t)
=
\epsilon_t\frac1K
+
(1-\epsilon_t)
\frac{(a+N_{ik})^\rho}
{\sum_j(a+N_{ij})^\rho},
]

with `epsilon_t` declining as experience accumulates.

Predictions:

1. early route entropy high;
2. individual histories diverge stochastically;
3. route entropy declines;
4. held-out self-route predictability rises;
5. between-individual route differences persist;
6. spatial segregation need not rise if route geometries overlap.

This is the direct model for **exploration -> refinement -> reuse**.

---

## 9. Reset prediction

If familiar resources, roost access or route geometry changes, effective history should partially reset.

A reset predicts:

- immediate route entropy increase;
- reduced self-history prediction from the old environment;
- exploratory excursions;
- subsequent emergence of a new stable personal solution.

This makes translocation, resource relocation and juvenile first independent flights decisive experiments.

---

## 10. Relation to the empirical pattern

The minimal model produces exactly the qualitative combination that motivated the question:

- same-individual history can remain predictive;
- individuals can retain persistent distributions;
- all individuals can share the same broad airspace;
- positive spatial segregation is not required;
- contemporaneous avoidance is not required.

Therefore a “traffic controller” is not necessary.

A sufficient minimal mechanism is:

> **repeated local choice + history-dependent reuse -> stochastic personal routes.**

Social information, morphology and resource knowledge can modify the priors or reinforcement strength, but none is mathematically required for individuality to exist.

---

## 10b. Short-memory inertia is not the same as persistent personal strategy

A simpler alternative is that an animal merely tends to repeat its **immediately previous** route.

Consider a symmetric K-route Markov chain:

- probability of staying on the current route = p;
- probability of switching to each other route = `(1-p)/(K-1)`.

Its stationary population distribution is uniform.

The nontrivial transition eigenvalue is

[
\lambda
=
p-\frac{1-p}{K-1}
=
\frac{Kp-1}{K-1}.
]

If two trips are separated by L transitions, the probability of using the same route is

[
P_{same}(L)
=
\frac1K
+
\left(1-\frac1K\right)\lambda^L.
]

Therefore the excess above the between-individual baseline `1/K` decays as

[
\Delta_{inertia}(L)
=
\left(1-\frac1K\right)
\left(\frac{Kp-1}{K-1}\right)^L.
]

Unless p=1, short-memory inertia eventually disappears.

This is qualitatively different from persistent individual route propensities theta_i, where distant trips remain correlated through the individual's accumulated history.

### Empirical discriminator

Estimate self-history advantage as a function of temporal lag.

- **short-memory inertia:** approximately exponential decay toward zero;
- **persistent personal route propensity:** non-zero long-lag plateau;
- **forgetting / environmental turnover:** intermediate decay to a lower plateau or reset.

Thus multi-day persistence is informative not only about whether individuality exists, but about the **memory architecture** capable of maintaining it.

The existing bat results do not estimate a full lag-decay curve, so they cannot identify which model applies. They motivate the prospective comparison.

---

## 11. Prospective discriminators

### Pure path dependence

Prediction:
individual route differences emerge even after controlling morphology and social group, with early stochastic choices predicting later use.

### Stable performance matching

Prediction:
morphological traits predict which route is reinforced.

### Social seeding

Prediction:
group information predicts destination convergence before individual route convergence.

### Active competition

Prediction:
co-presence changes instantaneous route choice and creates additional separation.

### Resource identity

Prediction:
conditioning on exact resource/task sequence removes the apparent personal route signal.

These mechanisms can therefore be separated experimentally rather than treated as interchangeable explanations.

---

## Claim ceiling

This model establishes a **sufficient generative mechanism** for persistent individual route specialization without centralized control or spatial exclusion.

It does not establish that the empirical bats use this exact reinforcement rule.

Terms such as reinforcement, symmetry breaking and route memory describe the model class; they should not be converted into unmeasured cognitive claims.
