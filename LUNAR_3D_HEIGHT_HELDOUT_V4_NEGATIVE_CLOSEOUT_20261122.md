# Lunar 3D GPS project: first height-open test and negative result closeout (2026-11-22)

## Actual execution and reproducibility

This closeout describes the first and only original-source native-height test after frozen source/exposure and predictive-scoring rules. It must **not** be merged into frozen JAE v0.3.8 or promoted to a new ecological positive finding.

- Source/exposure v1/v2 PASS/STOP: CI [run 45021250335](https://github.com/zuizui0223/batter/actions/runs/45021250335), artifact 14753319752. No numerical GPS heights inspected.
- Original-reference-qualified v3: CI [run 45022625250](https://github.com/zuizui0223/batter/actions/runs/45022625250), artifact 14754516922; before numeric heights, *P. hastatus* 2021–22 had 9 matched animals/13 cells×night-clock strata; *Hypsignathus* had 6 matched animals/17 strata. *Hypsignathus* retained the original v1 short-duration STOP (19 days vs frozen 35), while passing separately declared v2/v3 short-time matched gates. No subject had multiple tag IDs in eligible v3 reference.
- [Frozen protocol](prospective/lunar_3d/LUNAR_V4_HEIGHT_SCORE_PREOPEN_FREEZE.md) committed at `9d48ea2dbe2f192fe1b40951ca486a1860cec1e2` before numeric lunar height was opened. Numeric-binning boundary implementation corrected (using `bisect_left` for frozen inclusivity) before the original-data v4 run.
- V4 original data CI **SUCCESS**: [run 45022997391](https://github.com/zuizui0223/batter/actions/runs/45022997391), artifact **14754825080** `lunar-v4-night-block-native-height-scores`. Source-free v4 synthetic tests passed. Code: `prospective/lunar_3d/lunar_height_score_v4.py`, test `test_lunar_height_score_v4.py`.
- Inputs: original hash-pinned published Movebank GPS and reference CSVs (source contracts), non-outlier fixes only, v3 source-verified same-individual/site/year/0.05° cell/2-hour local-solar-time matched repeated nights; outcome=recorded native height, **not AGL**; altitude bins relative to a **training-night-only individual median**.
- Predictive comparison: B0 pooled within matched stratum versus B1 pooled additionally by bright/dark geometry, both smoothed with Jeffreys alpha 0.5, fixed five bins; whole-night excluded scoring; equal stratum, night, exposure and individual averaging; descriptive 5,000 individual bootstrap CIs. This is not a weather/habitat-adjusted causal analysis.

## First real native-altitude evidence: heldout prediction fails

| Exact target / test | *Phyllostomus hastatus* 2021–22 (primary) | *Hypsignathus monstrosus* (secondary short-period) |
|---|---:|---:|
| Native height coordinate | GPS MSL (not AGL) | GPS ellipsoid (not AGL) |
| Qualified v3 animals / spatial-clock strata | 9 / 13 | 6 / 17 |
| Scored GPS fixes / distinct individual nights | 1,614 / 62 | 1,826 / 43 |
| Whole-night×stratum×exposure heldout folds | 85 | 90 |
| B0 absolute heldout log score, nats/fix | -0.83017527 | -0.95645897 |
| B1 absolute heldout log score, nats/fix | -0.89275599 | -0.96835212 |
| **Δ = B1−B0, nats/fix** | **−0.06258072** | **−0.01189315** |
| Animal-bootstrap descriptive 95% interval | **[−0.09286730, −0.03242784]** | [−0.07161513, +0.04370400] |
| Animals with positive incremental score | **1/9** | **2/6** |
| One-sided animal signflip tail (positive alternative) | 0.99805 | 0.68750 |

**Decision:** The frozen predictive lunar effect **FAILS** in the primary source, with a negative interval. The secondary context does not rescue/confirm a positive effect. These are proper-score results for this *particular simple lunar-binned predictor* with limited within-animal nights. Do NOT assert lunar light has no biological effect or that other states/habitat interactions are absent. Added lunar stratification can be penalized for sparse class-specific training: a negative increment is not a direct estimate of predation or response magnitude. The bootstrap assumes exchangeable animals; 9 and 6 animals provide limited independent information.

## Predeclared sensor and shape diagnostics

- *P. hastatus*: native MSL GPS bright/dark **pooled**, unmatched height medians 24/32 m; these are descriptive, confounded by individual/date, not a valid paired lunar shift. All 1,614 admitted native heights were finite/within ±10 km. Both `gps_hdop` and `gps_vdop` were present in only **21.62%** of selected fixes, below the frozen >=80% sensitivity threshold; therefore GPS-DOP-filtered test **NOT ESTIMABLE**.
- *Hypsignathus*: native ellipsoid bright/dark pooled medians 488.05/487.90 m (not above-ground heights). All 1,826 selected native heights finite/within range. `gps_dop` available in **100%**. With predeclared DOP<=8, 1,792 fixes / 6 animals remain: Δ **−0.01928937 nats/fix**, bootstrap interval **[−0.07747406,+0.03735551]**, 2/6 animals positive. This corroborates *absence of improvement in this predictor*, not absence of biological influence.
- Secondary explicitly *non-forecast* night-centered shape scores: *P. hastatus* Δ **−0.02905226** (95% [−0.04941820,−0.00787927], 2/9 positive); *Hypsignathus* Δ **−0.04161073** (95% [−0.06368171,−0.02042671], 0/6 positive). Centering using target-night median is allowed solely to describe the per-night profile **shape**; it cannot predict unobserved absolute height or independent state changes.
- No calibrated DEM/geoid/GPS-height uncertainty was delivered. The earlier tag-offset robustness in `TAG_ALTITUDE_BIAS_AUDIT_RESULT.md` concerns a distinct individual-identity task; it cannot validate these new lunar AGL effects.

## Scientific claim ceiling and stop

The following **are not demonstrated**: lunar reorganization of the bat 3D fear landscape; moon-induced reduction in AGL/under-canopy flight; diet-dependent resource tracking; causal predation avoidance; moonlight-vs-cloud quasi-random treatment; external generality; height/behavioral state mediation. The study also lacks suitable recording effort/non-flight denominator to test lunar suppression of total nightly activity. Moon categories represent geometry (Moon elevation + phase, twilight filter), not measured light incident on the bat.

**No rescue search**: Do not tune bins, individual/cell thresholds, exposure definitions, DOP limits, holdout units or species after seeing these height scores to obtain a positive result in these opened sources. If pursued further, predeclare a materially different question and source under an independent programme; transparent post-hoc diagnostics are allowed only to explain the negative result, not to overwrite this comparison.

**State:** source audit completed; first original-data lunar vertical proper-score outcome negative; manuscript JAE release and resource×SDM main records untouched.
