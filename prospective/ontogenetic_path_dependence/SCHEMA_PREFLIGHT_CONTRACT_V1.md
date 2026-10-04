# Ontogenetic route-formation schema preflight contract v1

## Status

**OUTCOME-BLIND STRUCTURAL PREFLIGHT.**

No route similarity, trajectory overlap, route entropy, corridor width, self-history advantage, maternal-history advantage, or ontogenetic slope may be calculated during this preflight.

## Sources

Primary:
- Goldshtein et al. 2022 dataset: `10.17632/gpcg9m5758.1`

Independent corroboration:
- Harten et al. 2020 dataset: `10.17632/n9d8gbz3xr.1`

The two sources are adjudicated separately.

## Required schema objects

### Source A — Goldshtein maternal-learning dataset

The preflight must determine whether the public files reproducibly expose:

1. pup identity;
2. mother identity;
3. mother-pup pairing;
4. timestamped movement coordinates;
5. independent versus maternally transported movement status, or an equivalent source-coded boundary;
6. independent trip/flight identity, or enough timing information to construct it without inspecting route geometry;
7. destination / tree / landing-site identity when available;
8. chronological order of independent trips.

### Source B — Harten first-flight dataset

The preflight must determine whether the public files reproducibly expose:

1. juvenile identity;
2. timestamped movement coordinates;
3. a source-defined first outdoor / first independent flight boundary;
4. trip/flight identity, or enough timing information to construct it without route-shape inspection;
5. chronological trip index;
6. destination information when available.

## Coordinate gate

Before any geometry is opened:
- identify CRS / longitude-latitude semantics from source metadata or source code;
- identify units;
- identify whether coordinates are raw, projected, filtered, smoothed, or interpolated;
- choose only a source-documented transformation to a metric coordinate system.

If coordinate semantics cannot be reproduced, STOP that source.

## Chronology gate

The formation programme requires strict causal ordering.

For any target trip t:
- a self-history predictor may use only trips completed before t;
- a maternal predictor may use only maternal/pup-carried exposure that occurred before the pup's first independent trip, unless the source explicitly supports a different predeclared exposure window;
- no future trip may leak into a predictor.

If the independence boundary cannot be established without looking at route outcomes, STOP the Source A crossover endpoint.

## Outcome-blind support counts

### Source A primary eligibility

A pup is structurally eligible only if all of the following can be counted without comparing route geometry:

- valid mother-pup identity;
- at least one usable pre-independence maternal-transport route/exposure relevant to an independently revisited destination or route domain;
- at least **4 independent target trips** after independence with valid coordinates;
- at least **2 earlier independent trips** available before at least one later target trip, so a self-history predictor is genuinely historical;
- at least **2 target trips in an early phase** and **2 in a later phase**, where phases are defined by chronological independent-trip order, not route outcome.

Primary Source A opens only if **>=5 independent pups** satisfy these conditions.

If fewer than 5 pass: STOP the maternal-to-self crossover primary. Do not lower the individual floor or pool Source B as rescue.

### Source B corroboration eligibility

A juvenile is structurally eligible only if:
- source-defined first-flight chronology is recoverable;
- at least **6 independent trips** have valid coordinates;
- at least **3 target trips** have >=2 strictly prior self-history trips.

Source B opens only if **>=5 independent juveniles** pass.

If fewer than 5 pass: STOP Source B without relaxing thresholds.

## Destination matching gate

Route formation must not be confounded with destination switching.

During schema/support preflight, determine whether exact destination / landing-site identity is available.

Preferred primary geometry is **destination-matched**:
- compare route histories only for trips terminating at the same destination or same source-defined destination class.

If exact destination identity is unavailable, the primary route-shape test does not automatically switch to all-trip geometry. Instead:
- document the limitation;
- use target-centred or destination-standardized geometry only if its construction can be frozen before route outcomes;
- otherwise STOP the route-shape endpoint and retain only non-route formation quantities explicitly authorized in a later contract.

## No-outcome list

The preflight must not calculate or inspect:
- Fréchet distance;
- DTW;
- Hausdorff distance;
- route KDE overlap;
- waypoint overlap;
- self-versus-mother similarity;
- self-versus-other similarity;
- early-versus-late route stereotypy;
- trip entropy;
- corridor width;
- route novelty;
- endpoint-specific route figures.

Published-paper statements may be read as source provenance, but the public raw outcome used by this programme stays unopened until the structural gate is frozen and passed.

## Pass outputs

The preflight report must return:
- exact dataset version and file identities;
- schema map;
- individual counts;
- mother-pup pair count;
- independent-trip count by individual;
- availability of destination identity;
- coordinate semantics;
- PASS/STOP separately for Source A and Source B.

No biological direction or effect size may appear in the preflight report.
