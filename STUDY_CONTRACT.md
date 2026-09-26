# Study contract v1 — individual vertical-use strategies

## Ecological claim

Population-level vertical heterogeneity can arise because individuals use different, repeatable
rules for moving through the vertical dimension. The critical prediction is **within-individual
repeatability across nights**, not merely between-individual heterogeneity.

## Competing explanations

A failed population-to-individual transfer result is compatible with at least four processes:

1. repeatable individual specialization;
2. night-specific wind or uplift conditions;
3. flexible within-individual behaviour;
4. unequal horizontal/topographic support among tracked animals.

This study discriminates (1) from the others by asking whether a bat predicts itself on another
night better than other bats predict it.

## H1 — repeatable individuality

For an eligible held-out session, define:

- `P_self(z|x,y)`: equal-session average of the same bat's other sessions;
- `P_population(z|x,y)`: equal-individual average from all other bats;
- `G = mean(log P_self - log P_population)` over target fixes in mutually supported cells.

Prediction: individual mean `G` is positive for repeat-tracked bats if individualized vertical
strategy is repeatable.

## H2 — ecological mechanism (prospective second stage)

If H1 has support, test whether individual differences are explained by different responses to
the nocturnal energy landscape rather than only different intercept heights. Candidate predictors
are terrain-relative height, topographic exposure, wind and modeled orographic uplift, with
individual random slopes.

H2 is not authorized to alter the H1 endpoint.

## Frozen primary choices

- taxon: *Tadarida teniotis*
- source: Movebank Data Repository DOI 10.5441/001/1.52nn82r9
- source file MD5: `570872ab7aba674b9bdc2f2ee6044a71`
- source-marked manual outliers: excluded in primary analysis
- vertical field: native GPS `height_above_msl`
- horizontal CRS: EPSG:3035
- cell size: 5 km
- altitude bins: (-inf,0), [0,50), [50,100), [100,200), [200,400), [400,800),
  [800,1600), [1600,3200), [3200,inf)
- session break: gap > 4 h within an individual
- minimum raw fixes per session: 50
- Jeffreys smoothing: 0.5 per altitude bin
- minimum scored fixes per held-out session: 50
- each session receives equal weight within a bat; each bat receives equal weight in population summaries

## Claim boundary

A positive result supports repeatable individuality in **vertical flight use under this tracking
design**. It does not by itself establish learned strategy, optimality, foraging behaviour,
causation by wind/topography, or long-term personality.

A non-positive result is informative: it favors flexible/context-dependent vertical use over a
stable individual-strategy explanation at this temporal scale.

## Relation to ODSP

The frozen ODSP analysis remains untouched. Its 4.02 effective-state thickness and failed
cross-individual transfer are historical motivation. `batter` asks a different biological
question with a different validation target: self-transfer across nights.
