# Individual peer-context reaction-norm result v1

## Status

**UNSUPPORTED IN BOTH YEARS.**

Authoritative fail-closed workflow:
- run: **37303659189**
- job: **111742078848**
- head: `8993b62f761724d4e1da145add349e58c1b1b311`
- workflow conclusion: **success**
- permutations: **9,999 / 9,999 valid** in each year.

Parent:
`INDIVIDUAL_PEER_CONTEXT_REACTION_NORM_CONTRACT_V1.md`

## Primary question

Does an individual-specific scalar response to contemporaneous peer-day H/V policy improve held-out prediction beyond a common year-level response slope?

Primary:

[
G_{RN}
=
E_iE_d[
SE(M1_{shared})-SE(M2_{individual})
].
]

Positive values favor stable individual-specific reaction slopes.

Frozen support required:
- (G_{RN}>0);
- one-sided p <= 0.05;
- >=70% of contributing individuals positive.

## 2022

Day-level focal units:
**211**

Contributing individuals:
**21**

Held-out target individual-days:
**172**

### Reaction-norm primary

- (G_{RN} = -0.06341)
- positive individuals: **6/21 = 28.6%**
- null mean: **-0.17571**
- null 95% interval: **[-0.62842, -0.01724]**
- one-sided p: **0.1163**
- verdict: **UNSUPPORTED_INDIVIDUAL_REACTION_NORM**

### Prediction scale

Against a zero-policy baseline:

- stable personal center M0: (R^2 = 0.2188)
- personal center + **shared** peer-context slope M1: (R^2 = 0.2483)
- personal center + **individual** peer-context slope M2: (R^2 = 0.2008)

Thus the individual-slope model predicts worse than the common-slope model and worse than the stable-center model.

The shared-context term gives a modest descriptive improvement over a stable center, but this P1 result does not establish a causal peer effect.

## 2023

Day-level focal units:
**36**

Contributing individuals:
**6**

Held-out target individual-days:
**30**

### Reaction-norm primary

- (G_{RN} = -0.08325)
- positive individuals: **3/6 = 50.0%**
- null mean: **-0.23929**
- null 95% interval: **[-0.65770, +0.03684]**
- one-sided p: **0.1595**
- verdict: **UNSUPPORTED_INDIVIDUAL_REACTION_NORM**

### Prediction scale

- stable personal center M0: (R^2 = 0.1257)
- shared-slope M1: (R^2 = 0.0244)
- individual-slope M2: (R^2 = -0.0389)

Here even the common peer-context slope reduces held-out prediction relative to a stable personal center.

## Main inference

The persistent field-policy component is **not well explained by a simple individual-specific scalar reaction to contemporaneous peer-day policy**.

The result narrows the model:

[
\boldsymbol\theta_{it}
\neq
\boldsymbol\theta_i
+
b_i\mathbf c_t
]

as a generally useful field prediction rule under this peer-context proxy.

This is informative because:
- peer-day residual identity remains supported in both years;
- the bivariate H/V carrier remains supported in both years;
- substantial stable individual variance remains after day effects are partitioned;
- yet neither a fixed personal-history centroid nor an individual peer-context slope provides a majority-consistent held-out forecasting rule.

Therefore the remaining individual information is better described as a **persistent personal distribution / region in policy space** than as:
- one fixed point;
- one autoregressive personal state;
- or one linear context-response slope.

## What remains plausible

The unexplained within-individual spread may reflect:
- unmeasured environmental dimensions rather than the peer-day proxy;
- nonlinear context response;
- multiple task/resource states;
- state-dependent switching among policy modes;
- individual-specific residual breadth / predictability;
- stochastic realization around a stable personal distribution.

The current analysis does not distinguish these classes.

## Strong negative boundary

Do not promote the wide observed distribution of fitted (b_i) values as evidence for reaction norms.

Although fitted individual slopes vary, they **do not improve held-out prediction consistently**. The predictive test takes precedence over descriptive slope heterogeneity.

## No rescue

Do not:
- fit a post-hoc 2x2 response matrix to obtain a positive result;
- select only positive individuals;
- relax the four-training-day or 70% rules;
- switch peer-context definitions;
- reinterpret p>0.05 as weak support.

## JAE firewall

This is post-JAE mechanism work and does not modify v0.4.0.
