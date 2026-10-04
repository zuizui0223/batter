# First-flight self-predictability emergence contract v1

## Status

**SEPARATE PROSPECTIVE CORROBORATION PROGRAMME.**

Source:
Harten et al. 2020, `10.1126/science.aay3354`

Public dataset:
`10.17632/n9d8gbz3xr.1`

This programme does not rescue the maternal-to-self crossover primary and does not modify JAE v0.4.0.

## Question

Does personal route predictability **emerge with independent experience** when observation begins at the first outdoor flights?

The key distinction is between:

- **stable predisposition / performance matching**: individual route differences should be present very early, before much independent experience;
- **path-dependent personal refinement**: held-out prediction from one's own history should strengthen as experience accumulates;
- **short-memory inertia**: self-history advantage should be dominated by only the most recent trip and should not generate a persistent long-history advantage.

## Population

Use only source-defined juveniles whose first independent/outdoor-flight chronology is reconstructable and that pass the frozen schema gate.

Biological replication unit:
**juvenile individual**.

GPS fixes are measurement units, not biological replicates.

## Strict chronology

For target trip t:
- the self-history library contains only independent trips completed before t;
- no future trips are used;
- trip 1 has no self-history score and is never imputed;
- any source-coded maternal transport or pre-flight period is not treated as independent self history.

## Primary series

For each eligible target trip, define:

`R_it = predictive advantage of focal juvenile's own prior independent history over an exchangeable other-juvenile history baseline`.

The exact route estimator and baseline matching are frozen after outcome-blind schema/sampling preflight and before route outcomes.

Required properties of the estimator:
- destination/task matching where source information permits;
- equal-history-trip weighting;
- equal-donor-individual weighting;
- no future leakage;
- route sampling standardized independently of outcome.

## Primary formation statistic

For each juvenile, estimate a predeclared monotonic experience effect:

`B_i = association(R_it, number of prior independent trips)`.

Primary programme statistic:

`B = equal-individual mean/median calibrated B_i`

with the exact robust estimator frozen before outcome opening.

Support for experience-dependent formation requires:
- positive programme-level experience effect;
- directionally positive effects in >=70% of evaluable juveniles;
- predeclared individual-level calibration passing its one-sided alpha=0.05 criterion.

No post-outcome breakpoint search is allowed.

## Secondary long-history test

If structurally possible, compare:
- recent-history predictor;
- accumulated-history predictor with the immediately previous trip excluded.

Path-dependent persistent propensity predicts that accumulated older history retains information.

Pure immediate-trip inertia predicts substantial collapse when the most recent trip is removed.

This is secondary and cannot rescue a failed formation slope.

## Early-state descriptive test

Before extensive experience, report:
- between-individual route dispersion;
- self-predictability once minimally estimable;
- route novelty/exploration.

Interpretation:

### Predisposition-dominant pattern
- strong, stable between-individual route differences from earliest estimable trips;
- little increase in self-history predictability with experience;
- stable traits would remain plausible primary carriers.

### Experience-dependent path dependence
- weak or unstable initial self predictability;
- increasing self-history advantage with accumulated trips;
- route solutions become personally stereotyped through experience.

### Mixed architecture
- early individual differences plus further experience-dependent refinement.

A mixed outcome is biologically admissible and should not be forced into a binary learning-versus-morphology interpretation.

## Reset logic

The present dataset may or may not contain a known environmental reset.

No deployment boundary is to be reinterpreted as a reset.

If no source-defined reset exists, the programme makes no reset claim.

## Claim ceiling

A supported result may show:

> personal route predictability builds across the first independent movement experience.

It does not establish:
- reinforcement learning as a specific algorithm;
- memory as the only carrier;
- absence of morphology;
- fitness advantage;
- universality across species.

## Stop rules

After outcome opening:
- no alternate experience axis;
- no hand-selected learning phase;
- no juvenile exclusion based on observed route effect;
- no destination pooling rescue;
- no alternate route metric rescue;
- no pooling with Source A;
- no JAE amendment.
