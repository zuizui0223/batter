# Individual peer-context reaction-norm contract v1

## Status

**POST-JAE, POST-OUTCOME MECHANISM DIAGNOSTIC — frozen before this reaction-norm statistic is calculated.**

This analysis does not modify JAE v0.4.0 and cannot rescue or reclassify any prior field-policy result.

## Question

Wild *Phyllostomus hastatus* retains low-dimensional H/V policy identity after shared source-day effects are controlled, but a fixed centroid of prior personal history does not improve next-session prediction for the predeclared majority of individuals.

The next mechanistic question is:

> **Do individuals differ reproducibly in how their low-dimensional movement policy responds to the contemporaneous policy state of conspecifics?**

This tests a minimal individual reaction norm:

[
\mathbf y_{id}
=
\boldsymbol\theta_i
+
b_i\mathbf c_{id}
+
\boldsymbol\epsilon_{id},
]

where:
- (mathbf y_{id}) = focal individual's equal-session mean H/V policy on source day d;
- (mathbf c_{id}) = equal-individual mean H/V policy of other bats from the same cohort and source day;
- (oldsymbol\theta_i) = persistent individual intercept;
- (b_i) = scalar personal responsiveness to the shared peer-day policy vector.

The scalar form is deliberately chosen before output to avoid fitting an under-supported 2x2 response matrix.

## Data

Analyse separately:
- *P. hastatus* 2022;
- *P. hastatus* 2023.

Use exactly the harmonized fixed-bin 360-s H/V session-policy rows already used by the supported bivariate field carrier.

No session definition, H/V feature definition, z-scoring, cohort definition, source-day mapping, or individual inclusion rule may be altered to improve this result.

## Day-level units

Within each cohort × source day × biological individual:
- average all valid session H/V policy vectors equally;
- call the result (mathbf y_{id}).

For that focal individual-day:
- compute (mathbf c_{id}) as the equal-individual mean of all other day-level (mathbf y_{jd}) from the same cohort and source day;
- require at least **2 peer individuals**.

No focal value contributes to its own peer context.

## Models

For each target individual-day ((i,d)), remove that **entire cohort-source-day** from model fitting before prediction.

### M0 — stable personal center

Using all remaining eligible days of individual i:

[
\hat{\mathbf y}^{(0)}_{id}
=
\bar{\mathbf y}_{i,-d}.
]

### M1 — common context response

Fit one scalar year-level slope (b_{shared,-d}) using all training individual-day units after removing the target cohort-day, with individual intercepts removed by within-individual centering:

[
b_{shared}
=
\frac{
\sum_{i,t}
(\mathbf c_{it}-\bar{\mathbf c}_i)^T
(\mathbf y_{it}-\bar{\mathbf y}_i)
}{
\sum_{i,t}
\|\mathbf c_{it}-\bar{\mathbf c}_i\|^2
}.
]

For the focal individual, estimate its training intercept:

[
\hat{\boldsymbol\theta}^{shared}_{i,-d}
=
\bar{\mathbf y}_{i,-d}
-
b_{shared,-d}\bar{\mathbf c}_{i,-d}.
]

Predict:

[
\hat{\mathbf y}^{(1)}_{id}
=
\hat{\boldsymbol\theta}^{shared}_{i,-d}
+
b_{shared,-d}\mathbf c_{id}.
]

### M2 — individual context response

Using only the focal individual's remaining eligible days:

[
b_{i,-d}
=
\frac{
\sum_t
(\mathbf c_{it}-\bar{\mathbf c}_{i,-d})^T
(\mathbf y_{it}-\bar{\mathbf y}_{i,-d})
}{
\sum_t
\|\mathbf c_{it}-\bar{\mathbf c}_{i,-d}\|^2
}.
]

Then:

[
\hat{\boldsymbol\theta}_{i,-d}
=
\bar{\mathbf y}_{i,-d}
-
b_{i,-d}\bar{\mathbf c}_{i,-d},
]

and

[
\hat{\mathbf y}^{(2)}_{id}
=
\hat{\boldsymbol\theta}_{i,-d}
+
b_{i,-d}\mathbf c_{id}.
]

## Structural support

A target individual-day is evaluable only if:
- the target has at least 2 peer individuals;
- the focal individual has at least **4** other eligible source days after target-day exclusion;
- the focal training peer-context denominator for (b_i) is finite and > (10^{-12});
- the shared-slope training denominator is finite and > (10^{-12}).

A biological individual contributes to the year statistic only if it has at least **2** evaluable target days.

A year is structurally evaluable only if:
- at least **5** biological individuals contribute;
- at least **15** target individual-days contribute.

No threshold relaxation.

## Primary P1 — individual reaction norm beyond a shared reaction

For each target:

[
\Delta^{RN}_{id}
=
\|\mathbf y_{id}-\hat{\mathbf y}^{(1)}_{id}\|^2
-
\|\mathbf y_{id}-\hat{\mathbf y}^{(2)}_{id}\|^2.
]

Positive means the personal slope predicts the held-out day better than the shared slope.

Aggregate:
1. equal mean across target days within individual;
2. equal mean across individuals within year.

Call the year statistic (G_{RN}).

Report:
- (G_{RN});
- individual mean improvements;
- positive-individual fraction;
- target count;
- descriptive held-out R2 for M0, M1, M2 against the zero-policy baseline.

## Secondary P2 — shared context beyond a stable center

For each target:

[
\Delta^{shared}_{id}
=
\|\mathbf y_{id}-\hat{\mathbf y}^{(0)}_{id}\|^2
-
\|\mathbf y_{id}-\hat{\mathbf y}^{(1)}_{id}\|^2.
]

This asks whether a common contemporaneous peer-context slope improves held-out prediction beyond a personal intercept.

P2 cannot rescue P1.

## Null

Within every cohort-source-day independently:
- retain the complete set of day-level H/V vectors;
- retain the exact set of biological labels present that day;
- randomly permute those labels among complete H/V vectors;
- recompute peer contexts from the permuted day-level identities;
- rerun the **entire** eligibility, leave-one-day-out fitting and prediction pipeline.

This preserves:
- cohort;
- source day;
- number of individuals per day;
- the full H/V day cloud;
- day-level shared context.

It breaks persistent cross-day linkage between biological identity and context response.

Permutations:
**9,999**.

Seeds:
- 2022: `202610052101`;
- 2023: `202610052102`.

Require at least 9,500 valid permutation statistics.

## Frozen support rule for P1

Individual reaction norms are called supported within a year only if:
- (G_{RN} > 0);
- one-sided permutation p <= 0.05;
- at least **70%** of contributing biological individuals have positive mean (Delta^{RN});
- structural and randomization support gates pass.

## Interpretation

### P1 supported

Evidence that individual policy is not only a persistent center: bats carry reproducibly different response gains to the same type of contemporaneous peer-day policy context.

Allowed wording:

> **The field policy contains individual-specific reaction norms to shared social/environmental context.**

This still does not identify whether the context signal is social causation or a proxy for weather, prey, phenology or another shared driver.

### P1 unsupported

Do not conclude that reaction norms are identical.

Conclude only that a scalar individual-specific peer-context gain does not improve held-out prediction consistently enough under this design.

This would favor:
- broader stochastic personal policy distributions;
- unmeasured context variables;
- nonlinear or multidimensional reactions;
- or insufficient repeated-day support.

## Hard ceiling

Even if supported, do not claim:
- peer behavior causally drives the focal bat;
- social imitation;
- a wind reaction norm;
- a universal bat response law;
- that (b_i) is learned rather than morphological/developmental.

The peer-day vector is an observable shared-context proxy.

## No rescue

Do not:
- change the 4-training-day minimum;
- fit a 2x2 (B_i) matrix after seeing P1;
- select only 2022 or only one colony based on output;
- remove negative individuals;
- change the 70% rule;
- redefine the peer context.
