# Forecast audit crosswalk — distinct estimands, not independent replications

## Status
Documentation-only synthesis recorded before this branch's first successful numerical execution. The public *Rhinolophus* source has already been inspected in earlier programmes, so **none of these related branches supplies an independent biological replication**. No original analysis or submission is reclassified.

## Comparison of already-frozen or running designs

| Endpoint | Target bat used to define held-out reference? | Any target-configuration observations used for prediction/reference? | Reference SD | Source support | What can be claimed if it passes? |
|---|---|---|---|---|---|
| 2026-10-08 original theta correspondence | **Yes** | Yes, all bat trials | within-target configuration, includes focal | 25 bat×config cells | Retrospective correspondence under complete-configuration standardization |
| `post-freeze/target-blind-forecast-audit-v1` primary | No | **No** | pooled configurations other than target | fixed 25 cells | History has absolute predictive value in an entirely unseen configuration under training reference |
| `post-freeze/target-blind-forecast-audit-v1` secondary | No | **Yes, peer bats only** | pooled configurations other than target | fixed 25 cells | Conditional relative identity transfer, given contemporaneous peer reference |
| **This branch** `diagnostic/rhino-peer-only-standardization-v1` | No | **Yes, peer bats only** | *other bats in target configuration*, excluding focal | >=3 bats/config, matched-support inclusive comparison; expected <=25 | Sensitivity of conditional reference-assisted transfer to removing all target-bat contributions from reference mean **and SD** |

The two peer-only experiments intentionally differ in the variance reference: training-only global SD versus target-configuration peer-only SD. A different result is **not** independent corroboration or automatic evidence of a biological change.

## Evaluation order
1. First verify the original 25-cell source reconstruction and any structural gate.
2. Prioritize the target-configuration-blind primary for a genuine no-peer deployment/forecasting claim.
3. Interpret this branch only as a target-self-exclusion sensitivity on structurally matched reference-assisted targets.
4. Interpret the `post-freeze/rhino-rank-two-forward-test-v1` nested rank-1/rank-2 forecast on its own, because its original standardization is also transductive; rank-two discriminability, rank-two quantitative prediction, and cold-start forecasting are distinct.
5. Treat all outputs as post-outcome diagnostics; **do not combine p-values or count as multiple independent species replications**.

## Scenarios
- Target-blind and peer-conditioned positive: evidence in these five observed bats for both cold-start scalar transfer and peer-normalized portability, not a unique flight law.
- Target-blind negative but peer-conditioned positive: relative organization may transfer while predicting an absolute new-configuration state remains unresolved.
- Both negative: prior within-configuration identity may remain valid, but not the stronger operational forecast reading.
- Peer-conditioned calibrations disagree: retain and report both; investigate dependency on reference precision and support (especially the two-bat configuration), not post-hoc select a favourable p-value.

## Critical source boundary
There are only five biological *Rhinolophus* individuals. Any within-archive label-exchangeability p-value and a five-cluster population uncertainty statement have different estimands. Do not promote a significant permutation alongside a bat-bootstrap CI spanning zero into a population-level generalization.
