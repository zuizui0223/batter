# Source C schema preflight contract v1

## Status

**OUTCOME-BLIND STRUCTURAL PREFLIGHT.**

No Source C GPS coordinate value, route similarity, self-history advantage, treatment effect on self-history, or treatment × experience statistic may be calculated during this preflight.

## Source

Mendeley Data:
`10.17632/wh7c636y3t.1`

## Required objects

Before opening the novel personal-history endpoint, determine whether public source files reproducibly expose:

1. bat identity;
2. early-life environmental condition: enriched / impoverished;
3. experimental season;
4. source colony/origin where available;
5. sex and age where available;
6. release / outdoor chronology;
7. nightly or trip-level identity;
8. GPS timestamp;
9. x-y or longitude-latitude coordinates;
10. enough tracking to construct repeated strictly prior self-history.

## Metadata/file-list stage

First open only:
- dataset metadata;
- folder/file names;
- file IDs;
- file sizes;
- hashes/content types where available.

Do not download data files until an explicit file-opening allowlist is frozen.

## Structural minimum for the planned treatment test

Before any self-history treatment outcome opens, the final structurally eligible set must contain:

- at least **12 bats total**;
- at least **5 enriched** and **5 impoverished** bats;
- at least **2 experimental seasons or an explicit reason the public GPS source contains only one season**;
- each primary bat must contain at least **20 structurally valid GPS foraging nights** under the estimator to be frozen before coordinates open.

If the public archive cannot meet these floors:
STOP the treatment/self-history primary. Do not lower them.

## Treatment provenance gate

Before the novel movement endpoint opens, recover from source metadata/code if possible:

- exact mapping Bat_ID -> enriched/impoverished;
- season;
- origin/source colony;
- any known exclusions from GPS analysis;
- allocation/balancing procedure.

If treatment labels are unavailable for GPS individuals:
STOP.

Do not infer treatment from published movement outcomes or maps.

## Allocation-aware calibration requirement

The final treatment-label null must respect the source design.

Before treatment/self-history outcome:
- determine which blocking variables were used or should be preserved from the source allocation (at minimum season; origin if identifiable and sufficiently replicated);
- freeze the permutation/blocking rule.

Do not choose the blocking structure after seeing self-history outcomes.

## No-outcome list

During preflight do not compute:
- own-history versus other-history distance;
- route overlap;
- home range;
- exploration area;
- maximum distance;
- self-history B or L;
- enriched versus impoverished route statistics.

Published paper results may be used only as source provenance.

## Pass output

Report:
- exact public files relevant to treatment/GPS;
- treatment-label availability;
- GPS individual counts by treatment and season;
- coordinate/time field semantics;
- whether the planned support floors can be evaluated outcome-blindly;
- PASS/STOP.

## JAE / Source B firewall

No result changes JAE v0.4.0 or Source B's frozen verdicts.
