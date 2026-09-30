# Nyctalus eligibility robustness result v1

## Status

**POST-OUTCOME SENSITIVITY DIAGNOSTIC.** This analysis cannot restore prospective status to the revised eligibility analysis and is not a rescue test.

Frozen diagnostic contract:
`post_freeze_extensions/nyctalus_eligibility_robustness/contract_v1.json`

Authoritative workflow:
- run: `36694266681`
- head: `35c2594cb2614a039f648796979b502fcfcb31d3`
- artifact: `11087271548`
- artifact digest: `sha256:df290350fecba26af25ac456ac6bb8cbf49fc88ce44dc8f5874e3b7dd77a4b00`

Only the minimum presence-qualified fixes per source track was varied. The 5-km grid,
session-median centering, vertical bins, >=50 scored common-support target events,
common-cell weighting, whole-track permutation unit, B=9,999 and seed=2026093001
were fixed.

## Result

| minimum fixes / track | evaluable n | observed identity | null mean | calibrated excess | null SD | p(null >= observed) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 36 | +0.00527 | -0.08074 | **+0.08600** | 0.04444 | 0.0115 |
| 20 | 36 | -0.00776 | -0.07198 | **+0.06423** | 0.03965 | 0.0370 |
| 30 | 34 | -0.00286 | -0.07063 | **+0.06777** | 0.04094 | 0.0323 |
| 40 | 31 | -0.00880 | -0.06908 | **+0.06028** | 0.04297 | 0.0676 |
| 50 | 27 | -0.01871 | -0.07045 | **+0.05175** | 0.04534 | 0.1224 |
| 75 | 16 | -0.01886 | -0.05276 | **+0.03390** | 0.05424 | 0.2649 |
| 100 | 5 | +0.03197 | -0.02889 | **+0.06086** | 0.07410 | 0.1559 |

The two already-opened endpoint analyses are reproduced by one code path:
- threshold 0 reproduces n=36, excess +0.08600498, p=0.0115 exactly;
- threshold 50 reproduces n=27, excess +0.05174737, p=0.1224 (difference from rounded archived excess <4e-7).

## Frozen synthesis

- calibrated excess is positive at **7/7** thresholds;
- range: **+0.03390 to +0.08600**;
- median: **+0.06086**;
- evaluable n falls from 36 to 5 as the session threshold becomes stricter.

Therefore the external Nyctalus signal is **directionally robust to the session-length eligibility rule**. The revised n=36 result is not an isolated sign reversal or a single-threshold positive effect.

The p-value, however, changes substantially as sample size/support is removed. That is expected to affect precision and is not used to select a preferred threshold.

## Claim boundary

The original >=50-fix analysis remains the prospective primary external validation and retains its frozen FAIL verdict (p=0.1224).

The sensitivity curve supports a narrower additional statement:

> Across a pre-frozen range of session-length eligibility thresholds, the Nyctalus calibrated centered-identity effect remains positive, providing convergent directional evidence that is not dependent on one relaxed eligibility cutoff.

It does **not** justify calling the n=36 result a prospective primary replication.
