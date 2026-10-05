# Mechanism synthesis v3 — persistent policy without spatial partition

## Scope

This synthesis belongs to `prospective/task-reset-lockin-v1`.

It does **not** modify JAE v0.4.0.

Its purpose is to separate:
1. empirical results established by frozen or externally fixed analyses;
2. post-outcome mechanism diagnostics;
3. mathematically sufficient mechanisms;
4. causal mechanisms that remain unidentified.

---

# 1. Empirical core

## 1.1 Individual specialization persists without general spatial partition

The JAE programme established that:
- individual vertical organization is persistent across independent bouts;
- self-history contains information about later individual behavior;
- positive terrain-relative segregation is not generally supported;
- synchronous co-use does not generally induce additional vertical separation.

Thus persistent individuality and spatial partition are empirically separable.

## 1.2 Persistent policy distance does not organize pairwise co-use separation

In P. hastatus, persistent fixed-bin bivariate policy coordinates were paired with the authoritative synchronous co-use dyads.

Observed Spearman association between persistent policy distance and observed dyad vertical separation:

- 2022: rho = +0.1879, one-sided p = 0.2743;
- 2023: rho = -0.1905, one-sided p = 0.6887.

Therefore even the year with a panel-level synchronous separation signal does not show that more behaviorally different dyads are more vertically separated.

Current interpretation:

> **policy differentiation is not a monotonic map to spatial partitioning.**

---

# 2. What is persistent?

## 2.1 Laboratory obstacle-flight policy is low dimensional

For Rhinolophus nippon across seven obstacle configurations:

- full 8-D movement policy carries individual identity;
- one held-out PCA axis is sufficient for discrimination;
- PC1 is extremely stable across leave-one-environment folds:
  - pairwise loading-vector cosine minimum ≈ 0.983;
  - median ≈ 0.996;
- PC1 is closely aligned with a transparent FlightIntensity axis based on speed and absolute vertical speed;
- a second stable axis is nearly orthogonal to FlightIntensity and is dominated by turning rate, path efficiency and vertical range.

Removing:
- PC1 alone leaves significant residual identity;
- PC1 + PC2 removes calibrated residual identity.

Thus the measured portable movement policy is best described as **approximately two-dimensional**, not irreducibly high dimensional and not purely one-dimensional.

A useful descriptive representation is:

[
oldsymbol	heta_i
=
(	heta_{intensity,i},	heta_{maneuver,i}).
]

## 2.2 One dominant scalar has real predictive meaning

Within R. nippon, the dominant FlightIntensity coordinate is not merely a classifier.

A leave-one-environment-out scalar model predicted held-out pairwise individual differences with:
- through-origin slope ≈ 1.03;
- Pearson r ≈ 0.555;
- sign accuracy ≈ 0.829;
- no-refit predictive R² ≈ 0.627.

Prediction errors were concentrated among pairs with small scalar separation.

So one scalar captures a large and quantitatively meaningful portion of the individual policy, while PC2 carries additional identity.

## 2.3 Species boundary

The same Rhino axis did not generalize to Miniopterus fuliginosus, and a Miniopterus-specific PCA1 diagnostic was also unsupported in the current sparse archive.

Therefore the supported claim is:

> **low-dimensional individual policy is strongly supported in R. nippon, but a universal cross-species bat policy axis is not.**

---

# 3. Field policy architecture

## 3.1 P. hastatus requires horizontal and vertical components jointly

Under harmonized 360-s bins:

- horizontal component H is repeatably individual;
- vertical component V is repeatably individual;
- the bivariate (H,V) carrier is supported in both 2022 and 2023;
- a scalar average of H and V can fail even when the vector carrier persists.

The dominant field direction is close to the transparent allocation contrast:

[
A=(H-V)/sqrt2.
]

The empirical H-V PC1 is stable across years and close to this horizontal-versus-vertical trade-off direction.

Interpretation:

> field individuality is better represented as a low-dimensional allocation policy than as a single overall movement-intensity scalar.

## 3.2 Policy is not identical to vertical-distribution shape

Across individuals, similarity in the bivariate movement policy did not predict similarity in centered vertical-distribution shape in either field year.

Thus:

[
	ext{persistent movement policy}

eq
	ext{full vertical phenotype}.
]

The policy is better interpreted as a control state that is expressed through additional context-dependent mappings.

---

# 4. Temporal maintenance in the field

## 4.1 Strictly prior self-history predicts future policy

Using no future sessions:

2022:
- K_past ≈ 0.373;
- 26/32 individuals positive;
- p = 0.0001.

2023:
- K_past ≈ 0.272;
- 6/7 individuals positive;
- p = 0.0258.

So the focal bat's own prior policy history predicts its later field session better than prior histories of other bats.

## 4.2 The latest session is not the whole explanation

After removing the immediately previous session from every history:

2022:
- K_older ≈ 0.341;
- 25/32 positive;
- p = 0.0001.

2023:
- positive direction but unsupported (p ≈ 0.171), with much smaller temporal support.

Therefore pure one-step inertia is insufficient for the well-supported 2022 series; 2023 does not independently establish deeper-history persistence.

## 4.3 Short-lag residual state is largely shared

Raw within-individual deviations around each bat's own mean showed positive temporal ordering beyond a shuffled fixed-trait null.

However, after subtracting contemporaneous peers:
- ±12 h peer-control: unsupported in both years;
- source-day peer adjustment: unsupported in both years.

Thus the short-lag residual autocorrelation should **not** be interpreted as evidence for an autonomous self-reinforcing internal state.

A shared time-varying environment can explain much of this short-lag component.

## 4.4 Stable residual individual identity survives peer/day correction

After subtracting source-day peer means, sessions still cluster by biological individual:

2022:
- K_peerday ≈ 0.163;
- 28/34 positive;
- p = 0.0002.

2023:
- K_peerday ≈ 0.301;
- 7/8 positive;
- p = 0.0153.

Thus shared daily conditions do not explain the full policy signal.

The parsimonious observational architecture is:

[
A_{it}
=
	heta_i
+
eta_{c,t}
+
arepsilon_{it},
]

where:
- (	heta_i) is a persistent individual-specific component;
- (eta_{c,t}) is a shared cohort/time effect;
- (arepsilon_{it}) is remaining session variation.

## 4.5 Long-span stability is asymmetric by year

Peer-controlled early-to-late identity:

Scalar allocation:
- 2022 borderline (p ≈ 0.052);
- 2023 unsupported.

Bivariate H,V policy:
- 2022 supported (p = 0.0004; 19/25 positive);
- 2023 unsupported (p ≈ 0.247).

Therefore:
- stable long-span policy is directly supported in the richer 2022 series;
- 2023 supports residual identity across all sessions but is too sparse/noisy to independently establish early-to-late 2-D stability.

---

# 5. What maintains specialization?

The current evidence no longer favors the strongest version of:

> every session reinforces a short-term internal behavioral state.

The short-lag state signal weakens after peer/day control.

The empirical maintenance result is instead:

> **individuals carry persistent low-dimensional policy differences, while shared environmental variation moves their realized behavior around those personal tendencies.**

This policy need not correspond to an exclusive region of physical space.

A minimal empirical model is:

[
mathbf x_{iet}
=
oldsymbolmu_{e,t}
+
mathbfLambda_{e,s}oldsymbol	heta_i
+
oldsymbolarepsilon_{iet}.
]

Here:
- (oldsymbol	heta_i) is persistent personal policy;
- (oldsymbolmu_{e,t}) is the shared context/environment;
- (mathbfLambda_{e,s}) converts the policy into the behavior observable in a given task/species/environment.

This architecture naturally explains:
- persistent individuality;
- exact-route changes;
- context dependence;
- strong spatial overlap;
- failure of policy distance to predict co-use separation;
- failure of a single movement metric to explain the full vertical phenotype.

---

# 6. Where self-reinforcement fits

A symmetric self-reinforcing choice process provides a **mathematically sufficient** explanation for specialization without partition.

For K feasible solutions and reinforcement parameter alpha:

[
P(A_{it}=kmidmathbf n_i(t))
=
rac{alpha+n_{ik}(t)}{Kalpha+t}.
]

Its asymptotic personal mixture is Dirichlet-distributed.

Expected within-individual concentration is:

[
E[H_i]=rac{alpha+1}{Kalpha+1}>rac1K.
]

But expected overlap between two independently reinforced individuals remains exactly:

[
Eleft[sum_k p_{ik}p_{jk}ight]=rac1K.
]

Thus self-reinforcement is sufficient to produce:
- stronger within-individual specialization;
- no expected between-individual repulsion.

The implementation verifier reproduced these identities over the frozen parameter grid.

However, the field data do **not** uniquely identify self-reinforcement as the biological origin of (	heta_i).

Self-reinforcement should therefore be presented as:
- a sufficient mechanism class;
- not the empirically established causal mechanism.

---

# 7. Current causal boundary

The origin of the persistent individual component remains unresolved.

Still compatible:
- stable morphology / flight performance;
- physiology;
- developmental differences;
- long-term learning / motor familiarity;
- long-lived spatial knowledge;
- combinations of these.

Currently unsupported or bounded:
- continued pairwise spatial exclusion as the maintenance requirement;
- simple body mass as a general carrier;
- a universal slow monotonic ontogenetic ramp;
- broad enriched/impoverished early environment as a determinant of carrier strength;
- an independent pulse/sensing carrier after strict cross-fitted movement/route nuisance control;
- a universal cross-species flight-policy axis.

---

# 8. Strongest current biological statement

> **Persistent individual specialization is carried by low-dimensional personal movement policies, not by continuously maintained spatial exclusion. Shared environmental conditions modulate their expression, but do not erase residual individual identity.**

For the field system, policy differences do not predict pairwise synchronous vertical separation.

Therefore the maintenance problem and the partitioning problem are distinct:

[
oxed{
	ext{persistent individual policy}

otRightarrow
	ext{persistent spatial segregation}
}
]

The next genuinely causal experiment is not another observational decomposition. It is a repeated-individual perturbation that changes the movement task while measuring the same individuals before and immediately after the change, ideally with morphology/performance measured independently.
