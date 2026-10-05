# Older-history field allocation persistence contract v1

## Status

**POST-OUTCOME TEMPORAL-MAINTENANCE FALSIFICATION DIAGNOSTIC.**

Frozen after:
- strict-past allocation maintenance was supported in P. hastatus 2022 and 2023;
- the most recent single session was descriptively predictive.

No latest-session-excluded result has yet been calculated.

## Question

Is strict-past predictability merely immediate behavioral inertia, or does information persist in **older personal history** after the most recent session is removed?

## Data and scalar

Use exactly the same:
- P. hastatus 2022/2023 fixed-bin 360-s sessions;
- chronology;
- cohort structure;
- allocation scalar
  `A=(H-V)/sqrt(2)`

as `STRICT_PAST_ALLOCATION_PERSISTENCE_CONTRACT_V1.md`.

## Latest-session exclusion

For target session q of individual i at time t:

1. collect all self sessions with time < t;
2. identify the most recent strictly prior self session;
3. remove it completely;
4. use the remaining older self sessions as the self-history library.

Primary minimum:
- at least **1 older self session after removal**.

Self predictor:
`theta_i,older = mean(A)`.

For every donor j:
- collect donor sessions with time < t;
- remove donor j's own most recent prior session;
- require at least 1 older donor session;
- donor predictor is mean of remaining older A values.

Require at least 2 evaluable donors.

## Target statistic

`K_q = mean_j |A_q-theta_j,older| - |A_q-theta_i,older|`.

Aggregate:
- equal targets within biological individual;
- equal individuals within year.

## Null

Use the same cohort-wise exact label-multiset shuffle as the strict-past test.

For every permuted dataset:
- reconstruct chronology;
- remove each assigned label's most recent prior session;
- recompute eligibility and K.

9,999 permutations.

Seeds:
- 2022: `202610051521`
- 2023: `202610051522`.

Require >=9,500 valid permutations.

## Support

A year supports older-history persistence if:
- K_old > 0;
- p <= 0.05;
- >=70% evaluable individuals have positive mean K.

## Stricter descriptive sensitivity

Repeat observed statistic requiring:
- >=2 older self sessions after latest removal;
- >=2 older sessions for each donor.

No additional p-value.

## Interpretation

### Supported after latest removal

Pure one-step inertia is insufficient. Information about the future remains in deeper personal history.

### Unsupported after latest removal

The strict-past result may be dominated by immediate state persistence or very short-memory behavior.

## Ceiling

Support still does not distinguish:
- long-term memory;
- stable morphology/performance;
- persistent internal state;
- repeated resource/task structure.

It only rules against a model in which **only the immediately previous session** carries personal information.
