# Cross-configuration echolocation-policy identity contract v1

## Status

**POST-PRIMARY, PROSPECTIVELY FROZEN SENSING DIAGNOSTIC.**

This contract is frozen after:
- movement Primary B PASS;
- post-primary performance/steering decomposition;
- pulse semantics opening established that `pulse` is a complete binary 0/1 event indicator.

No bat-level pulse comparison has yet been calculated.

## Question

Does an individual-specific sensing rhythm transfer across obstacle configurations, independently of absolute flight-path location?

A positive result would extend the portable individual signature from movement output to echolocation emission timing.

## Data

Use only the same 45 authoritative *Rhinolophus nippon* CSV trajectories used by Primary B.

Use:
- `Time (Seconds)`;
- `pulse`.

Do not use X/Y/Z to construct pulse features.

## Pulse-event reconstruction

For each CSV:

1. retain rows with finite time and pulse exactly 0 or 1;
2. stable-sort by time;
3. for duplicate timestamps, aggregate pulse by logical maximum (an event is retained if any duplicate row has pulse=1);
4. require positive total duration;
5. pulse-event times are timestamps where pulse=1;
6. require >=30 pulse events;
7. compute strictly positive consecutive inter-pulse intervals (IPIs);
8. require >=29 positive IPIs.

No smoothing, event merging or refractory threshold is introduced.

## Frozen six-feature sensing vector

For each valid trajectory:

1. `log_pulse_rate = log(N_pulse / duration)`;
2. median of `log(IPI)`;
3. 10th percentile of `log(IPI)`;
4. 90th percentile of `log(IPI)`;
5. IQR of `log(IPI)` = q75 - q25;
6. sample SD of `log(IPI)`.

All features must be finite.

## Environment standardization

Use the same configuration-removal logic as the authoritative movement Primary B:

For each usable environment × pulse feature:
- arithmetic mean across valid trajectories;
- sample SD;
- z-score within environment.

A usable environment requires:
- >=2 valid trajectories;
- >=2 distinct bat identities.

If any pulse feature has zero/nonfinite SD in any usable environment, drop that feature species-wide.

Require >=4 of 6 pulse features to remain.

## Leave-one-environment-out identity

A candidate bat must occur in >=3 usable environments.

For target trajectory q from bat i in environment e:

- for each bat j, average j's valid trajectory vectors within every other environment;
- average those environment centroids equally;
- require the focal bat to have >=2 other environments;
- require >=2 donor bats with >=2 other environments.

Distance:
Euclidean distance in retained environment-z-scored pulse-feature space.

`P_q = mean(distance to other-bat centroids) - distance to own-bat centroid)`.

Individual:
equal-target mean `P_i`.

Species:
equal-bat mean `P`.

Positive means the pulse timing pattern is closer to the same bat's sensing history from other obstacle configurations.

## Null

Use the exact cluster-level cross-environment null architecture from movement Primary B:

- within each usable environment independently, permute complete bat × environment trajectory clusters as indivisible units among bat labels;
- preserve all within-cluster pulse trajectories and exact cluster sizes;
- break only cross-environment identity correspondence.

9,999 permutations.

Seed:
`202610042231`.

Valid-permutation minimum:
9,500.

## Diagnostic support rule

Report:
- P;
- individual P_i;
- positive fraction;
- null mean and 95% interval;
- one-sided permutation p.

Call the post-primary sensing diagnostic **supported** only if:
- P > 0;
- p <= 0.05;
- >=70% of evaluable bats have P_i > 0.

This is not promoted to a new confirmatory primary.

## Interpretation

### Supported

The portable individual signature spans both:
- movement policy;
- echolocation emission timing.

This supports a broader **individual sensorimotor policy** interpretation over a movement-only route-memory account.

### Unsupported

The portable individuality established by Primary B remains a movement-policy result; sensing individuality is not inferred.

## Important ceiling

Even if supported, the result does not distinguish:
- learned long-lived sensorimotor style;
- stable morphology/physiology;
- developmental predisposition.

A manipulation or longitudinal reset remains necessary for that causal distinction.
