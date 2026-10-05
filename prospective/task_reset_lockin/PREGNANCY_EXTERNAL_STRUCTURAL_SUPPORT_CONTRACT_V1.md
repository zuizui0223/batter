# Pregnancy external call-sampled 3-D structural support contract v1

## Status

**OUTCOME-BLIND STRUCTURAL PREFLIGHT.**

This contract is frozen after:
- pregnancy representative workbook headers established source fields
  `Call no., Time, x, y, z, ... Speed`;
- Teshima `pulse` semantics were established as a binary event indicator;
- no pregnancy row 2+ value has been opened by this programme.

## External source

Mendeley dataset:
`10.17632/hbb2t3dnbc.1`

Source-defined groups:
- Bat 1–5: pregnant females;
- Bat 6–10: post-lactating females.

Each `Bat N.xlsx` is treated as one biological individual.

## Measurement harmonization

The external validation will not compare continuous Teshima trajectories to call-sampled pregnancy coordinates directly.

Instead, a later frozen estimator will:

1. subset Teshima *R. nippon* trajectories to rows with `pulse != 0`;
2. compute movement summaries from those call/pulse-sampled 3-D points;
3. compute the same summaries from pregnancy workbook rows `Time,x,y,z`.

Thus both cohorts are observed at echolocation-event times.

The transparent policy formulas remain fixed:
- FlightIntensity;
- ManeuveringExtent.

Only the observation process changes.

## Authorized structural opening now

For all ten pregnancy workbooks:

- verify file name/size/SHA256;
- open workbook sheet list;
- for every sheet report:
  - sheet name;
  - used-dimension reference only;
  - number of rows implied by the dimension;
  - whether row-1 headers contain the exact structural set
    `Call no., Time, x, y, z`.

Do not read row 2+ values.

## Candidate flight/session unit

At this stage, a workbook sheet is only a **source-defined repeated session table**.

Do not yet call it:
- a flight;
- a day;
- a trial

unless source documentation establishes that meaning.

The external identity test may use sheet as the repeated observational unit if:
- each sheet contains one internally ordered call-sampled 3-D sequence;
- support is adequate across individuals.

## Frozen structural support floor

A sheet is structurally candidate-usable if:
- exact Time/x/y/z header set is present;
- dimension implies >=21 data rows after the header.

The threshold 21 is fixed before data rows are opened because the later call-sampled estimator will require:
- >=20 finite 3-D call points;
- >=10 finite positive-time turning observations.

An individual is structurally candidate-eligible if it has >=5 candidate-usable sheets.

External programme proceeds only if:
- >=4 pregnant bats are candidate-eligible;
- >=4 post-lactating bats are candidate-eligible.

## Group blocking

Because reproductive condition shifts movement phenotype and individuals are nested within condition, any later individual-identity randomization must preserve:

`pregnant / post-lactating`

group membership.

No permutation of identity across reproductive groups.

## No outcome opening

Do not calculate:
- speed;
- vertical speed;
- turning;
- path efficiency;
- vertical range;
- FlightIntensity;
- ManeuveringExtent;
- individual repeatability;
- pregnancy effects.

## Adaptive-learning public dataset disposition

The adaptive-learning Mendeley files opened so far expose:
- IPI;
- Distance;
- Duration;
- acoustic-call tables.

They do not expose source X/Y/Z movement trajectories.

Therefore that dataset is **not** part of the fixed 3-D external policy validation.
