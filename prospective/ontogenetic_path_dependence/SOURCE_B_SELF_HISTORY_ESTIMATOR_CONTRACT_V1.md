# Source B first-flight self-history estimator contract v1

## Status

**PROSPECTIVE PRIMARY OUTCOME CONTRACT — frozen before any Source B x/y route value is opened by this programme.**

Parent:
- `FIRST_FLIGHT_SELF_PREDICTABILITY_CONTRACT_V1.md`
- `SOURCE_B_FIRST_FLIGHT_PROVENANCE_V1.md`
- `SOURCE_B_ALL_INDIVIDUAL_DAYCOUNT_RESULT_V1.md`

Source:
Harten et al. 2020, Science, DOI `10.1126/science.aay3354`.
Public data: `10.17632/n9d8gbz3xr.1`.

## Biological question

> Does a juvenile's own accumulated independent movement history become progressively more informative about its future spatial solution from the first outdoor flights onward?

The primary object is **personal spatial-history predictability**.

Exact destination preference is treated as part of the learned/personal spatial solution rather than conditioned away in the primary. This is intentional: the maintenance question concerns where and how an individual repeatedly solves its nightly movement problem.

A future exact-destination corridor analysis, if structurally possible, is a separate secondary and cannot rescue this primary.

## Cohorts

Analyse the two source-defined ordinary, non-translocation cohorts separately inside the calibration and then aggregate individuals equally:

- `GPS_2016_2017`: 8 juveniles;
- `GPS_2017_2018`: 14 juveniles.

Do not pool translocation, resampled, simulated, or adult comparison folders.

## Raw movement fields

Use only the source-code-defined daily movement object:

- `data(day).track.x`
- `data(day).track.y`
- `data(day).track.time`

If any of these fields are unavailable or not numeric in the ordinary archive, STOP. Do not substitute longitude/latitude or another processed route representation after opening outcomes.

Source code already uses x/y directly for route geometry; these coordinates are therefore the frozen primary spatial representation.

## Sampling standardization

Within each day:

1. retain fixes with finite x, y and time;
2. sort by time;
3. create 30-second bins relative to that day's first retained timestamp;
4. retain the first fix in each 30-second bin;
5. no interpolation;
6. no smoothing.

A structurally valid movement day requires **>=20 standardized fixes**.

Rationale fixed before outcome:
- prevents variable logger frequency from weighting route similarity;
- retains short early flights rather than requiring long adult-like nights.

## Experience axis

For each juvenile, order **structurally valid movement days** chronologically.

Let target valid-day ordinal be `t`.

The primary formation window is:

- target ordinals **3 through 20 inclusive**;
- prior-experience count `e=t-1`, therefore e=2,...,19.

An individual is primary-evaluable only if it has **>=20 structurally valid movement days**.

The programme opens only if **>=5 juveniles** pass this post-coordinate structural gate.

If fewer than five pass: STOP. Do not shorten the 20-day horizon after outcome opening.

## History library

For target day t of juvenile i:

Self history:
- strictly earlier valid days only;
- use the **most recent min(5,e)** valid days.

Thus training-history size rises identically from 2 to 5 days and is capped at 5 from target ordinal 6 onward.

No future day may enter self history.

## Experience-matched other histories

For each target i,t, eligible donors are other juveniles in the **same cohort** with at least t valid movement days.

For donor j:
- use the donor's valid-day ordinals corresponding to the same history depth:
  `max(1,t-5),...,t-1`;
- never use donor day t or later;
- donor individuals are weighted equally.

Require **>=3 eligible donor juveniles** for a target day.

If a target day has fewer than three donors it is structurally ineligible; no cross-cohort donor rescue is allowed.

## Day-to-day spatial distance

For one standardized target fix q and one history day h:

[
d(q,h)=min_{pin h}|q-p|_2.
]

Distances use source x/y coordinates directly.

For the focal juvenile:

[
D_{self}(q)=mathrm{mean}_{hin H_i(t)} d(q,h).
]

For donor j:

[
D_j(q)=mathrm{mean}_{hin H_j(t)} d(q,h).
]

Other-individual comparator:

[
D_{other}(q)=mathrm{mean}_{j
e i}D_j(q).
]

Per target day:

[
R_{it}=mathrm{mean}_{qin target}left[D_{other}(q)-D_{self}(q)ight].
]

Positive R means the target night lies closer to the juvenile's own prior spatial history than to experience-matched conspecific history.

Weighting hierarchy:
- equal standardized fix within target day;
- equal history day within predictor;
- equal donor individual;
- equal target day within juvenile summaries;
- equal juvenile at programme level.

## Primary formation statistic

For each juvenile i:

[
B_i=ho_S(e,R_{it}),
]

the Spearman correlation between prior valid-day count e and daily self-history advantage R over target ordinals 3–20.

Programme statistic:

[
B=mathrm{mean}_i B_i.
]

No breakpoint, polynomial, spline, or selected "learning phase" is allowed.

## Primary null calibration

Use **whole-history identity permutation within cohort**.

For each permutation:

1. keep every target trajectory and target identity fixed;
2. keep each juvenile's complete chronological movement history intact;
3. independently within each cohort, permute complete history-library identities among juvenile labels;
4. for target i,t, the permuted assigned library is treated as pseudo-self;
5. all remaining eligible experience-matched history libraries form the pseudo-other comparator with equal donor weighting;
6. recompute every R_it, B_i and B through the complete pipeline.

This preserves:
- cohort;
- experience day;
- history size;
- each juvenile's ontogenetic spatial expansion;
- sampling density after 30-s standardization;
- all route autocorrelation inside a history.

It breaks only the link between a target juvenile and its true personal past.

Permutations:
**9,999**

Seed:
`20261004021`

Primary one-sided p:

[
p_B=rac{1+#(B_{null}ge B_{obs})}{10000}.
]

## Frozen support rule

Experience-dependent personal-history formation is supported only if:

1. `B_obs - mean(B_null) > 0`;
2. `p_B <= 0.05`;
3. at least **70% of primary-evaluable juveniles have B_i > 0**.

No component may be dropped after the result is opened.

## Secondary late-history confirmation

Predeclared secondary:

For target ordinals **11–20**, calculate each juvenile's mean R and then the equal-individual programme mean `L`.

Calibrate L under the same 9,999 whole-history identity permutations.

This asks whether, after independent experience has accumulated, true personal history is actually informative in absolute predictive terms.

It cannot rescue a failed primary B.

## Descriptive early/late curve

Report equal-individual mean R for each target ordinal 3–20 with individual-bootstrap intervals.

This is descriptive only. No ordinal may be selected post hoc as a breakpoint.

## Mechanistic interpretation

### Primary supported

Allowed claim:

> From the first outdoor flights onward, the predictive value of a juvenile's own movement history increased relative to experience-matched conspecific history.

This is direct evidence that **personal experience becomes an increasingly important carrier of individual spatial specialization**.

It supports path-dependent personal refinement but does not uniquely identify memory, reinforcement learning, resource familiarity, or sensorimotor learning.

### Primary unsupported but late L supported

Allowed bounded interpretation:

> Personal history predicts later movement, but the current data do not show a monotonic build-up over the first 20 valid flight days.

Do not relabel this as experience-dependent formation.

### Neither supported

Do not infer absence of learning. The relevant personal information may be destination-specific, arise before the first usable GPS flight, or be represented at a different scale.

## Stable-performance alternative

A stable morphology/performance mechanism can create persistent individuality from very early flights.

The primary discriminator is therefore the **experience gradient B**, not merely a positive late self-history advantage.

A positive B is harder to explain by a fixed individual trait alone, although morphology may still interact with experience.

## Stop rules after coordinate opening

No:
- alternative spatial distance family;
- DTW, Fréchet, Hausdorff, KDE-overlap or grid-score rescue;
- alternative downsampling interval;
- alternative history cap;
- alternative 20-day horizon;
- post-hoc early/late split;
- donor pooling across cohorts;
- individual exclusion based on observed R or B;
- translocation rescue;
- Source A pooling.

## JAE firewall

No Source B result can modify JAE v0.4.0.
