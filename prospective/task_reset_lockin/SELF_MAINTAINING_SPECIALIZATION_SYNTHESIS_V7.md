# Self-maintaining specialization synthesis v7

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V6.**

JAE v0.4.0 remains frozen and unchanged.

V7 incorporates:
- field policy variance decomposition;
- peer-plus-past forecast;
- individual peer-context reaction-norm test;
- policy-breadth persistence test;
- strict-past and older-history temporal diagnostics.

The central revision from V6 is important:

> **The stable empirical object is a low-dimensional personal policy bias / center, not yet a complete stable personal probability distribution with repeatable width and reaction slope.**

---

## 1. Starting point: specialization does not require spatial partitioning

The JAE programme establishes that repeatable individual vertical strategies can persist while:
- terrain-relative added segregation is unsupported in 0/4 panels;
- contemporaneous co-use separation is unsupported in 3/4 panels;
- policy distance does not predict dyadic co-use separation in the same wild system.

For *P. hastatus*:
- 2022: rho(policy distance, co-use vertical separation) = **+0.188**, p=**0.2743**;
- 2023: rho = **-0.190**, p=**0.6887**.

Thus:

[
\boxed{
\text{individual specialization}
\not\equiv
\text{spatial partitioning}
}
]

The maintenance carrier must therefore be sought at another level.

---

## 2. Portable low-dimensional personal policy exists

### Laboratory *Rhinolophus nippon*

Cross-configuration movement identity:
- full 8-D K = **+0.94356**, p=**0.0001**;
- one training-derived PC is sufficient for held-out identity;
- transparent FlightIntensity K = **+0.49656**, p=**0.0003**;
- transparent ManeuveringExtent K = **+0.23375**, p=**0.0027**;
- transparent 2-D K = **+0.55428**, p=**0.0001**;
- calibrated residual identity after removing that transparent 2-D span is unsupported.

FlightIntensity also predicts held-out pairwise magnitude:
- no-refit R² ≈ **0.627**;
- calibration slope ≈ **1.031**;
- pair-order accuracy ≈ **82.9%**.

### External *Carollia perspicillata*

The fixed representation transfers:
- fixed 2-D K ≈ **+0.348**, 6/7 positive, p=**0.0007**;
- FlightIntensity alone K ≈ **+0.368**, p=**0.0014**.

Thus low-dimensional personal movement policy is recurrent, although not universal across bats.

---

## 3. Wild field movement contains a low-dimensional personal carrier

For wild *Phyllostomus hastatus*, use the two-dimensional field coordinate:

[
\boldsymbol\theta=(H,V),
]

where:
- H = horizontal movement intensity;
- V = vertical movement intensity.

Fixed-bin carrier:

### 2022
- K_2D = **+0.65314**
- 32/34 positive
- p=**0.0001**

### 2023
- K_2D = **+0.27052**
- 9/11 positive
- p≈**0.033**

Thus repeatable individual information is present in low-dimensional free-ranging movement policy.

---

## 4. The strongest stable object is the personal center / bias

Variance decomposition gives the clearest magnitude interpretation.

### 2022

Equal-axis descriptive fractions:
- individual = **52.5%**
- cohort-day = **17.3%**
- residual = **30.1%**

Axis-specific:
- H individual fraction = **31.7%**
- V individual fraction = **73.4%**

The vertical-intensity axis is especially strongly individualized.

### 2023

Equal-axis fractions:
- individual = **33.6%**
- cohort-day = **1.7%**
- residual = **64.7%**

So the stable personal component remains, but realized sessions occupy a much broader cloud around it.

This year contrast argues against treating the policy as one immutable behavioral constant.

---

## 5. Personal history is temporally predictive

Using the one-dimensional allocation axis:

[
A=(H-V)/\sqrt2,
]

strictly prior self-history predicts the next session better than strictly prior conspecific histories.

### 2022
- K_past = **+0.37266**
- 26/32 positive
- p=**0.0001**

### 2023
- K_past = **+0.27201**
- 6/7 positive
- p=**0.0258**

Thus the field carrier is not merely a static between-individual clustering artifact.

It contains temporally transferable personal information.

---

## 6. But the depth of that history is not universal

Remove the immediately previous self session and use only older history.

### 2022
- K_older = **+0.34147**
- 25/32 positive
- p=**0.0001**

The stricter descriptive >=2-older-session version remains directionally strong:
- K=**+0.21334**
- 19/27 positive.

Therefore pure one-step inertia is insufficient in 2022.

### 2023
- K_older = **+0.14170**
- 5/7 positive
- p=**0.1713**
- verdict: unsupported.

So there is no evidence for one universal memory depth or one universal lag law.

The one-dimensional allocation axis can carry deep history in one year and fail to establish it in another.

---

## 7. A fixed personal-history centroid is too simple

After contemporaneous peer-day adjustment, adding strictly prior personal H/V history improves average squared prediction relative to the randomized pipeline, but fails the frozen majority-consistency rule.

### 2022
- pooled no-refit R² improvement architecture ≈ **8.0%**
- 16/30 individuals improve = **53.3%**
- verdict: unsupported.

### 2023
- pooled ≈ **16.6%**
- 4/7 improve = **57.1%**
- verdict: unsupported.

Therefore:

> **personal history contains information, but one fixed mean of that history is not a general deterministic forecasting rule.**

---

## 8. Simple individual reaction norms are also unsupported

A separately frozen held-out test compared:

[
M1: \theta_i + b_{shared}c_t
]

with

[
M2: \theta_i + b_i c_t,
]

where (c_t) is the contemporaneous peer-day H/V policy proxy.

### 2022
- G_RN = **-0.06341**
- 6/21 positive
- p=**0.1163**
- R²:
  - stable center M0 = **0.2188**
  - shared slope M1 = **0.2483**
  - individual slope M2 = **0.2008**

### 2023
- G_RN = **-0.08325**
- 3/6 positive
- p=**0.1595**
- R²:
  - M0 = **0.1257**
  - M1 = **0.0244**
  - M2 = **-0.0389**

Even the shared-slope P2 calibration is unsupported:
- 2022 p=**0.1733**
- 2023 p=**0.8105**

Thus descriptive variation in fitted slopes must not be called a stable reaction norm.

For this observable context proxy:

[
\boxed{
\theta_i+b_i c_t
}
]

is not a useful general predictive law.

---

## 9. Stable policy breadth is not established either

A third frozen component test asked whether individuals retain a repeatable width of their peer-day-adjusted H/V policy distribution.

### 2022
- K_W = **+0.18142**
- 11/16 positive = **68.75%**
- p=**0.0899**
- verdict: unsupported.

A secondary early-late log-breadth Spearman correlation is positive:
- rho=**0.629**
- p=**0.009**

but cannot rescue the failed primary.

### 2023
- structural STOP: no individual met the frozen >=6 eligible-day requirement.

Therefore V6's wording that each individual has a stable full personal policy distribution is too strong.

Current evidence does **not** establish stable individual:
- reaction slope;
- distribution width;
- full covariance structure.

---

## 10. What persists, exactly?

The evidence hierarchy now distinguishes four possible components.

### A. Personal policy center / bias
**SUPPORTED.**

Evidence:
- cross-configuration lab identity;
- external *Carollia* transfer;
- wild H/V carrier;
- peer-day residual identity;
- substantial individual variance fractions;
- strict-past prediction.

### B. Long-history depth
**CONTEXT-DEPENDENT / HETEROGENEOUS.**

- deeper-than-latest history supported in 2022;
- not established in 2023.

### C. Individual context-response slope
**UNSUPPORTED under the current peer-day proxy.**

### D. Stable individual policy breadth
**NOT ESTABLISHED.**

Hence the safest empirical object is:

[
\boxed{
\text{persistent low-dimensional personal bias}
}
]

plus substantial time-varying realization.

---

## 11. Learned scene-specific solutions are a separate layer

Laboratory and external reset evidence show that literal routes can:
- become individually stereotyped with learning;
- persist when a familiar scene returns;
- break and reorganize after mirror/reset geometry.

At the same time, the higher-level movement-policy signal transfers across different configurations.

Therefore:

[
\boxed{
\text{portable personal policy bias}
+
\text{learned scene-specific solution}
+
\text{current context}
\rightarrow
\text{realized movement}
}
]

is still the best hierarchy.

The learned route is not identical to the portable policy.

---

## 12. Revised minimal stochastic model

Do not write a fixed deterministic point:

[
x_{it}=\theta_i.
]

Do not write a confirmed individual reaction norm:

[
x_{it}=\theta_i+B_i c_t.
]

And do not write a confirmed stable personal covariance:

[
x_{it}\sim N(\theta_i,\Sigma_i).
]

The current evidence supports the weaker and cleaner decomposition:

[
\boxed{
x_{iet}
=
F(E_e,\theta_i,m_{i,e})
+
\zeta_{iet}
}
]

where:
- (	heta_i) = persistent low-dimensional individual bias / prior;
- (E_e) = current task/environment;
- (m_{i,e}) = learned scene-specific solution/history;
- (zeta_{iet}) = unresolved time-varying realization.

The data establish (	heta_i) much more strongly than they establish the structure of (zeta).

---

## 13. Why the negative mechanism tests are useful

The programme has now falsified several easy explanations for the residual cloud around the individual center:

- not simply spatial exclusion;
- not one immutable route;
- not only the latest session;
- not a universal fixed past centroid;
- not a simple peer-context common slope;
- not a simple individual peer-context slope;
- not yet a confirmed stable personal breadth.

This is not failure to find a mechanism.

It localizes the unresolved mechanism:

> **the persistent information is carried at the level of a low-dimensional individual bias, while the process generating bout-to-bout deviations around that bias is more complex than the simplest memory, linear-context, or fixed-variance models tested here.**

---

## 14. Current ecological interpretation

The most defensible broad statement is now:

> **Individual specialization can be maintained as a persistent bias in how an animal solves movement problems, without requiring exclusive ownership of physical space.**

That bias:
- transfers across contexts in laboratory data;
- recurs in an independent species;
- appears in wild low-dimensional movement;
- predicts future behavior from personal history;
- can survive removal of the immediately previous session in at least one well-supported year.

But its expression remains plastic/stochastic enough that:
- one fixed personal forecast rule fails;
- one individual reaction slope fails;
- one stable breadth phenotype is not established.

So the conceptual shift is not:

[
\text{spatial niche} \to \text{fixed personality constant}.
]

It is:

[
\boxed{
\text{exclusive spatial niche}
\to
\text{persistent behavioral policy bias with flexible realization}
}
]

---

## 15. Strongest next causal question

The same archival field data are now close to their mechanistic ceiling.

Further post-hoc basis changes would risk mechanism fishing.

The decisive next experiment should manipulate a causal component within the same individuals:

1. estimate baseline policy bias across multiple tasks;
2. learn a scene-specific solution;
3. impose a true geometry/resource reset;
4. measure the first post-reset bout before relearning;
5. follow re-stabilization;
6. restore the original task;
7. independently manipulate or measure biomechanics.

Key predictions:

- portable bias (	heta_i) transfers immediately;
- scene-specific route (m_{i,e}) breaks at reset and rebuilds;
- old scene solution is retrieved when the scene returns;
- reversible biomechanical load shifts performance if biomechanics contributes to (	heta_i).

This separates:
- intrinsic performance;
- long-lived sensorimotor policy;
- learned scene memory;
- current environmental realization.

---

## Bottom line

The mechanism is now narrower than V6:

> **What persists is not a private volume of space, not one literal route, and not yet a fully stable personal behavioral distribution. The strongest recurring object is a low-dimensional individual movement-policy bias that survives substantial spatial overlap and flexible bout-to-bout realization.**

That is the current post-JAE mechanism ceiling.
