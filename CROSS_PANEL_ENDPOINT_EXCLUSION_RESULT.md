# Cross-panel endpoint-exclusion result v1

Contract frozen before output:
`contract/cross_panel_endpoint_exclusion_v1.json`
(blob `84998d2e6daf4f60054be2fc6ba96118396164c8`).

Primary result run: **36317089590**.  
Independent zero-radius reconstruction QA: **36319042915**.

## Baseline reconstruction

The QA reproduced the pre-exclusion common-cell score exactly to the frozen 1e-12 tolerance in
all five comparative panels:

| panel | frozen | zero-radius reconstruction |
|---|---:|---:|
| *Eidolon* | 0.1767955693 | 0.1767955693 |
| *Hypsignathus* | 0.0222375678 | 0.0222375678 |
| *P. hastatus* 2022 | 0.0491545713 | 0.0491545713 |
| *P. hastatus* 2023 | 0.0325173954 | 0.0325173954 |
| *P. hastatus* 2016 | -0.0039104748 | -0.0039104748 |

## Frozen 1-km primary endpoint

| panel | n | frozen min n | observed | null mean | calibrated excess | p upper | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| *Eidolon helvum* | 11 | 15 | 0.2500 | -0.1400 | +0.3900 | 0.0002 | **FAIL — n gate** |
| *Hypsignathus monstrosus* | 19 | 15 | 0.1909 | -0.1174 | +0.3082 | 0.0002 | **PASS** |
| *P. hastatus* 2022 | 30 | 15 | 0.0552 | -0.1640 | +0.2192 | 0.0002 | **PASS** |
| *P. hastatus* 2023 | 12 | 10 | 0.0930 | -0.0594 | +0.1524 | 0.0002 | **PASS** |
| *P. hastatus* 2016 | 10 | 6 | 0.0908 | -0.2670 | +0.3578 | 0.0002 | **PASS** |

Thus **4/5 comparative panels pass** the predeclared 1-km rule.

The *Eidolon* failure is not a disappearance of the calibrated signal. Its observed-minus-null
difference is +0.390 with p=0.0002, but endpoint exclusion reduces the evaluable set to 11
individuals, below the frozen minimum of 15. The fixed 500-m and 2-km sensitivities remain strongly
above their nulls (p=0.0005 at both radii) but are descriptive and cannot rescue the failed n gate.

## Relation to focal *Tadarida*

The prior frozen focal 1-km endpoint exclusion remains **FAIL** (p=0.1109). It is not overwritten.

Therefore the endpoint audit rejects a simple claim that endpoint-associated structure explains
the comparative result in general: four comparative panels retain the signal under the same
predeclared exclusion, and *Eidolon* retains a strong calibrated difference but loses the required
sample size.

It does **not** establish universal independence from central-place structure. The manuscript must
retain *Tadarida* as a failure, report the *Eidolon* attrition failure, and avoid interpreting the
x-y-only endpoint proxy as a verified roost, colony, lek, or causal mechanism.

The appropriate ecological statement is that repeatable vertical/3-D airspace identity is not
generally removed by coarse endpoint-neighbourhood exclusion, while central-place-associated
movement remains a plausible, panel-dependent contributor.
