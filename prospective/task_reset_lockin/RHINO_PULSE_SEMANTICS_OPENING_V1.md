# Rhino pulse-semantics opening contract v1

## Status

**POST-PRIMARY STRUCTURAL PROBE.**

The authoritative movement-policy primary did not use `pulse`; pulse values have remained outside the evidence used for Primary A/B.

This probe is frozen after the movement-policy result and before pulse values are inspected for individual differences.

## Biological motivation

Primary B shows transferable individual movement-policy identity across obstacle configurations, including a steering-style-only signature.

The next question is whether individuality extends from movement output into echolocation sensing behaviour.

Before defining a sensing-policy estimator, the public CSV `pulse` field must be understood from source values.

## Authorized data

Only the 45 authoritative *Rhinolophus nippon* CSV files.

Read:
- `Time (Seconds)`;
- `pulse`.

Do not use X/Y/Z in this probe.

## Authorized summaries

Across the complete Rhino dataset and separately by CSV **without reporting bat-wise or environment-wise contrasts**, report:

- row count;
- missing pulse count;
- finite pulse count if numeric;
- number of unique non-missing pulse tokens;
- if <=20 unique tokens, list them;
- otherwise report min/max and 1%, 50%, 99% quantiles if numeric;
- count of values equal to zero;
- count of nonzero values;
- whether pulse changes sparsely through time;
- for each CSV, only the total number of rows and number/proportion nonzero/missing; filename may be retained for provenance but do not aggregate by bat identity.

## Forbidden at this stage

Do not calculate:
- pulse-rate differences among bats;
- inter-pulse interval identity;
- cross-environment pulse identity;
- correlation of pulse with speed/turning;
- any p-value involving pulse.

## Next decision

After semantics opening, freeze one estimator appropriate to the observed encoding.

Examples:
- binary event indicator -> inter-pulse intervals / emission rate;
- pulse timestamps -> interval statistics;
- categorical pulse state -> state occupancy/transition features.

Do not choose among these after looking at bat-level effects.

