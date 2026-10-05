# Wild-field FlightIntensity persistence contract v1

## Status

**POST-JAE PROSPECTIVE MECHANISM BRIDGE.**

JAE v0.4.0 remains frozen.

This contract is fixed before calculating the new session-level FlightIntensity identity outcome.

## Biological question

Does the strongest portable laboratory policy coordinate — FlightIntensity — also travel with the same individuals across repeated wild GPS sessions in the fruit-bat panels that motivated the maintenance problem?

A positive result would establish a field-side low-dimensional carrier candidate.

It would not yet establish that this coordinate causes the centered vertical-distribution individuality in JAE.

## Panels

Use exactly the four original terrain-evaluable fruit-bat panels:

- Hypsignathus monstrosus;
- Phyllostomus hastatus 2022;
- P. hastatus 2023;
- P. hastatus 2016.

Use the exact source files, checksums, source-outlier exclusions, manipulated-animal exclusions, session segmentation and admitted cohorts from the frozen replication contracts.

No new animal/session inclusion rule.

## Movement endpoints

Within each retained session:

1. sort retained source-valid fixes by timestamp;
2. project longitude/latitude using the exact cohort UTM projection already frozen in the JAE replication architecture;
3. parse the frozen primary source vertical field;
4. for every consecutive pair require:
   - finite x,y,z;
   - 0 < dt <= 1800 s;
5. compute:
   - horizontal displacement;
   - vertical displacement dz;
   - 3-D displacement;
   - 3-D speed;
   - absolute vertical speed.

No interpolation or smoothing.

A session is policy-valid only if it has >=50 valid consecutive intervals.

## Session feature vector

For every policy-valid session:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed.

No route, altitude-level, turning, path-efficiency or vertical-range quantity enters this first bridge.

## Standardization

Within each frozen cohort separately:

- z-score each of the four session features across policy-valid sessions using the cohort mean and sample SD;
- if any feature SD is zero/nonfinite, that cohort is structurally stopped;
- define

`I_session = mean(z1,z2,z3,z4)`.

This is the exact transparent FlightIntensity architecture, adapted to session-level field summaries.

## Structural support

An individual is eligible only if it has >=2 policy-valid sessions in the same admitted cohort.

A panel opens the identity outcome only if it contains >=5 eligible biological individuals.

No threshold relaxation.

## Held-out self-history statistic

For each target session s of individual i:

- self centroid = equal-session mean I over i's other eligible sessions in the same cohort;
- for each other eligible individual j, donor centroid = equal-session mean I over all eligible sessions of j in that cohort;
- require >=2 donor individuals.

Target advantage:

`H_s = mean_j |I_s - I_j| - |I_s - I_i,-s|`.

Positive means the held-out session is closer to its own other-session FlightIntensity than to other individuals' histories.

Aggregate:
- equal target sessions within individual;
- equal individuals within panel.

Panel statistic:
`H_panel`.

## Null

Within each cohort independently:
- permute the exact observed multiset of biological individual labels across complete sessions;
- preserve session feature values, cohort membership and the exact number of session labels per individual.

9,999 permutations.

Panel seeds:
- Hypsignathus: `202610051301`;
- P. hastatus 2022: `202610051302`;
- P. hastatus 2023: `202610051303`;
- P. hastatus 2016: `202610051304`.

One-sided p:
`(1 + #null >= observed)/(10000)`.

## Panel support

Support requires:
- H_panel > 0;
- p <= 0.05;
- >=70% eligible individuals have positive individual mean H.

## Cross-panel bridge rule

A field-side FlightIntensity carrier is called supported only if >=3 of 4 panels pass the panel rule.

If fewer than three pass:
- stop the policy-to-vertical-shape bridge;
- do not switch to another policy axis.

## Additional audits

Report descriptively:
- session feature distributions;
- interval counts;
- per-individual number of valid sessions;
- maximum single-session influence on H by leave-one-session deletion, without new inference.

## Claim ceiling

A positive result supports:

> a low-dimensional movement-intensity coordinate itself persists with wild individuals across sessions.

It does not show:
- that I causes vertical specialization;
- memory;
- morphology;
- fitness benefit;
- universal applicability to all bats.

The vertical-shape bridge requires a separate frozen contract after this result.
