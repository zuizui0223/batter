# Early-seed versus recent-history diagnostic v1

## Status

**POST-PRIMARY ONTOGENETIC MECHANISM DIAGNOSTIC.**

This diagnostic was motivated after the Source B monotonic-formation primary was opened.
It is not an independent confirmatory test and cannot rescue the failed primary formation rule.

It reuses without modification:
- the MATLAB-native standardized-coordinate bridge v2;
- 30-s within-day standardization;
- valid-day threshold >=20 fixes;
- source x/y coordinates;
- mean nearest-point day-to-history distance;
- whole-history identity permutation within cohort;
- equal-individual biological weighting.

## Biological question

The primary result showed:
- personal-history advantage is already positive at the earliest estimable target day 3;
- later history is strongly predictive;
- but a universal monotonic increase through days 3–20 fails.

The next bounded question is:

> **Is the individual's earliest independent movement history already predictive of later spatial use, and does recent personal history add identity-specific information beyond that early seed?**

This separates:
- rapid establishment of individual spatial bias;
- later personal updating/refinement.

It does not identify learning versus morphology uniquely.

## Population

Use exactly the Source B primary-complete juveniles:
- ordinary non-translocation cohorts only;
- >=20 structurally valid movement days;
- same cohort restrictions as the frozen primary.

Late target window:
- valid-day ordinals **11–20** only.

This window was already predeclared as the primary programme's late-history window.

## Equal-depth history comparison

For every target valid day t in 11..20:

### Early seed

Use exactly the donor individual's first **2** structurally valid movement days:
- valid-day ordinals 1 and 2.

### Recent seed

Use exactly the same donor individual's immediately preceding **2** valid movement days:
- ordinals t-2 and t-1.

Thus early and recent histories contain exactly two days each.

No history-size advantage is allowed.

## Eligible donor set

For target individual i at t:
- donor must be in the same cohort;
- donor must have at least t valid days;
- target individual must be present among donors;
- require self + >=3 other donors.

Use the same donor set for early and recent calculations.

## Distance and identity advantage

For each target and donor compute the already-frozen mean nearest-point distance using the two history days.

For representation h in {early,recent}:

[
R^h_{it}
=
D^h_{other,it}
-
D^h_{self,it}.
]

Positive means the target lies closer to its true personal history than to other juveniles' histories.

## D1 — early-seed persistence

For each juvenile:

[
E_i = mean_{t=11}^{20} R^{early}_{it}.
]

Programme statistic:

[
E = mean_i E_i.
]

Diagnostic support for an early-established personal seed requires:
- E - mean(E_null) > 0;
- one-sided p <= 0.05;
- >=70% of evaluable juveniles have E_i > 0.

## D2 — identity-specific updating beyond the early seed

For each juvenile:

[
Q_i
=
mean_t(R^{recent}_{it}-R^{early}_{it}).
]

Programme statistic:

[
Q=mean_i Q_i.
]

A positive raw Q is not enough, because all juveniles may become more spatially self-similar at nearby ages.

Therefore Q is calibrated under the same whole-history identity permutation.

Diagnostic support for individual-specific later updating requires:
- Q - mean(Q_null) > 0;
- one-sided p <= 0.05;
- >=70% of evaluable juveniles have Q_i > 0.

## Null

Use 9,999 whole-history identity permutations within cohort.

For each permutation:
1. keep target trajectories and target identities fixed;
2. keep every donor's complete chronological history intact;
3. permute complete history identities among target labels within cohort;
4. use the assigned pseudo-self donor for both early and recent history;
5. use all remaining eligible donors as pseudo-other;
6. recompute E and Q.

Seed:
`202610061001`.

This preserves:
- ontogenetic spatial expansion;
- day-specific sampling support;
- early/recent temporal structure;
- each donor's own trajectory autocorrelation.

It breaks only the target-to-true-personal-history link.

## Interpretation matrix

### E supported, Q unsupported

Rapid/stable establishment:
early independent movement already carries most later identity information.

### E unsupported, Q supported

Later personal refinement dominates:
early movement is weakly informative but recent individual history gains identity-specific predictive value.

### E and Q supported

Mixed architecture:

> **individual spatial organization is established very early and is then further updated/refined through individual experience.**

### neither supported

The previous late-history signal may depend mainly on short-lived or context-specific history not retained from the earliest movement period.

## Claim ceiling

Even E + Q support does not establish:
- reinforcement learning as the algorithm;
- morphology absent;
- first valid day equals literally the first physical flight if earlier source days fail the structural valid-day gate;
- fitness benefit.

Use the phrase **earliest structurally valid independent movement history**, not "first flight", unless source-day identity is separately proven.

## No rescue

Do not:
- change 2-day history depth;
- move the late window;
- select juveniles after outcome;
- use a different distance;
- condition on destination post hoc;
- use translocation data;
- relabel this diagnostic as the failed formation primary.
