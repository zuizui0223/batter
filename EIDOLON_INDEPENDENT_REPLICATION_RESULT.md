# Independent replication — *Eidolon helvum*

Date: 2026-09-26  
Workflow run: `36239067232`  
Frozen contract boundary: `41f93119036854d4181a073144c2e3ab1d780979`

## Why this is an independent test

The replication species, source and decision rule were selected before numeric height values were
opened. The public Movebank archive contains 18,154 GPS records from 63 animals; structural
preflight found 42 animals with at least two >=50-fix sessions while reading only height
presence/missingness, not numeric height outcomes.

The analysis was stratified within exact `study_site × year` cohorts. A target bat was therefore
compared only with other bats from the same geographic and annual context. Cross-cohort pooling
could not create the population baseline.

The native vertical coordinate is GPS `height_above_ellipsoid`; no AGL interpretation is made.

## Frozen 5-km replication result

Twenty individuals remained evaluable after the common-horizontal-support scoring rule.

- conditional identity gain: **+0.21898 nats/fix**
- marginal-height identity gain: **+0.00210**
- identity × location increment: **+0.21688**
- individuals with positive conditional gain: **17/20 = 85%**
- median individual conditional gain: **+0.1564**
- median individual identity × location increment: **+0.1339**

All five preregistered replication conditions passed:

1. at least 15 evaluable individuals: 20;
2. mean conditional identity gain > 0;
3. more than half of individuals positive: 85%;
4. mean identity × location increment > 0;
5. conditional identity gain > marginal identity gain.

Terminal replication category: **supported**.

## Cohort structure

Every cohort with at least one evaluable individual had a positive cohort-mean conditional gain:

| Site × year | Evaluable individuals | Conditional gain | Marginal gain | Identity × location |
|---|---:|---:|---:|---:|
| Burkina Faso, Ouagadougou 2013 | 2 | +0.888 | -0.034 | +0.922 |
| Burkina Faso, Ouagadougou 2014 | 5 | +0.159 | -0.018 | +0.177 |
| Ghana, Accra 2009 | 1 | +0.242 | +0.194 | +0.048 |
| Ghana, Accra 2011 | 2 | +0.105 | +0.021 | +0.084 |
| Ghana, Kibi (Old Tafo) 2013 | 2 | +0.193 | +0.041 | +0.152 |
| Zambia, Kasanka 2014 | 8 | +0.122 | -0.015 | +0.136 |

Zambia 2013 was structurally admitted but had no individual retain enough common horizontal
support for the final target score; it therefore contributes no biological sign.

## Spatial-scale checks

These were frozen sensitivities and cannot redefine the 5-km primary result.

- 2.5 km: conditional +0.2968; marginal +0.0055; identity × location +0.2913;
  14 evaluable individuals, 78.6% positive.
- 10 km: conditional +0.1734; marginal +0.0467; identity × location +0.1268;
  29 evaluable individuals, 72.4% positive.

The qualitative result therefore survives both finer and coarser horizontal aggregation in this
species.

## Cross-species interpretation

The key qualitative pattern from *Tadarida teniotis* replicated in a phylogenetically and
ecologically different bat:

- individual history predicts vertical state across nights;
- almost none of that information is an individual-wide marginal height preference in *Eidolon*;
- the information appears when height is coupled to horizontal place.

The focal *Tadarida* analysis additionally shows that this pattern persists in height above ground
and is not explained by terrain elevation alone. The *Eidolon* replication cannot make that AGL
claim because its archived native vertical axis is height above ellipsoid.

An exploratory difference is spatial grain: *Tadarida* self-transfer collapses around 10 km,
whereas *Eidolon* remains positive at 10 km. With only two species this is a hypothesis, not a
comparative conclusion: the horizontal grain of vertical specialization may itself vary among
movement ecologies.

## Claim ceiling

This replication supports **repeatable, place-specific vertical airspace organization** in a
second bat species. It does not establish foraging, personality, learning, optimality, or a
shared physiological mechanism.
