# Independent call-sampled two-axis policy validation contract v1

## Status

**PROSPECTIVE EXTERNAL VALIDATION OF A FIXED TWO-AXIS BEHAVIOURAL REPRESENTATION.**

This contract is frozen after:
- the source-cohort call-sampled observation-process bridge passed;
- the independent public 3-D structural gate passed with 4 pregnant and 5 post-lactating individuals;
- no row-2+ movement value from the independent cohort has been opened by this programme.

## Independent source

Public Mendeley dataset:
- id: `hbb2t3dnbc`
- version: 1
- DOI: `10.17632/hbb2t3dnbc.1`

Independent species:
*Kuhl's pipistrelle* (`Pipistrellus kuhlii`).

The source experiment recorded repeated search/landing sequences in a 3-D flight room. The public workbooks expose repeated sheets with exact columns:
- `Call no.`
- `Time`
- `x`
- `y`
- `z`

The representation is evaluated at echolocation-call sampling times, matching the passed source-cohort bridge.

## Frozen biological units

Eligible independent individuals are fixed from the structural audit:

Pregnant:
- Bat 1
- Bat 2
- Bat 3
- Bat 5

Post-lactating:
- Bat 6
- Bat 7
- Bat 8
- Bat 9
- Bat 10

Bat 4 remains excluded under the fail-closed integrity audit.

No later result may re-admit Bat 4.

## Reproductive-condition block

Pregnant and post-lactating bats differ in movement phenotype in the source experiment.

Therefore:
- all standardization is performed separately within reproductive condition;
- donor comparisons are only within reproductive condition;
- label permutations are only within reproductive condition;
- no identity is inferred from the group difference.

The external validation does **not** test a pregnancy effect.

## Repeated observational unit

Every workbook sheet that:
- has the exact required Time/x/y/z schema;
- passes the frozen numeric support below

is treated as one source-defined repeated call-sampled 3-D sequence.

The analysis calls this a `sequence`, not a flight/day/trial, because the public workbook sheet semantics are not redefined here.

Exclude non-trajectory sheets such as `curvature`.

## Numeric sequence cleaning

For each candidate sheet:

1. read only Time, x, y, z from rows 2+;
2. retain rows with all four values finite;
3. stable-sort by Time ascending;
4. retain the first duplicate Time;
5. require >=20 retained 3-D points;
6. require positive total duration and 3-D path length;
7. require >=19 positive-Time speed intervals;
8. require >=10 finite horizontal turning-rate observations.

An individual remains externally evaluable only if >=5 valid sequences remain after numeric cleaning.

The external test opens only if:
- all four fixed pregnant bats remain evaluable;
- >=4 of the five fixed post-lactating bats remain evaluable.

No threshold relaxation.

## Frozen eight movement features

Compute exactly the same call-sampled features as in the passed bridge:

1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turning rate;
6. p90 absolute horizontal turning rate;
7. 3-D path efficiency = endpoint displacement / total path length;
8. vertical range.

Turning rate uses wrapped horizontal-heading difference divided by segment-midtime spacing.

No feature replacement and no feature dropping.

## External group standardization

Within each reproductive-condition block and each of the eight features:

- calculate mean and sample SD across all valid sequence feature vectors in that block;
- subtract the block mean;
- divide by the block SD.

All eight block SDs must be finite and positive.

This gives a **relative policy phenotype within condition** and removes the known group-wide reproductive-state shift.

The fixed axes are not refit.

## Frozen transparent axes

For every standardized sequence:

`I = mean(z1,z2,z3,z4)`

`M = mean(-z1,z5,z6,z7,z8)`

where:
- I = FlightIntensity;
- M = ManeuveringExtent.

No weights are fitted from this external cohort.

## E1 — fixed 2-D individual identity

For target sequence q from individual i:

- self centroid = equal-sequence mean of all other valid sequences from i;
- donor centroid = equal-sequence mean for each other individual in the same reproductive-condition block;
- self distance = Euclidean distance from q to own centroid in (I,M);
- donor distance = mean Euclidean distance from q to donor centroids, donors weighted equally;
- `K_q = D_other - D_self`.

Aggregate:
1. equal target sequence within individual;
2. equal individuals within reproductive block;
3. equal pregnant/post-lactating block means for the overall statistic.

Thus prolific individuals and the larger five-bat block do not dominate the programme statistic.

## E2 — component diagnostics

Report the same external identity statistic separately for:
- I only;
- M only.

These are descriptive components and do not rescue E1.

## E3 — block-specific direction

Report pregnant and post-lactating mean K separately.

External support requires both block means > 0.

## Null

Within each reproductive-condition block independently:

- shuffle the exact observed individual-label multiset across complete valid sequences;
- preserve the observed number of sequences assigned to every individual label;
- preserve every feature vector;
- do not move labels across reproductive condition.

Recompute the entire E1 statistic.

Permutations:
**9,999**

Seed:
`202610051121`.

One-sided p:
`(1 + #null >= observed)/(1+n_valid)`.

Require >=9,500 valid permutations.

## External support rule

Call the external fixed-axis representation supported only if all are true:

- overall K > 0;
- one-sided p <= 0.05;
- >=70% of evaluable individuals have positive individual mean K;
- pregnant block mean K > 0;
- post-lactating block mean K > 0.

No rescue by:
- refitting PCA;
- changing I or M weights;
- dropping one reproductive group;
- selecting individuals after outcome opening;
- changing sequence support thresholds;
- using acoustic variables.

## Interpretation

If supported:

> the same predeclared two-axis movement-policy representation reveals persistent individual organization in an independent species, cohort and 3-D tracking experiment.

This supports **generality of the representation**, not equality of the numerical individual parameters across species.

If unsupported:

> the two-axis law remains internally strong in the source *Rhinolophus* cohort but does not externally transfer to this independent call-sampled 3-D system.

## Claim ceiling

Even external support does not identify whether individual coordinates arise from:
- morphology;
- physiology;
- development;
- learning;
- long-term sensorimotor habit.

It also does not establish a universal two-axis law across bats.
