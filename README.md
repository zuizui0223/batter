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
