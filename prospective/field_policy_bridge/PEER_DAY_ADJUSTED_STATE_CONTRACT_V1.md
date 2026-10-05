# Peer-day-adjusted allocation-state persistence contract v1

## Status

**POST-OUTCOME DYNAMIC-STATE FALSIFICATION DIAGNOSTIC.**

Frozen after:
- strict-past allocation maintenance was supported in P. hastatus 2022 and 2023;
- latest-session-excluded older history remained supported in 2022;
- within-individual allocation deviations showed positive temporal persistence under a fixed-individual-mean null;
- persistent policy distance did not predict synchronous vertical separation.

No peer-day-adjusted temporal persistence result has yet been calculated.

## Question

Can the observed within-individual temporal state persistence be explained by a **shared day-level environment** that affects all bats in a colony similarly?

Examples include:
- weather;
- food availability;
- nightly disturbance;
- common colony state.

The diagnostic removes a contemporaneous peer estimate of that shared day effect before testing temporal order within the focal individual.

## Data

Use exactly the fixed-bin 360-s P. hastatus 2022 and 2023 allocation sessions and

`A=(H-V)/sqrt(2)`

from the existing field-policy programme.

Use source datetimes from the raw timestamps.

Analyse years separately.

## Source calendar day

For every frozen session:
- recover the earliest valid source datetime assigned to that exact cohort × session × biological individual;
- use its source-native calendar date via `.date()`;
- do not reconstruct day by integer-dividing epoch time.

## Peer-day common-state estimator

For focal session q of individual i in cohort c on source date d:

1. collect all policy-valid sessions on date d in cohort c from biological individuals j != i;
2. first average A within each peer individual j for that date;
3. then average peer-individual daily means equally.

Call this:

`C_{c,d,-i}`.

Require at least **2 distinct peer individuals**.

Define peer-day-adjusted focal state:

`A*_{q}=A_q-C_{c,d,-i}`.

No focal session contributes to its own common-state estimate.

## Individual eligibility

A biological individual is eligible only if:
- it has at least **4** peer-day-adjusted sessions;
- at least 3 positive-time adjacent pairs exist after chronological sorting.

## Primary statistic

For each eligible individual:

1. sort A* sessions by exact source start time;
2. do not create a lag pair across tied timestamps;
3. center by that individual's mean A*;
4. define deviations u*;
5. compute the same normalized lag-1 persistence as in the original state test:

`R_i^* = mean_adjacent(u_t^* u_{t-1}^*) / mean_all((u_t^*)^2)`.

Year statistic:
equal-individual mean `R_peerday`.

## Null

For every individual independently:
- keep its complete adjusted A* multiset unchanged;
- keep all source timestamps unchanged;
- randomly permute A* values among that individual's timestamps.

This preserves:
- biological individual mean and variance after peer-day adjustment;
- the exact temporal sampling schedule;
- the observed peer-day subtraction;
- all between-individual stable differences in adjusted values.

It destroys only within-individual temporal order after common-day adjustment.

9,999 permutations.

Seeds:
- 2022: `202610051601`
- 2023: `202610051602`.

One-sided p for positive persistence.
Require >=9,500 valid permutations.

## Support floor

A year opens only if:
- >=5 eligible biological individuals;
- >=15 total adjusted adjacent pairs.

Otherwise STOP that year.

## Descriptive diagnostics

Report:
- number and fraction of original policy sessions receiving a valid peer-day estimate;
- distribution of number of peer individuals contributing per focal session;
- elapsed-gap distribution;
- short-gap and long-gap normalized persistence split at the year-specific median positive gap.

No additional p-values for gap subsets.

## Interpretation

### Supported after peer-day adjustment

A shared day-level colony environment is insufficient to explain the temporal state persistence.

This strengthens a focal-individual internal/history-dependent state interpretation.

### Unsupported after adjustment

The original temporal persistence may be substantially explained by common temporal environmental structure or by support loss.

## Ceiling

Even a positive result does not prove reinforcement learning or memory.

Unmeasured individual-specific environmental sequences can still generate autocorrelation.
