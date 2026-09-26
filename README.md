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

The original *Tadarida teniotis* signal is now independently replicated.

### Focal *Tadarida teniotis*

At 5-km horizontal conditioning:

- MSL conditional self-transfer = **+0.428 nats/fix** (5/6 evaluable bats positive)
- AGL conditional self-transfer = **+0.337** (4/6 positive)
- terrain-elevation self-transfer = **+0.007**
- MSL identity × location = **+0.376**
- AGL identity × location = **+0.591**

The signal therefore lies mainly in place-specific vertical organization rather than a stable
preferred height or repeated microtopographic elevation.

### Independent *Eidolon helvum*

The source and pass rule were frozen before numeric height was opened. Within exact site × year
cohorts, the 5-km replication returned:

- **20 evaluable individuals**
- conditional identity gain = **+0.219 nats/fix**
- **17/20 (85%)** individual means positive
- marginal-height identity = **+0.002**
- identity × location = **+0.217**
- all five frozen replication criteria passed

Thus a second bat species independently reproduces the key conditional-over-marginal result.

The current biological statement is:

> **Individual bats carry repeatable, place-specific vertical signatures across nights. Identity
> is expressed mainly through coupling between horizontal place and vertical state, not through
> one individual-wide preferred flight altitude.**

See `MANUSCRIPT_SPINE.md`, `CROSS_SPECIES_SYNTHESIS.md`,
`EIDOLON_INDEPENDENT_REPLICATION_RESULT.md`, `THREE_COMPONENT_RESULT.md`,
`AGL_SELF_TRANSFER_RESULT.md`, and `UPLIFT_REACTION_NORM_RESULT.md`.

## Same-night context control

A post-primary control compared each target session against two sources of information: the same
bat on another night versus other bats tracked on the target calendar night. At 5 km, the
cross-night self predictor still won for most evaluable bats:

- AGL: +0.484 nats/fix, 4/5 individuals positive;
- MSL: +0.436 nats/fix, 4/5 individuals positive.

Thus the fine-scale vertical signature is not well explained by a shared calendar-night state
alone. See `NIGHT_CONTEXT_CONTROL_RESULT.md`.

## Independent replication

Completed successfully in *Eidolon helvum*. Candidate selection, source identity, structural
eligibility, site-year cohorting, 5-km primary scale and the five-part pass rule were frozen before
numeric height outcomes were opened. The resulting 20-individual panel passed every criterion.
The 2.5-km and 10-km frozen sensitivities also retained positive conditional and
identity × location gains.
