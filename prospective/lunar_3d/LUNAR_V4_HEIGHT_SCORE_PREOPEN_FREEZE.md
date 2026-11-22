# Lunar source v4: PRE-HEIGHT frozen scored comparison (2026-11-22)

**Frozen before any numerical native GPS height value from the new lunar project is opened.** Source support already inspected, not altitude outcomes. See v1/v2 original support and v3 follow-up data admission at GitHub Actions run #45022625250 (original authenticated source + reference; v3 PASS P. hastatus 9 animals/13 matched strata; H. monstrosus 6 animals/17 matched strata). We do not change v1/v2 outcomes and we do not claim an independent data source or general dietary law.

## Analysis target and two source roles

- **Primary** *Phyllostomus hastatus* 2021–22, DOI 10.5441/001/1.321, native `height_above_msl`, within-population v1+v2+v3 eligible.
- **Secondary exploratory** *Hypsignathus monstrosus*, DOI 10.5441/001/1.278, native `height_above_ellipsoid`, v2+v3 eligible but *failed* v1's independently frozen >=35-day span criterion (its span was 19 days).
- Do not pool estimates in meters across MSL and ellipsoid frames; no AGL is obtained.
- Endpoint: predictive conditional distribution of **recorded GPS altitude among recorded fixes**. No exposure denominator for nightly total activity, no habitat-specific predation or prey mechanism, no measured solar radiation at the animal.

## Locked observations and eligibility

Download original GPS and reference CSVs, verify MD5/length against `contract/{phyllostomus,hypsignathus}_replication_v1.json`; use the exact v3 source reference and source outlier logic, same moon Sun/altitude/classification, GPS presence, within animal × site × local-solar year × 0.05° cell × 2-hour local-solar clock, and same 2 nights/exposure and 8 fixes/night + 20 fixes/exposure minimum, within <=45-day gap. This **height-blind** stratum list is computed before parsing numeric altitudes. No source after v3 admission is added. No changed threshold after height response is seen.

On v3 admitted records only, parse native numeric GPS height. Exclude missing or nonfinite height and implausible |>10,000m| values. Report counts per exposure and source; do not tune this range after inspecting results. The original filters apply to both baseline and lunar predictor and to all scored events.

## Fixed prediction algorithm / primary target

For every **whole local-solar-night** left out (all GPS fixes on that night for each animal/stratum), train only on the other nights of the same animal × site × year × 0.05° cell × 2-hour clock stratum. Never split fixes randomly. To avoid additive constant tag offset, anchor class thresholds to the **training-only median native height of the same animal**, pooling its other eligible matched strata and nights in the same calendar year and study site (excluding all target-night records for that animal). Do not recompute the median using heldout observations. Discretize `height - training_median` into five fixed bins: (-∞, -100], (-100, -25], (-25,25], (25,100], (100,∞), measured in meters. This adjustment does **not** remove night-varying GPS height error or genuine between-night mean-height differences.

**Baseline B0**: pooled training-night bin distribution conditional on individual+matched spatial cell+clock, with symmetric Dirichlet(0.5) smoothing. **Lunar B1**: same fixed source rows and bins but condition additionally on the genuinely observed astronomical bright/dark category (same smoothing). The same animal, target fixes, bin boundaries and train-fold median apply to both. Moon category is a covariate, never a derived height label. No other covariates entered here: the matched design controls coarse XY/clock, and this is *not* a full weather/habitat/season-adjusted causal model.

Primary score is heldout log probability of each observed height bin (nats/fix); **difference B1−B0**. Report absolute B0 and B1 and paired Δ. Within each animal, mean over fixes in each stratum×night×exposure, then average strata within night+exposure, nights within exposure, and **equal weight bright/dark exposures**; finally equal-weight biological individuals. Cross-study effects must be kept separate. Require >=5 scored animals and both classes per individual; otherwise STOP this comparison.

Uncertainty: 5,000 animal-level bootstrap replicates using fixed seed 20261122 for 95% descriptive percentile interval and enumerate all 2^n animal-level sign flips for a descriptive one-sided sign-flip tail proportion. Animal, not fix/stratum/night, is the inferential replication unit. Signflip and bootstrap rely on strong assumptions for small n and are not proof of random assignment. We will not adjust algorithms or promote a positive post-hoc model variant after these outputs.

## Registered source and sensor sensitivity

- Original published reference distinguishes MSL vs ellipsoid; neither is AGL. Without independently verified DEM/geoid and sensor calibration, no claims about distance from vegetation, canopy, ground or predator-exposure height.
- Inspect GPS DOP/HDOP/VDOP values **only after this contract is frozen**. A separate predeclared high-quality sensitivity uses `gps_hdop<=5` **and** `gps_vdop<=8` for *P. hastatus*, and `gps_dop<=8` for *Hypsignathus*. Require at least 80% of v3 admitted outcome rows to contain numerical applicable DOP and >=5 individuals with retained matched stratum support after filtering; else sensitivity marked NOT ESTIMABLE. Report quality nonmissing fraction in every case; do not substitute another filter.
- Do not use source outlier flag derived from numerical altitude except source-authored flags already in v3.
- If the scored lunar increment is positive but quality sensitivity non-estimable, **do not claim robustness to GPS measurement error**. If matched groups disappear after excluding extreme heights, no broadened source set may be used.
- Shape-only exploratory secondary: within each heldout/training night×stratum, subtract the **same night's** median and use fixed five bins [-100,-25,25,100]; the returned log score is for **centered session shape**, NOT forecasting original altitude or flight's absolute height. Do not substitute this for failed primary. The median of target heights is used only to define this secondary target.

## Acceptance and interpretation

- P. hastatus primary supports a **predictive lunar effect** only if B1−B0 equal-animal mean >0 and 95% animal-bootstrap interval lies >0, and the added-information sign-flip proportion is <=0.05. Even this is observational and does not establish that moonlight is the causal input, that the animal responds to visual predation, or that altitude of insects is reallocated.
- H. monstrosus is independent within-lunation *context* but not external population confirmation of a general law. Report exact scores and support; do not combine source-level p values.
- A negative or interval-overlapping result stops the claim; future hypothesis tuning must use an external unopened dataset.
- Frozen JAE v0.3.8 / `main`, resource×SDM master ledger and previous assertions remain unchanged.

Expected reproducibility artifact: anonymized source-level scientific metrics, predeclared quality profile, fold counts, exact parameter values, CI, descriptive p values, and action run URL. Never commit raw GPS, individual ID, timestamps or fine spatial coordinates.
