# Rhinolophus coordinate-support opening v1

## Status

**STRUCTURAL NUMERIC SUPPORT GATE — frozen before any individual-identity outcome is calculated.**

Authorized by:
`STRUCTURAL_SUPPORT_ADJUDICATION_V2.md`.

## Authorized data

Only the 45 CSV files assigned prospectively to:
*Rhinolophus nippon*.

Read only:
- Time (Seconds)
- X
- Y
- Z

Do not use or summarize:
- pulse.

Do not open:
- any Miniopterus numeric CSV value;
- kiku.pkl/yubi.pkl numeric payloads.

## Allowed calculations

Per trajectory only:
- finite-value count;
- duplicate-time removal count;
- positive duration;
- 3-D path length;
- positive-dt interval count;
- the eight already-frozen Primary-B raw features;
- validity booleans under the frozen Primary-A and Primary-B trajectory criteria.

Across trajectories, only structural support calculations are allowed:
- valid trajectory count by environment × bat;
- usable Primary-B environment count;
- sample SD of each frozen feature within environment solely to implement the predeclared zero/nonfinite-SD feature gate;
- retained feature names;
- candidate bat/environment support;
- target/donor support counts.

## Forbidden

Do not calculate:
- pairwise route distance;
- D_self;
- D_other;
- A_q or A_species;
- K_q or K_species;
- identity classification;
- permutation nulls;
- same-bat versus other-bat route contrasts.

## Gate

Primary A opens only if full coordinate-valid support still yields >=2 eligible environments with >=3 repeated target bats each.

Primary B opens only if:
- >=6 frozen features survive the SD gate;
- >=3 candidate bats remain with >=3 usable environments;
- at least one target trajectory is supported for every candidate bat;
- every included target has own history from >=2 other environments and >=2 other-bat donor centroids.

No rescue or threshold relaxation.
