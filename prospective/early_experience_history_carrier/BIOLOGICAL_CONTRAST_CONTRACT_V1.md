# Early-experience effect on personal-history dependence — biological contrast contract v1

## Status

**BIOLOGICAL CONTRAST FROZEN BEFORE THE NEW ROUTE-HISTORY OUTCOME IS OPENED.**

Exact raw-file parsing and route-distance implementation will be frozen only after outcome-blind schema inspection.

## Primary question

Does randomized early environmental experience alter the strength of later personal spatial-history dependence in free-ranging foraging?

## Primary individual quantity

For each structurally eligible bat i, the programme will estimate a predeclared personal-history advantage summary:

`H_i`

where larger H means held-out wild movement is better predicted by that bat's own strictly prior movement history than by experience-matched histories of other bats under the frozen comparator design.

The exact daily estimator is frozen after schema inspection and before coordinate outcome opening.

## Primary treatment contrast

Let:
- E = enriched early environment;
- I = impoverished early environment.

Primary statistic:

`T = mean(H_i | E) - mean(H_i | I)`

with equal bat weighting.

The treatment test is **two-sided**.

Reason:
the experiment strongly predicts that early experience can change later behaviour, but current theory does not uniquely determine whether enrichment should:
- strengthen route/history reuse through improved learning and refinement, or
- weaken route lock-in through greater exploration and flexibility.

The sign therefore has mechanistic meaning but is not chosen after the data.

## Calibration

Primary inference must respect the source randomization.

Preferred:
exact or Monte-Carlo treatment-label randomization under the recoverable source assignment blocks fixed before outcome opening.

If the exact block structure cannot be recovered, the primary does not silently switch to an arbitrary covariate model; a new randomization-provenance amendment must be frozen first.

## Minimum support

The primary opens only if:
- >=5 enriched bats;
- >=5 impoverished bats;
- each included bat has enough strictly chronological repeated movement to construct H under the later frozen estimator.

## Secondary: baseline predisposition versus experience

If baseline personality traits can be linked to the GPS bats, a predeclared mechanistic secondary will compare:

- randomized environmental treatment;
- baseline behavioural predisposition measured before treatment;

as predictors of H.

The secondary asks whether **personal-history dependence is more strongly associated with experienced environment than with the individual's measured pre-treatment behavioural disposition**.

The exact baseline variable/PC cannot be selected after viewing H and must be frozen from source definitions first.

## Interpretation

### Treatment effect supported

Allowed claim:

> randomized early experience altered the later strength of personal spatial-history dependence.

This would provide causal evidence that individual specialization can be maintained by an experience-shaped history carrier rather than requiring continued spatial exclusion.

### No treatment effect

Do not infer that experience is irrelevant.

Possible bounded interpretations:
- early environment changes exploration but not history dependence;
- personal-history dependence arises too rapidly after release to retain the captive-treatment signal;
- stable constraints dominate this particular route-history metric.

## Stop rules

After H is opened:
- no changing treatment groups;
- no selecting a different history horizon;
- no switching distance metric;
- no post-hoc donor restriction;
- no dropping bats based on observed H;
- no selecting a baseline personality axis based on its correlation with H;
- no reinterpretation of a source-published exploration effect as this new endpoint.

## Independence

This test does not rescue the failed Harten 2020 monotonic formation primary.

It is a new randomized causal test of what modulates the **maintenance carrier**.
