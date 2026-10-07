# Aharon 2017 Figure-3 navigation-policy primary contract v1

## Status

**PROSPECTIVE PRIMARY DEFINITION FROM PUBLIC SOURCE STRUCTURE. NUMERIC DATA NOT OPENED.**

Source:
Aharon, Sadot & Yovel (2017),
*Bats Use Path Integration Rather Than Acoustic Flow to Assess Flight Distance along Flyways*,
Current Biology 27:3650–3657.e3.
DOI: `10.1016/j.cub.2017.10.012`.

Public dataset:
Mendeley Data v3, DOI `10.17632/f6mvhj5gj9.3`.

The public dataset description states that Figure 3 exposes, by biological bat and condition:

1. turning-point matrices, one trial per column;
2. slowing-point matrices, one trial per column;
3. trial-level mean speed.

No numeric matrix value has been opened in this programme.

## Why Figure 3 is fixed

Figure 3 is selected before outcome opening because it is the only public layer explicitly described as containing all three:

- where the bat turns;
- where it begins slowing;
- how fast the trial was flown.

This jointly represents the timing/location of the navigational decision and its movement expression.

Do not switch to Figures 1, 2 or 4 because their results look stronger.

## Biological question

> Does individual navigation organization remain identifiable across the Figure-3 source-defined manipulation conditions?

The source paper experimentally changes external navigation information while testing distance estimation along the same flyway task.

The primary is therefore a perturbation-portability test, not ordinary repeatability.

## Structural opening required before numeric analysis

Recover from the Figure-3 public file, without printing values:

- all variable names;
- biological bat IDs encoded in variable prefixes;
- condition suffixes;
- number of trial columns for every bat × condition turning matrix;
- number of trial columns for every bat × condition slowing matrix;
- number of trial values for every bat × condition speed vector.

Proceed only if:

- >=4 biological bats are present in >=2 common conditions;
- each retained bat has >=5 structurally paired trials per retained condition;
- turning, slowing and speed are all available for the same retained bat × condition cells.

If this fails:
**STOP_FIGURE3_NAVIGATION_POLICY_PRIMARY**.

No bat or feature may be dropped to rescue the primary.

## Frozen trial-level representation

For each bat × condition × trial, define exactly three source-native quantities:

### T — turning location

Use the mean of finite turning-point entries in that trial column.

The source description identifies alternating rows as right/left turns; no side-specific weighting is used.

### S — slowing location

Use the mean of finite slowing-point entries in that trial column.

No left/right split in the confirmatory primary.

### V — mean speed

Use the corresponding source trial mean-speed value.

Trial vector:

[
N=(T,S,V).
]

A trial is valid only if all three are finite.

No fitted weights.

## Condition handling

The actual Figure-3 condition labels must be recovered structurally before values are opened.

The confirmatory comparison uses **all source-defined Figure-3 conditions shared by the retained bats**.

No condition subset may be selected by outcome.

## Shared-condition residualization

For each of T, S and V:

1. calculate the pooled mean within each source condition without using bat identity;
2. subtract the condition mean from every trial;
3. calculate one pooled residual sample SD across all retained conditions;
4. require finite SD >0;
5. divide residuals by that common SD.

Thus the representation removes shared condition shifts while retaining individual organization and individual × condition differences.

## Bat × condition centroids

For each bat i and condition c:

[
ar N_{i,c}
=
operatorname{mean}_{trials} N.
]

Equal-trial weighting.

## Primary cross-condition identity statistic

For each target bat i in each target condition c:

- history centroid = equal-condition mean of that bat's centroids from all other retained Figure-3 conditions;
- donor history centroid j = the same construction for each other retained bat;
- self distance = Euclidean distance from target centroid to own other-condition history;
- other distance = mean Euclidean distance to other bats' histories.

Target advantage:

[
A_{i,c}
=
d_{other}-d_{self}.
]

Aggregate:
- equal conditions within bat;
- equal bats overall.

Programme statistic K is the equal-bat mean advantage.

## Exact null

Permute complete biological identity labels attached to the history centroids while preserving:

- source condition;
- trial values;
- condition support;
- the exact bat label multiset.

The final exact permutation space depends on the structurally recovered number of bats.

Before numeric values are opened, record:

[
n!
]

and its minimum attainable one-sided p-value.

If the exact permutation resolution cannot attain p<=0.05:
**STOP_CONFIRMATORY_PVALUE_UNIDENTIFIABLE**.

No asymptotic rescue.

## Support

Confirmatory support requires:

- K > 0;
- exact one-sided p <=0.05.

Report:
- K;
- exact p;
- bat-specific mean advantages;
- positive-bat fraction;
- trial support by condition;
- complete exact null.

## Diagnostics

Report T-only, S-only and V-only K values descriptively.

No component-wise p-values.

No component can rescue a failed three-dimensional primary.

## Claim ceiling

If supported, allowed:

> **Individual navigation organization remains identifiable across experimentally changed navigation conditions in a path-integration task.**

Do not claim:
- path integration itself is individual-specific;
- the same latent carrier as Rhino I/M;
- learned versus intrinsic origin;
- generality to wild space use;
- causal storage in a particular sensory system.

This source tests portability of individual navigation organization across manipulated external conditions.
