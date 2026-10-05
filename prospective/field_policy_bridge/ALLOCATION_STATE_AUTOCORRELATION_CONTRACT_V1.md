# Within-individual allocation-state autocorrelation contract v1

## Status

**POST-OUTCOME DYNAMIC-STATE DIAGNOSTIC.**

Frozen after:
- persistent field allocation individuality was established;
- strict-past self-history prediction was supported in P. hastatus 2022 and 2023.

No within-individual temporal autocorrelation result has yet been calculated.

## Question

Can the temporal self-predictability be explained entirely by a fixed individual mean plus exchangeable session noise?

Under a pure stable-trait model,

[
A_{it}=	heta_i+arepsilon_{it},
]

where (arepsilon_{it}) is temporally exchangeable within individual, the ordering of a bat's session deviations contains no extra information.

A history/state model predicts that deviations from the individual's typical allocation can persist from one session to the next.

## Data

Use exactly the fixed-bin 360-s P. hastatus 2022 and 2023 sessions and

[
A=(H-V)/sqrt2.
]

Use source timestamps to order sessions exactly as in the strict-past programme.

Analyse years separately.

## Individual statistic

For every biological individual with at least **4** eligible sessions:

1. order its session A values by source start time;
2. if sessions have identical start times, do not create a lag pair across that tie;
3. compute the individual's full-series mean (ar A_i);
4. define centered deviations
   [
   u_{it}=A_{it}-ar A_i;
   ]
5. compute normalized lag-1 persistence
   [
   R_i=
   rac{mathrm{mean}_{adjacent}(u_{it}u_{i,t-1})}
        {mathrm{mean}_{all}(u_{it}^2)}.
   ]

Require positive denominator and at least 3 valid adjacent-time pairs.

Year statistic:
- equal-individual mean (R=mathrm{mean}_i R_i).

This is not ordinary pooled autocorrelation; individuals are biological replicates and receive equal weight.

## Null: fixed trait + exchangeable within-individual residuals

For each permutation independently for every biological individual:

- keep that individual's complete A-value multiset unchanged;
- keep the observed session timestamps unchanged;
- randomly permute A values among that individual's timestamps;
- recompute R_i and equal-individual R.

This preserves exactly:
- individual mean;
- individual variance and marginal distribution;
- number of sessions;
- temporal sampling schedule;
- all between-individual differences.

It destroys only within-individual temporal ordering.

9,999 permutations.

Seeds:
- 2022: `202610051541`
- 2023: `202610051542`.

One-sided p for positive persistence.
Require >=9,500 valid permutations.

## Gap sensitivity

Descriptive only.

For observed adjacent pairs:
- report elapsed-time distribution;
- split pairs at the year-specific median positive gap;
- calculate the same normalized persistence contribution separately for short-gap and long-gap adjacent pairs.

No extra p-values.

## Interpretation

### R > null

A fixed individual mean plus exchangeable noise is insufficient. Temporary departures from a bat's typical policy persist through time, consistent with an internal/history-dependent policy state.

### R indistinguishable from null

Strict-past predictability can be explained by stable individual differences without evidence that within-individual deviations themselves propagate.

## Ceiling

Positive serial persistence still does not uniquely identify:
- memory;
- learning;
- reinforcement;
- physiology.

Environmental autocorrelation can also produce serial state dependence. The result therefore strengthens a persistent-state model but does not prove self-reinforcement.
