# Nyctalus independent external validation v1

## Status

**FULLY PROSPECTIVE EXTERNAL VALIDATION.** The source, source SHA, cohort definition, exact structural n, estimator, vertical bins, permutation counts/seeds, pass rules and interpretation matrix were frozen before numeric `Height` values were opened.

Source:
- *Nyctalus noctula*
- Zenodo DOI `10.5281/zenodo.7535030`
- raw file `Observed_GPS_locations.csv`
- SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

Authoritative validation workflow:
- run: `36668803219`
- head: `6371c42acf01ae9aa87c639047881fcae9e53001`
- aggregate artifact: `11077433129`
- digest: `sha256:16bd0f7455a54f59fcb2aff82e88fd784f9c9689d5f82313a0788456357dd639`

## Prospective primary replication

**5-km centered individual vertical organization: PASS**

- exact evaluable individuals: **36 / frozen 36**
- observed common-stratum identity: **+0.00527 nats/fix**
- permutation-null mean: **−0.08074**
- calibrated excess: **+0.08600**
- one-sided p(null >= observed): **0.0115**

Interpretation: the central rule independently replicates in a new species, study, repository and tracking programme: after track-median centering and identical coarse-horizontal weighting, same-individual history contains more held-out information about the full vertical distribution than expected under whole-track identity exchangeability.

## Prospective mechanism replication

**5-km × source HMM movement state (ARM/COM): FAIL**

- exact evaluable individuals: **27 / frozen 27**
- observed common-stratum identity: **+0.02401 nats/fix**
- permutation-null mean: **−0.02673**
- calibrated excess: **+0.05074**
- one-sided p(null >= observed): **0.0707**

The effect is directionally positive, but it does not satisfy the frozen p<=0.05 rule.

Interpretation: the independent source confirms centered vertical individuality, but does **not** establish that the identity signal persists after conditioning on the source study's independently classified commuting/area-restricted movement states. Behavioural-state mixture remains a plausible contributor in this external system.

## Structurally stopped families

No vertical outcomes were opened for:
- 500-m × source movement state (preflight n=10, required 19);
- >=1-day × source movement state (preflight n=7, required 19).

No alternate grid, state definition, lag, sex/age subgroup or rescue endpoint is opened.

## Prospective synthesis

**primary_PASS_state_FAIL**

> Independent centered individuality replicates, but the external source does not establish persistence within source movement states; behavioural-state mixture remains a plausible contributor.

## Claim boundary

This result materially strengthens the generality of repeatable centered vertical organization across bats. It does not show that the stronger post-freeze within-state mechanism is universal, and it does not prove morphology, memory, learning, personality or a particular resource mechanism.
