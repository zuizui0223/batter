# Wild policy bridge structural preflight contract v1

## Status

**OUTCOME-BLIND WITH RESPECT TO VERTICAL DISTRIBUTION DIFFERENCES.**

No vertical histogram, Hellinger distance, pairwise vertical divergence or policy–vertical correlation may be calculated in this preflight.

## Allowed structural information

Use:
- individual ID;
- session ID;
- timestamp;
- projected x/y;
- session order;
- horizontal speed;
- horizontal turning;
- horizontal cell;
- broad speed×turn state;
- counts of events by individual × split × stratum.

Although source ingestion may carry height fields, the preflight must not:
- read height values into any calculation;
- center height;
- bin height;
- compare height between individuals.

## Session support

An individual is structurally eligible only if:
- >=4 retained sessions total;
- odd-session side has >=2 sessions;
- even-session side has >=2 sessions;
- each side has >=2 policy-valid sessions under the frozen interval/turn support rule.

## Pair support proxy

For each reciprocal target side:

- count held-out events by individual × 2-km cell × broad state;
- a pairwise stratum passes if each individual has >=10 events;
- a pair passes if >=3 strata pass.

A panel passes structural preflight only if:
- >=6 structurally eligible individuals;
- each reciprocal fold has >=15 eligible individual pairs.

## Output

For each panel report:
- session counts per individual;
- valid policy-session counts by odd/even side;
- eligible individuals;
- eligible pair counts by reciprocal fold;
- state thresholds;
- PASS/STOP.

No vertical outcome summary may appear.
