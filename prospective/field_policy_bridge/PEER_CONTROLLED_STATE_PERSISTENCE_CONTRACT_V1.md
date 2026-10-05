# Peer-controlled allocation-state persistence contract v1

## Status

**POST-OUTCOME SHARED-ENVIRONMENT ROBUSTNESS DIAGNOSTIC.**

Frozen after:
- strict-past allocation self-prediction was supported in both P. hastatus years;
- within-individual temporal ordering of allocation deviations exceeded a fixed-trait + exchangeable-noise null in both years;
- the remaining alternative is that temporally autocorrelated shared environmental conditions drive the apparent within-individual state persistence.

No peer-controlled temporal-state result has yet been calculated.

## Question

Does within-individual temporal persistence remain after subtracting the allocation tendency expressed by other bats sampled at approximately the same time?

## Data

Use exactly the same fixed-bin 360-s P. hastatus sessions and allocation scalar

[
A=(H-V)/sqrt2
]

as the strict-past programme.

Analyse 2022 and 2023 separately.

## Contemporaneous peer control

For focal session q from individual i at start time t and frozen cohort c:

1. consider sessions from **other biological individuals only** in c;
2. retain peer sessions whose start time is within (pm12) hours of t;
3. first average A within each donor individual if a donor has multiple qualifying sessions;
4. average donor means equally.

Require at least **2 donor individuals**.

Define

[
A^{resid}_{iq}=A_{iq}-overline A_{peers,t}.
]

Thus common short-term shifts expressed across bats are removed before testing personal temporal state.

## Within-individual state statistic

For every biological individual with at least 4 peer-controlled sessions:

- order residual sessions by source start time;
- do not connect tied timestamps;
- subtract that individual's mean peer-controlled residual;
- compute the same normalized lag-1 statistic as
  `ALLOCATION_STATE_AUTOCORRELATION_CONTRACT_V1.md`.

Require at least 3 valid adjacent pairs.

Year statistic:
- equal-individual mean (R_{peer}).

## Null

Within every individual:
- preserve its complete peer-controlled residual multiset;
- preserve its observed eligible timestamps;
- randomly permute residuals across those timestamps.

This preserves:
- persistent individual offset after peer control;
- variance and residual distribution;
- sampling schedule;
- the exact contemporaneous peer correction already applied.

It destroys only personal temporal ordering.

9,999 permutations.

Seeds:
- 2022: `202610051551`
- 2023: `202610051552`.

One-sided positive p.
Require >=9,500 valid permutations.

## Window sensitivity

Descriptive only:
repeat the observed statistic with peer windows:
- ±6 h;
- ±24 h.

Report support counts and R, without additional p-values.

## Interpretation

### Supported after peer control

Shared cohort-level temporal forcing alone is insufficient. A temporally persistent **individual-specific state component** remains.

### Unsupported after peer control

The earlier serial persistence can plausibly arise from shared short-term environmental forcing.

## Ceiling

Peer control is not a measured weather model. Individuals can experience different microenvironments, resources or social contexts even at the same clock time. Support therefore strengthens but does not uniquely prove an internal-memory mechanism.
