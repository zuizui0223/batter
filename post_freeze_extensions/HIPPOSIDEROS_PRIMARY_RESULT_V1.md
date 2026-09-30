# Hipposideros prospective external validation v1

## Status

**GENUINELY RESPONSE-UNOPENED EXTERNAL PRIMARY — FAIL.**

Numeric AGL `height` was opened only after the outcome-blind structural receipt had been generated and committed.

Authoritative preflight:
- workflow: `36717598652`
- preflight head: `f1bed47595606bbe73900382cf613de1e7b98bcc`
- receipt commit created by workflow: `75bbbf1`
- raw SHA256: `263f2a6a9416939d4b61008b91077997d1f592be0ba5d1c23355a225f2c073c7`
- numeric height values read before receipt: **false**

Authoritative primary validation:
- workflow: `36717769795`
- head: `8d214866163a568078607ee05a3eccb29bc85e38`
- artifact: `11096159784`
- artifact digest: `sha256:269b56f7ee121fd5bb907f48846726e58bb9ad6f197d6f6a4a2711e6cdfbf3f5`

## Outcome-blind structure frozen before Height

Raw GPS IDs:
- D-prefix: 11
- H-prefix: 8

The original prefix-count mapping rule failed because 11/8 did not match the paper's 9/8 tracked sample.

Before Height was opened, the already-frozen >=50-fix session rule was then applied as an outcome-blind provenance filter:
- D21: zero >=50-fix nights
- D22: zero >=50-fix nights
- all other D IDs: at least one >=50-fix night
- all H IDs: at least one >=50-fix night

This yielded exactly 17 source-effective IDs:
- D-prefix: 9 -> *Hipposideros armiger*
- H-prefix: 8 -> *Hipposideros pratti*

The full primary preflight then required:
- >=2 qualifying >=50-fix nights;
- fixed EPSG:32648 5-km cells;
- >=50 common-support target events;
- >=3 estimator-evaluable individuals for a species panel;
- >=5 estimator-evaluable individuals source-wide.

Preflight result:
- repeat IDs: *H. armiger* 9, *H. pratti* 7
- estimator-evaluable IDs: *H. armiger* **8**, *H. pratti* **5**
- source total: **13**
- both species panels PASS structural eligibility
- Height-opening receipt: **HEIGHT_MAY_OPEN**

## Frozen primary result

Primary source-level statistic:
- eligible species panels: **2**
- evaluable individuals: **8 *H. armiger* + 5 *H. pratti***
- observed centered identity: **-0.07574594**
- permutation-null mean: **-0.03106233**
- null SD: **0.04189362**
- calibrated excess: **-0.04468361**
- null-standardized deviation: **-1.0666**
- null 2.5–97.5% interval: **-0.11493 to +0.04982**
- one-sided p(null >= observed): **0.8616**
- one-sided lower-tail p: **0.1385**
- frozen primary verdict: **FAIL**

The source-level effect is not merely non-significant; its calibrated excess is negative.

## Secondary species diagnostics

These species-specific results were predeclared as secondary diagnostics and do not replace the source-level primary verdict.

| species | n | observed | null mean | calibrated excess | p upper |
|---|---:|---:|---:|---:|---:|
| *Hipposideros armiger* | 8 | -0.02972 | -0.04901 | **+0.01929** | 0.3721 |
| *Hipposideros pratti* | 5 | -0.12177 | -0.01311 | **-0.10866** | 0.9678 |

For *H. armiger*, the secondary calibrated direction is weakly positive but far from the frozen source-level criterion.

For *H. pratti*, the secondary calibrated direction is negative. Because species-specific tests are secondary, this is evidence of heterogeneity worth reporting, not a new confirmatory "anti-identity" claim.

## Interpretation

The independent Hipposideros source does **not** prospectively replicate the centered vertical-individuality rule under the frozen species-stratified protocol.

This strengthens the generality boundary:

> repeatable centered vertical individuality is a real pattern in multiple bat systems, but it is not a universal property of bat tracking datasets or species under the same estimator.

The result is compatible with substantial taxon/context dependence in the stability of vertical organization.

## No-rescue rule

Do not rescue this FAIL by:
- changing the 5-km grid;
- changing centered-height bins;
- pooling species after seeing the result;
- dropping *H. pratti* and promoting *H. armiger*;
- lowering fix/session or common-support thresholds;
- switching to absolute height;
- selecting a different altitude reference;
- opening temperature, speed, competition or other mechanism analyses to overwrite the primary verdict.

Any future Hipposideros ecological follow-up must be explicitly labeled post-primary mechanism exploration and cannot alter this external replication verdict.

The frozen JAE v0.3.8 submission on `main` remains unchanged.
