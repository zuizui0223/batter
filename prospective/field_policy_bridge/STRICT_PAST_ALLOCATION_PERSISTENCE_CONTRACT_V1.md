# Strict-past field allocation persistence contract v1

## Status

**POST-OUTCOME TEMPORAL-MAINTENANCE DIAGNOSTIC.**

Frozen after:
- P. hastatus fixed-bin H and V persistence was supported;
- a stable negative H-V coupling was observed;
- the transparent allocation scalar
  `A=(H-V)/sqrt(2)`
  was defined prospectively in `FIELD_ALLOCATION_AXIS_CONTRACT_V1.md`.

No strict-past A-history result has yet been calculated.

## Question

Does a bat's **strictly prior** allocation history predict its next eligible field session better than strictly prior histories of conspecifics?

This is the temporal version of the maintenance hypothesis:

> individual policy is carried forward by the individual's own history.

## Data

Analyse separately:
- P. hastatus 2022;
- P. hastatus 2023.

Use exactly the fixed-bin 360-s policy-valid sessions from
`PHYLLOSTOMUS_FIXED_BIN_HARMONIZATION_CONTRACT_V2.md`.

Per session:
- H and V are the frozen within-cohort standardized components;
- `A=(H-V)/sqrt(2)`.

## Chronology

Recover each session's start time from the first valid source timestamp assigned to the same frozen:
- cohort;
- session id;
- biological individual.

Chronology is determined only from source timestamps.

No lexical sorting of session names is used as time.

If two sessions of the same cohort have identical start timestamps:
- they are considered simultaneous;
- neither may enter the other's history.

## Target eligibility

For target session q of individual i at start time t:

### Self history
Use only sessions of i in the same frozen cohort with start time < t.

Require:
- at least **2** prior self sessions.

Self predictor:
`theta_i,<t = mean(A)`
over those prior sessions.

### Donor histories
For each donor j in the same cohort:
- use only j sessions with start time < t;
- require at least **2** prior sessions for donor j.

Require at least **2** evaluable donors.

Donor predictor:
`theta_j,<t = mean(A)`.

## Target advantage

`D_self = |A_q - theta_i,<t|`

`D_other = equal-donor mean |A_q - theta_j,<t|`

`K_q = D_other - D_self`.

Positive K means the focal bat's strictly prior policy history predicts its future session better than contemporaneously available histories from other bats.

## Aggregation

- equal targets within biological individual;
- equal biological individuals within year.

Year statistic:
`K_past`.

Report:
- K_past;
- individual means;
- positive-individual fraction;
- target count;
- distribution of number of prior self sessions.

## Null

Within each frozen cohort independently:

- shuffle the exact observed individual-label multiset across complete session records;
- keep each session's:
  - A value;
  - start time;
  - cohort;
- preserve the total session count assigned to every individual label;
- recompute strict-past histories and eligibility from the permuted sequence.

Thus the null breaks temporal continuity of biological identity while preserving the cohort's time series and label frequencies.

9,999 permutations.

Seeds:
- 2022: `202610051511`
- 2023: `202610051512`.

A permutation is valid only if >=3 individual-level means are estimable.
Require >=9,500 valid permutations.

## Support rule

A year supports strict-past maintenance if:
- K_past > 0;
- one-sided p <= 0.05;
- >=70% of evaluable individuals have positive mean K.

## Recent-history sensitivity

Descriptive only:
repeat observed statistic using the most recent:
- 1 prior self session;
- 2 prior self sessions;

with donor histories truncated to the same maximum history length.

No additional p-values.

This separates:
- immediate inertia;
- accumulated personal-history prediction.

## Interpretation

### Strict-past support

> personal allocation policy is temporally self-predictive in the field; its future expression is better predicted by the bat's own prior sessions than by other bats' prior histories.

### Support only for most-recent history

More consistent with short-memory inertia.

### Support with accumulated history and not merely the latest session

More consistent with a persistent personal policy state.

## Ceiling

This remains observational.
It does not establish whether the stable policy is:
- learned;
- morphological;
- physiological;
- genetic.

It cannot modify JAE v0.4.0 classifications.
