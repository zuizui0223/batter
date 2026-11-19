# Lewanzik 2019 original XLSX recovery: blind structure gate and frozen analysis contract (2026-11-19)

Status: source retrieval attempt; **not** an empirical reanalysis until native file authenticity, schema, and reproducibility gates pass.

## Provenance

Primary published data: https://doi.org/10.5061/dryad.gp65g2t ; published filename `Lewanzik_etal_2019_JAE_DATA.xlsx` (83.76 KB).
Direct file_stream ID `83444` resolved by the published Dryad file link. Original article: https://pmc.ncbi.nlm.nih.gov/articles/PMC6849779/ .

Access checks in the assistant runtime: publication/metadata accessible; the actual file_stream download returned HTTP403, and local container had no DNS route. A GitHub Actions runner will separately attempt the documented file_stream and REST downloads and log each failure; no claim of downloadable raw data is made until SHA256 and workbook sheet/header receipt succeed.

## Exact design (published)

- One 3-minute block: 1 min EMPTY audio (pre); 1 min bat search calls with 0/12/24/48/96 feeding buzzes; 1 min EMPTY audio (post).
- 12 lakes × 6 playback emitter species × 5 buzz levels, one combination per lake in randomized order; the 3-min blocks are **not independent animal subjects**.
- Receivers: *Myotis daubentonii*, *Pipistrellus nathusii*, *P. pipistrellus*, and a pooled NEV (Nyctalus/Eptesicus/Vespertilio) group; the latter is NOT a species.
- Original response was Y_playback minus Y_pre, with X=Y_pre simultaneously included as predictor; this mechanically produces beta=rho−1 when stationary and no treatment effect. Original model fitted buzz × emitter and buzz² × emitter, **not** buzz × pre-density. Their negative baseline coefficient cannot by itself establish a density-moderated effect of cue information.
- 0 buzz = **search calls played**, not silence. It is a valid 0-feeding-information reference when emitter/search acoustics are matched, but not a no-social-information reference.
- Empty pre/post controls are time-adjacent; comparing absolute Y_playback to the pre period alone is potentially susceptible to temporal drift/response carryover.

## Pre-outcome source gate

Try only URLs corresponding to the published original Dryad file and documented dataset API. Validate: HTTP status, response size, ZIP magic, xlsx workbook.xml + relationships + worksheets, sheet names and column header candidates. Record source URL, file size, SHA256 and schema in a JSON receipt. **Do not output biological row values, effect signs, conditional subgroup estimates or p-values in this gate.** Do not upload full bat data as artifacts or commit it.

If original file cannot be downloaded or lacks pre/playback/site/buzz/emitter identifiers, STOP. No data-derived substitution and no inferred "true zero" in incomplete row sets.

## Primary prospectively frozen target after blind schema gate

For each receiver category separately and with lake as held-out group, estimate the change in the **treatment response to buzz content** with baseline conspecific activity using a prospective regression of Y_playback, NOT raw Δ on X. Exact model form to start:

Y_playback ~ f(X_pre) + buzz_level + emitter + buzz_level×emitter + buzz_level×f(X_pre) + minutes_after_sunset + other_species + (1 | lake)

- Outcome: original absolute species/group bat-seconds per playback minute, with appropriate overdispersion / transformed-scale check.
- X_pre: same species/group pre-minute activity, transformed log1p and standardized using TRAINING lakes only; no external taxonomy conversion.
- Buzz levels: predeclared ordered 0/12/24/48/96, linear ordinal for primary interaction; if same-emitter comparisons exist at each lake, hold emitter and site constant in counterfactual marginal contrasts.
- f(X_pre) = log1p(X_pre) as primary; sensitivity is flexible monotone (not outcome-optimized) and site-within centering.
- Contrast C(low), C(high) = predicted Y_playback(buzz=96,X_pre=a) − predicted Y_playback(buzz=0,X_pre=a) for the same emitter/lake/clock context; primary moderator M=C(high)−C(low) at TRAINING distribution pre-specified low/high quantiles (25% vs 75%).
- Primary performance: leave-one-lake-out predictive improvement on held-out absolute activity for main-effects versus buzz×X_pre, report all 12 lake-group scores and sign counts. No pseudo-independent 6×5×receiver replication. If a lake is structurally missing for a response species, report test gate and actual independent lake count.
- Uncertainty: lake-level bootstrap/cluster-robust small-sample approach, **not** naive row bootstrap. If fewer than 8 independently evaluable lakes, STOP inference.
- If buzz-zero and buzz-96 are not jointly observed in independent lake×emitter strata after source filtering, STOP the primary contrast rather than extrapolate.
- A positive moderator would show pre-activity conditions modify the *relative* response to buzz information in this setting. It would **not** identify competition costs, reciprocity, adaptive fitness benefit, or species-wide universality.

Secondary nonconfirmation: model post minute only as exploratory time-asymmetric response; it can be altered by carryover. Any within-site negative baseline slope in change-scores is reported as an identification sensitivity, NOT a novel biological law.

## Published outcome boundary

The paper already establishes context-sensitive eavesdropping and species-specific buzz response in this exact source. Even if the new interaction is detected here, a true independent macro generalization needs untouched new source studies with the same estimand and a lake/population/study held-out gate.

See `CROSS_STUDY_SIGN_AND_BASELINE_COUPLING_AUDIT_V1.md` and scripts.

Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC6849779/ ; https://doi.org/10.5061/dryad.gp65g2t .
