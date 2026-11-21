# Ducke measured-food source v2: pre-run (post-outcome) specificity and design-stratum audit

2026-11-20 | exploratory, already-open original source. This prospective *code freeze within a post-hoc source* cannot turn results into confirmation.

## Fixed input
- Original user-supplied Dryad ZIP SHA256 `55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce`; XLSX SHA256 `1fad327f61de4f144a44d1d889726ee8743d4edaf1eae87cdc2d5e2bc86bb9a6`.
- Prior exact same-plot/same-date and paper-period eligibility: 46 plots, 103 matched plot-nights, 810 captures and 573 frugivores, 7 RAPELD source layout blocks. Missing fruit rows are NOT zero imputed. Response is **conditional captured-guild fraction**, not absolute occurrence, actual foraging or a species SDM.
- Frozen original source figure-4 list: 12 bat-food candidate fruit genera; other 10 original listed genera have NOT been established to be uneaten by all bats. Neither group is a causal treatment.

## Frozen models
Same L2 ridge penalty `0.15`, same training-only feature normalization, same held-out plots and equal-site log score as v1. Baseline = elevation + sampled PO-design indicator + count of eligible matched nights. Candidate regressors are fixed and evaluated jointly, not selected after seeing this diagnostic:
1. B = baseline;
2. F = B + log1p(candidate 12-genera fruiting-plant count);
3. O = B + log1p(remaining 10-genera fruiting-plant count);
4. FO = B + both log1p F and log1p O;
5. G = B + log1p(total 22-genera fruiting-plant count).

## Frozen comparisons
- **Primary specificity challenge:** `FO - O` (food candidate increment beyond other fruits) and `FO - F` (other fruits increment beyond food candidates) in equal-group heldout mean log-score. Also `F-O` and `FO-G` reported as *model contrasts*, not causal effects.
- Full 46 eligible plots: seven entire source layout blocks held out; leave-one-plot-out is an explicitly weaker, dependent sensitivity.
- Additional fixed *design-stratum check*: analyze only the 29 plot sources from L3–L8 (not the 17 added PO-design sites), with six entire L3–L8 blocks. This is an exploratory change in target population and sample size, **not a rescue of the primary seven-block result**.
- Run each model for `frug`, `glean`, `nectar`. These guild shares are compositional and dependent; cross-guild contrast is descriptive only.
- No new p-values, bootstrap CI or multiple testing thresholds; report all fold signs, support and conditional increments regardless of direction. Do not pool original bat captures as independent sites or infer physical height.

## Interpretation gates
If `FO-O` is positive but small or mixed across blocks, it is **not** evidence of trophic specificity. If `FO-O` is negative/nonpositive, downgrade any phrase suggesting unique 12-genera contribution after other-genera control. Absence of original vegetation clutter, detector registration, plot-relative effort and genuinely independent geographic populations remains limiting in every case. The 2026 3D bat tracking sources remain distinct and do not provide a matched 5D resource+height observational record.

## Reproducibility and record safety
Use the existing pure-stdlib `ducke_guild_cv_engine_v1.predict` function, no raw observed animal IDs or coordinates committed to GitHub. Source-sensitive aggregate effects go to `ducke_source_specificity_v2.json` only after tests and code are fixed. Baseline v1 `F-B` must replay `+0.016084661100832526` to within 1e-7 for frugivore seven-block mean; if not, fail closed.