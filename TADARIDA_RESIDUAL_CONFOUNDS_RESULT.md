# Tadarida residual-confound robustness v1 — result

Date: 2026-09-27

The decision rules were frozen in `contract/tadarida_residual_confounds_v1.json` before these
outputs were opened.

## Predeclared verdict

- **A — AGL common-cell calibration: PASS**
- **B — 1-km night-endpoint/roost-proxy exclusion: FAIL**
- **C — grid sensitivity: PARTIAL** (2.5 km PASS; 10 km FAIL)

Therefore the strongest predeclared focal claim is **not authorized**.

## A. Terrain-relative AGL identity survives at 5 km

The implementation reproduced the frozen ordinary AGL decomposition and then standardized self
and other vertical profiles to the same horizontal cell-use weights.

| Quantity | Value |
|---|---:|
| Evaluable individuals | 6 |
| Common-cell AGL marginal identity | +0.266 |
| Permutation-null mean | -0.180 |
| Observed − null mean | **+0.446** |
| One-sided permutation p | **0.0161** |
| Individual-bootstrap 95% interval | -0.021 to +0.598 |

The frozen pass rule is met.

Thus the focal vertical-identity signal is not restricted to MSL altitude: terrain-relative AGL
contains repeatable individual information after 5-km horizontal cell-use standardization.

The individual bootstrap interval remains broad, so this result should not be described as
uniformly strong across all six evaluable bats.

## B. Night-endpoint neighborhood exclusion does not pass the primary rule

The exclusion used only x-y and time. For each bat, the first five and last five fixes of every
retained BatDay were pooled, and the medoid endpoint defined a fixed night-endpoint proxy.
No vertical outcome was used to define the proxy.

At the predeclared 1-km radius:

| Quantity | Value |
|---|---:|
| Events removed | 602 |
| Events retained | 9,227 |
| Evaluable individuals | 6 |
| Common-cell AGL marginal identity | +0.099 |
| Permutation-null mean | -0.180 |
| Observed − null mean | +0.279 |
| One-sided permutation p | **0.1109** |
| Individual-bootstrap 95% interval | -0.413 to +0.563 |

This **fails** the frozen p<=0.05 rule.

The fixed-radius sensitivities fail in the same direction:

- 500 m: common-cell marginal +0.131, calibrated +0.303, p=0.0978;
- 2,000 m: +0.059, calibrated +0.266, p=0.1446.

The endpoint proxy is not asserted to be the true biological roost. Endpoint clusters are diffuse
for several bats, so the correct inference is limited:

> Removing the predeclared departure/arrival neighborhood weakens the standardized AGL identity
> enough that the primary calibration test no longer passes.

Accordingly, **central-place departure/arrival structure remains a viable contributor** to the
focal terrain-relative identity result.

A secondary common-cell conditional increment remains above its estimator null after the 1-km
exclusion (raw +0.118, permutation p=0.0158), but the contract designated common-cell marginal
identity as the primary endpoint. This secondary result cannot rescue the failed primary test.

## C. The focal AGL result is scale-dependent

### 2.5 km — PASS

- n=5;
- common-cell marginal = **+0.603**;
- null mean = -0.109;
- calibrated difference = **+0.712**;
- p=**0.011**;
- bootstrap 95% = +0.046 to +1.357.

### 10 km — FAIL

- n=7;
- common-cell marginal = -0.013;
- null mean = -0.250;
- calibrated difference = +0.237;
- p=**0.1018**;
- bootstrap 95% = -0.343 to +0.235.

The predeclared global scale-robustness rule therefore fails.

The focal terrain-relative result is supported at 2.5 and 5 km, but not at 10 km.

## Allowed focal interpretation

> **European free-tailed bats show repeatable terrain-relative vertical identity after horizontal
> cell-use standardization at fine-to-intermediate horizontal grain (2.5–5 km).**

But the manuscript must also state:

- the effect is not established at 10 km;
- the 1-km night-endpoint exclusion does not pass;
- therefore central-place departure/arrival structure remains a possible contributor.

## Consequence for the cross-panel paper

The cross-panel 5-km result—vertical identity beyond horizontal cell-use weighting—remains the
main comparative finding.

The focal AGL analysis supports the vertical interpretation at the primary 5-km grain, but it
does **not** license a stronger claim that the effect is independent of central-place behavior or
spatial scale.

No further endpoint-proxy retuning or new radii are permitted within this analysis family.
