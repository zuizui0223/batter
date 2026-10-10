# Molossus co-foraging functional-threshold source gate V1 — frozen before author file opening

**Status 2026-10-08: original author Mendeley metadata ONLY; no 5-second success, attack, call-density, flight, or prey records have been retrieved or analyzed for this proposed programme.**

## Fixed source and non-novelty boundary

Source: Krivoruchko et al. (2024), *PNAS*, DOI `10.1073/pnas.2321724121`. Open author data [Mendeley v1](https://doi.org/10.17632/h7krh54zxc.1), dataset ID EXACTLY `h7krh54zxc`. Published description: **10 *Molossus nigricans* bats** with counts of attempted attacks, successfully completed captures inferred using chewing after attacks, and detected conspecific calls in **5-second bins**. The original authors ALREADY demonstrated a beneficial range of low conspecific call density and a decline at high densities. That nonlinear population curve is firmly **PRIOR ART**.

## New and narrower question

Are differences among independently recognized bats in the *shape* or crossover of their conspecific-density response reproducible **across separated foraging bouts/nights**, after allowing distinct baselines and different exposure distributions, and can that response predict independently held-out successful capture events?

This would concern **functional individual modulation of social co-use**, not 3D route identity, individual learning or 3D field niche adaptation. No analysis of any outcome is permitted until the categorical gate below is documented and an endpoint is frozen.

## Categorical support requirements (not outcome thresholds)

A true independent confirmatory **individual social-payoff crossover** requires all of:
1. Stable physical ID mapping for >=8 evaluable bats from the originally described ten, never constructed from repeated 5-second windows.
2. An explicit timestamp + day/independent-bout boundary; >=3 separated bouts per bat, including separate occasions held out in time. Adjacent 5-sec bins and multiple attacks in the same uninterrupted foraging episode do NOT count as independent occasions. Distinct days are preferred; if not available, strong evidence of discrete nonadjacent bouts plus a blocked out-of-bout design is mandatory, and the result is less general.
3. At least 2 independent separated bouts per bat that each genuinely contain both a prespecified **low/intermediate** and **high** conspecific-call exposure regime, with at least one held out from estimation. Do not select exposure cut-points to obtain a positive slope; prespecify cut-points on external acoustic biology or use a bounded continuous function with fixed knots based on training only.
4. Matched call-density definition and detection effort, recording-quality/time/device IDs, and success indicator availability. Conspecific **call counts** are not exact physical-bat counts; if identity correction cannot be made, label the predictor *acoustic social exposure*.
5. Enough independent bat×bout variation to distinguish individual random slopes from temporal shift, bat-specific measurement heteroscedasticity and pseudoreplication. If coverage fails, STOP; do not pool distinct species or fabricate unlabeled sessions.
6. Clear original publication statement of what constitutes a **successful attack**, and absence of data leakage: prey capture successes are outcomes, **not** predictors for acoustic density classification.

**Gate statuses:** `STOP_API_OR_SOURCE_INACCESSIBLE`, `STOP_NO_STABLE_PHYSICAL_ID`, `STOP_NO_INDEPENDENT_BOUT_REPLICATION`, `STOP_INSUFFICIENT_WITHIN_BOUT_DENSITY_CROSSING`, `HOLD_METADATA_ONLY_NEEDS_ORIGINAL_STRUCTURAL_FILES`, or (only with categorical proof) `PASS_TO_NEW_FROZEN_ENDPOINT_CONTRACT`.

The present metadata alone gives 10 claimed bats and 5-second measurements, **not** verified independent-bout labels. The DEFAULT STATUS is `HOLD_METADATA_ONLY_NEEDS_ORIGINAL_STRUCTURAL_FILES`; never assert eligibility from many rows.

## Conditional analysis design (only if support passes)

- Training: freeze and extract binned acoustic conspecific exposure and verified capture success by physical bat and independent bout. Fit a shared density-response function as prespecified by the *published* functional curve, plus bat-specific slope/threshold deviations estimated **on training bouts only**.
- Primary out-of-bout increment: difference in proper predictive score (e.g. held-out binomial log loss for success given a captured/attempted event or Poisson deviance of verified captures per valid effort-time), personal response vs a heteroscedastic shared-response model. **Fix one before reading numerical outcomes**.
- Validation: equal independent-bat weighting; fully held-out bouts; bat-cluster uncertainty and blocked negative controls; do not shuffle bat labels under unequal nuisance variance. Report all bat differences, including failure. Evaluate coverage/positivity across exposures.
- Separate mechanisms: observing distinct response curves DOES NOT tell acoustic masking vs physical congestion vs prey-resource supply; conspecific calls are exposure proxies and this observational source cannot causally identify those effects.
- This cannot estimate **3D route geometry**, which the author dataset does not claim to contain. A positive functional result would only bound future 3D policy hypotheses.
- STOP if no independent bouts or not enough source variation. Do not rescue with next-day windows that are really temporally contiguous segments or with outcomes already inspected.

## Frozen metadata-only access task

A separate exact-source script may call official Mendeley public endpoints:
- `GET https://api.data.mendeley.com/datasets/h7krh54zxc?version=1`
- `GET https://api.data.mendeley.com/datasets/h7krh54zxc/files?version=1`
Strictly request **JSON metadata** (file names/types/sizes, version/DOI) only. Do **not** follow `download_url` or `view_url` for biological measurements, do not open CSV lines or compute numerical effects. Result must distinguish HTTP403 API failure from absence of underlying data. Record any false parser assumptions chronologically and do not promote metadata PASS to numeric analyses.

The source may already contain bat IDs/time fields, but the metadata-only script **cannot verify** that; only a later source-header/bout-structure audit after an explicit separate gate could.

**Scientific disposition until proof:** a high-priority independent *functional*, **not 3D**, source candidate. No new biological effect and no publication-ready individual-threshold conclusion.
