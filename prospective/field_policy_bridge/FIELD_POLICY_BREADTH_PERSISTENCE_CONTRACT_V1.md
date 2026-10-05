# Field policy breadth persistence contract v1

## Status

**POST-JAE, POST-OUTCOME MECHANISM DIAGNOSTIC — frozen after the scalar peer-context reaction-norm test failed and before any early/late policy-breadth matching statistic is calculated.**

This analysis tests a distinct component of individual variation: persistent differences in within-individual policy variability ("predictability").

It cannot modify JAE v0.4.0 and cannot rescue prior reaction-norm or forecast tests.

## Question

The field data support persistent H/V policy identity, but:
- a fixed prior-history centroid is not a majority-consistent forecast rule;
- an individual-specific scalar peer-context reaction slope is unsupported.

The next bounded question is:

> **Are some bats consistently narrower or broader in their realized low-dimensional policy distribution than others?**

In behavioural-reaction-norm terminology, this is individual variation in residual within-individual variability / predictability.

## Data

Analyse separately:
- *Phyllostomus hastatus* 2022;
- *P. hastatus* 2023.

Use exactly the harmonized fixed-bin 360-s H/V policy rows from the established field carrier.

No session, bin, cohort, H/V feature, z-score or source-day definition may change.

## Day-level residual policy

For each cohort × source day × individual:

1. average all valid session H/V vectors equally to form day-level focal policy (mathbf y_{id});
2. require at least 2 other individuals on that cohort-day;
3. compute peer-day context as the equal-individual mean of those other bats:
   (mathbf c_{id});
4. define residual day policy:
   [
   mathbf r_{id}=mathbf y_{id}-mathbf c_{id}.
   ]

No focal vector contributes to its own peer context.

The coefficient on peer context is fixed at 1 because this diagnostic is explicitly anchored to the already-used peer-day residual architecture. Do not fit or select a reaction slope here.

## Temporal split

Within each biological individual:
- sort eligible residual day vectors by source date;
- require at least **6** eligible source days;
- split chronologically:
  - early = first floor(n/2) days;
  - late = remaining days;
- require at least **3** days in each half.

No breakpoint selection.

## Policy breadth

For a half with m day vectors:

[
W
=
rac{1}{m-1}
sum_d
|mathbf r_d-ar{mathbf r}|^2.
]

This is the trace of the ordinary sample covariance matrix in H/V policy space.

For matching, use:

[
L=log(max(W,10^{-12})).
]

Thus the test concerns multiplicative differences in policy breadth and remains defined if numerical breadth is extremely small.

## Primary matching statistic

Within each cohort, an individual is evaluable only if:
- it has valid early and late breadth;
- at least 2 other evaluable individuals exist in that cohort.

For individual i:

- self distance:
  [
  D_{self,i}=|L_{early,i}-L_{late,i}|;
  ]

- other distance:
  [
  D_{other,i}
  =
  mean_{j
eq i}|L_{early,i}-L_{late,j}|.
  ]

Individual breadth-identity advantage:

[
K_i=D_{other,i}-D_{self,i}.
]

Aggregate equally across evaluable biological individuals within year:

[
K_W=mean_i K_i.
]

Positive means an individual's early policy breadth is closer to its own later breadth than to peers' later breadth.

## Null

Within each cohort independently:
- keep all early breadths fixed;
- permute the complete late-breadth labels among the evaluable individuals;
- recompute the full K statistic.

9,999 permutations.

Seeds:
- 2022: `202610052201`;
- 2023: `202610052202`.

A year is structurally evaluable only if:
- at least **5** individuals contribute in total;
- at least 9,500 valid permutations are obtained.

## Frozen support rule

Persistent individual policy breadth is supported within a year only if:
- (K_W>0);
- one-sided permutation p <= 0.05;
- >=70% of evaluable individuals have (K_i>0).

## Secondary descriptive outputs

Report:
- early and late W for every evaluable individual;
- early/late Spearman correlation of log breadth across individuals;
- median early W and late W;
- number of eligible days and half sizes.

Do not use secondary quantities to rescue the primary.

## Interpretation

### Supported

Allowed:

> **Individuals differ persistently not only in where they lie in policy space but in how broadly they range around their personal policy state.**

This would establish a repeatable predictability / breadth component.

### Unsupported

Do not infer equal within-individual variance.

Conclude only that early policy breadth does not predict later breadth consistently under this split and support rule.

Remaining explanations include:
- context-specific variance;
- state switching;
- temporal changes in breadth;
- estimation noise from limited repeated days;
- unresolved environmental covariates.

## Hard ceiling

Even if supported, policy breadth is not automatically:
- exploration;
- flexibility;
- cognitive unpredictability;
- adaptive bet-hedging.

It is residual realized variability after this peer-day adjustment.

## No rescue

Do not:
- lower the 6-day minimum;
- choose a breakpoint after output;
- select one axis (H or V) after seeing the 2-D result;
- remove high-variance individuals;
- replace log breadth with another transform;
- promote a secondary correlation if K_W fails.
