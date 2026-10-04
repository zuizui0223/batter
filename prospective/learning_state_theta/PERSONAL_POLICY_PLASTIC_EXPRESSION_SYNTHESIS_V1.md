# Personal policy as a stable prior with plastic expression — synthesis v1

## Status

**SYNTHESIS AFTER PROSPECTIVE OUTCOME OPENING.**

Branch:
`prospective/learning-state-theta-v1`

This synthesis does not modify JAE v0.4.0.

## New empirical bridge

Two independent *Rhinolophus* datasets now constrain different pieces of the same architecture.

### Teshima 2026 — configuration transfer

In *Rhinolophus nippon* across seven obstacle configurations:

- full movement-policy identity transfers across configurations:
  `K=+0.94356, p=0.0001, 5/5 positive`;
- one training-only PCA dimension is sufficient;
- a transparent speed + vertical-speed `FlightIntensity` scalar is sufficient:
  `K=+0.49656, p=0.0003, 5/5 positive`;
- pairwise scalar ordering is 82.17% stable across configurations;
- a scalar estimated from other configurations predicts held-out pairwise magnitude:
  beta=1.031, Pearson r=0.555.

This supports a portable individual control coordinate.

### Yamada 2020 raw re-analysis — learning transfer

Public Figshare row data:
`10.6084/m9.figshare.19102712.v1`

Structural provenance was resolved outcome-blind:
- 14 bats;
- 7 permeable/chain;
- 7 reflective/acrylic;
- source trials 1 and 12;
- 28/28 one-to-one raw-sheet crosswalk.

The frozen 8-D raw-coordinate analogue STOPPED because no bat met the predeclared >=100-row rule. That threshold was not relaxed.

A separate preregistered scalar route used source-native maximum flight speed.

Published learning shift reproduced:
- permeable: 2.464 -> 3.356 m/s, mean within-bat change +0.892 m/s;
- reflective: 2.548 -> 2.822 m/s, mean within-bat change +0.273 m/s.

After subtracting each condition x trial population mean and scaling by the frozen pooled within-state SD:

### Prospective primary

[
K =
mean(
D_{other first}
-
D_{own first}
)
]

for trial-12 targets.

Result:
- `K=+0.52771`;
- permutation `p=0.0052`;
- 12/14 bats positive;
- permeable: 5/7 positive;
- reflective: 7/7 positive.

Verdict:
**SUPPORTED_PERSONAL_SPEED_STATE_PERSISTENCE**

Thus the naive-to-familiar transition changes the population operating state without erasing all personal speed-state information.

---

# Condition dependence

Post-primary exact 7! condition-wise permutations show strong heterogeneity.

## Permeable / strong-learning condition

- mean learning shift: +0.892 m/s;
- `K=+0.17577`;
- 5/7 positive;
- exact `p_K=0.2593`;
- Pearson first->12th residual correlation: `r=0.0026`, p=.498;
- pairwise-order accuracy: 0.571, p=.386.

The calibrated within-condition evidence for a persistent ordering is weak.

## Reflective / weaker-learning condition

- mean learning shift: +0.273 m/s;
- `K=+0.87965`;
- 7/7 positive;
- exact `p_K=0.00159`;
- Pearson first->12th residual correlation: `r=0.8980`, p=.00238;
- pairwise-order accuracy: 0.9524, p=.00159.

Personal speed state is highly persistent.

## Between-condition contrast

[
Delta K=K_{reflective}-K_{permeable}=+0.70389.
]

Post-primary two-sided randomization:
`p=0.0822`.

Therefore the data are suggestive but do **not** establish a statistically calibrated difference in persistence between acoustic conditions.

Do not claim a causal plasticity-individuality trade-off.

---

# Revised minimal model

The evidence no longer favors either extreme:

### Extreme 1
`individuality = fixed immutable body constant`

### Extreme 2
`individuality = arbitrary route memorized forever`

A better current representation is:

[
x_{i,e,t}
=
mu_{e,t}
+
alpha_{e,t}	heta_i
+
h_{i,e,t}
+
arepsilon_{i,e,t}.
]

Where:

- `mu_e,t`: shared response to environment and learning state;
- `theta_i`: latent personal control prior;
- `alpha_e,t`: context-dependent expression of that prior;
- `h_i,e,t`: task-specific personal solution/lane/history component;
- `epsilon`: trial variation.

### Evidence for theta

- held-out cross-configuration one-dimensional identity in Teshima;
- stable scalar rank and held-out magnitude calibration;
- Yamada overall first-to-twelfth self-history persistence.

### Evidence that alpha is not necessarily constant

- Yamada reflective condition retains almost complete individual order;
- permeable condition shows a much larger mean learning shift and little calibrated rank persistence;
- the between-condition persistence contrast is suggestive but not conclusive.

### Evidence for h

- within-configuration absolute lane/route placement can be individual-specific;
- translation-invariant literal route shape is not robust;
- external reset literature shows configuration-specific learned paths can be rebuilt.

---

# Answer to the original maintenance question

Individual specialization need not be maintained by individuals continually occupying mutually exclusive volumes of space.

A plausible evidence-backed mechanism is:

1. individuals possess or acquire a personal control prior;
2. the environment and learning state move the common operating point;
3. that prior remains expressed to varying degrees;
4. task-specific experience determines the realized spatial solution;
5. repeated use of the resulting solution preserves recognizable individual organization.

In short:

> **what persists need not be a place or a route; it can be a personal control tendency whose expression is plastic.**

---

# Answer to the "pi" analogy

The current evidence argues against irreducible mathematical opacity, at least for the *Rhinolophus* obstacle-flight system.

The portable individual component is surprisingly compressible:
- one linear latent dimension is sufficient in held-out configurations;
- a transparent movement-intensity scalar captures roughly half the full 8-D identity advantage;
- that scalar predicts held-out differences in magnitude;
- a related personal speed state persists across a naive-to-familiar transition overall.

The hard part is therefore not writing *some* low-dimensional rule.

It is identifying the causal decomposition of that rule:

[
	heta_i
quad	ext{versus}quad
alpha_{e,t}
quad	ext{versus}quad
h_{i,e,t}.
]

That is an identifiability problem, not evidence that bat flight is mathematically unrepresentable.

---

# Strongest remaining causal experiment

Track the same identified bats through:

1. baseline unfamiliar task;
2. repeated learning;
3. obstacle mirror/reset;
4. reversible biomechanical load manipulation.

A decisive design would test:

[
x_{i,t}
=
mu_t
+
alpha_t	heta_i
+
eta,Load_t
+
h_{i,task(t)}
+
epsilon.
]

Predictions:

- learning changes `mu_t` and possibly `alpha_t`;
- mirror/reset changes `h_i,task`;
- reversible load changes performance if biomechanics carries theta;
- removing the load should restore the pre-load individual ordering if theta is a stable intrinsic performance prior.

This would separate:
- stable biomechanics;
- plastic sensorimotor control;
- task-specific learned solution

within the same individual.
