# Field policy variance decomposition result v1

## Status

**POST-OUTCOME DESCRIPTIVE VARIANCE DECOMPOSITION.**

Authoritative fail-closed workflow:
- run: **37301093567**
- job: **111733725467**
- head: `f52c1a8f522143743cbe9788587c8ef7c39362dd`
- workflow conclusion: **success**

Parent:
`FIELD_POLICY_VARIANCE_DECOMPOSITION_V1.md`

## Model

For each year and each standardized field-policy component:

[
y = \text{cohort fixed effect} + u_{individual} + u_{cohort-day} + \epsilon .
]

Reported fractions are descriptive REML variance fractions.

## 2022

Sessions: **228**  
Individuals: **34**  
Source days: **39**

### Horizontal movement intensity H

- individual fraction: **0.3171**
- cohort-day fraction: **0.3142**
- residual fraction: **0.3687**
- conditional individual ICC after day removal: **0.4624**

### Vertical movement intensity V

- individual fraction: **0.7338**
- cohort-day fraction: **0.0325**
- residual fraction: **0.2337**
- conditional individual ICC after day removal: **0.7585**

### Equal-axis descriptive summary

- individual: **0.5255**
- day: **0.1733**
- residual: **0.3012**
- conditional individual ICC: **0.6104**

The stable individual component is therefore especially strong on the vertical-intensity axis.

## 2023

Sessions: **43**  
Individuals: **11**  
Source days: **9**

### Horizontal movement intensity H

- individual fraction: **0.2810**
- cohort-day fraction: **0.0333**
- residual fraction: **0.6856**
- conditional individual ICC: **0.2907**

### Vertical movement intensity V

- individual fraction: **0.3913**
- cohort-day fraction: **0.00006**
- residual fraction: **0.6086**
- conditional individual ICC: **0.3913**

### Equal-axis descriptive summary

- individual: **0.3362**
- day: **0.0167**
- residual: **0.6471**
- conditional individual ICC: **0.3410**

Thus the 2023 field policy retains a stable individual component, but most session-level variation lies outside the stable intercept.

## Leave-one-out robustness

Full-data individual fractions are not driven by one individual or one source day.

### 2022 H
- drop-one-individual range: **0.276–0.369**
- drop-one-day range: **0.290–0.376**

### 2022 V
- drop-one-individual range: **0.597–0.887**
- drop-one-day range: **0.695–0.931**

### 2023 H
- drop-one-individual range: **0.209–0.408**
- drop-one-day range: **0.167–0.329**

### 2023 V
- drop-one-individual range: **0.332–0.486**
- drop-one-day range: **0.277–0.487**

## Numerical caution

The full four fitted models report `converged=true`.

Some leave-one-out refits emitted boundary / non-positive-Hessian / occasional optimization warnings. Therefore:
- treat the full-data variance fractions as the main descriptive quantities;
- use leave-one-out ranges only as rough robustness diagnostics;
- do not interpret tiny day components as formal evidence of exact zero variance;
- do not attach inferential p-values to the variance fractions.

## Mechanistic implication

A fixed deterministic individual policy point is too strong.

The data are better represented as:

[
\boldsymbol\theta_{it}
=
\boldsymbol\theta_i
+
\boldsymbol\eta_{d(t)}
+
\boldsymbol\xi_{it},
]

with axis- and year-specific variance magnitudes.

In 2022, especially for vertical movement intensity, the stable individual center is the dominant source of variation.

In 2023, the stable individual center remains present but sits inside a much broader session-level cloud.

This directly complements the peer-plus-past forecast boundary:
a persistent individual component can be strong at the variance/identity level even when one prior-history centroid does not improve next-session prediction for >=70% of individuals.

The empirical object is therefore better described as a **persistent personal distribution in policy space** than as one immutable coordinate.

## Claim boundary

Supported descriptively:
- substantial stable individual field-policy variance;
- large year/axis differences in the fraction of policy variation that is stable;
- particularly strong 2022 vertical-intensity individuality.

Not established:
- causal origin of the individual variance;
- equality/inequality of variance fractions by formal test;
- stable morphology as the cause;
- individual-specific environmental slopes;
- deterministic prediction of a future session.

## JAE firewall

This is post-JAE mechanism work and does not modify v0.4.0.
