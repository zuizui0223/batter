# Claim amendment history — Supporting Information

Date: 2026-09-27

This document records the analytical history relevant to interpretation. Historical results are
retained; later calibration changes their biological interpretation rather than erasing them.

## v0.3 — original comparative architecture synthesis

The original session-level decomposition used:

- conditional identity, `G_cond`;
- ordinary marginal identity, `G_marg`;
- `G_adv = G_cond - G_marg`.

Raw signs suggested conditional-dominant panels and one marginal-dominant
*Phyllostomus hastatus* 2022 panel.

This stage was empirically frozen after an outcome-blind public source screen.

## v0.3.1 — focal claim ceiling

An independently frozen focal refinement was reconciled with the comparative paper.

Although early-to-late identity assignment in *Tadarida teniotis* was strongly supported
(exact p = 0.000174), a stronger test of a stable individual-specific residual cell × height map
after marginal altitude adjustment was not supported (p = 0.160).

The manuscript therefore stopped describing positive conditional information as proof of a
stable place-specific route.

## v0.3.3 — manuscript-ready architecture version

The paper was expanded and formatted for Journal of Animal Ecology, with the central language
still describing multiple predictive architectures.

This version was later placed on scientific hold and marked DO NOT SUBMIT.

## v0.3.4 — estimator calibration and horizontal standardization

A diagnostic concern was raised after the original results were known:

1. the finite-sample exchangeability expectation of `G_adv` might not be zero;
2. ordinary marginal identity might inherit horizontal cell-use differences.

The *Tadarida* calibration algorithm was frozen before its calibration output was opened.
It showed a strongly negative null for `G_adv` and a large shift in marginal identity after
self and other profiles were integrated using identical horizontal weights.

Before opening any non-*Tadarida* calibration output, one common cross-panel calibration
contract was frozen. The decisive result was the 2022 *P. hastatus* panel:

- original `G_adv = -0.120`;
- common-cell conditional increment = +0.0066.

The sole strong marginal-dominant panel therefore disappeared. The multiple-architecture
interpretation was explicitly superseded.

The revised primary biological statement became:

> identity-matched vertical profiles retain more held-out predictive information than expected
> under session-level exchangeability after occupancy among the tested horizontal cells is
> standardized.

## Residual-confound tests frozen before output

Before rewriting the paper, three focal tests were frozen with explicit decision rules:

- AGL common-cell calibration;
- night-endpoint-neighbourhood exclusion;
- 2.5- and 10-km grain sensitivity.

Results:

- AGL 5 km: PASS, p = 0.0161;
- AGL 2.5 km: PASS, p = 0.011;
- AGL 10 km: FAIL, p = 0.1018;
- 1-km endpoint-neighbourhood exclusion: FAIL, p = 0.1109;
- fixed 0.5- and 2-km endpoint sensitivities also failed.

Accordingly, the revised manuscript explicitly limits the claim to coarse horizontal occupancy
at the tested scale and retains fine-scale/central-place structure as a possible contributor.

## Governance rule

No failed result above was rescued by changing its predeclared threshold, radius, grain,
permutation unit, smoothing parameter or source set after output was opened.

The public-data source universe remains closed.
