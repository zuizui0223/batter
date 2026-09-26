# batter

Ecological re-analysis of 3-D movement in the European free-tailed bat (*Tadarida teniotis*).

## Question

Does an individual bat carry a repeatable vertical-use strategy across nights, after horizontal position is already known?

The project starts from an earlier ODSP result: the population support is vertically thick
(`exp(H(Z|X,Y)) = 4.02` effective altitude states), yet a pooled location-conditioned
vertical distribution did not transfer to two held-out individuals. That result is treated as
motivation only. `batter` is a separate ecological study and does not retune or reopen the
frozen ODSP endpoint.

## Primary hypothesis

If vertical flight strategy is individualized and repeatable, then for a held-out bat-night,
the target bat's own other-night distribution `P(z | x,y, individual)` should predict vertical
state better than a population distribution learned from other individuals.

Primary endpoint:

`mean[log P_same-individual(z|x,y) - log P_other-individuals(z|x,y)]`

The sampling unit is a bat-night/session, not a 30-s GPS fix. Fixes are used to estimate
within-session distributions; inference is summarized at the individual level.

## Important semantic boundary

The raw tracking stream measures flight height, not verified foraging. Until a behavioural
classifier or independent foraging annotation is validated, this repository uses the terms
**vertical flight-use strategy** and **vertical-use strategy**, not “foraging-height strategy”.

## Data

Primary source: O'Mara et al. 2021, Current Biology, Movebank Data Repository
DOI 10.5441/001/1.52nn82r9. The exact original CSV is checksum-pinned in the study contract.

## Workflow

1. Verify the archived source byte-for-byte.
2. Exclude source-marked manual outliers for the primary analysis.
3. Segment each individual's record into tracking sessions using a frozen 4-hour gap rule.
4. Project x-y to EPSG:3035 and use the inherited 5-km grid.
5. Hold out each eligible session in turn.
6. Predict it from the same bat's other sessions and from other bats.
7. Score only x-y cells supported by both predictors.
8. Aggregate session scores to equal-weight individual summaries.
9. Treat topography/wind/AGL mechanisms as a second-stage analysis, not as a rescue if repeatability is absent.

See `STUDY_CONTRACT.md` and `contract/individual_vertical_strategy_v1.json`.


## Current ecological result

The first study version now supports a more specific interpretation than the original ODSP
motivation.

On the matched annotated dataset, at 5-km horizontal conditioning:

- MSL conditional self-transfer = **+0.428 nats/fix** (5/6 evaluable bats positive)
- AGL conditional self-transfer = **+0.337** (4/6 positive)
- terrain-elevation self-transfer = **+0.007**

The signal is primarily place-specific rather than a stable population-wide height preference:

- MSL identity × location increment = **+0.376**
- AGL identity × location increment = **+0.591**
- AGL marginal identity gain = **-0.255**

At 2.5 km the conditional gains rise to +0.866 (MSL) and +0.766 (AGL); at 10 km the AGL
mean falls to -0.045. Individual specialization is therefore strongest at fine horizontal scales.

The current biological statement is:

> **European free-tailed bats show repeatable individual fine-scale organization of vertical
> airspace use. Individual identity is carried mainly by place × vertical-state coupling,
> persists when altitude is expressed relative to terrain, and is not explained by
> microtopographic route fidelity alone.**

A separately frozen cross-night uplift reaction-norm test did not establish one shared mechanism,
so the cause of these individual 3-D routes remains open.

See `MANUSCRIPT_SPINE.md`, `THREE_COMPONENT_RESULT.md`,
`AGL_SELF_TRANSFER_RESULT.md`, and `UPLIFT_REACTION_NORM_RESULT.md`.
